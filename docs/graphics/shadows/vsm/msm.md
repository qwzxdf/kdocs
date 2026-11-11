---
title: MSM
tags:
  - 描画
---

# MSM

VSM は影を柔らかくぼかせて速い一方で、遮蔽物が重なる所に光漏れが出ます。原因はシャドウ マップの 1 画素に混ざった深度を「平均と分散」の 2 つの数だけで覚えていることです。2 つの数では山が 1 つの分布しか表せません。遮蔽物が 2 枚あっても間の隙間が明るく抜けて見えます。

<strong>MSM（Moment Shadow Mapping）</strong>は、覚える数を 4 つに増やして、この問題に正面から答える方式です。深度の 1 乗から 4 乗までの平均を保存して、そこから「この点より手前にある遮蔽物の割合」の下限を計算で求めます。遮蔽物が 2 枚までなら影の濃さを厳密に復元できます。1 回のテクスチャ読み出しで済みぼかしやミップも使えます。代償は判定のたびに小さな連立方程式を解くことです。

!!! tip "ポイント"
    - MSM は深度の 4 つのモーメント `(z, z², z³, z⁴)` を保存します。VSM の 2 つに 2 つを足した形です。
    - 判定はモーメントを満たす分布のうち「手前にある割合」が最も小さくなるものを求めて、その値を影の濃さにします。
    - 保存は 16 ビット × 4 チャンネルの 64 ビットです。専用の行列で回してから保存するので、16 ビットでも精度が持ちます。
    - 4 つのモーメントは多項式なので、ライトの near と far をぴったり合わせなくても結果が変わりません。
    - 遮蔽物が 3 層以上重なる所では、まだ漏れが残ります。

!!! info "このページを読む前に"
    - [VSM, ESM and MSM](index.md)（このセクション全体の地図と、読む順番）
    - [EVSM](evsm.md)（同じ 4 チャンネルを使う別の対策）

## 光漏れが出る理由 {#why}

シャドウ マップの 1 画素にはぼかしやミップのせいで、複数の深度が混ざっています。次の図は遮蔽物 A（深度 0.3）と遮蔽物 B（深度 0.6）が半分ずつ混ざった画素です。

<svg class="fig flow" viewBox="0 0 720 300" role="img" aria-label="1 画素の中に 2 つの深度がある。VSM は 1 つの山に潰し、MSM は 2 つの値として扱う"><defs><marker id="msA" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">1 画素に深度が 2 つ混ざったとき</text>
<line x1="40" y1="200" x2="680" y2="200" stroke="currentColor" stroke-width="2" marker-end="url(#msA)"/><text x="680" y="222" text-anchor="end" style="font-size:12px">深度 z（0 = 近い、1 = 遠い）</text>
<text x="40" y="222" text-anchor="start" style="font-size:12px">0</text>
<path d="M40,200 C150,200 190,92 296,92 C402,92 440,200 552,200" fill="rgba(76,139,245,0.18)" stroke="#4c8bf5" stroke-width="2.5"/>
<text x="296" y="82" text-anchor="middle" style="font-size:12px;font-weight:600">VSM が見る分布（平均 0.45・山 1 つ）</text>
<line x1="232" y1="200" x2="232" y2="120" stroke="#e5aa28" stroke-width="5"/><line x1="424" y1="200" x2="424" y2="120" stroke="#e5aa28" stroke-width="5"/>
<text x="232" y="112" text-anchor="middle" style="font-size:12px;font-weight:600">遮蔽物 A（z = 0.3）</text><text x="424" y="112" text-anchor="middle" style="font-size:12px;font-weight:600">遮蔽物 B（z = 0.6）</text>
<line x1="488" y1="200" x2="488" y2="150" stroke="#e5484d" stroke-width="3" stroke-dasharray="5 4"/><text x="488" y="142" text-anchor="middle" style="font-size:12px;font-weight:600;fill:#e5484d">受光点 t = 0.65</text>
<rect x="40" y="244" width="640" height="46" rx="9" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="1.5"/>
<text x="360" y="263" text-anchor="middle" style="font-size:12px">本当の影の濃さは 1.0（A も B も手前にある）。VSM は 0.64 で、約 36 % の光が漏れる。</text>
<text x="360" y="281" text-anchor="middle" style="font-size:12px">MSM は 1.0。同じ画素の 4 つのモーメントから、2 つの遮蔽物を逆算できる。</text></svg>


受光点の深度 `t = 0.65` は A にも B にも隠れているので、完全に影のはずです。VSM はこの画素を「平均 0.45・分散 0.0225」の 1 つの山として覚えます。チェビシェフの不等式から出る遮蔽の確率は 0.64 で、残りの約 36 % は光が漏れます。MSM は同じ画素の 4 つのモーメントから 2 つの深度を復元できるので、1.0 を返します（「数字で確かめる」の節で、ほかの `t` の値も並べます）。

漏れの大きさは遮蔽物の間隔で決まります。A と B が近いほど 1 つの山に近づいて漏れは減り離れるほど増えます。ライトから見て手前の壁の裏に別の壁があるような場面で目立ちます。

## モーメントから分布を取り出す {#moments}

画素に混ざった深度の分布を `Z` とします。`Z` の 1 乗から `m` 乗までの平均 `b_j = E[z^j]` を**モーメント**と呼びます。VSM が持つのは `b_1`（平均）と `b_2`（二乗の平均）だけで、MSM は `b_1` から `b_4` までを持ちます。

知りたいのは「受光点 `t` より手前にある重みの合計」、つまり `Z` の累積分布 `F(t)` です。ところが同じモーメントを満たす分布は無数にあって、`F(t)` は 1 つに決まりません。そこで MSM は「そのモーメントを満たす分布の中で `F(t)` が最小になるもの」を採ります。その値は影の濃さの取りうる最小値（最も厳しい下限）になります。

この問題の答えは支持点が高々 3 つの分布（3 本のディラックのデルタ）になります。モーメント問題の理論（Markov-Krein の定理）から分かる性質です。支持点の 1 つは受光点 `t` で、残りの 2 つを計算で求めます。それが遮蔽物 A と B の深度の推定値です。VSM のチェビシェフの不等式は 2 つのモーメントだけを使う場合の答えにあたります。

なぜ 4 つなのかは論文が自動評価で決めています。深度の関数を 37 種類（べき乗、根、指数、対数、三角関数など）用意してその組み合わせを数千通り試して、影の誤差が小さい組を選びました。4 つのモーメント `(z, z², z³, z⁴)` はそのうち誤差が小さい候補の 1 つです。

## 保存するデータと量子化 {#storage}

1 画素 4 チャンネルを 16 ビットずつ使うので、64 ビットです。2048 × 2048 のシャドウ マップなら `2048 × 2048 × 8 B ＝ 32 MiB` です。32 ビット浮動小数点で持てば 64 MiB で、VSM（32 ビット × 2）の 2 倍です。

16 ビットの整数に素直に詰めると、精度が足りません。`(z, z², z³, z⁴)` は互いに強く相関していて、取りうる範囲は 4 次元の箱の中の細い領域だけです。論文の補足資料はこの素直な量子化では 64 ビットのうち有効に使えるのが約 49.4 ビットまでで、残りの約 14.6 ビットが「この値の組は有効な組である」ことの表現に消えると見積もっています。

そこで、モーメントのベクトルに 4 × 4 の行列を掛けて、領域が箱の中で広がる向きに回してから保存します。補足資料によるとこの変換でエントロピーが 12.3 ビット増えて、無駄は約 2.3 ビットまで減ります。行列は論文が最適化で決めた定数です。

書き出し側は行ベクトルに行列を右から掛けて、第 1 成分に 0.035955884801 を足します。読み出し側は同じ値を引いてから逆行列を掛けます。

```hlsl
static const float kOffset = 0.035955884801;     // 量子化の変換で第 1 成分に足す値

// ---- 書き出し側（シャドウ パスのピクセル シェーダー）--------------------
// 4 つのモーメント (z, z^2, z^3, z^4) を、16 ビットで無駄が少なくなる向きに回して返す。
float4 EncodeMoments(float z) {
  float z2 = z * z;
  float4 moments = float4(z, z2, z2 * z, z2 * z2);
  // 行ベクトルに右から掛ける（mul(v, M)）。M は論文の 4x4 行列
  float4 optimized = mul(moments, float4x4(
      -2.07224649,    13.7948857237,   0.105877704,    9.7924062118,
      32.23703778,   -59.4683975703,  -1.9077466311, -33.7652110555,
      -68.571074599,  82.0359750338,   9.3496555107,  47.9456096605,
      39.3703274134, -35.364903257,   -6.6543490743, -23.9728048165));
  optimized[0] += kOffset;                       // 値域を 0..1 の箱に収めるための平行移動
  return optimized;
}
```


`mul(moments, M)` は行ベクトル × 行列です。HLSL の行列リテラルは書いた順に行から詰まります。2 つの行列が逆行列の関係にあることは、Python で掛け合わせて確かめました（要素の誤差は最大 7 × 10⁻⁹）。

書き出しはシャドウ パスのピクセル シェーダーで行います。

```hlsl
float4 ShadowPassPS(float4 pos : SV_Position) : SV_Target {
  // pos.z は D3D の [0,1] の深度。ライトが平行光なら線形。
  // 点光源・スポットライトの射影では、線形深度に直してから渡す（足した注意）。
  return EncodeMoments(pos.z);
}
```


`pos.z` は Direct3D の `[0, 1]` の深度です。平行光（正射影）なら深度が線形なので、そのまま使えます。点光源やスポットライトの透視射影では、深度が非線形なので線形な深度に直してから渡します。補足資料の Listing 1 も `FragmentDepth` を「シャドウ マップ空間の線形な深度」としています。

変換後の値がどこまで 0〜1 に収まるかを乱数で作った混合分布 2 万個で調べました。最小は約 −6 × 10⁻⁸、最大は 1 でした。範囲はほぼ `[0, 1]` に収まりますが、桁落ちで 0 をわずかに割る値は出ます。UNORM のレンダー ターゲットは 0 に丸めるので、実害はこの誤差の分だけです。16 ビットに丸めてから戻した場合の誤差は、モーメントごとに最大でおよそ 1 × 10⁻⁵ でした。この誤差を `moment_bias`（次の節）で吸収します。

シャドウ マップを作ったあとは通常のテクスチャと同じフィルタを使えます。ガウスぼかしの 2 パス、ミップ マップ、異方性フィルタ、MSAA のリゾルブです。変換が線形なので回した後の値を平均しても、元のモーメントを平均した結果を回した値と一致するからです。

<svg class="fig flow" viewBox="0 0 720 230" role="img" aria-label="MSM の処理の流れ。書き出し、フィルタ、読み出し、解く、影の濃さ"><defs><marker id="msB" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">MSM の 1 フレーム</text>
<rect x="12" y="50" width="124" height="60" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="74" y="72" text-anchor="middle" style="font-size:12px;font-weight:600">シャドウ パス</text><text x="74" y="92" text-anchor="middle" style="font-size:11px">4 モーメントを回して書く</text>
<rect x="156" y="50" width="124" height="60" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="218" y="72" text-anchor="middle" style="font-size:12px;font-weight:600">フィルタ</text><text x="218" y="92" text-anchor="middle" style="font-size:11px">ぼかし・ミップ・異方性</text>
<rect x="300" y="50" width="124" height="60" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="362" y="72" text-anchor="middle" style="font-size:12px;font-weight:600">サンプル</text><text x="362" y="92" text-anchor="middle" style="font-size:11px">元のモーメントへ戻す</text>
<rect x="444" y="50" width="124" height="60" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="506" y="72" text-anchor="middle" style="font-size:12px;font-weight:600">解く</text><text x="506" y="92" text-anchor="middle" style="font-size:11px">3 点の分布を作る</text>
<rect x="588" y="50" width="120" height="60" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="648" y="72" text-anchor="middle" style="font-size:12px;font-weight:600">影の濃さ</text><text x="648" y="92" text-anchor="middle" style="font-size:11px">0 〜 1</text>
<line x1="136" y1="80" x2="156" y2="80" stroke="currentColor" stroke-width="2" marker-end="url(#msB)"/><line x1="280" y1="80" x2="300" y2="80" stroke="currentColor" stroke-width="2" marker-end="url(#msB)"/><line x1="424" y1="80" x2="444" y2="80" stroke="currentColor" stroke-width="2" marker-end="url(#msB)"/><line x1="568" y1="80" x2="588" y2="80" stroke="currentColor" stroke-width="2" marker-end="url(#msB)"/>
<text x="74" y="138" text-anchor="middle" style="font-size:11px">16 ビット × 4</text><text x="218" y="138" text-anchor="middle" style="font-size:11px">線形な処理だけ</text><text x="362" y="138" text-anchor="middle" style="font-size:11px">1 回だけ読む</text><text x="506" y="138" text-anchor="middle" style="font-size:11px">3×3 の連立方程式</text>
<rect x="12" y="160" width="696" height="52" rx="9" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="1.5"/><text x="360" y="182" text-anchor="middle" style="font-size:12px">フィルタが線形なので、回した後の値をそのままぼかせる。読み出しの行列は書き出しの逆行列。</text><text x="360" y="200" text-anchor="middle" style="font-size:12px">重いのは「解く」だけで、1 画素あたり 1 回のテクスチャ読み出しで済む。</text></svg>


## 影の濃さを求める {#solve}

読み出しはサンプルして元のモーメントへ戻す 1 関数です。

```hlsl
// フィルタ済みの値を、元の 4 つのモーメントに戻す。
float4 DecodeMoments(float4 optimized) {
  optimized[0] -= kOffset;
  return mul(optimized, float4x4(
       0.2227744146, 0.1549679261, 0.1451988946, 0.163127443,
       0.0771972861, 0.1394629426, 0.2120202157, 0.2591432266,
       0.7926986636, 0.7963415838, 0.7258694464, 0.6539092497,
       0.0319417555, -0.1722823173, -0.2758014811, -0.3376131734));
}
```


判定の関数は 4 つの段階で進みます。引数は復元したモーメント（`moments`）、受光点の深度（`fragment_depth`）、2 つのバイアスです。

```hlsl
// 戻り値: 1 = 完全に影、0 = 光が当たる
float Hamburger4Msm(float4 moments, float fragment_depth, float depth_bias, float moment_bias) {
  // ① モーメントを 0.5 の方へわずかに寄せる。ハンケル行列を正定値に保つための安定化
  float4 b = lerp(moments, float4(0.5, 0.5, 0.5, 0.5), moment_bias);
  float3 z;
  z[0] = fragment_depth - depth_bias;
```


最初にモーメントを 0.5 の方へ `moment_bias` だけ寄せます。論文が示す例は `3e-5` です。画素の中の深度がすべて同じ（遮蔽物が 1 枚だけで平ら）だと分散 `D22` が 0 になって、次の割り算が破綻します。わずかに寄せるとそのような画素でも行列が正定値のまま保たれます。量子化の誤差を吸収する役目も兼ねています。

`depth_bias` は受光点の深度を手前へずらして、自分の面に自分の影が落ちる自己遮蔽（シャドウ アクネ）を避けます。値は深度の単位（0〜1）なので、near と far の幅が広いほど大きくなります。

```hlsl
  // ② ハンケル行列 B のコレスキー分解 (B = L D L^T)。自明でない要素だけ持つ
  float L32D22 = mad(-b[0], b[1], b[2]);          // L32 * D22
  float D22 = mad(-b[0], b[0], b[1]);             // 分散 E[z^2] - E[z]^2
  float squared_depth_variance = mad(-b[1], b[1], b[3]);   // z^2 の分散
  float D33D22 = dot(float2(squared_depth_variance, -L32D22), float2(D22, L32D22));
  float inv_d22 = 1.0 / D22;
  float L32 = L32D22 * inv_d22;
```


4 つのモーメントからハンケル行列（斜めに同じ値が並ぶ行列）`B` を作ります。

```text
    | 1    b1   b2 |
B = | b1   b2   b3 |
    | b2   b3   b4 |
```

`B` を `L D L^T` に分解して `D22`（深度の分散）、`L32`、`D33` を出します。コードは割り算を減らすために `D33 * D22` と `L32 * D22` の形で持ちます。`squared_depth_variance` は `z²` の分散 `b4 − b2²` で VSM の分散の 1 つ上の次数にあたります。

```hlsl
  // ③ c = B^-1 * (1, z0, z0^2)^T を、前進代入 → 対角の割り算 → 後退代入で求める
  float3 c = float3(1.0, z[0], z[0] * z[0]);
  c[1] -= b.x;
  c[2] -= b.y + L32 * c[1];
  c[1] *= inv_d22;
  c[2] *= D22 / D33D22;
  c[1] -= L32 * c[2];
  c[0] -= dot(c.yz, b.xy);
```


ここで `c = B⁻¹ · (1, z0, z0²)ᵀ` を求めます。`z0` は受光点の深度です。前進代入、対角の割り算、後退代入の 3 手順で逆行列は作りません。

```hlsl
  // ④ c0 + c1 z + c2 z^2 = 0 を解いて、残り 2 つの支持点 z[1]、z[2] を得る
  float p = c[1] / c[2];
  float q = c[0] / c[2];
  float d = (p * p / 4.0) - q;
  float r = sqrt(d);
  z[1] = -(p / 2.0) - r;
  z[2] = -(p / 2.0) + r;
```


`c0 + c1 z + c2 z² ＝ 0` の 2 つの解が残りの支持点 `z[1]` と `z[2]` です。この式は「3 つの支持点 `z0, z1, z2` が与えられたモーメントを満たす」という条件から出てきます（補足資料の Proposition 10）。判別式 `d` が負になると平方根が NaN になるので、`B` が正定値であること（`moment_bias` による安定化）が前提です。

```hlsl
  // ⑤ 3 点のディラックのデルタの分布を作り、z[0] より手前の重みの合計を返す
  float4 sw = (z[2] < z[0]) ? float4(z[1], z[0], 1.0, 1.0)
            : ((z[1] < z[0]) ? float4(z[0], z[1], 0.0, 1.0)
                             : float4(0.0, 0.0, 0.0, 0.0));
  float quotient = (sw[0] * z[2] - b[0] * (sw[0] + z[2]) + b[1])
                 / ((z[2] - sw[1]) * (z[0] - z[1]));
  return saturate(sw[2] + sw[3] * quotient);
}
```


3 点の位置が決まったので手前にある重みを数えます。場合は 3 つです。

1. `z[2] < z[0]`: 2 点（`z[1]` と `z[2]`）が受光点より手前にあります。影の濃さは 1 に近い値になります。
2. `z[1] < z[0]` かつ `z[2] ≥ z[0]`: 1 点だけが手前にあります。
3. どちらでもない: 3 点とも受光点より奥か同じです。影の濃さは 0 です。

`quotient` はこの場合ごとの重みをモーメントの式から直接計算したものです。補足資料の Algorithm 2 は重みを連立方程式 `A · w = (1, b1, b2)ᵀ` で求めますが、Listing 3 はその解を閉じた式にしてあります。`saturate` は数値の誤差で範囲を外れた値を 0〜1 に収めます。

## 数字で確かめる {#numbers}

上の判定を Python に写して、2 層と 3 層の画素で調べました（`moment_bias = 10⁻⁶`、`depth_bias = 0`、量子化なしの 64 ビット浮動小数点）。「本当の値」は受光点より手前にある遮蔽物の重みの合計です。

遮蔽物 A（0.3）と B（0.6）が半分ずつの画素です。

- `t = 0.35`: 本当の値 0.5、VSM 0.000、MSM 0.500
- `t = 0.45`: 本当の値 0.5、VSM 0.000、MSM 0.500
- `t = 0.55`: 本当の値 0.5、VSM 0.308、MSM 0.500
- `t = 0.65`: 本当の値 1.0、VSM 0.640、MSM 1.000
- `t = 0.80`: 本当の値 1.0、VSM 0.845、MSM 1.000
- `t = 0.95`: 本当の値 1.0、VSM 0.917、MSM 1.000

MSM は全部の `t` で厳密な値を返しました。VSM は 0.35 と 0.45 で、半分の影を 0 と見て光を 100 % 通します。奥の `t = 0.95` でも 8 % が漏れます。2 層の分布は受光点を含めて支持点が 3 つなので、4 つのモーメントで完全に決まります。

遮蔽物が 3 枚（0.2、0.4、0.7 が 3 分の 1 ずつ）の画素では、結果が変わります。

- `t = 0.35`: 本当の値 0.333、VSM 0.000、MSM 0.224
- `t = 0.45`: 本当の値 0.667、VSM 0.007、MSM 0.399
- `t = 0.65`: 本当の値 0.667、VSM 0.526、MSM 0.535
- `t = 0.80`: 本当の値 1.0、VSM 0.761、MSM 0.910

MSM は常に本当の値以下で、これが「下限」の意味です。VSM よりは本当の値に近いものの `t = 0.45` では 0.399 と 0.667 の差が残ります。遮蔽物が 3 層以上重なる所は 4 つのモーメントでは表せないので、漏れが残ります。

## 影の濃さを持ち上げる {#bleed}

MSM は漏れが小さいとはいえ 3 層以上の所や量子化の誤差で、薄い影が残ることがあります。VSM 系でよく使う下限を切り捨てる後処理が、MSM にも使えます。

```hlsl
// 足した: 光漏れを和らげる場合の持ち上げ（clamp 以下を 0 に、1 を 1 に張り直す）
float ReduceBleeding(float shadow, float clamp_value) {
  return saturate((shadow - clamp_value) / (1.0 - clamp_value));
}
```


これは**足した**処理で論文のものではありません。`clamp_value = 0.2` なら濃さ 0.2 以下を 0 にして、残りを 0〜1 に引き伸ばします。薄い影が消える代わりに柔らかい半影も少し硬くなります。0 のままなら素の MSM です。後処理の詳しい話は [光漏れの対策](light-bleeding.md) にあります。

## 通して使う {#usage}

ピクセル シェーダーからシャドウ マップを引いて判定する流れです。

```hlsl
float4 ShadePS(float3 world_pos : TEXCOORD0) : SV_Target {
  float4 clip = mul(float4(world_pos, 1.0), g_world_to_light);
  float3 ndc = clip.xyz / clip.w;
  float2 uv = float2(ndc.x * 0.5 + 0.5, 0.5 - ndc.y * 0.5);   // D3D は v が下向き
  if (any(uv < 0.0) || any(uv > 1.0) || ndc.z > 1.0) {        // 足した: シャドウ マップの外は影にしない
    return float4(1, 1, 1, 1);
  }
  float4 moments = DecodeMoments(g_moment_map.SampleLevel(g_linear_sampler, uv, 0));
  float shadow = Hamburger4Msm(moments, ndc.z, g_depth_bias, g_moment_bias);
  shadow = ReduceBleeding(shadow, g_light_bleed_clamp);
  float lit = 1.0 - shadow;
  return float4(lit, lit, lit, 1.0);
}
```


`g_moment_map.SampleLevel` は 1 回だけです。PCF のように複数回サンプルしなくても、ぼかしはシャドウ マップの側で済ませてあるからです。シャドウ マップの外は影にしないように 1.0 を返します。この処理は論文のコードにない、**足した**部分です。

!!! note "確かめた範囲"
    判定の関数は Python に写して、上の数字を確かめました。HLSL は `fxc`（`ps_5_0`）で `ShadowPassPS` と `ShadePS`（Hamburger 版と Hausdorff 版の両方）をコンパイルして、エラーが出ないことを確かめました。GPU で実際にシャドウ マップを作って描画したものではありません。

??? example "完成形（Hamburger 4MSM と Hausdorff 4MSM。通して置く）"
    ここまでのコードを 1 つのファイルにまとめたものです。

```hlsl
// MSM（Hamburger 4MSM）の通し実装。Peters & Klein の補足資料の Listing 1〜3 を元に、
// 定数バッファとシェーディングの main を足した。
cbuffer ShadowConstants : register(b0) {
  float4x4 g_world_to_light;  // ワールド → ライトのクリップ空間（x,y は -1..1、z は 0..1）
  float g_depth_bias;         // 自己遮蔽よけ。深度（0..1）での値。一例: 1e-3
  float g_moment_bias;        // 16 ビット量子化の誤差よけ。論文の一例: 3e-5
  float g_light_bleed_clamp;  // 足した: 下の「影の濃さを持ち上げる」の下限。一例: 0.0〜0.3
  float _pad;
};

Texture2D<float4> g_moment_map : register(t0);   // R16G16B16A16_UNORM の MSM
SamplerState g_linear_sampler : register(s0);    // 線形（できれば異方性）フィルタ

static const float kOffset = 0.035955884801;     // 量子化の変換で第 1 成分に足す値

// ---- 書き出し側（シャドウ パスのピクセル シェーダー）--------------------
// 4 つのモーメント (z, z^2, z^3, z^4) を、16 ビットで無駄が少なくなる向きに回して返す。
float4 EncodeMoments(float z) {
  float z2 = z * z;
  float4 moments = float4(z, z2, z2 * z, z2 * z2);
  // 行ベクトルに右から掛ける（mul(v, M)）。M は論文の 4x4 行列
  float4 optimized = mul(moments, float4x4(
      -2.07224649,    13.7948857237,   0.105877704,    9.7924062118,
      32.23703778,   -59.4683975703,  -1.9077466311, -33.7652110555,
      -68.571074599,  82.0359750338,   9.3496555107,  47.9456096605,
      39.3703274134, -35.364903257,   -6.6543490743, -23.9728048165));
  optimized[0] += kOffset;                       // 値域を 0..1 の箱に収めるための平行移動
  return optimized;
}

float4 ShadowPassPS(float4 pos : SV_Position) : SV_Target {
  // pos.z は D3D の [0,1] の深度。ライトが平行光なら線形。
  // 点光源・スポットライトの射影では、線形深度に直してから渡す（足した注意）。
  return EncodeMoments(pos.z);
}

// ---- 読み取り側 ----------------------------------------------------------
// フィルタ済みの値を、元の 4 つのモーメントに戻す。
float4 DecodeMoments(float4 optimized) {
  optimized[0] -= kOffset;
  return mul(optimized, float4x4(
       0.2227744146, 0.1549679261, 0.1451988946, 0.163127443,
       0.0771972861, 0.1394629426, 0.2120202157, 0.2591432266,
       0.7926986636, 0.7963415838, 0.7258694464, 0.6539092497,
       0.0319417555, -0.1722823173, -0.2758014811, -0.3376131734));
}

// 戻り値: 1 = 完全に影、0 = 光が当たる
float Hamburger4Msm(float4 moments, float fragment_depth, float depth_bias, float moment_bias) {
  // ① モーメントを 0.5 の方へわずかに寄せる。ハンケル行列を正定値に保つための安定化
  float4 b = lerp(moments, float4(0.5, 0.5, 0.5, 0.5), moment_bias);
  float3 z;
  z[0] = fragment_depth - depth_bias;

  // ② ハンケル行列 B のコレスキー分解 (B = L D L^T)。自明でない要素だけ持つ
  float L32D22 = mad(-b[0], b[1], b[2]);          // L32 * D22
  float D22 = mad(-b[0], b[0], b[1]);             // 分散 E[z^2] - E[z]^2
  float squared_depth_variance = mad(-b[1], b[1], b[3]);   // z^2 の分散
  float D33D22 = dot(float2(squared_depth_variance, -L32D22), float2(D22, L32D22));
  float inv_d22 = 1.0 / D22;
  float L32 = L32D22 * inv_d22;

  // ③ c = B^-1 * (1, z0, z0^2)^T を、前進代入 → 対角の割り算 → 後退代入で求める
  float3 c = float3(1.0, z[0], z[0] * z[0]);
  c[1] -= b.x;
  c[2] -= b.y + L32 * c[1];
  c[1] *= inv_d22;
  c[2] *= D22 / D33D22;
  c[1] -= L32 * c[2];
  c[0] -= dot(c.yz, b.xy);

  // ④ c0 + c1 z + c2 z^2 = 0 を解いて、残り 2 つの支持点 z[1]、z[2] を得る
  float p = c[1] / c[2];
  float q = c[0] / c[2];
  float d = (p * p / 4.0) - q;
  float r = sqrt(d);
  z[1] = -(p / 2.0) - r;
  z[2] = -(p / 2.0) + r;

  // ⑤ 3 点のディラックのデルタの分布を作り、z[0] より手前の重みの合計を返す
  float4 sw = (z[2] < z[0]) ? float4(z[1], z[0], 1.0, 1.0)
            : ((z[1] < z[0]) ? float4(z[0], z[1], 0.0, 1.0)
                             : float4(0.0, 0.0, 0.0, 0.0));
  float quotient = (sw[0] * z[2] - b[0] * (sw[0] + z[2]) + b[1])
                 / ((z[2] - sw[1]) * (z[0] - z[1]));
  return saturate(sw[2] + sw[3] * quotient);
}

// Hausdorff 4MSM。「支持点は 0..1 の中にある」という知識を足して、近い遮蔽物の影を少し濃くする。
// 3 点の解が 0..1 から出たときだけ、0 と 1 を支持点に含む 4 点の解に切り替える。
float Hausdorff4Msm(float4 moments, float fragment_depth, float depth_bias, float moment_bias) {
  float4 b = lerp(moments, float4(0.5, 0.5, 0.5, 0.5), moment_bias);
  float3 z;
  z[0] = fragment_depth - depth_bias;

  // ここまでは Hamburger4Msm の ①〜④ と同じ
  float L32D22 = mad(-b[0], b[1], b[2]);
  float D22 = mad(-b[0], b[0], b[1]);
  float squared_depth_variance = mad(-b[1], b[1], b[3]);
  float D33D22 = dot(float2(squared_depth_variance, -L32D22), float2(D22, L32D22));
  float inv_d22 = 1.0 / D22;
  float L32 = L32D22 * inv_d22;
  float3 c = float3(1.0, z[0], z[0] * z[0]);
  c[1] -= b.x;
  c[2] -= b.y + L32 * c[1];
  c[1] *= inv_d22;
  c[2] *= D22 / D33D22;
  c[1] -= L32 * c[2];
  c[0] -= dot(c.yz, b.xy);
  float p = c[1] / c[2];
  float q = c[0] / c[2];
  float r = sqrt((p * p / 4.0) - q);
  z[1] = -(p / 2.0) - r;
  z[2] = -(p / 2.0) + r;

  float shadow;
  if (z[1] < 0.0 || z[2] > 1.0) {
    // 3 点の解が 0..1 の外へ出た。支持点を {0, z_free, z0, 1} の 4 点にして解き直す
    float z_free = ((b[2] - b[1]) * z[0] + b[2] - b[3]) / ((b[1] - b[0]) * z[0] + b[1] - b[2]);
    float w1_factor = (z[0] > z_free) ? 1.0 : 0.0;   // z_free が受光点より手前なら、その重みも数える
    shadow = (b[1] - b[0] + (b[2] - b[0] - (z_free + 1.0) * (b[1] - b[0]))
                          * (z_free - w1_factor - z[0]) / (z[0] * (z[0] - z_free)))
           / (z_free - w1_factor) + 1.0 - b[0];
  } else {
    float4 sw = (z[2] < z[0]) ? float4(z[1], z[0], 1.0, 1.0)
              : ((z[1] < z[0]) ? float4(z[0], z[1], 0.0, 1.0)
                               : float4(0.0, 0.0, 0.0, 0.0));
    float quotient = (sw[0] * z[2] - b[0] * (sw[0] + z[2]) + b[1])
                   / ((z[2] - sw[1]) * (z[0] - z[1]));
    shadow = sw[2] + sw[3] * quotient;
  }
  return saturate(shadow);
}

// 足した: 光漏れを和らげる場合の持ち上げ（clamp 以下を 0 に、1 を 1 に張り直す）
float ReduceBleeding(float shadow, float clamp_value) {
  return saturate((shadow - clamp_value) / (1.0 - clamp_value));
}

float4 ShadePS(float3 world_pos : TEXCOORD0) : SV_Target {
  float4 clip = mul(float4(world_pos, 1.0), g_world_to_light);
  float3 ndc = clip.xyz / clip.w;
  float2 uv = float2(ndc.x * 0.5 + 0.5, 0.5 - ndc.y * 0.5);   // D3D は v が下向き
  if (any(uv < 0.0) || any(uv > 1.0) || ndc.z > 1.0) {        // 足した: シャドウ マップの外は影にしない
    return float4(1, 1, 1, 1);
  }
  float4 moments = DecodeMoments(g_moment_map.SampleLevel(g_linear_sampler, uv, 0));
  float shadow = Hamburger4Msm(moments, ndc.z, g_depth_bias, g_moment_bias);
  shadow = ReduceBleeding(shadow, g_light_bleed_clamp);
  float lit = 1.0 - shadow;
  return float4(lit, lit, lit, 1.0);
}
```


## Hausdorff 4MSM {#hausdorff}

深度は 0〜1 の範囲に収まるので、「支持点は 0 以上 1 以下」という制約を足すと下限をもう少し厳しく（大きく）できます。これが **Hausdorff 4MSM** です。これまでの方式は制約のない実数全体で解くので **Hamburger 4MSM** と呼ばれます。名前は 2 つのモーメント問題（Hamburger 問題と Hausdorff 問題）から来ています。

3 点の解が `[0, 1]` の外へ出たときに支持点を `{0, z_free, z0, 1}` の 4 点に切り替えます。`z_free` は残る 1 点の位置を表す式で決まります（補足資料の Proposition 11）。

```hlsl
// Hausdorff 4MSM。「支持点は 0..1 の中にある」という知識を足して、近い遮蔽物の影を少し濃くする。
// 3 点の解が 0..1 から出たときだけ、0 と 1 を支持点に含む 4 点の解に切り替える。
float Hausdorff4Msm(float4 moments, float fragment_depth, float depth_bias, float moment_bias) {
  float4 b = lerp(moments, float4(0.5, 0.5, 0.5, 0.5), moment_bias);
  float3 z;
  z[0] = fragment_depth - depth_bias;

  // ここまでは Hamburger4Msm の ①〜④ と同じ
  float L32D22 = mad(-b[0], b[1], b[2]);
  float D22 = mad(-b[0], b[0], b[1]);
  float squared_depth_variance = mad(-b[1], b[1], b[3]);
  float D33D22 = dot(float2(squared_depth_variance, -L32D22), float2(D22, L32D22));
  float inv_d22 = 1.0 / D22;
  float L32 = L32D22 * inv_d22;
  float3 c = float3(1.0, z[0], z[0] * z[0]);
  c[1] -= b.x;
  c[2] -= b.y + L32 * c[1];
  c[1] *= inv_d22;
  c[2] *= D22 / D33D22;
  c[1] -= L32 * c[2];
  c[0] -= dot(c.yz, b.xy);
  float p = c[1] / c[2];
  float q = c[0] / c[2];
  float r = sqrt((p * p / 4.0) - q);
  z[1] = -(p / 2.0) - r;
  z[2] = -(p / 2.0) + r;

  float shadow;
  if (z[1] < 0.0 || z[2] > 1.0) {
    // 3 点の解が 0..1 の外へ出た。支持点を {0, z_free, z0, 1} の 4 点にして解き直す
    float z_free = ((b[2] - b[1]) * z[0] + b[2] - b[3]) / ((b[1] - b[0]) * z[0] + b[1] - b[2]);
    float w1_factor = (z[0] > z_free) ? 1.0 : 0.0;   // z_free が受光点より手前なら、その重みも数える
    shadow = (b[1] - b[0] + (b[2] - b[0] - (z_free + 1.0) * (b[1] - b[0]))
                          * (z_free - w1_factor - z[0]) / (z[0] * (z[0] - z_free)))
           / (z_free - w1_factor) + 1.0 - b[0];
  } else {
    float4 sw = (z[2] < z[0]) ? float4(z[1], z[0], 1.0, 1.0)
              : ((z[1] < z[0]) ? float4(z[0], z[1], 0.0, 1.0)
                               : float4(0.0, 0.0, 0.0, 0.0));
    float quotient = (sw[0] * z[2] - b[0] * (sw[0] + z[2]) + b[1])
                   / ((z[2] - sw[1]) * (z[0] - z[1]));
    shadow = sw[2] + sw[3] * quotient;
  }
  return saturate(shadow);
}
```


近い所から落ちる短い影が少し濃くなります。ただし、補足資料は Hamburger 4MSM の方を勧めています。Hausdorff 版は分岐が 1 つ増えて少し遅く、16 ビット量子化の誤差が短い距離の影でより目立つからです。通常は Hamburger を使って、短距離の影が薄いと感じたときに試すという順番になります。

## 近い面と遠い面を合わせなくてよい {#invariance}

モーメントが多項式（`z^j`）であることには、使いやすさの利点があります。ライトの near と far を変えることは、深度を拡大して平行移動することにあたります。多項式の組はこの変換で別の多項式の組に写るだけで、持っている情報は変わりません。補足資料はこれが多項式だけの性質だと証明しています（Proposition 20）。

EVSM のように指数を使う方式は near と far に敏感です。`exp(c · z)` の `c` が深度の幅に対して大きすぎると、桁あふれします。MSM にはその心配がありません。ただし、16 ビット量子化の精度は深度の幅が広いと落ちます。シーンに合わせて near と far を詰めておくのは、今でも有効です。

## 長所と短所 {#pros-cons}

長所は光漏れが VSM と ESM よりずっと小さいことです。フィルタが自由に使えてサンプルは 1 回です。指数を使わないので浮動小数点のあふれとも無縁です。

短所は画素ごとの計算が重いことです。連立方程式を解いて平方根を取ります。メモリは 64 ビットで VSM（32 ビット × 2）と同じ大きさですが、ESM の 1 チャンネルより重いです。バイアスの調整も 2 つ（`depth_bias` と `moment_bias`）あります。3 層以上の重なりでは漏れが残ります。

## VSM 系の比較 {#compare}

| 手法 | チャンネル | 光漏れ | 判定 | 実装 |
| --- | --- | --- | --- | --- |
| VSM | 2 | 大きい | 軽い | 簡単 |
| ESM | 1 | 影が薄れる | 軽い | 簡単 |
| EVSM | 4（32 ビット） | 小さい | 中 | 中 |
| MSM | 4（16 ビット） | 最も小さい | 重い | 複雑 |

MSM を選ぶのは VSM 系のぼかしの利点が欲しくて、EVSM の漏れや桁あふれが気になるときです。逆に、判定の計算を軽くしたい場合やメモリが 1 チャンネルしか使えない場合は、ESM の方が向いています。

## ゲームでの使いどころ {#in-games}

向いているのは広い面積の影を半影つきで安く描きたい場面です。太陽光のカスケード シャドウのうち遠いカスケードでは、PCF の大きなカーネルを避けて、ぼかしだけで済ませられます。複数のライトを 1 つのアトラスに入れる場合も 1 回のサンプルで済む利点が効きます。

向かないのは薄い遮蔽物が何枚も重なる場面（葉の多い木の影など）と判定の計算を 1 画素ごとに払いたくないモバイル GPU のような環境です。そのような場面では[PCF との比較](comparison.md) にあるとおり PCF の方が安定します。

## よくあるミス {#mistakes}

??? failure "影が真っ黒な筋やノイズで抜ける（NaN）"
    原因は `moment_bias` が 0 のまま平らな遮蔽物だけの画素で `D22` が 0 になることです。割り算が無限大になって `sqrt` が NaN を返します。`moment_bias` に `3e-5` 程度を入れます。

??? failure "平らな面に縞模様の自己影が出る"
    原因は `depth_bias` が足りないことです。モーメントの空間で判定するので、PCF のような「傾き × 係数」のバイアスはかけられません。値を少し大きくします。広い範囲を 1 枚のシャドウ マップで覆っているならカスケードに分けて、1 画素あたりの深度の幅を縮めます。

??? failure "16 ビットの MSM が、縞状にむらになる"
    原因は変換行列を通さずに `(z, z², z³, z⁴)` を 16 ビット UNORM にそのまま書いていることです。有効な値の領域が箱の隅に細く寄っているので、桁が足りません。`EncodeMoments` と `DecodeMoments` の組を使います。書き出しと読み出しの片方だけに行列を通すと判定が全部ずれます。

??? failure "遠い影が消えるまたは全部が影になる"
    原因は線形でない深度を書いていることです。透視射影のシャドウ マップに `pos.z` をそのまま書くと値が 1 の近くに潰れて、4 乗するとほとんど区別できなくなります。ビュー空間の距離を near と far で 0〜1 に正規化した値を書きます。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] MSM は深度の 4 つのモーメントを保存して、「手前にある割合」の下限を計算します。
    - [x] 遮蔽物が 2 層までなら厳密です。3 層以上は VSM より小さい漏れが残ります。
    - [x] 16 ビット × 4 で保存するときは、専用の行列で回してから書いて、読むときに戻します。
    - [x] `moment_bias`（`3e-5` 程度）と `depth_bias` の 2 つを調整します。
    - [x] 近い面と遠い面を合わせなくても結果は変わりませんが、量子化の精度のためにできるだけ詰めます。

## 参考 {#references}

読んだ範囲は次の 2 つです。

- Christoph Peters, Reinhard Klein, "Supplementary Document on Moment Shadow Mapping"（補足資料。全文）。Hamburger・Hausdorff 4MSM のアルゴリズムと証明、量子化の行列とエントロピーの見積もり評価に使った 37 個の関数、HLSL の Listing 1〜4。<http://momentsingraphics.de/Media/I3D2015/MomentShadowMappingSupplementary.pdf>
- 著者のプロジェクト ページにある論文の概要。<http://momentsingraphics.de/I3D2015.html>

論文の本文（Christoph Peters, Reinhard Klein, "Moment Shadow Mapping", Proceedings of the 19th ACM SIGGRAPH Symposium on Interactive 3D Graphics and Games, 2015, [10.1145/2699276.2699277](https://doi.org/10.1145/2699276.2699277)）は、読めていません。このページが本文のものとして書いた数字（`3e-5` の例、64 ビット、12.3 ビット、49.4 ビット、2.3 ビット）は補足資料と概要に書かれた範囲です。論文の評価（速度、他の方式との比較の図）は解説していません。

そのほかの資料は次のとおりです。このページではどちらも読んでいません。

- Thomas Donnelly, Andrew Lauritzen, "Variance Shadow Maps", Symposium on Interactive 3D Graphics and Games, 2006
- Andrew Lauritzen, Michael McGuire, "Layered Variance Shadow Maps", Graphics Interface 2008

## 関連ページ

- [VSM, ESM and MSM](index.md)
- [EVSM](evsm.md)
- [光漏れの対策](light-bleeding.md)
- [Comparison with PCF](comparison.md)
