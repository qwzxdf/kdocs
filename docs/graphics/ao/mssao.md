---
title: MSSAO
tags:
  - 描画
---

# MSSAO

SSAO は半径を大きくするほど遠くの暗がりを拾えますが、読む範囲が広がって重くなります。かといってサンプル数を増やさずに散らすとノイズが出て、それをぼかして消すと細部も一緒にぼやけます。MSSAO（Multi-Resolution Screen-Space Ambient Occlusion）は、この行き詰まりを<strong>解像度を変えて計算する</strong>ことで抜けようとした方式です。ここでは、Thai-Duong Hoang と Kok-Lim Low の論文を読んで、アルゴリズムを説明します。

!!! tip "ポイント"
    - 近くの遮蔽物による細かい影は細かい解像度で、遠くの遮蔽物による柔らかい影は粗い解像度で求めます。どの解像度でもサンプリングの範囲は小さいままで済みます。
    - 層の結果は足し合わせるのではなく、最大値と平均を組み合わせて合成します。
    - 層をまたぐ拡大には深度と法線を見るバイラテラル アップサンプルを使います。
    - 最も細かい層では最後のぼかしが要りません。細部が保たれます。
    - 代わりにメモリを多く使います。論文では普通の SSAO の 1.85 倍です。

!!! info "このページを読む前に"
    - [SSAO（半球）](ssao-hemisphere.md)（サンプルを半球に散らす基本の SSAO）
    - [SAO](sao.md)（深度ミップでキャッシュ効率を上げる方法）
    - [Upsampling AO](filtering/upsample.md)（バイラテラル アップサンプルの考え方）

## 発想 {#idea}

AO は遠くの遮蔽物ほど低周波になります。遠くから来る遮蔽は境目がなだらかで、細かい解像度で見る意味がありません。反対に近くの遮蔽物が作る影は境目がはっきりしていて、細かい解像度が要ります。そこで、半球を入れ子の複数の半球に分け大きい半球ほど粗い解像度で計算します。

ただし、大きい半球のサンプルを内側の半球との「差分」の部分だけに限ることはしません。それぞれの半球ではその半球全体からサンプルを取ります。粗い解像度では p に近い画素が p 自身と同じ画素にまとめられてしまい近くの遮蔽物を取り逃がします。この取り逃しは最後に平均を使って補います。

論文は似て見える別の発想とは違うと書いています。遠くの遮蔽物を少ないサンプルで拾いその寄与を重く掛ける方式です。この方式は寄与を大きくするので、ブロック状のアーティファクトが出て、それをぼかすと画像が全体にぼやけます。

<svg class="fig flow" viewBox="0 0 760 260" role="img" aria-label="入れ子の半球と解像度"><defs><marker id="mh" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">半球を入れ子に分け、大きい半球ほど粗い解像度で計算する（MSSAO の考え方）</text><line x1="30" y1="220" x2="740" y2="220" stroke="currentColor" stroke-width="3"/><path d="M30,220 A170,170 0 0 1 370,220 Z" fill="rgba(148,163,184,0.12)" stroke="#94a3b8" stroke-width="2"/><text x="200" y="44" text-anchor="middle" style="font-size:12px;font-weight:700">Res3（粗い）</text><path d="M90,220 A110,110 0 0 1 310,220 Z" fill="rgba(76,139,245,0.12)" stroke="#4c8bf5" stroke-width="2"/><text x="200" y="104" text-anchor="middle" style="font-size:12px;font-weight:700">Res2</text><path d="M145,220 A55,55 0 0 1 255,220 Z" fill="rgba(229,170,40,0.25)" stroke="#e5aa28" stroke-width="2"/><text x="200" y="159" text-anchor="middle" style="font-size:12px;font-weight:700">Res1（細かい）</text><circle cx="200" cy="220" r="6" fill="currentColor"/><text x="200" y="242" text-anchor="middle" style="font-size:13px;font-weight:700">着色点 p</text><circle cx="230" cy="192" r="5" fill="#e5484d"/><text x="240" y="186" text-anchor="start" style="font-size:12px;font-weight:400">q0</text><circle cx="285" cy="160" r="5" fill="#e5484d"/><text x="295" y="154" text-anchor="start" style="font-size:12px;font-weight:400">q1</text><circle cx="70" cy="150" r="5" fill="#e5484d"/><text x="80" y="144" text-anchor="start" style="font-size:12px;font-weight:400">q2</text><text x="410" y="70" text-anchor="start" style="font-size:13px;font-weight:400">・半球が大きいほど、粗い解像度で計算する</text><text x="410" y="98" text-anchor="start" style="font-size:13px;font-weight:400">・半球ごとに、その半球の全体から</text><text x="410" y="126" text-anchor="start" style="font-size:13px;font-weight:400">  サンプルを取る（内側との差分だけではない）</text><text x="410" y="154" text-anchor="start" style="font-size:13px;font-weight:400">・結果は最大値で合わせ、平均で補う</text><text x="410" y="182" text-anchor="start" style="font-size:13px;font-weight:400">・どの解像度でも、カーネルは数画素と小さい</text></svg>

## 処理の流れ {#flow}

論文の全体の手順は次のとおりです。

1. 最も細かい解像度で G バッファ（視点空間の位置と法線）を描く
2. 粗い側へ向かって G バッファをダウンサンプルする
3. 最も粗い層から細かい層へ向かって、層ごとに次の 3 つを行う。(a) 近傍をサンプルして近い遮蔽（AOnear）を求める (b) 1 つ粗い層の結果をフィルターして拡大し、遠い遮蔽（AOfar）にする (c) 2 つを合成する
4. 最も細かい層の合成結果が、最終的な AO になる

AOnear はその層の画素の近傍だけから求めます。AOfar はもう 1 つ粗い層で合成した結果を拡大したもので、それより遠い遮蔽を表します。粗い層の結果が細かい層へ順に引き継がれるので、細かい層の画素はすべての粗い層の情報を持った状態で合成を行います。

<svg class="fig flow" viewBox="0 0 760 290" role="img" aria-label="層ごとの処理の流れ"><defs><marker id="mc" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">粗い層から細かい層へ、合成した AO を引き継ぐ</text><rect x="40" y="102.0" width="56" height="56" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="68.0" y="176.0" text-anchor="middle" style="font-size:12px;font-weight:400">Res4（最も粗い）</text><rect x="166" y="90.0" width="80" height="80" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="206.0" y="188.0" text-anchor="middle" style="font-size:12px;font-weight:400">Res3</text><rect x="316" y="76.0" width="108" height="108" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="370.0" y="202.0" text-anchor="middle" style="font-size:12px;font-weight:400">Res2</text><rect x="494" y="60.0" width="140" height="140" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="564.0" y="218.0" text-anchor="middle" style="font-size:12px;font-weight:400">Res1（最も細かい）</text><line x1="98" y1="100" x2="164" y2="100" stroke="currentColor" stroke-width="2" marker-end="url(#mc)"/><text x="131.0" y="88" text-anchor="middle" style="font-size:11px;font-weight:400">拡大→AOfar</text><line x1="248" y1="100" x2="314" y2="100" stroke="currentColor" stroke-width="2" marker-end="url(#mc)"/><text x="281.0" y="88" text-anchor="middle" style="font-size:11px;font-weight:400">拡大→AOfar</text><line x1="426" y1="100" x2="492" y2="100" stroke="currentColor" stroke-width="2" marker-end="url(#mc)"/><text x="459.0" y="88" text-anchor="middle" style="font-size:11px;font-weight:400">拡大→AOfar</text><text x="380" y="40" text-anchor="middle" style="font-size:12px;font-weight:400">AOnear は各層で、その層の近傍から求める。AOfar は 1 つ粗い層の結果をフィルターして拡大した値</text><text x="380" y="252" text-anchor="middle" style="font-size:12px;font-weight:400">G バッファ（位置・法線）は、Res1 から Res4 へ向かって、4 画素ずつまとめて下げておく</text><text x="380" y="272" text-anchor="middle" style="font-size:12px;font-weight:400">合成した値は (最大値, 和, 個数) の 3 つ組で、粗い層から細かい層へ引き継ぐ</text></svg>

## ダウンサンプル {#downsample}

各画素は 1 つ細かい層の 4 つの子画素から、視点空間の位置と法線を作ります。平均ではなく中央値を使います。4 つの子画素を視点空間の深度で並べ真ん中の 2 つの位置を平均します。中央値は平均よりも値の揺れが小さいので、フレーム間の安定性が上がります。

ただし、中央値だけでは視点空間の点どうしの相対距離が保たれません。細かい層で遠かった点が粗い層では近づき遮蔽物が AO の影響半径の外の受け手に影を落とすアーティファクトが出ます。そこで、4 つの子画素の位置の最大距離が閾値 dthreshold より大きいときだけ、中央値の代わりに 4 つのうちの 1 つ（深度が 2 番目に小さいもの）をそのまま選びます。いつもこの方法にしないのは中央値ほど安定せずカメラの動きでひどいちらつきが出るためです。法線も位置と同じ方法で下げます。論文の実験では dthreshold は 1 です。

層の数は AO の影響半径で決まります。論文は 4 か 5 層が遠くまで届く AO と粗い層の解像度不足によるアーティファクトの、釣り合いのよい所だと書いています。層を増やしても粗くなるほど AO は低周波・低コントラストになるので、得られるものが少なくなります。

## サンプリング {#sampling}

AO の影響半径 dmax（視点空間の長さ）を最も細かい層の画面空間の半径に投影し、その層ごとに半分にしていきます。論文の式（5）は次のとおりです。

```text
r0(p) = s × dmax / (2 × z × tan(α / 2))
ri(p) = r0(p) / 2^i
Ri(p) = min(rmax, ri(p))
```

s は最も細かい層でのビューポートの大きさ（正方形を仮定）、α はカメラの視野角、z は画素 p の視点空間の深度です。近いほど z が小さいので半径は画面上で大きくなります。

半径はどの層でも rmax 画素に切り詰めます。細かい層は半球が小さいので ri をそのまま使わなくてよく、カメラが物体に近づいたときの半径の暴走も防げます。論文の標準値は rmax = 5 で、これは 11×11 画素のカーネルに当たります。

11×11 の全部の画素は読まず 1 画素おきに 36 点だけ読みます。121 回のテクスチャ読み込みが 36 回になります。これは乱数を使わないインターリーブ サンプリングに似たパターンで、あとで 3×3 のぼかしを掛けて隙間を埋めます。最も細かい層だけは 16 点のポアソン ディスクでサンプリングし、最後のぼかしをしません。半径が小さいのでぼかさなくても十分だからです。式（5）の半径が 1 画素未満になる画素は、その層ではサンプルを取りません。

## AO の式 {#formula}

AOnear は N 個のサンプルから、次の式（6）で求めます。

```text
AOnear(p) = (1/N) × Σ ρ(p, di) × max(0, cosθi)
```

di はサンプル qi と p の視点空間での距離、θi は p の法線と p から qi へ向かうベクトルの角度です。ρ は距離による減衰で式（7）は次のとおりです。

```text
ρ(p, di) = 1 - min(1, (di / dmax)^2)
```

遮蔽物を小さい球と見なすと p から見込む立体角は距離の 2 乗に反比例するので、2 次の減衰にしています。この式はサンプルの向きと距離を別々に扱うのでなく、距離をサンプルの値の中に入れています。そのため、サンプルが画面空間の 2 次元にだけ散らばり少ないサンプル数でも分散が小さくなります。論文の図では Crytek の方式が幾何の小さな変化で 4/8 から 3/8 に不連続に変わるのに対して、この式は滑らかに変わります。

半球の下側にあるサンプルを捨てることはしません。棄却サンプリングは分散が大きくなるためです。

## 層の合成 {#combine}

層をまたぐ合成がこの方式の核心です。AOnear は (和, サンプル数) の組で、AOfar と合成結果は (最大値, 和, 総サンプル数) の 3 つ組で持ちます。式（10）は次のとおりです。

```text
最大値 = max(AOnear の和 / N, AOfar の最大値)
和     = AOnear の和 + AOfar の和
個数   = N + AOfar の個数
```

和とサンプル数を別々に持つのは、サンプルを取らない層（半径が 1 画素未満）があるためです。正規化した値だけを持つと最後の層で正しい平均を取り戻せません。

最も細かい層では最大値と平均を式（11）で 1 つにします。

```text
AOmax     = max(AOnear の和 / N, AOfar の最大値)
AOaverage = (AOfar の和 + AOnear の和) / (AOfar の個数 + N)
AOfinal   = 1 - (1 - AOmax) × (1 - AOaverage)
```

出力は 1 - AOfinal で、遮蔽されていない度合い（アクセシビリティ）です。

最大値を使う理由を論文は 2 つ挙げています。1 つは内側の遮蔽物が複数の層で重複して数えられるのを防ぐこと。もう 1 つはある層で取り逃した遮蔽をほかの層が拾えることです。SSAO は視線から見えない遮蔽を判定できず遠くのサンプルが近くの遮蔽を薄めてしまいます。最大値を残すとこの薄まりをある程度抑えられます。

最大値だけでは足りません。ある点が複数の層で遮蔽されていることが多く、最終値は最大値より大きくなるべきだからです。そこで、平均で最大値を調整します。式（11）は 0 ≤ AOmax ≤ AOfinal ≤ 1 になるようにできています。

## フィルターとアップサンプル {#filter}

層ごとに拡大の前に 3×3 の低域フィルターを掛けます。最大値を残していると隣り合う画素が別の層の最大値を持つため、出力が「きれい」になりません。フィルターはこれとインターリーブ サンプリングの隙間を一緒に解決します。重みは画素間の距離から `1 / ((dx + 1)(dy + 1))` と簡単に決めます。

拡大はバイラテラル アップサンプルです。現在の層の画素 p に対して、1 つ粗い層の最も近い 4 画素を混ぜます。各画素の重みは次の 3 つの積です。

- 双線形の重み: 9/16、3/16、3/16、1/16
- 法線の重み: `((n · ni + 1) / 2)^tn`（式 8）
- 深度の重み: `(1 / (1 + |zi - z|))^tz`（式 9）

tn と tz は許容度を表す冪で、シーンの大きさに依存します。小さいシーンでは近くの画素が視点空間でも近いため、大きな深度の差をより厳しく扱うよう冪を大きくします。論文の図では tn = 8、tz = 16 です。最近傍のブロック状の見た目と双線形の遮蔽の漏れをどちらも避けられます。

## 時間方向のフィルター {#temporal}

低解像度の G バッファはフレーム間で一貫しにくく、カメラが動くと画素が別の低解像度画素に切り替わって、ちらつきが出ます。ちらつきは主に物体の輪郭で起きます。論文は最後に時間的な再投影のパスを足すことで消しています。

現在の画素を前フレームの画面に投影し直し、前フレームの深度と近い（`|1 - zprev / pz| < ε`）なら見えていたと見なして、前フレームの AO と混ぜます。

```text
AOcurr = k × AOprev + (1 - k) × AO
```

k が大きいほど安定しますが、カメラが動くと残像のようにぼけます。論文では k = 0.5 が標準です。式の再投影は静的なシーンだけに使えます。動く物体にはオプティカル フローを G バッファに保存して補うと書かれています。

## HLSL で書く {#hlsl}

論文は擬似コードで書かれていて、シェーダーは載っていません。ここでは、論文の式（5）〜（11）と Table 1・4 の手順を HLSL に直して説明します。層ごとに 1 回ずつフルスクリーンのピクセル シェーダー（または Compute）で動かす想定です。このコードはコンパイルも実行もしていません。論文に書かれていない処理（画面外の扱いや正規化）は、私が足したのでコメントに「足した」と書きました。

### 定数と半径 {#hlsl-radius}

```hlsl
// 影響半径などのパラメーター。値は論文の実験で使われたもの（一例）。
static const float kAoRadius = 2.0;   // dmax：AO の影響半径（視点空間の長さ。シーンの単位）
static const float kRMax     = 5.0;   // 1 つの層で読む半径の上限（画素）。5 なら 11×11 の範囲
static const float kTn       = 8.0;   // 法線の許容度（冪）。大きいほど法線の差を厳しく見る
static const float kTz       = 16.0;  // 深度の許容度（冪）。シーンが小さいほど大きくする

// 視点空間の深度 z の画素に対する、最も細かい層での AO 半径（画素）。式 (5) の r0。
// viewport_height は最も細かい層の高さ、tan_half_fov は tan(α / 2)。
float FinestRadius(float z, float viewport_height, float tan_half_fov) {
  return viewport_height * kAoRadius / (2.0 * z * tan_half_fov);
}
```

`FinestRadius` は視点空間の長さ `kAoRadius` が、深度 `z` の位置で画面上の何画素に見えるかを返します。近い画素ほど `z` が小さいので半径は大きくなり遠い画素は小さくなります。

```hlsl
// level 番目の層（0 が最も細かい層）で読む半径（画素）。
// 論文の式 (5) は添字を 0 から振っていて、本文の説明（最も細かい層が Res1）とは 1 つずれている。
// ここでは、最も細かい層を level = 0 として扱う。
float KernelRadius(float finest_radius, int level) {
  float r = finest_radius / exp2(level);  // 層が 1 つ粗くなるごとに、半径（画素）は半分になる
  return min(kRMax, r);                   // 上限で切る。カメラが近いときの半径の暴走を防ぐ
}
```

粗い層は 1 画素が広い範囲を表すので、同じ世界の長さでも必要な画素数は半分になります。上限 `kRMax` で切るので近い画素や細かい層でも読む範囲は最大でも 11×11 に収まります。

### 近傍のサンプリング {#hlsl-near}

```hlsl
Texture2D<float4> gPosition;  // この層の視点空間の位置（xyz）
Texture2D<float4> gNormal;    // この層の視点空間の法線（xyz）

// 画素 pix の近傍から AOnear を求める。戻り値は (遮蔽の和, サンプル数)。式 (6)・(7)。
float2 AoNear(int2 pix, int2 size, float3 p, float3 n, float radius) {
  float sum = 0.0;
  float count = 0.0;
  int r = (int)floor(radius);       // 半径が 1 画素未満なら r = 0 になり、サンプルを取らない

  // 1 画素おきに読む（インターリーブ）。r = 5 なら -5, -3, -1, 1, 3, 5 の 6×6 = 36 点。
  for (int dy = -r; dy <= r; dy += 2) {
    for (int dx = -r; dx <= r; dx += 2) {
      if (dx == 0 && dy == 0) continue;               // 自分自身は読まない
      int2 q_pix = pix + int2(dx, dy);
      if (any(q_pix < 0) || any(q_pix >= size)) continue;  // 足した：画面外は数えない

      float3 d = gPosition.Load(int3(q_pix, 0)).xyz - p;  // p から遮蔽候補 q へ向かうベクトル
      float dist = length(d);
      if (dist < 1e-5) continue;                     // 足した：同じ点は向きが定まらない

      // 距離による減衰。dmax で 0 になり、近いほど 1 に近い（式 7）。
      float falloff = 1.0 - min(1.0, (dist * dist) / (kAoRadius * kAoRadius));
      // 法線の向きとの角度。半球の下側にある点は、負になるので 0 に切る。
      float cos_theta = saturate(dot(n, d / dist));

      sum += falloff * cos_theta;   // 遮蔽の寄与。近く・法線の向きにあるほど大きい
      count += 1.0;                 // 半球の下側のサンプルも数える（棄却しない）
    }
  }
  return float2(sum, count);
}
```

`sum` に足す値は距離の減衰と角度の積です。半球の下側に落ちたサンプルは `cos_theta` が 0 になって寄与しませんが、`count` には数えます。棄却すると分散が大きくなると論文が書いているためです。

最も細かい層は論文では 16 点のポアソン ディスクを使い最後のぼかしをしません。上のコードはそのほかの層のインターリーブの方だけを示しています。

### 合成 {#hlsl-combine}

```hlsl
// 3 つ組 (最大値, 遮蔽の和, 総サンプル数)。粗い層から細かい層へ引き継ぐ。
// 和と個数を別々に持つのは、サンプルを取らない層があっても、最後に平均を正しく出すため。

// 最も細かい層ではない層：AOnear と AOfar を合成する。式 (10)。
float3 CombineLevel(float2 near_sc, float3 far_mss) {
  float near_ao = near_sc.y > 0.0 ? near_sc.x / near_sc.y : 0.0;  // サンプルがない層は 0 とする
  return float3(max(near_ao, far_mss.x),   // 最大値：どの層かで取り逃した遮蔽を拾う
                near_sc.x + far_mss.y,     // 和：全層の遮蔽の合計
                near_sc.y + far_mss.z);    // 個数：全層のサンプル数の合計
}

// 最も細かい層：最大値と平均を 1 つにして、「遮蔽されていない度合い」を返す。式 (11)。
float FinalAccessibility(float2 near_sc, float3 far_mss) {
  float near_ao = near_sc.y > 0.0 ? near_sc.x / near_sc.y : 0.0;
  float ao_max = max(near_ao, far_mss.x);
  float ao_avg = (far_mss.y + near_sc.x) / max(far_mss.z + near_sc.y, 1.0);  // 全層の平均
  float ao_final = 1.0 - (1.0 - ao_max) * (1.0 - ao_avg);      // 最大値を平均で押し上げる
  return 1.0 - ao_final;   // 1 なら遮蔽なし、0 なら完全に遮蔽
}
```

`ao_final` は `ao_max` 以上 1 以下になります。最大値が 0.3 で平均が 0.2 なら `1 - 0.7 × 0.8 = 0.44` です。最大値だけを使うと 0.3 のままで、複数の層に遮蔽物があるときに薄くなりすぎるため、平均で押し上げます。

### フィルターとバイラテラル アップサンプル {#hlsl-upsample}

```hlsl
Texture2D<float3> gCoarseAo;        // 1 つ粗い層の CombineLevel の結果（フィルター済み）
Texture2D<float4> gCoarsePosition;  // 1 つ粗い層の位置
Texture2D<float4> gCoarseNormal;    // 1 つ粗い層の法線

// 深度と法線の重み。式 (8)・(9)。
float BilateralWeight(float3 p, float3 n, float3 q, float3 qn) {
  float w_n = pow((dot(n, qn) + 1.0) * 0.5, kTn);      // 法線が近いほど 1
  float w_z = pow(1.0 / (1.0 + abs(q.z - p.z)), kTz);  // 深度が近いほど 1
  return w_n * w_z;
}

// 細かい層の画素 pix に対する、粗い層からの AOfar を求める。
float3 UpsampleFar(int2 pix, float3 p, float3 n, int2 coarse_size) {
  int2 base = pix >> 1;                                  // 最も近い粗い画素
  int2 off = int2((pix.x & 1) ? 1 : -1, (pix.y & 1) ? 1 : -1);  // 次に近い画素の向き
  // 双線形の重み：最も近い 9/16、横と縦の隣が 3/16 ずつ、斜めが 1/16。
  int2 taps[4] = { base, base + int2(off.x, 0), base + int2(0, off.y), base + off };
  float w_b[4] = { 9.0 / 16.0, 3.0 / 16.0, 3.0 / 16.0, 1.0 / 16.0 };

  float3 sum = 0.0;
  float w_sum = 0.0;
  for (int i = 0; i < 4; ++i) {
    int2 c = clamp(taps[i], 0, coarse_size - 1);        // 足した：端では範囲内に収める
    float3 q = gCoarsePosition.Load(int3(c, 0)).xyz;
    float3 qn = gCoarseNormal.Load(int3(c, 0)).xyz;
    float w = w_b[i] * BilateralWeight(p, n, q, qn);    // 双線形 × 深度 × 法線
    sum += w * gCoarseAo.Load(int3(c, 0));
    w_sum += w;
  }
  return sum / max(w_sum, 1e-5);   // 足した：重みの合計で割る（論文は重みの合計の扱いを書いていない）
}
```

`BilateralWeight` は深度と法線が近い粗い画素ほど 1 に近づき輪郭を挟んだ画素はほぼ 0 になります。これで手前の物体の AO が背景へにじむのを防ぎます。

拡大の前に掛けるフィルターはここでは省きました。論文は粗い層の結果に 3×3 のバイラテラル フィルターを掛けると書き Table 4 に重み `1 / ((dx + 1)(dy + 1))` を示しています。深度と法線の重みも掛けるかは読んだ範囲には書かれていないので、実装するときは上の `BilateralWeight` を掛ける形で試して、見た目を確かめます。

層ごとの流れは次のとおりです。最も粗い層は `AoNear` だけで始めます（`far` は `(0, 0, 0)`）。それより細かい層は `UpsampleFar` で `far` を作り `CombineLevel` で合成して、次の層へ渡します。最も細かい層では `CombineLevel` の代わりに `FinalAccessibility` を呼びます。

## 論文の評価 {#evaluation}

論文は Blizzard の SSAO、NVIDIA の HBAO、Volumetric AO と比較しています。3 つのシーン（Sibenik、Conference Room、Sponza）を 512×512 で描き dmax は 2、層は 4 つ rmax は 5 です。Blender のレイトレース結果を基準にした SSIM は、MSSAO が 85.62%、86.66%、89.04% で他の 3 つより高くなっています。

実行時間（ミリ秒、512×512）は論文の表 8 で次のとおりです。古い GeForce 8600M GT では、Sibenik で MSSAO が 24.8、Blizzard が 24.9、Conference で 24.4 対 22.2、Sponza で 24.1 対 30.6 です。Sibenik は同程度、Conference は Blizzard が速く、Sponza は MSSAO が速くなっています。HBAO は約 91〜93 で、どれより大幅に遅くなりました。新しい GeForce 460M GTX では、MSSAO が約 6.5、Blizzard が約 5.2、Volumetric AO が約 6.0 で、わずかに負けています。1024×1024（表 9）では MSSAO が 21.9〜24.0 で、Blizzard の 24.9〜28.9 と Volumetric AO の 22.9〜24.8 より速くなりました。論文は最後のぼかしがないことが理由の 1 つではないかと推測しています。2010 年前後の GPU での測定なので、今のハードウェアにそのまま当てはめられる数字ではありません。

## 限界 {#limits}

論文は限界を次のように挙げています。

### メモリ {#memory}

最も細かい層以外では位置・法線・AO・フィルター後の AO の 4 つのバッファが要ります。AO のバッファは最大値・和・個数を運ぶため、1 チャンネルでなく 3 チャンネルです。1024×1024 から 128×128 までの 4 層で、普通の SSAO の 1.85 倍のメモリです。ゲームではほかのパスとメモリを共有するため、帯域の面で影響が出るかもしれません。バッファの再利用が改善案として挙げられています。

### 粗い解像度による誤差 {#coarse-error}

深度の不連続が多い領域はわずかに過剰な遮蔽になります。細い形状（椅子の脚や木の葉）では時間方向の一貫性が悪くなります。ただし、論文はこうしたアーティファクトは稀で、目立たないとしています。

### 画面空間の限界 {#screen-space}

どの SSAO とも同じく視錐台の外や最初の層の裏にある遮蔽物は、わかりません。デプス ピーリングや複数カメラのような対策は、精度を上げても考え方そのものは変えません。

## 使いどころ {#use}

論文の貢献は小さいカーネルを複数の解像度で使い最大値で合成する考え方です。深度のミップを使う [SAO](sao.md) や [XeGTAO](xegtao.md) がこの考え方とどう関係するかは、このページでは各方式の原典を読んでいないので説明しません。読み比べるときは半径をどう解像度に割り当てるか層をどう合成するか拡大でどう輪郭を守るかの 3 点を見ると、違いが分かります。

## よくあるミス {#mistakes}

??? failure "層の結果を足し合わせて、全体が暗くなりすぎる"
    内側の遮蔽物が複数の層で重複して数えられます。論文のように最大値を残して平均で調整します。

??? failure "拡大に双線形補間を使って、遮蔽が輪郭の外へ漏れる"
    深度と法線を見ないと手前の物体の AO が背景へにじみます。バイラテラル アップサンプルにします。

??? failure "和と個数を正規化して持ちサンプルのない層で平均が狂う"
    半径が 1 画素未満の層はサンプルを取りません。正規化した値だけを引き継ぐと最後に平均が正しく取れません。和と個数を別々に持ちます。

??? failure "カメラが動くと輪郭でちらつく"
    低解像度の G バッファで、画素が別の画素に切り替わっています。時間方向の再投影のパスを足します。

## これだけ覚える {#summary}

- 近い遮蔽は細かい解像度、遠い遮蔽は粗い解像度で小さいカーネルのまま求める
- 層は足さずに最大値で取り逃しを拾い平均で調整して合成する
- 拡大は深度と法線を見るバイラテラル アップサンプルで行う
- 代償はメモリ（論文で 1.85 倍）と粗い解像度による輪郭の誤差

## 参考資料 {#references}

- Thai-Duong Hoang, Kok-Lim Low. "Efficient Screen-Space Approach to High-Quality Multi-Scale Ambient Occlusion." The Visual Computer, 2012（National University of Singapore）. [https://www.comp.nus.edu.sg/~lowkl/publications/mssao_visual_computer_2012.pdf](https://www.comp.nus.edu.sg/~lowkl/publications/mssao_visual_computer_2012.pdf)
    - このページの式、パラメーター（rmax = 5、tn = 8、tz = 16、k = 0.5、dthreshold = 1）、評価の数字、限界はこの論文を読んだ内容です。
    - 同じ著者のより短い版（CGI 2011、2010 年の VRST の発表）は、読んでいません。論文の誌面の巻号とページは取得した原稿に書かれていないため、確かめていません。
    - 「使いどころ」では、他の方式との関係を、このページでは確かめていないので説明していません。式は、読みやすさのため記号を簡略化して書き直しています。HLSL は、論文の式と手順を直した説明用で、コンパイルも実行もしていません。画面外・正規化・ゼロ除算などの処理は、論文にないので足しました（コメントに「足した」と書いてあります）。

## 関連ページ {#related}

- [SSAO（半球）](ssao-hemisphere.md)
- [SAO](sao.md)
- [XeGTAO](xegtao.md)
- [Upsampling AO](filtering/upsample.md)
