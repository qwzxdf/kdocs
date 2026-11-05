---
title: Lumen and Nanite
tags:
  - 描画
---

# Lumen and Nanite

Unreal Engine 5 の Lumen と Nanite は、名前だけが先に広まって中で何をしているのかが見えにくい技術です。ゲームを作る側から見るとライトマップを焼く待ち時間と LOD を手で作る手間を、GPU の仕組みで置き換える試みです。このページの中心は Lumen です。Lumen の SIGGRAPH 2022 の発表（Wright、Narkowicz、Kelly）を全部読んでレイをどう飛ばすか光をどこに貯めるかノイズをどう減らすかを、HLSL と数字で整理します。Nanite はこの発表が触れる範囲（カードの撮影、フォールバック メッシュ）に絞ります。

!!! tip "ポイント"
    - Lumen は画面、メッシュ SDF、グローバル SDF、ハードウェア レイトレの順にレイの続きを引き継ぐ。当たった点の光はその場で計算せずサーフェス キャッシュから読む。
    - 薄い壁は距離場の格子の間に落ちて、レイが突き抜ける。距離場を膨らませると防げる。2 次元の実験で薄さ 0.2 ボクセルの壁を拾える割合は、膨らませなしで 13 %、0.5 ボクセルで 100 % だった。
    - ノイズ対策の中心は画面の 1/16 の格子に置いたスクリーン プローブ（八面体 8×8）。3×3 のフィルタが画面での 48×48 に相当する。
    - 積の重点サンプリング（BRDF と前フレームの光の積）は、同じ本数のレイで誤差を大きく減らす。このページの玩具の実験では誤差が 26.9 % から 2.2 % に下がった。
    - ソフトウェア トレースとハードウェア トレースの得失は、シーンで逆転する。重なったメッシュが多いシーンでは差が 10 倍を超えた（PS5、1080p）。

!!! info "このページを読む前に"
    - [Global Illumination (GI)](index.md)
    - [DDGI](ddgi.md)（動的なプローブによる GI）
    - [Mesh Shaders](../pipeline/mesh-shaders.md)（Nanite に近い考え方の入り口）

## 読んだ資料 {#sources}

- Daniel Wright, Krzysztof Narkowicz, Patrick Kelly, "Lumen: Real-time Global Illumination in Unreal Engine 5"（SIGGRAPH 2022、Advances in Real-Time Rendering in Games）。スライド全 199 枚の本文と読み上げ原稿を全部読みました。画像や動画の中身は読めていません。
- 発表が参照する論文や発表（Wright 2015 の距離場による遮蔽、Wright 2021 の Radiance Caching、Stachowiak 2015 と 2018、Karis 2021 の Nanite、Netzel 2022 のレイトレーシング）は、読んでいません。このページでは発表が述べている範囲だけを書きます。
- Nanite の内部（クラスターの大きさ階層、ソフトウェア ラスタライザー）は読んでいないので、書きません。旧版にあった数字は出典がないため削除しました。
- 実験の数字（薄い壁、八面体、積の重点サンプリング）はこのページが説明のために書いた C++ で出したものです。Lumen のコードそのものではありません。

HLSL は `fxc`（`ps_5_0` と `cs_5_0`）でコンパイルして確かめ C++ は MSVC で実行しました。HLSL は Lumen の実装ではなく、発表の説明を小さく書き直したものです。

## Lumen が解く 3 つの問題 {#problems}

発表は動的な間接光の根本的な問題を 3 つ挙げています。

1. **レイをどう飛ばすか。** ハードウェア レイトレは速い将来の手段ですが、DXR 非対応の GPU や 60 fps の家庭用機では、規模を落とせません。メッシュが大きく重なったシーンでは 2 段の BVH が遅くなります。そこで、ソフトウェアのレイトレも用意します。
2. **間接光の経路全体をどう解くか。** 1 回の反射だけでは足りません。屋内には多重反射が反射の中には GI が要ります。最初の反射が最も重要なので拡散は Final Gather、鏡面は反射のデノイズで解きます。2 回目以降はサーフェス キャッシュのフィードバックで解きます。
3. **ノイズをどう減らすか。** 拡散 GI に画素ごとに 1 本のレイさえ使えません。ところが、屋内の高い品質には有効なサンプルが数百いります。

この 3 つが後の節の構成になります。

## トレースの流れ {#pipeline}

Lumen は複数のトレース方法を順に使います。画面、メッシュ SDF、グローバル SDF（またはハードウェア）、最後にスカイライトです。各段階はレイがどこまで進んだか（TraceDistance）と当たったかどうかを書き出して、次の段階に渡します。次の段階はその続きから再開します。

<svg class="fig flow" viewBox="0 0 660 194" role="img" aria-label="Lumen のトレースの流れ(各段階が t と hit を次へ渡す)"><defs><marker id="ar" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#94a3b8"/></marker></defs><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">Lumen のトレースの流れ(各段階が t と hit を次へ渡す)</text><rect x="10" y="34" width="140" height="50" rx="6" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="80.0" y="56.0" text-anchor="middle" font-size="11" fill="currentColor">画面(HZB)</text><text x="80.0" y="70.0" text-anchor="middle" font-size="11" fill="currentColor">最も正確</text><rect x="180" y="34" width="140" height="50" rx="6" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="250.0" y="56.0" text-anchor="middle" font-size="11" fill="currentColor">メッシュ SDF</text><text x="250.0" y="70.0" text-anchor="middle" font-size="11" fill="currentColor">2 m まで</text><rect x="350" y="34" width="140" height="50" rx="6" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="420.0" y="56.0" text-anchor="middle" font-size="11" fill="currentColor">グローバル SDF</text><text x="420.0" y="70.0" text-anchor="middle" font-size="11" fill="currentColor">2 m から先</text><rect x="10" y="114" width="140" height="50" rx="6" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="80.0" y="136.0" text-anchor="middle" font-size="11" fill="currentColor">ハードウェア</text><text x="80.0" y="150.0" text-anchor="middle" font-size="11" fill="currentColor">(選択)</text><rect x="180" y="114" width="140" height="50" rx="6" fill="rgba(148,163,184,0.18)" stroke="#94a3b8"/><text x="250.0" y="136.0" text-anchor="middle" font-size="11" fill="currentColor">スカイライト</text><text x="250.0" y="150.0" text-anchor="middle" font-size="11" fill="currentColor">外れたら</text><line x1="150" y1="59.0" x2="180" y2="59.0" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#ar)"/><line x1="320" y1="59.0" x2="350" y2="59.0" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#ar)"/><line x1="420.0" y1="84" x2="80.0" y2="114" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#ar)"/><line x1="150" y1="139.0" x2="180" y2="139.0" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#ar)"/></svg>

最初が画面なのはレイの始まり付近で、最も正確だからです。画面のトレースは GBuffer とレイトレのシーンの食い違い（自己交差）を直し、スキンメッシュのようにソフトウェアのレイトレが扱えない物の間接影も出せます。細かい GI はどれだけ寄っても出せます。線形のステップだと薄い物（歩道、テーブル、ドア）を飛び越えて光が漏れるため、Hi-Z（HZB）の走査を使い斜めのレイの反復を制限します。拡散レイは半解像度で追います。画面の外か面の裏に出たときは最後に遮蔽されていなかった位置まで戻してから、次の段階に渡します。戻さないと次の段階の始点が壁の中になり光が漏れます。

画面のトレースの後で解決したレイは取り除きます（コンパクション）。残ったレイだけを詰めると後続のトレースが最大 50 % 速くなると、発表は書いています。詰め方も重要です。ローカルなアトミックで詰めると、同じ wave 内のレイの始点がばらばらになります。128×128 の大きなスレッド グループの中で、Z 順のまま prefix sum で詰めると、反射のトレースが 21 % 速くなりました。

## ソフトウェア トレース {#swrt}

### メッシュ SDF {#mesh-sdf}

メッシュごとに符号つき距離場（SDF）を作りインポート時にメッシュと一緒に保存します。解像度はメッシュの大きさとインポート設定で決まります。符号は各ボクセルから 64 本のレイを飛ばして、三角形の裏面に当たった数で決めます。巨大な 150 万三角形のメッシュでも生成に約 0.6 ms です。保存は疎な 8³ ボクセルのブリックで、各ボクセルは面から ±4 ボクセル以内の距離だけを 1 バイトで持ちます（狭い帯）。ミップごとに解像度が半分になり最大距離が倍になります。

ブリックは固定サイズのプール（320 MB）に入れ毎フレーム GPU が各アセットに必要なミップをカメラ距離から計算して、CPU がストリーミングします。割り当ては単純な線形アロケーターで、断片化しません。

トレースはミップを使ったレイマーチです。面に近いと細かいミップ、遠いと粗いミップで空きを速く飛ばします。反復は 64 回までで超えたら、そこを当たりとして報告します。当たった点の法線は±0.5 ボクセルの 6 点の中心差分で求めます。距離場には UV も材質もないので、当たった位置と法線だけが分かります。光はあとで説明するサーフェス キャッシュから読みます。

### グローバル SDF {#global-sdf}

全メッシュを毎フレーム回ると遅いので、近くの精密なトレースは短く（2 m まで）します。その先は全メッシュの SDF を 1 つにまとめた**グローバル SDF**が引き継ぎます。カメラを中心とした 4 つのクリップマップ（各 256³）で、疎なブリックと狭い帯の作りはメッシュ SDF と同じです。

マージは高価なので徹底的にキャッシュします。遠いクリップマップほど更新を間引き静的なブリックと動的なブリックを分けて、動いた物のブリックだけを更新します。動いたブリックを GPU 上で列挙し、その範囲のオブジェクトだけを数えます。

### 薄い壁と距離場の膨らませ {#expand}

距離場の格子はボクセルより薄い物を表せません。薄い壁が 2 つの格子点の間にあると、保存した距離はどちらも正で補間してもゼロにならずレイが壁を通り抜けます。暗い屋内と明るい屋外の境の壁をすり抜けると、大きな光漏れになります。

対策は距離場をボクセルの対角の半分だけ膨らませる（距離から引く）ことです。膨らませは実行時に行うので元のデータは保存したままです。ただし、膨らませで面が厚くなるので始点が面の中に入り接触影が消えます。そこで、始点では 0 にして距離に比例して増やします（スライド 50）。反射ではグレージング角のレイが自己交差するため、「現在の面までの距離」を上限にします。

このページの 2 次元の実験で確かめました。厚さ 0.2 ボクセルの壁を向きと位置をランダムに置き格子点の距離を双線形補間して、壁を横切るレイを細かく歩きます。膨らませの量ごとに当たりを拾えた割合を数えました。

<svg class="fig flow" viewBox="0 0 640 230" role="img" aria-label="薄い壁(厚さ 0.2 voxel)を拾えた割合(%)"><defs><marker id="ar" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#94a3b8"/></marker></defs><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">薄い壁(厚さ 0.2 voxel)を拾えた割合(%)</text><line x1="60" y1="190" x2="600" y2="190" stroke="#94a3b8"/><line x1="60" y1="40" x2="60" y2="190" stroke="#94a3b8"/><text x="54" y="194.0" text-anchor="end" font-size="10" fill="currentColor">0</text><text x="54" y="119.0" text-anchor="end" font-size="10" fill="currentColor">50</text><text x="54" y="44.0" text-anchor="end" font-size="10" fill="currentColor">100</text><rect x="104.5" y="170.3" width="43.0" height="19.7" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="126.0" y="166.29" text-anchor="middle" font-size="10" fill="currentColor">13.14</text><text x="127.5" y="206" text-anchor="middle" font-size="11" fill="currentColor">0</text><rect x="239.5" y="73.4" width="43.0" height="116.6" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="261.0" y="69.42" text-anchor="middle" font-size="10" fill="currentColor">77.72</text><text x="262.5" y="206" text-anchor="middle" font-size="11" fill="currentColor">0.25</text><rect x="374.5" y="40.0" width="43.0" height="150.0" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="396.0" y="36.0" text-anchor="middle" font-size="10" fill="currentColor">100</text><text x="397.5" y="206" text-anchor="middle" font-size="11" fill="currentColor">0.5</text><rect x="509.5" y="40.0" width="43.0" height="150.0" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="531.0" y="36.0" text-anchor="middle" font-size="10" fill="currentColor">100</text><text x="532.5" y="206" text-anchor="middle" font-size="11" fill="currentColor">0.707</text></svg>

膨らませなしでは 13.14 %、0.25 ボクセルで 77.72 %、0.5 ボクセルで 100 % でした。0.707（2 次元の対角の半分）では余裕が出ます。**ボクセルの大きさの半分程度の膨らませで、薄い壁が拾える**ことが分かります。

```hlsl
```hlsl
// ================= ① メッシュ SDF のレイマーチ =================

Texture3D<float> g_mesh_sdf : register(t0);      // 1 つのメッシュの距離場（オブジェクト空間、ミップつき。値は [m]）
cbuffer SdfCB : register(b0) {
  float3 g_sdf_min;        // 距離場の範囲の最小の角（オブジェクト空間）[m]
  float g_voxel_size;      // ミップ 0 の 1 ボクセルの大きさ [m]
  float3 g_sdf_extent;     // 範囲の大きさ [m]
  float g_max_expand;      // 膨らませの最大値 [m]。ボクセルの対角の半分が目安
  float g_expand_ramp;     // 膨らませが最大になる距離 [m]（足した値）
  float3 g_pad0;
};

float SampleSdf(float3 p, float mip) {
  float3 uvw = (p - g_sdf_min) / g_sdf_extent;                    // 0〜1 の 3D 座標
  return g_mesh_sdf.SampleLevel(g_linear_clamp, uvw, mip);
}

// 6 点の中心差分で法線を求める（スライド 36: ±0.5 ボクセル）。
float3 SdfNormal(float3 p) {
  float h = 0.5 * g_voxel_size;
  return normalize(float3(
      SampleSdf(p + float3(h, 0, 0), 0) - SampleSdf(p - float3(h, 0, 0), 0),
      SampleSdf(p + float3(0, h, 0), 0) - SampleSdf(p - float3(0, h, 0), 0),
      SampleSdf(p + float3(0, 0, h), 0) - SampleSdf(p - float3(0, 0, h), 0)));
}

struct SdfHit { bool hit; float t; };

// レイ原点 o・方向 d（単位）・最大距離 t_max。膨らませ（expand）は薄い壁を取りこぼさないために距離を縮める量。
// 原点から 0 で始め距離に比例して増やす（スライド 50: 接触影を残すため）。
SdfHit TraceMeshSdf(float3 o, float3 d, float t_max) {
  SdfHit r;
  r.hit = false;
  r.t = t_max;
  float t = 0.0;
  [loop] for (int i = 0; i < 64; ++i) {                          // 64 回で打ち切り（スライド 36）
    float expand = g_max_expand * saturate(t / g_expand_ramp);   // 距離に応じて線形に膨らませる
    float mip = clamp(log2(max(t, g_voxel_size) / g_voxel_size) * 0.5, 0.0, 3.0);   // 遠いほど粗いミップ（足した式）
    float dist = SampleSdf(o + d * t, mip) - expand;             // 膨らませた面までの距離
    if (dist < 0.01 * g_voxel_size) { r.hit = true; r.t = t; return r; }
    t += max(dist, 0.1 * g_voxel_size);                          // 球トレース。最小の歩幅で止まらないようにする（足した値）
    if (t >= t_max) return r;
  }
  r.hit = true;                                                  // 64 回で当たりにする（スライド 36: 打ち切りは当たりとして報告）
  r.t = t;
  return r;
}
```
```

`TraceMeshSdf` は距離に応じた `expand`（始点で 0、`g_expand_ramp` で最大）を引いた距離で球トレースします。`mip` の式は遠いほど粗いミップを引く簡単な式で、このページが決めたものです（発表は具体的な式を載せていません）。64 回目に達したら当たりにするのは、発表の通りです。

### 閉じていないメッシュと葉 {#edge-cases}

メッシュが閉じていない（スキャン データなど）と距離場に無限に続く負の領域ができます。生成時に 4 ボクセル先に仮想の面を入れて（負の距離を 4 ボクセルで折り返して）対処します。完全な解ではなくラスターとの食い違いが残ります。

葉のように部分的に透ける面は膨らませが全部の光を止めてしまいます。そこで「カバレッジ」という値を距離場のインスタンスごとに持ちグローバル SDF にも別のチャンネルとして入れます。レイマーチ中にカバレッジに応じて歩幅を増やし、膨らませを減らします。当たりには確率的な透明度を使います。アニメーションする葉は事前に作った距離場が追従しないので、バイアスを足します。

## サーフェス キャッシュ {#surface-cache}

距離場には UV も頂点属性もないので、当たった点の材質や光をその場で計算できません。しかも材質グラフは重く複数の影つきライトの直接光も多重反射も高価です。そこで、メッシュの表面を「カード」に写して、材質と光を貯めます。

### カード {#cards}

カードはメッシュごとに作る軸に平行な投影面です。サーフェル（小さな円盤）を K-means 風にクラスタリングして作りインポート時に生成します（150 万三角形で約 0.2 ms）。うまく作れなければ 6 面のキューブマップ風の投影に戻します。投影ベースなので頂点属性はいらず引くのも速く、実行時に撮り直せ薄い両面の壁も表せます。

カードの中身はランタイムに撮影します（正射影カメラでメッシュを描く）。出力は GBuffer 風の固定形式で、アトラスは 4096×4096 です。このページの C++ で各形式のメモリを計算しました。アルベド（BC7）は 16 MB、不透明度（BC4）は 8 MB、深度（R16）は 32 MB、法線は 16 MB、エミッシブ（BC6H）は 16 MB で、合計 88 MB です。無効なテクセルは深度を最大値にして印を付けます。撮影は毎フレーム 512×512 テクセルの予算で、距離と GPU からのフィードバックの優先度順に行い古いページも少しずつ撮り直します。Nanite を使うと全カードを 1 回の描画で撮れて、約 10 倍速くなると書かれています。

遠くの小さなインスタンスはグループにまとめて、6 枚のカードで撮影します。建物のように外から見る前提の物の LOD になります。

### 引き方 {#sampling}

当たり点の位置と法線からそのメッシュの 6 枚のカードのうち法線の符号で 3 枚を選びます。カードの深度を 4 点取得して、手動で双線形にします。深度がヒット点と合わない（遮蔽された）サンプルと投影が引き伸ばされる向きのサンプルは、重みを下げます。無効な画素は捨て最後に 3 枚を混ぜます。

```hlsl
```hlsl
// ================= ② サーフェス キャッシュの引き方 =================

struct Card {
  float3 origin;           // カードの投影の原点（ワールド）
  float3 axis_u, axis_v;   // 画面内の 2 軸
  float3 normal;           // 投影の向き（軸平行）
  float2 size;             // カードの大きさ [m]
  float4 atlas_rect;       // アトラス内の矩形（xy = 左上の UV、zw = 大きさ）
};

Texture2D<float4> g_card_radiance : register(t1);   // 直接光 + 間接光（rgb）
Texture2D<float> g_card_depth : register(t2);       // カードの深度 [m]（最大値 = 無効な画素。スライド 69）

// 1 枚のカードからヒット点 p・法線 n の光を引く。重みを w に返す。
float3 SampleCard(Card c, float3 p, float3 n, out float w) {
  float3 rel = p - c.origin;
  float2 uv = float2(dot(rel, c.axis_u) / c.size.x, dot(rel, c.axis_v) / c.size.y);
  w = 0;
  if (any(uv < 0.0) || any(uv > 1.0)) return 0;                  // カードの外
  float2 atlas_uv = c.atlas_rect.xy + uv * c.atlas_rect.zw;
  float depth_here = dot(rel, c.normal);                          // ヒット点のカードからの距離
  float stored = g_card_depth.SampleLevel(g_linear_clamp, atlas_uv, 0);
  if (stored > 1e8) return 0;                                    // 無効な画素（深度 = 最大）は捨てる
  float depth_w = exp(-abs(stored - depth_here) / 0.1);          // 深度が合わない = 遮蔽されたサンプル（0.1 m は足した値）
  float normal_w = saturate(dot(c.normal, n));                   // 投影が引き伸ばされる向きは弱く
  w = depth_w * normal_w;
  return g_card_radiance.SampleLevel(g_linear_clamp, atlas_uv, 0).rgb;
}

// 法線の符号で軸平行の 6 枚から 3 枚を選び重みで混ぜる（スライド 70）。
float3 SampleSurfaceCache(Card cards[6], float3 p, float3 n) {
  float3 sum = 0;
  float wsum = 0;
  int idx[3] = { n.x >= 0 ? 0 : 1, n.y >= 0 ? 2 : 3, n.z >= 0 ? 4 : 5 };   // 6 枚: +X, -X, +Y, -Y, +Z, -Z
  [unroll] for (int i = 0; i < 3; ++i) {
    float w;
    float3 c = SampleCard(cards[idx[i]], p, n, w);
    sum += c * w;
    wsum += w;
  }
  return wsum > 1e-4 ? sum / wsum : 0.0;                          // 全部外れなら黒（足りない分はエネルギーが失われる。スライド 7）
}
```
```

重みの式（指数と 0.1 m）はこのページが決めた値です。発表は重みの要素（深度の差、法線の内積、双線形）だけを述べています。全部が外れたら黒にします。足りない分はエネルギーが失われますが、光が漏れるよりは目立ちません（スライド 7）。

### 光の更新 {#lighting-update}

サーフェス キャッシュは材質に加えて、直接光と間接光も持ちます。ライトマップに似ていて同じ問題があります。始点を面から離すバイアスが要りジオメトリの内側にあるテクセルは、裏面に当たったレイを黒にして光漏れを防ぎます。

毎フレーム、全部を更新するのは高価なので、固定の予算で優先度の高いページだけを更新します。優先度は最後に使われたフレームから、最後に更新したフレームを引いた値です。使われているのに古いほど先に更新します。基数ソートのヒストグラムで予算（直接光は 1024×1024 テクセル、間接光は 512×512 テクセル）に達するまで、桶を選びます。

```hlsl
```hlsl
// ================= ⑥ サーフェス キャッシュの更新の優先度 =================

struct PageInfo { uint last_used; uint last_updated; };
StructuredBuffer<PageInfo> g_pages : register(t7);
RWStructuredBuffer<uint> g_histogram : register(u0);   // 優先度 0〜255 ごとのページ数
cbuffer FrameCB : register(b1) { uint g_frame; uint g_page_count; uint g_budget_pages; uint g_pad1; };

// 優先度 = LastUsed − LastUpdated（使われたのに、古いほど先）。256 段に丸めて数える（スライド 74）。
[numthreads(64, 1, 1)]
void PageHistogramCS(uint3 dtid : SV_DispatchThreadID) {
  if (dtid.x >= g_page_count) return;
  PageInfo p = g_pages[dtid.x];
  uint priority = (p.last_used > p.last_updated) ? (p.last_used - p.last_updated) : 0;   // 使われていなければ 0
  priority = min(priority, 255u);
  InterlockedAdd(g_histogram[priority], 1);
}

RWStructuredBuffer<uint> g_threshold : register(u1);

// 大きい優先度の桶から予算のページ数に達するまで足し、その桶を境目にする。
[numthreads(1, 1, 1)]
void FindThresholdCS() {
  uint total = 0;
  uint threshold = 0;
  for (int b = 255; b >= 0; --b) {
    total += g_histogram[b];
    if (total >= g_budget_pages) { threshold = (uint)b; break; }
  }
  g_threshold[0] = threshold;                                     // これ以上の優先度のページを更新する
}
```
```

間接光は 4×4 のタイルに半球のプローブを 1 つ置きプローブのテクセルからだけレイを追います。プローブの位置と方向を 4 フレームでジッターし、周りの 4 プローブを補間します。補間はプローブの面より後ろのテクセルを除く平面の重みとプローブの深度マップによる可視性の重みで、光漏れを抑えます。2 回目の反射のために現在フレームの直接光と前フレームの間接光を引くので、毎フレーム 2 回分、それ以降の反射はフィードバックで増えます（n+2 回）。間接光の更新の予算は Lumen 全体の 1/16 未満だそうです。

グローバル SDF のヒットはどのインスタンスに当たったか分かりません。そのため、全カードを 4 つのクリップマップ（各 64³）にも入れます。ボクセルは 6 方向ごとの放射輝度を持ち補間して引きます。この「ボクセル ライティング」は粗いので、サーフェス キャッシュの主な限界とされています。

## ハードウェア レイトレ {#hwrt}

ハードウェア レイトレは三角形との交差を正確に出し、動的な材質評価が要る鋭い画面外の反射を出せます。ただし、スキンメッシュのようにカードのない物は、サーフェス キャッシュの光が使えないので、ヒット ライティング（その場で材質と光を評価する）が要ります。

Lumen のハードウェア経路は 2 つの照明モードに整理されています。**サーフェス キャッシュ モード**は、any-hit シェーダーを使わず（全部を不透明として扱う）、closest-hit は法線とキャッシュのパラメータだけを取り出します。ペイロードは UE4 の 64 バイトから 20 バイトに縮みます（HitT、半透明の旗、両面の旗、材質、法線、プリミティブ、インスタンス）。**ヒット ライティング モード**は、一度サーフェス キャッシュで追ってから、並べ替えて再トレースします。速度が桁違いに違います。The Matrix Awakens（PS5、1080p）の反射のトレースはサーフェス キャッシュで 2.44 ms、ヒット ライティングで 11.54 ms でした。材質が重いと動的評価は予算に入りません。しかも空光がサーフェス キャッシュから来る場面では、見た目の差もあまりありませんでした。

ほかに次の工夫が書かれています。

- **半透明と α マスク。** 半透明のメッシュは飛ばし、α マスクはカードの不透明度で 50 % 未満なら飛ばします。飛ばす回数は `MaxTranslucentSkipCount` で制限します。
- **Nanite のフォールバック メッシュ。** Nanite の形そのものは BLAS に入らないので、簡略な代用メッシュを入れます。位相が合わないため GBuffer からのレイが自己交差します。短いレイをイプシロンの距離まで裏面を無視して飛ばしてから、長いレイを飛ばして直します。
- **遠景（far-field）。** TLAS は毎フレーム作り直すので、100K インスタンスが限界でしたが、デモは 50 万個を超え 100 万個を目指しました。トレース距離を 200 m に絞ると、GI の空の遮蔽が消えました。そこで、World Partition の HLOD を遠景として入れレイ マスクで近景と排他にしました。近景を先に追い外れたら遠景を追います。
- **TLAS の重なり。** 近景と遠景を同じ TLAS に重ねると、近景のトレースが 44 % 遅くなりました。遠景を平行移動して重ならないようにすると、近景 1.77 ms、遠景 0.60 ms に収まりました（重ねた場合は 2.37 ms と 1.04 ms、基準は 1.65 ms）。

## Final Gather {#final-gather}

間接光の拡散を解くには 2 つの古典的な方法がありました。プローブからトレースして放射照度を前もって積分する方法は、放射照度が画素でなくプローブで計算されるため、光漏れと過剰な遮蔽が出ます。画素からトレースして画面空間のデノイザーでノイズを取る方法は、レイがばらばらで遅くデノイズが全解像度で高価です。Lumen はその中間を取りました。

### スクリーン プローブ {#screen-probes}

画面の画素の上にプローブ（スクリーン プローブ）を置いて、そこからトレースします。均一に置き形の細かい所だけ細分します。プローブの放射輝度を同じ平面にある周りの画素に補間し、プローブの位置を毎フレームジッターして、時間方向に蓄積します。

Final Gather は 3 つの部分でできています。

- **スクリーン空間の放射輝度キャッシュ。** 各辺 1/16 の解像度（プローブごとに 8×8 の方向）です。
- **ワールド空間の放射輝度キャッシュ。** 2 m より遠い光を低い空間解像度で、高い方向解像度（スクリーン プローブの 8×8 に対して 32×32）で持ちます。小さな遠い窓から差す光のような少数のレイでは見落とす光を解きます。クリップマップの配置で画面上の間隔を一定にします。
- **全解像度の補間、積分、時間フィルタ、接触 AO。** 16 画素以内の接触 AO は、時間フィルタの後にかけて遅れを避けます。

このページの C++ でスライドの数字から計算しました。1920×1080 の 1/16 は 120×68 = 8160 プローブで、各 64 本なら 522,240 本、画素あたり 0.252 本です。発表の Epic 設定（Final Gather は 1/4 rpp）と合います。フィルタはプローブ空間の 3×3 が、画面での 48×48 に当たります（3 プローブ × 16 画素）。大きな空間フィルタを安く掛けられるのが利点です。

### 八面体マップと放射照度 {#octahedral}

プローブの放射輝度は 8×8 の八面体マップに持ちます（球を正八面体に投影して正方形に展開する方法）。放射照度は各テクセルの方向に余弦を掛けて足します。

```hlsl
```hlsl
// ================= ④ スクリーン プローブ: 八面体マップ =================

Texture2D<float4> g_probe_radiance : register(t4);   // 8x8 の八面体マップを並べたアトラス（rgb = 放射輝度）

float2 OctEncode(float3 d) {
  d /= (abs(d.x) + abs(d.y) + abs(d.z));                          // 正八面体に投影
  float2 e = d.xy;
  if (d.z < 0.0) e = (1.0 - abs(e.yx)) * float2(d.x >= 0.0 ? 1.0 : -1.0, d.y >= 0.0 ? 1.0 : -1.0);   // 下半球を折り返す
  return e * 0.5 + 0.5;                                          // 0〜1
}

float3 OctDecode(float2 uv) {
  float2 e = uv * 2.0 - 1.0;
  float3 d = float3(e.x, e.y, 1.0 - abs(e.x) - abs(e.y));
  if (d.z < 0.0) d.xy = (1.0 - abs(d.yx)) * float2(d.x >= 0.0 ? 1.0 : -1.0, d.y >= 0.0 ? 1.0 : -1.0);
  return normalize(d);
}

// 1 つのプローブの放射照度。8x8 の各テクセルの方向を余弦で重みづけして足す。
// テクセルの立体角は一様ではないが、ここでは 4π / 64 で近似した（足した近似。誤差は C++ で測った）。
float3 ProbeIrradiance(int2 probe_origin_texel, float3 normal) {
  float3 sum = 0;
  const float d_omega = 4.0 * kPi / 64.0;
  [unroll] for (int y = 0; y < 8; ++y) {
    [unroll] for (int x = 0; x < 8; ++x) {
      float3 dir = OctDecode((float2(x, y) + 0.5) / 8.0);
      float cos_w = max(dot(normal, dir), 0.0);
      sum += g_probe_radiance.Load(int3(probe_origin_texel + int2(x, y), 0)).rgb * cos_w * d_omega;
    }
  }
  return sum;                                                     // 放射照度 E。拡散の出力は albedo / π × E
}
```
```

`OctEncode` と `OctDecode` は方向と UV の変換です。下半球は折り返します。`ProbeIrradiance` は各テクセルに同じ立体角 `4π/64` を掛けています。八面体マップの立体角は一様ではありません。C++ で各テクセルを 32×32 に刻んで測ると、全体は 4π（12.5659）ですが、最小 0.1028、最大 0.2879 で最大と最小の比は 2.80 でした。同じ立体角で近似すると空の例で最大約 11 % の誤差が出ます。テクセルごとの立体角を使うと約 5 % に下がりました。残りの誤差は 8×8 の解像度が窓のような鋭い光を表せないためです。

画素は周りの 4 つのプローブの重みで補間します。同じ平面にないプローブの重みを下げます。

```hlsl
```hlsl
// ================= ⑤ 4 つのプローブからの補間 =================

Texture2D<float> g_probe_depth : register(t5);       // プローブの位置の線形深度 [m]
Texture2D<float4> g_probe_normal : register(t6);     // プローブの位置の法線

// 画素 (n, depth) に対する、周りの 4 プローブの重み。同じ平面にないプローブは重みを小さくする（スライド 146・78）。
float4 ProbeWeights(float2 frac_pos, int2 probe_ij, float3 n, float pixel_depth) {
  float4 w;
  [unroll] for (int i = 0; i < 4; ++i) {
    int2 o = int2(i & 1, i >> 1);
    float wb = lerp(1.0 - frac_pos.x, frac_pos.x, (float)o.x) * lerp(1.0 - frac_pos.y, frac_pos.y, (float)o.y);   // 双線形
    float probe_depth = g_probe_depth.Load(int3(probe_ij + o, 0));
    float3 probe_n = g_probe_normal.Load(int3(probe_ij + o, 0)).xyz;
    float wd = exp(-abs(probe_depth - pixel_depth) / max(0.05 * pixel_depth, 1e-3));   // 深度の差（5 % は足した値）
    float wn = pow(saturate(dot(probe_n, n)), 8.0);                                       // 法線の差（指数 8 は足した値）
    w[i] = wb * wd * wn;
  }
  return w / max(w.x + w.y + w.z + w.w, 1e-4);
}
```
```

重みは双線形に深度の差と法線の差を掛けたものです（5 % と指数 8 は、このページが決めた値）。

### 積の重点サンプリング {#product}

重点サンプリングは重要度の見積もりが正しいほど効きます。Lumen は前フレームのスクリーン放射輝度キャッシュを再投影し、どの方向から光が来ているかを知っています。プローブはスクリーン空間の低解像度なので、スレッド グループを丸ごと 1 つ使えます。BRDF が 0 の方向（面の裏）と光の弱い方向のレイを捨てて、重要な方向にまとめ直します（BRDF だけ光だけ MIS より良いと書かれています）。スライドは 4 倍のレイを追った品質と述べています。

簡単な玩具で効果の大きさを見ました。半球に 2 つの明るい窓がある環境で、64 本のレイによる放射照度の推定誤差を 4000 回の試行で測りました。

<svg class="fig flow" viewBox="0 0 640 230" role="img" aria-label="放射照度の推定誤差(%、64 本、半球に窓が 2 つ)"><defs><marker id="ar" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#94a3b8"/></marker></defs><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">放射照度の推定誤差(%、64 本、半球に窓が 2 つ)</text><line x1="60" y1="190" x2="600" y2="190" stroke="#94a3b8"/><line x1="60" y1="40" x2="60" y2="190" stroke="#94a3b8"/><text x="54" y="194.0" text-anchor="end" font-size="10" fill="currentColor">0</text><text x="54" y="119.0" text-anchor="end" font-size="10" fill="currentColor">20</text><text x="54" y="44.0" text-anchor="end" font-size="10" fill="currentColor">40</text><rect x="104.5" y="55.9" width="43.0" height="134.1" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="126.0" y="51.86249999999998" text-anchor="middle" font-size="10" fill="currentColor">35.77</text><text x="127.5" y="206" text-anchor="middle" font-size="11" fill="currentColor">一様</text><rect x="239.5" y="89.0" width="43.0" height="101.0" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="261.0" y="85.0125" text-anchor="middle" font-size="10" fill="currentColor">26.93</text><text x="262.5" y="206" text-anchor="middle" font-size="11" fill="currentColor">余弦</text><rect x="374.5" y="173.6" width="43.0" height="16.4" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="396.0" y="169.6125" text-anchor="middle" font-size="10" fill="currentColor">4.37</text><text x="397.5" y="206" text-anchor="middle" font-size="11" fill="currentColor">光だけ</text><rect x="509.5" y="181.8" width="43.0" height="8.2" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="531.0" y="177.7875" text-anchor="middle" font-size="10" fill="currentColor">2.19</text><text x="532.5" y="206" text-anchor="middle" font-size="11" fill="currentColor">積</text></svg>

一様なサンプリングは 35.8 %、余弦（BRDF だけ）は 26.9 %、前フレームの光だけは 4.4 %、BRDF と前フレームの光の積は 2.2 % でした。積で同じ誤差にするのに必要な余弦サンプリングの本数は、約 9,700 本です。前フレームの見積もりがほとんど正しい理想的な場合なので、これは上限です。実際は、光が動く見積もりが外れるといった理由で、利益は小さくなります。発表の述べる「4 倍」のほうが現実的な値でしょう。

### 全解像度の時間フィルタ {#temporal}

プローブのジッターを使うので、安定した時間フィルタが要ります。近傍クランプは使えないので深度と法線の差で履歴を捨てます。その代わり照明の変化への反応が遅く、動く物の後ろにゴーストが出ます。そこで、トレースが速く動く物に当たったと検出して、その画素のフィルタを速くします。

距離ごとに許せる遅れが違います。最も近い接触 AO は遅れを許せずスクリーン放射輝度キャッシュは時間蓄積、ワールド放射輝度キャッシュはプローブの使い回し、スカイライトは数フレームかけた更新で済みます。

### 半透明とフォグ {#translucency}

半透明とフォグには予算が不透明の 1/8 ほどしかありません。視錐台全体を froxel グリッドのプローブで覆い 3×3 か 4×4 の八面体プローブをトレースします。見えないプローブは HZB で飛ばします。空間フィルタと時間蓄積をかけ SH2 の放射照度に積分します。前方の半透明パスやボリューメトリック フォグが、これを補間します。遠い光は別のワールド放射輝度キャッシュ（16×16）で補います。

## 反射 {#reflections}

反射は Stachowiak の確率的な手法に沿っています（読んでいない）。GGX の見える範囲を重点サンプリングしてレイを作り空間の再利用、時間蓄積、バイラテラル フィルタを順にかけます。バイラテラル フィルタは最後の手段で、空間再利用の後に分散が大きい領域と新しく見えた領域（2 倍の強さ）にだけ使います。トーンマップした重みでファイアフライを抑えます。

ばらつくレイの追跡は遅いので、粗さで方法を変えます。粗さ 0.4 以上は拡散のために作ったスクリーン放射輝度キャッシュ（8×8）で足ります。GGX の見える範囲から方向を選びプローブから放射輝度を補間するだけで、反射のレイが要りません。多くのシーンでコストが 50〜70 % 下がります。粗さ 0.3〜0.4 の光沢はレイを短くして、外れたらワールド放射輝度キャッシュ（32×32）から補間します。レイが近い始点の順に並ぶので、並べ替えが要らず道路の反射で 16 % 下がりました。クリアコートの二重反射は下の塗装にスクリーン放射輝度キャッシュを再利用し、上のクリアコートだけを追います。

パイプラインはタイル単位で空や再利用で済んだ領域を飛ばします。不透明、半透明、水で複数回走らせるので必要な領域だけを動かせることが大切です。

## 性能 {#performance}

測定は 1080p で Temporal Super Resolution で 4K に出力しています。High 設定は 60 fps を狙い（メッシュ SDF なし、Final Gather は 1/16 rpp、反射は 1/4 rpp）、Epic 設定は 30 fps を狙います（Final Gather は 1/4 rpp、反射は 1 rpp）。

<svg class="fig flow" viewBox="0 0 640 230" role="img" aria-label="Lumen の合計(ms、PS5、1080p)"><defs><marker id="ar" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#94a3b8"/></marker></defs><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">Lumen の合計(ms、PS5、1080p)</text><line x1="60" y1="190" x2="600" y2="190" stroke="#94a3b8"/><line x1="60" y1="40" x2="60" y2="190" stroke="#94a3b8"/><text x="54" y="194.0" text-anchor="end" font-size="10" fill="currentColor">0</text><text x="54" y="119.0" text-anchor="end" font-size="10" fill="currentColor">6</text><text x="54" y="44.0" text-anchor="end" font-size="10" fill="currentColor">12</text><rect x="104.0" y="155.4" width="43.0" height="34.6" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="125.5" y="151.375" text-anchor="middle" font-size="10" fill="currentColor">2.77</text><rect x="150.0" y="132.1" width="43.0" height="57.9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="171.5" y="128.125" text-anchor="middle" font-size="10" fill="currentColor">4.63</text><text x="150.0" y="206" text-anchor="middle" font-size="11" fill="currentColor">Nanite</text><rect x="284.0" y="136.4" width="43.0" height="53.6" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="305.5" y="132.375" text-anchor="middle" font-size="10" fill="currentColor">4.29</text><rect x="330.0" y="81.2" width="43.0" height="108.8" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="351.5" y="77.25" text-anchor="middle" font-size="10" fill="currentColor">8.7</text><text x="330.0" y="206" text-anchor="middle" font-size="11" fill="currentColor">Lyra</text><rect x="464.0" y="110.2" width="43.0" height="79.8" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="485.5" y="106.25" text-anchor="middle" font-size="10" fill="currentColor">6.38</text><rect x="510.0" y="48.6" width="43.0" height="141.4" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="531.5" y="44.625" text-anchor="middle" font-size="10" fill="currentColor">11.31</text><text x="510.0" y="206" text-anchor="middle" font-size="11" fill="currentColor">Matrix</text><rect x="450" y="34" width="12" height="10" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="466" y="43" text-anchor="start" font-size="11" fill="currentColor">High</text><rect x="450" y="50" width="12" height="10" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="466" y="59" text-anchor="start" font-size="11" fill="currentColor">Epic</text></svg>

Lumen の合計は PS5 で、Lumen in the Land of Nanite（ソフトウェア）が High 2.77 ms、Epic 4.63 ms、Lyra（ソフトウェア）が 4.29 ms と 8.70 ms、The Matrix Awakens（ハードウェアと遠景）が 6.38 ms と 11.31 ms です。Lake House（2080 Ti、ハードウェア）は Epic で 7.25 ms、Final Gather を 1 rpp にした ArchVis で 11.25 ms でした。

ソフトウェアとハードウェアの得失はシーンで変わります。Final Gather のトレース時間（PS5、1080p）は Land of Nanite（ほとんどの面に約 100 のメッシュが重なる）で、ソフトウェア 0.94 ms に対してハードウェア 10.03 ms でした。Lyra は 1.21 ms と 1.41 ms で、大差がありません。The Matrix Awakens は、1.83 ms、1.72 ms、遠景つきのハードウェア 2.13 ms でした。

<svg class="fig flow" viewBox="0 0 640 230" role="img" aria-label="Final Gather のトレース時間(ms、PS5、1080p)"><defs><marker id="ar" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#94a3b8"/></marker></defs><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">Final Gather のトレース時間(ms、PS5、1080p)</text><line x1="60" y1="190" x2="600" y2="190" stroke="#94a3b8"/><line x1="60" y1="40" x2="60" y2="190" stroke="#94a3b8"/><text x="54" y="194.0" text-anchor="end" font-size="10" fill="currentColor">0</text><text x="54" y="119.0" text-anchor="end" font-size="10" fill="currentColor">5.5</text><text x="54" y="44.0" text-anchor="end" font-size="10" fill="currentColor">11</text><rect x="104.0" y="177.2" width="43.0" height="12.8" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="125.5" y="173.1818181818182" text-anchor="middle" font-size="10" fill="currentColor">0.94</text><rect x="150.0" y="53.2" width="43.0" height="136.8" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="171.5" y="49.22727272727275" text-anchor="middle" font-size="10" fill="currentColor">10.03</text><text x="150.0" y="206" text-anchor="middle" font-size="11" fill="currentColor">Nanite</text><rect x="284.0" y="173.5" width="43.0" height="16.5" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="305.5" y="169.5" text-anchor="middle" font-size="10" fill="currentColor">1.21</text><rect x="330.0" y="170.8" width="43.0" height="19.2" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="351.5" y="166.77272727272728" text-anchor="middle" font-size="10" fill="currentColor">1.41</text><text x="330.0" y="206" text-anchor="middle" font-size="11" fill="currentColor">Lyra</text><rect x="464.0" y="165.0" width="43.0" height="25.0" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="485.5" y="161.04545454545453" text-anchor="middle" font-size="10" fill="currentColor">1.83</text><rect x="510.0" y="166.5" width="43.0" height="23.5" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="531.5" y="162.54545454545453" text-anchor="middle" font-size="10" fill="currentColor">1.72</text><text x="510.0" y="206" text-anchor="middle" font-size="11" fill="currentColor">Matrix</text><rect x="450" y="34" width="12" height="10" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="466" y="43" text-anchor="start" font-size="11" fill="currentColor">ソフトウェア</text><rect x="450" y="50" width="12" height="10" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="466" y="59" text-anchor="start" font-size="11" fill="currentColor">ハードウェア</text></svg>

発表の結論は次の通りです。最速を求め品質が落ちてよくメッシュが重なる（キットバッシュ）ならソフトウェアです。最高の品質、鏡面の反射、スキンメッシュの間接光が要るならハードウェアです。

## Nanite {#nanite}

Nanite の仕組みそのものは、このページの資料に含まれません。この発表が述べる Nanite との関係は、次の 3 点です。1 つ目はカードの撮影です。Nanite を使うと全カードを 1 回の描画で撮れ連続した LOD のおかげで小さなターゲットも簡略化でき、約 10 倍速くなります。2 つ目はハードウェア レイトレで、Nanite の形そのものは BLAS に入らないため、簡略なフォールバック メッシュを使うことです。3 つ目はそのフォールバック メッシュの位相がもとの形と合わず GBuffer から出すレイが自己交差することで、短い裏面無視のレイで直します。

## 自分の描画に取り入れるなら {#apply}

Lumen を自作するのは大規模な作業ですが、考え方は部分的に使えます。

- **簡略なシーンでレイを飛ばす。** 距離場や低ポリのメッシュに対して追います。薄い壁は距離場を膨らませて拾います。
- **光をキャッシュして使い回す。** ライトマップやプローブに貯め更新の予算を固定します。優先度は「使われたのに古い」順です。
- **低い解像度のプローブで集める。** 画面の格子点だけで追い周りは平面の重みで補間します。
- **前フレームの光を重要度に使う。** 見積もりが当たるほど同じ本数で誤差が下がります。
- **トレース段階を引き継ぐ。** 各段階が「どこまで進んだか」を書き出し、次の段階が続きから再開します。

## 限界 {#limits}

発表が挙げる限界は次の通りです。ボクセル ライティングは粗い。カードはインポート時に置くので、メッシュのアニメーションに追従しない（葉は深度の重みのバイアスで緩和するが、キャラクターには効かない）。層が多い木のようなメッシュは妥当な枚数のカードで覆えず反射で目立つ（拡散では、少しエネルギーが減るだけ）。発表は今後の課題としてエミッシブの明示的なサンプリング、スキンメッシュ対応、サーフェス キャッシュなしのモード、60 fps での品質、葉の品質を挙げています。

## 数字を出した C++ {#experiment}

薄い壁、八面体の立体角、積の重点サンプリング、スライドの数字からの見積もりを次の C++ で出しました。最初は壁の距離場と八面体の部品です。

```cpp
```cpp
// Lumen の数字を確かめる実験。
//   [1] 薄い壁を取りこぼさないために距離場を膨らませる量と拾える割合（2 次元）
//   [2] 八面体マップ 8x8 のテクセルの立体角の偏りと放射照度の誤差
//   [3] 積の重点サンプリング（BRDF × 前フレームの光）と、余弦サンプリングの誤差
//   [4] スライドの数字から出すメモリとレイの本数
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdio>
#include <random>
#include <vector>

constexpr double kPi = 3.14159265358979323846;
struct V3 { double x, y, z; };
static double Dot(V3 a, V3 b) { return a.x * b.x + a.y * b.y + a.z * b.z; }
static V3 Norm(V3 a) { double l = std::sqrt(Dot(a, a)); return {a.x / l, a.y / l, a.z / l}; }

// ---------------- [1] 薄い壁 ----------------
// 壁の中心線は点 c を通り法線が (cos a, sin a)。厚みは t。格子（間隔 1）の各点に壁までの符号つき距離を保存する。
struct Wall { double cx, cy, nx, ny, t; };
static double WallDist(const Wall& w, double x, double y) {
  return std::fabs((x - w.cx) * w.nx + (y - w.cy) * w.ny) - w.t * 0.5;   // 負なら壁の内側
}
// 保存した格子の値を双線形補間で引く（距離場のテクスチャを引くのと同じ）。
static double Sdf(const Wall& w, double x, double y) {
  double fx = std::floor(x), fy = std::floor(y), u = x - fx, v = y - fy;
  double d00 = WallDist(w, fx, fy), d10 = WallDist(w, fx + 1, fy), d01 = WallDist(w, fx, fy + 1), d11 = WallDist(w, fx + 1, fy + 1);
  return (d00 * (1 - u) + d10 * u) * (1 - v) + (d01 * (1 - u) + d11 * u) * v;
}

// ---------------- [2] 八面体 ----------------
static V3 OctDecode(double u, double v) {
  double ex = u * 2 - 1, ey = v * 2 - 1;
  V3 d{ex, ey, 1 - std::fabs(ex) - std::fabs(ey)};
  if (d.z < 0) {                                              // 下半球を折り返す
    double x = (1 - std::fabs(d.y)) * (d.x >= 0 ? 1 : -1), y = (1 - std::fabs(d.x)) * (d.y >= 0 ? 1 : -1);
    d.x = x; d.y = y;
  }
  return Norm(d);
}
// 空の放射輝度（一例）: 上が明るく、横から強い光（窓）が差す。
static double Rad(V3 d) {
  double sky = 0.3 + 0.7 * std::max(0.0, d.z);
  double win = 8.0 * std::exp(-std::acos(std::clamp(Dot(d, Norm({1, 0.2, 0.3})), -1.0, 1.0)) / 0.25);
  return sky + win;
}
```
```

`Sdf` は格子の各点に保存した壁までの距離を双線形補間して引きます。距離場のテクスチャを引くのと同じ動作です。`Rad` は上が明るく横から強い光（窓）が差す空の例です。次が `main` です。

```cpp
```cpp
int main() {
  std::mt19937 rng(11);
  std::uniform_real_distribution<double> uni(0, 1);

  // ---- [1] ----
  std::printf("[1] thin wall (thickness 0.2 voxel): fraction of rays that register a hit\n");
  std::printf("expand[voxel]  hit rate\n");
  for (double expand : {0.0, 0.25, 0.5, 0.707}) {
    int hit = 0, n = 200000;
    for (int i = 0; i < n; ++i) {
      double a = uni(rng) * kPi;                                 // 壁の向き
      Wall w{uni(rng) * 4, uni(rng) * 4, std::cos(a), std::sin(a), 0.2};
      double phi = (20 + 70 * uni(rng)) * kPi / 180;             // 壁と光線の角（20°〜90°）
      double ra = a + kPi / 2 + (phi - kPi / 2);                 // 光線の向き（壁の向きに対して phi）
      double dx = std::cos(ra), dy = std::sin(ra);
      double px = w.cx + (uni(rng) - 0.5) * 2, py = w.cy + (uni(rng) - 0.5) * 2;   // 壁の中心線の上の点
      double along = -(px - w.cx) * w.ny + (py - w.cy) * w.nx;   // 中心線上の位置
      px = w.cx - w.ny * along; py = w.cy + w.nx * along;        // 中心線へ射影
      bool found = false;
      for (double s = -3; s <= 3 && !found; s += 0.02) {         // 交差点の前後 3 voxel を細かく歩く
        double x = px + dx * s, y = py + dy * s;
        if (Sdf(w, x, y) - expand <= 0) found = true;            // 膨らませた面の内側に入ったら当たり
      }
      hit += found;
    }
    std::printf("%6.3f         %6.2f %%\n", expand, 100.0 * hit / n);
  }

  // ---- [2] ----
  std::printf("\n[2] octahedral 8x8: texel solid angle (sampled 64x64 per texel), sum should be 4pi\n");
  std::array<double, 64> omega{};
  double total = 0, mn = 1e9, mx = 0;
  for (int y = 0; y < 8; ++y)
    for (int x = 0; x < 8; ++x) {
      // 1 テクセルの立体角: テクセルを 32x32 に刻み、小片の 3 点を単位球へ投影して、外積の大きさ（平行四辺形の面積）を足す
      double sum = 0;
      const int S = 32;
      for (int j = 0; j < S; ++j)
        for (int i = 0; i < S; ++i) {
          double u0 = (x + double(i) / S) / 8, v0 = (y + double(j) / S) / 8, du = 1.0 / (8 * S);
          V3 a = OctDecode(u0, v0), b = OctDecode(u0 + du, v0), c = OctDecode(u0, v0 + du);
          V3 e1{b.x - a.x, b.y - a.y, b.z - a.z}, e2{c.x - a.x, c.y - a.y, c.z - a.z};
          V3 cr{e1.y * e2.z - e1.z * e2.y, e1.z * e2.x - e1.x * e2.z, e1.x * e2.y - e1.y * e2.x};
          sum += std::sqrt(Dot(cr, cr));                         // 単位球上の小片の面積 = 立体角
        }
      omega[y * 8 + x] = sum; total += sum; mn = std::min(mn, sum); mx = std::max(mx, sum);
    }
  std::printf("sum = %.4f (4pi = %.4f), min texel = %.4f, max texel = %.4f, 4pi/64 = %.4f, max/min = %.2f\n",
              total, 4 * kPi, mn, mx, 4 * kPi / 64, mx / mn);
  std::printf("irradiance for normals, uniform 4pi/64 vs per-texel omega vs reference (G of an example sky)\n");
  for (V3 n : {V3{0, 0, 1}, V3{1, 0, 0}, Norm({1, 0.2, 0.3}), V3{0, 0, -1}}) {
    double e_uniform = 0, e_exact = 0;
    for (int y = 0; y < 8; ++y)
      for (int x = 0; x < 8; ++x) {
        V3 d = OctDecode((x + 0.5) / 8, (y + 0.5) / 8);
        double c = std::max(0.0, Dot(n, d)) * Rad(d);
        e_uniform += c * 4 * kPi / 64;
        e_exact += c * omega[y * 8 + x];
      }
    double ref = 0;                                              // 参照: 球を 600x1200 に刻む
    for (int i = 0; i < 600; ++i)
      for (int j = 0; j < 1200; ++j) {
        double th = (i + 0.5) / 600 * kPi, ph = (j + 0.5) / 1200 * 2 * kPi;
        V3 d{std::sin(th) * std::cos(ph), std::sin(th) * std::sin(ph), std::cos(th)};
        ref += std::max(0.0, Dot(n, d)) * Rad(d) * std::sin(th) * (kPi / 600) * (2 * kPi / 1200);
      }
    std::printf("n=(%5.2f,%5.2f,%5.2f)  ref=%.3f  per-texel=%.3f (%+.1f%%)  uniform=%.3f (%+.1f%%)\n", n.x, n.y, n.z, ref,
                e_exact, 100 * (e_exact - ref) / ref, e_uniform, 100 * (e_uniform - ref) / ref);
  }

  // ---- [3] ----
  std::printf("\n[3] product importance sampling, 64 rays, hemisphere around +z, 4000 trials\n");
  const int M = 4096;                                            // 半球を一様に刻んだ候補の方向
  std::vector<V3> dirs(M);
  for (int i = 0; i < M; ++i) {
    double z = (i + 0.5) / M, ph = i * 2.399963229728653;        // 黄金角の螺旋（z は一様 = 立体角が一様）
    double r = std::sqrt(1 - z * z);
    dirs[i] = {r * std::cos(ph), r * std::sin(ph), z};
  }
  const double d_omega = 2 * kPi / M;
  auto lum = [](V3 d) { return 0.05 + 12.0 * std::exp(-std::acos(std::clamp(Dot(d, Norm({0.6, 0, 0.8})), -1.0, 1.0)) / 0.12)
                                    + 6.0 * std::exp(-std::acos(std::clamp(Dot(d, Norm({-0.7, 0.1, 0.7})), -1.0, 1.0)) / 0.12); };
  auto lum_prev = [&](V3 d) { return lum(Norm({d.x + 0.03, d.y - 0.02, d.z})); };   // 前フレーム: 少しずれた推定
  double truth = 0;
  for (int i = 0; i < M; ++i) truth += lum(dirs[i]) * dirs[i].z * d_omega;
  auto run = [&](const char* name, const std::vector<double>& q) {   // q: 各候補を選ぶ確率の重み（正規化前）
    double qs = 0;
    for (double v : q) qs += v;
    std::vector<double> cdf(M);
    double acc = 0;
    for (int i = 0; i < M; ++i) { acc += q[i] / qs; cdf[i] = acc; }
    double se = 0;
    const int N = 64, T = 4000;
    for (int t = 0; t < T; ++t) {
      double est = 0;
      for (int k = 0; k < N; ++k) {
        int i = int(std::lower_bound(cdf.begin(), cdf.end(), uni(rng)) - cdf.begin());
        i = std::min(i, M - 1);
        double p = q[i] / qs;                                    // 候補 i を選ぶ確率
        est += lum(dirs[i]) * dirs[i].z * d_omega / (p * N);      // 候補 i の寄与 f·dΩ を、選ぶ確率 p で割る（N 本の平均）
      }
      se += (est - truth) * (est - truth);
    }
    double rmse = std::sqrt(se / T);
    std::printf("%-28s rmse/E = %6.2f %%\n", name, 100 * rmse / truth);
    return rmse;
  };
  std::vector<double> q_uniform(M), q_cos(M), q_light(M), q_product(M);
  for (int i = 0; i < M; ++i) {
    q_uniform[i] = 1.0;
    q_cos[i] = dirs[i].z;
    q_light[i] = lum_prev(dirs[i]) + 0.02;                       // 光だけ（BRDF を無視）
    q_product[i] = lum_prev(dirs[i]) * dirs[i].z + 0.02 * dirs[i].z;   // BRDF × 光（積）。+0.02 は外れた推定の保険
  }
  double r_u = run("uniform", q_uniform);
  double r_c = run("cosine (BRDF only)", q_cos);
  double r_l = run("lighting only (prev frame)", q_light);
  double r_p = run("product (BRDF x prev frame)", q_product);
  std::printf("equivalent cosine rays for the product result: %.0f\n", 64 * (r_c / r_p) * (r_c / r_p));
  (void)r_u; (void)r_l;

  // ---- [4] ----
  std::printf("\n[4] numbers from the slides\n");
  double atlas = 4096.0 * 4096;
  std::printf("surface cache atlas 4096x4096 = %.1f M texels\n", atlas / 1e6);
  std::printf("  albedo BC7 8bpp = %.0f MB, opacity BC4 4bpp = %.0f MB, depth R16 = %.0f MB, normal = 16 MB (slide), emissive BC6H 8bpp = %.0f MB\n",
              atlas / 1048576, atlas * 0.5 / 1048576, atlas * 2 / 1048576, atlas / 1048576);
  std::printf("  sum = %.0f MB\n", atlas / 1048576 + atlas * 0.5 / 1048576 + atlas * 2 / 1048576 + 16 + atlas / 1048576);
  std::printf("global SDF: 4 clipmaps of 256^3, 1 byte = %.0f MB if dense (the slides say sparse)\n", 4.0 * 256 * 256 * 256 / 1048576);
  std::printf("voxel lighting: 4 clipmaps of 64^3 x 6 directions x 4 bytes (RGBA8, assumed) = %.1f MB\n", 4.0 * 64 * 64 * 64 * 6 * 4 / 1048576);
  int w = 1920, h = 1080;
  int pw = (w + 15) / 16, ph = (h + 15) / 16;
  std::printf("screen probes at 1/16 res: %d x %d = %d probes, 8x8 rays each = %d rays = %.3f rays/pixel\n", pw, ph, pw * ph, pw * ph * 64,
              double(pw * ph * 64) / (double(w) * h));
  std::printf("filter: 3x3 probes x 16 px = %d x %d pixels\n", 3 * 16, 3 * 16);
  std::printf("mesh SDF pool = 320 MB (slide), Global SDF coarse mip = 1/4 res\n");
  return 0;
}
```
```

```text title="実行結果"
[1] thin wall (thickness 0.2 voxel): fraction of rays that register a hit
expand[voxel]  hit rate
 0.000          13.14 %
 0.250          77.72 %
 0.500         100.00 %
 0.707         100.00 %
```

```text title="実行結果（続き）"
[2] octahedral 8x8: texel solid angle (sampled 64x64 per texel), sum should be 4pi
sum = 12.5659 (4pi = 12.5664), min texel = 0.1028, max texel = 0.2879, 4pi/64 = 0.1963, max/min = 2.80
irradiance for normals, uniform 4pi/64 vs per-texel omega vs reference (G of an example sky)
n=( 0.00, 0.00, 1.00)  ref=3.273  per-texel=3.277 (+0.1%)  uniform=3.183 (-2.8%)
n=( 1.00, 0.00, 0.00)  ref=3.781  per-texel=3.969 (+5.0%)  uniform=4.205 (+11.2%)
n=( 0.94, 0.19, 0.28)  ref=4.153  per-texel=4.350 (+4.8%)  uniform=4.573 (+10.1%)
n=( 0.00, 0.00,-1.00)  ref=1.098  per-texel=1.044 (-4.9%)  uniform=0.994 (-9.5%)
```

```text title="実行結果（続き）"
[3] product importance sampling, 64 rays, hemisphere around +z, 4000 trials
uniform                      rmse/E =  35.77 %
cosine (BRDF only)           rmse/E =  26.93 %
lighting only (prev frame)   rmse/E =   4.37 %
product (BRDF x prev frame)  rmse/E =   2.19 %
equivalent cosine rays for the product result: 9695
```

```text title="実行結果（続き）"
[4] numbers from the slides
surface cache atlas 4096x4096 = 16.8 M texels
  albedo BC7 8bpp = 16 MB, opacity BC4 4bpp = 8 MB, depth R16 = 32 MB, normal = 16 MB (slide), emissive BC6H 8bpp = 16 MB
  sum = 88 MB
global SDF: 4 clipmaps of 256^3, 1 byte = 64 MB if dense (the slides say sparse)
voxel lighting: 4 clipmaps of 64^3 x 6 directions x 4 bytes (RGBA8, assumed) = 24.0 MB
screen probes at 1/16 res: 120 x 68 = 8160 probes, 8x8 rays each = 522240 rays = 0.252 rays/pixel
filter: 3x3 probes x 16 px = 48 x 48 pixels
mesh SDF pool = 320 MB (slide), Global SDF coarse mip = 1/4 res
```

## よくあるミス {#mistakes}

??? failure "薄い壁から光が漏れる"
    距離場が壁を取りこぼしている。距離場をボクセルの対角の半分程度膨らませる。始点では 0 にして距離で増やす。

??? failure "接触影が消える"
    膨らませを始点から一定の量にしている。始点では 0 にし距離に比例して増やす。

??? failure "画面のトレースを切ったら、自己交差が出る"
    GBuffer とレイトレのシーンの食い違いを画面のトレースが隠していた。短いレイをイプシロンの距離まで裏面無視で飛ばしてから、長いレイを飛ばす。

??? failure "ライトの色が動いてから、数フレーム遅れて反映される"
    サーフェス キャッシュは固定予算で、優先度の高いページから更新する。反映の遅れはこの仕組みの代償で、故障ではない。

??? failure "八面体のプローブで、放射照度が偏る"
    テクセルの立体角を一様にしている。八面体の立体角は最大と最小で 2.8 倍違う。テクセルごとの立体角を使う。

## これだけ覚える {#summary}

!!! abstract "まとめ"
    - [x] Lumen は画面、メッシュ SDF、グローバル SDF、ハードウェア、スカイライトを引き継いで追う。
    - [x] 当たった点の光は、サーフェス キャッシュ（カード）から読む。更新は固定予算と優先度で行う。
    - [x] ノイズはスクリーン プローブ、ワールド放射輝度キャッシュ、積の重点サンプリングで減らす。
    - [x] 薄い壁は距離場を膨らませて拾う。始点では 0、距離で増やす。
    - [x] ソフトウェアとハードウェアの得失はシーンで逆転する。重なりが多ければソフトウェア。

## 参考 {#references}

- Daniel Wright, Krzysztof Narkowicz, Patrick Kelly, "Lumen: Real-time Global Illumination in Unreal Engine 5", SIGGRAPH 2022, Advances in Real-Time Rendering in Games. スライド全 199 枚の本文と読み上げ原稿を読んだ。画像と動画は読めていない。
- Daniel Wright, "Radiance Caching for Real-time Global Illumination", SIGGRAPH 2021. 読んでいない。Final Gather の元の発表として挙げる。
- Daniel Wright, "Dynamic Occlusion with Signed Distance Fields", SIGGRAPH 2015. 読んでいない。
- Brian Karis, Rune Stubbe, Graham Wihlidal, "A Deep Dive into Nanite Virtualized Geometry", SIGGRAPH 2021. 読んでいない。
- Aleksander Netzel, Tiago Costa, 他, "Ray Tracing Open Worlds in Unreal Engine 5", SIGGRAPH 2022. 読んでいない。
- Tomasz Stachowiak, Yasin Uludag, "Stochastic Screen-Space Reflections", SIGGRAPH 2015. 読んでいない。
- このページの HLSL と C++ の実験（薄い壁、八面体の立体角、積の重点サンプリング）は説明のために書いたもの。

## 関連ページ {#related}

- [Global Illumination (GI)](index.md)
- [DDGI](ddgi.md)
- [Voxel GI](voxel-gi.md)
- [Taxonomy of Methods](theory/taxonomy.md)
- [Mesh Shaders](../pipeline/mesh-shaders.md)
- [Visibility Buffer](../pipeline/visibility-buffer.md)
