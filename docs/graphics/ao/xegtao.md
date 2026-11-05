---
title: XeGTAO
tags:
  - 描画
---

# XeGTAO

[GTAO](gtao.md) の論文はアルゴリズムを 30 行の疑似コードで示します。ところが、これをそのまま実装すると論文に書いていない細部で何度も迷います。深度をどう読むか中心の画素をどうずらすかノイズをどう振るか薄い物体や半径の端をどう扱うか、デノイズをどうするか。Intel の XeGTAO はこれらを全部決めた GTAO の実用的な実装です（HLSL、MIT ライセンス）。このページでは XeGTAO のソースを読み 4 つのコンピュート シェーダーを、論文の疑似コードの行番号と対応させながら、コメント付きの完成形で書き直します。論文の積分式がモンテカルロの正解と合うことも C++ で確かめました。

!!! tip "ポイント"
    - 4 つのコンピュート シェーダーで動く。深度のプリフィルタ（ミップ付きのビュー空間 Z）、法線（深度から作る場合）、メイン（GTAO）、デノイズ。
    - 品質はスライスの数と 1 スライスあたりのステップ数で決まる。Low が 1 × 2、Medium が 2 × 2、High が 3 × 3、Ultra が 9 × 3 である。
    - ノイズは Hilbert 曲線で画素の並びを散らし、R2 列で値にする。フレームごとに添字をずらし TAA と組み合わせて収束させる。
    - 遠いサンプルほど粗い深度ミップを読む。ミップの番号は `log2(画面上の距離) − 3.3` で決まる。
    - 既定の半径は 0.5（ワールド単位）に補正の 1.457 を掛けた値である。シーンの縮尺に合わせて決める。

!!! info "このページを読む前に"
    - [GTAO](gtao.md)（地平線を探す積分の考え方）
    - [AO Filtering](filtering/index.md)（バイラテラル ブラーと時間方向の蓄積）

## 読んだ資料 {#sources}

- Intel XeGTAO のソース（GameTechDev/XeGTAO、`XeGTAO.h`、`XeGTAO.hlsli`、`vaGTAO.hlsl`）。バージョン 1.30（ベント法線対応）の master を全部読みました。デバッグ表示のコードとリファレンスの RTAO の部分は、解説していません。
- Jimenez, Wu, Pesce, Jarabo, "Practical Realtime Strategies for Accurate Indirect Occlusion", Activision Technical Memo ATVI-TR-16-01（2016）。第 1〜7 節（結果まで）を読みました。付録と結論、参考文献は読んでいません。

XeGTAO のコードは MIT ライセンスです。このページのコードは XeGTAO の構成と式を参考にして、読んで理解した形に私が書き直したもので、コピーではありません。半精度（`min16float`）、ベント法線、薄い物体の補正は省いています。

## 4 つのパス {#passes}

<svg class="fig flow" viewBox="0 0 730 134" role="img" aria-label="XeGTAO のパス"><defs><marker id="xe-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#94a3b8"/></marker></defs><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">XeGTAO のコンピュート シェーダー(1 フレーム)</text><rect x="10" y="36" width="108" height="60" rx="6" fill="rgba(148,163,184,0.18)" stroke="#94a3b8"/><text x="64.0" y="70.0" text-anchor="middle" font-size="10" fill="currentColor">深度 (NDC)</text><line x1="118" y1="66" x2="128" y2="66" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#xe-a)"/><rect x="128" y="36" width="108" height="60" rx="6" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="182.0" y="56.0" text-anchor="middle" font-size="10" fill="currentColor">① プリフィルタ</text><text x="182.0" y="70.0" text-anchor="middle" font-size="10" fill="currentColor">ビュー空間 Z</text><text x="182.0" y="84.0" text-anchor="middle" font-size="10" fill="currentColor">5 段のミップ</text><line x1="236" y1="66" x2="246" y2="66" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#xe-a)"/><rect x="246" y="36" width="108" height="60" rx="6" fill="rgba(148,163,184,0.18)" stroke="#94a3b8"/><text x="300.0" y="63.0" text-anchor="middle" font-size="10" fill="currentColor">② 法線</text><text x="300.0" y="77.0" text-anchor="middle" font-size="10" fill="currentColor">(深度から)</text><line x1="354" y1="66" x2="364" y2="66" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#xe-a)"/><rect x="364" y="36" width="108" height="60" rx="6" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="418.0" y="56.0" text-anchor="middle" font-size="10" fill="currentColor">③ メイン</text><text x="418.0" y="70.0" text-anchor="middle" font-size="10" fill="currentColor">スライス・地平線</text><text x="418.0" y="84.0" text-anchor="middle" font-size="10" fill="currentColor">可視性 + エッジ</text><line x1="472" y1="66" x2="482" y2="66" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#xe-a)"/><rect x="482" y="36" width="108" height="60" rx="6" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="536.0" y="63.0" text-anchor="middle" font-size="10" fill="currentColor">④ デノイズ</text><text x="536.0" y="77.0" text-anchor="middle" font-size="10" fill="currentColor">エッジを保つ</text><line x1="590" y1="66" x2="600" y2="66" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#xe-a)"/><rect x="600" y="36" width="108" height="60" rx="6" fill="rgba(148,163,184,0.18)" stroke="#94a3b8"/><text x="654.0" y="70.0" text-anchor="middle" font-size="10" fill="currentColor">AO (R8)</text><text x="10" y="122" text-anchor="start" font-size="10" fill="currentColor">TAA があるとき: ノイズの添字を 288 × (フレーム % 64) ずらし、デノイズは 1 回で足りる</text></svg>

1. **深度のプリフィルタ**: NDC の深度をビュー空間の Z [m] に直し、5 段のミップを作ります。1 グループ（8 × 8 スレッド）が 16 × 16 画素を担当し、1 スレッドが 2 × 2 画素を書きます。
2. **法線**: 深度から、ビュー空間の法線を作ります。G バッファの法線があれば不要です。
3. **メイン**: 画素ごとにスライスを取り地平線を探して、可視性を出します。同時にデノイズに使うエッジも書きます。
4. **デノイズ**: エッジを保つフィルターで、ノイズをならします。TAA があれば 1 回で足ります（XeGTAO は、0〜3 の段階を持ちます）。

メインのパスは元の XeGTAO では 4 つの品質プリセットごとに別のエントリ ポイント（`CSGTAOLow`、`Medium`、`High`、`Ultra`）です。違いはスライス数とステップ数だけです。

## 座標とパラメーター {#constants}

```hlsl
// XeGTAO（Intel、MIT ライセンス）の構成を、読んで理解した形に書き直した HLSL。
// 元のコードは 4 つのコンピュート シェーダーに分かれる。ここでも同じ分け方にしている。
//   ① PrefilterDepthsCS : NDC の深度 → ビュー空間の Z にして、5 段のミップを作る
//   ② NormalsCS         : 深度から、ビュー空間の法線を作る（G バッファの法線がなければ）
//   ③ MainPassCS        : スライスごとに地平線を探して、可視性を出す（GTAO の本体）
//   ④ DenoiseCS         : エッジを保つ空間フィルター
// 論文: Jimenez ほか "Practical Realtime Strategies for Accurate Indirect Occlusion" (2016) の Algorithm 1 に沿う。
// 簡略化: min16float（半精度）は使わず float。ベント法線、薄い物体の補正は省いた。

cbuffer GtaoCB : register(b0) {
  int2 g_size;                  // ビューポートの大きさ [px]
  float2 g_pixel_size;          // 1 / 大きさ
  float2 g_depth_unpack;        // x = 乗数、y = 加数。ビュー空間 Z = x / (y - 深度)
  float2 g_ndc_to_view_mul;     // NDC → ビュー空間の xy の倍率（tanHalfFOV の 2 倍。y は符号反転）
  float2 g_ndc_to_view_add;     // 同じく加算（tanHalfFOV の -1 倍と +1 倍）
  float2 g_ndc_mul_pixel;       // g_ndc_to_view_mul × g_pixel_size。1 画素がビュー空間でどれだけか
  float g_radius;               // 影響半径 [m]。XeGTAO の既定は 0.5
  float g_falloff_range;        // 半径の端で弱める範囲（割合）。既定 0.615
  float g_radius_multiplier;    // 半径にかける補正。既定 1.457
  float g_final_power;          // 最終の可視性にかけるべき乗。既定 2.2
  float g_sample_power;         // サンプルを手前に寄せる強さ。既定 2.0
  float g_mip_offset;           // 深度ミップの選び方のオフセット。既定 3.3
  int g_noise_index;            // フレーム番号 % 64（TAA があるとき）。なければ 0
  int g_slice_count;            // スライス数（品質プリセット）
  int g_steps_per_slice;        // 1 スライスの片側のステップ数
  float g_denoise_beta;         // デノイズの中心画素の重み。既定 1.2
  float2 g_pad;
};

static const float kPi = 3.14159265358979;
static const float kHalfPi = 1.5707963267949;

// ================= 共通：座標の変換 =================

// NDC の深度（0〜1）→ ビュー空間の Z [m]。投影行列の (2,2), (3,2) から作った定数を使う。
float ViewSpaceDepth(float ndc_depth) {
  return g_depth_unpack.x / (g_depth_unpack.y - ndc_depth);
}

// 画面の位置（0〜1）とビュー空間の Z から、ビュー空間の位置を作る。
float3 ViewSpacePosition(float2 screen_uv, float view_z) {
  float2 xy = (g_ndc_to_view_mul * screen_uv + g_ndc_to_view_add) * view_z;   // 画面の位置 × tan(FOV/2) × Z
  return float3(xy, view_z);
}
```

ビュー空間の位置は画面の位置（0〜1）に `tan(FOV/2) × 2` を掛けて −`tan(FOV/2)` を足し、Z を掛けて作ります。CPU 側では投影行列から次のように作ります。

- `depthLinearizeMul = −proj[3][2]`、`depthLinearizeAdd = proj[2][2]`（行ベクトルの行列のとき）。ビュー空間 Z ＝ mul / (add − 深度)。
- `tanHalfFOVY = 1 / proj[1][1]`、`tanHalfFOVX = 1 / proj[0][0]`。
- `NDCToViewMul = (tanHalfFOVX × 2, tanHalfFOVY × −2)`、`NDCToViewAdd = (−tanHalfFOVX, tanHalfFOVY)`。

XeGTAO の設定の既定値をソースの `XeGTAO.h` から引く一覧にします。

| 設定 | 既定値 | 範囲（ツールチップ） |
| --- | --- | --- |
| Radius | 0.5 | 0 以上 |
| RadiusMultiplier | 1.457 | 0.3〜3.0 |
| FalloffRange | 0.615 | 0〜1 |
| SampleDistributionPower | 2.0 | 1.0〜3.0 |
| ThinOccluderCompensation | 0.0 | 0〜0.7 |
| FinalValuePower | 2.2 | 0.5〜5.0 |
| DepthMIPSamplingOffset | 3.30 | 2.0〜6.0 |
| DenoiseBlurBeta | 1.2 | （無効は 1e4） |

`Radius` は見た目を最も大きく変えます。シーンの縮尺に合わせて決める値で、既定の 0.5 は「1 が 1 m」のときの値です。実際に使われるのは `Radius × RadiusMultiplier ＝ 0.5 × 1.457 ＝ 0.729` です。補正の 1.457 はスクリーン空間に固有の偏りを打ち消して、レイトレースの正解に合わせるための値だとコードのコメントが説明しています。

`FalloffRange` は半径の端で影響を弱めるための範囲（割合）です。0 にすると半径の端で AO が急に途切れます。`SampleDistributionPower` はサンプルを手前に寄せる強さで、既定の 2.0 は「小さい隙間のほうが、大きな面より重要」という判断です。`FinalValuePower` は最後の可視性にかけるべき乗で、上のヒューリスティックが何をするかを変えます。`DepthMIPSamplingOffset` は性能（テクスチャ帯域）と品質の主なトレードオフで、薄い物体と時間的な安定に影響します。

<svg class="fig flow" viewBox="0 0 620 262" role="img" aria-label="1 つのスライスの幾何"><defs><marker id="xe-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#94a3b8"/></marker></defs><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">1 つのスライス: 視線 v、傾いた法線、地平線の角 h0 と h1</text><circle cx="300" cy="240" r="5" fill="#e5aa28"/><text x="310" y="256" text-anchor="start" font-size="11" fill="currentColor">画素</text><line x1="300" y1="240" x2="300" y2="70" stroke="#94a3b8" stroke-width="2" marker-end="url(#xe-a)"/><text x="306" y="80" text-anchor="start" font-size="11" fill="currentColor">v(視線)</text><line x1="300" y1="240" x2="356.2" y2="100.9" stroke="#4c8bf5" stroke-width="2.5" marker-end="url(#xe-a)"/><text x="362.1909890123868" y="100.92242181498187" text-anchor="start" font-size="11" fill="currentColor">射影した法線</text><line x1="300" y1="240" x2="138.9" y2="139.3" stroke="#e5aa28" stroke-width="2" stroke-dasharray="5 3"/><text x="132.87086173027905" y="143.31533979569107" text-anchor="end" font-size="12" fill="currentColor">h0</text><line x1="300" y1="240" x2="472.2" y2="159.7" stroke="#e5aa28" stroke-width="2" stroke-dasharray="5 3"/><text x="478.1984795369635" y="163.7025302692671" text-anchor="start" font-size="12" fill="currentColor">h1</text><polygon points="300,240 198.2,176.4 202.9,169.5 208.1,162.9 213.7,156.6 219.7,150.8 226.1,145.4 232.9,140.5 240.0,136.1 247.4,132.1 255.0,128.7 262.9,125.9 271.0,123.6 279.2,121.8 287.5,120.7 295.8,120.1 304.2,120.1 312.5,120.7 320.8,121.8 329.0,123.6 337.1,125.9 345.0,128.7 352.6,132.1 360.0,136.1 367.1,140.5 373.9,145.4 380.3,150.8 386.3,156.6 391.9,162.9 397.1,169.5 401.8,176.4 406.0,183.7" fill="rgba(76,139,245,0.22)" stroke="none"/><text x="300" y="180" text-anchor="middle" font-size="11" fill="currentColor">開けている範囲</text><line x1="40" y1="240" x2="560" y2="240" stroke="#94a3b8" stroke-width="3"/><text x="560" y="256" text-anchor="end" font-size="11" fill="currentColor">面</text><text x="40" y="60" text-anchor="start" font-size="11" fill="currentColor">h0 = -acos(horizonCos1)、h1 = acos(horizonCos0)</text><text x="40" y="78" text-anchor="start" font-size="11" fill="currentColor">可視性 = |射影した法線| × (iarc(h0) + iarc(h1))</text></svg>

## パス 1：深度のプリフィルタ {#prefilter}

メインのパスは遠いサンプルを読むときフル解像度の深度を読みません。粗いミップを読むのでキャッシュが効きサンプルが遠くても帯域が増えません。そのミップを 1 回のディスパッチで作ります。

```hlsl
// ================= ① 深度のプリフィルタ =================

Texture2D<float> g_ndc_depth : register(t0);              // 描画済みの深度バッファ
SamplerState g_point_clamp : register(s0);
RWTexture2D<float> g_mip0 : register(u0);                 // ビュー空間の Z（フル解像度）
RWTexture2D<float> g_mip1 : register(u1);                 // 1/2
RWTexture2D<float> g_mip2 : register(u2);                 // 1/4
RWTexture2D<float> g_mip3 : register(u3);                 // 1/8
RWTexture2D<float> g_mip4 : register(u4);                 // 1/16
groupshared float g_scratch[8][8];                        // ミップ 1 の値を、グループ内で受け渡す

// 4 つの深度を混ぜてミップにする。XeGTAO は「いちばん奥との差で重みを下げる」重み付き平均を使う。
// 単純な平均だと、物体の縁で前景と背景の間の「存在しない」深度ができ、そこから偽の影が出る。
float DepthMipFilter(float d0, float d1, float d2, float d3) {
  float max_depth = max(max(d0, d1), max(d2, d3));
  float radius = 0.75 * g_radius * g_radius_multiplier;   // 経験的に 0.75 倍（XeGTAO の depthRangeScaleFactor）
  float falloff_range = g_falloff_range * radius;
  float falloff_from = radius * (1.0 - g_falloff_range);
  float mul = -1.0 / falloff_range;                       // 奥との差が falloff_from を超えたら重みが下がる
  float add = falloff_from / falloff_range + 1.0;
  float w0 = saturate((max_depth - d0) * mul + add);
  float w1 = saturate((max_depth - d1) * mul + add);
  float w2 = saturate((max_depth - d2) * mul + add);
  float w3 = saturate((max_depth - d3) * mul + add);
  return (w0 * d0 + w1 * d1 + w2 * d2 + w3 * d3) / (w0 + w1 + w2 + w3);   // 最大の画素の重みは 1 なので 0 割りにならない
}

[numthreads(8, 8, 1)]       // 1 スレッド = 2 x 2 画素。1 グループ = 16 x 16 画素
void PrefilterDepthsCS(uint2 id : SV_DispatchThreadID, uint2 gid : SV_GroupThreadID) {
  // ミップ 0: 2 x 2 を Gather で 1 回に読み、ビュー空間の Z にして書く。
  uint2 base = id * 2;
  float4 d4 = g_ndc_depth.GatherRed(g_point_clamp, base * g_pixel_size, int2(1, 1));   // (x=左下..の並び: w, z, x, y)
  float d_tl = min(ViewSpaceDepth(d4.w), 65504.0);        // 半精度の上限で切る（無限遠が inf にならない）
  float d_tr = min(ViewSpaceDepth(d4.z), 65504.0);
  float d_bl = min(ViewSpaceDepth(d4.x), 65504.0);
  float d_br = min(ViewSpaceDepth(d4.y), 65504.0);
  g_mip0[base + uint2(0, 0)] = d_tl;
  g_mip0[base + uint2(1, 0)] = d_tr;
  g_mip0[base + uint2(0, 1)] = d_bl;
  g_mip0[base + uint2(1, 1)] = d_br;

  // ミップ 1。
  float m1 = DepthMipFilter(d_tl, d_tr, d_bl, d_br);
  g_mip1[id] = m1;
  g_scratch[gid.x][gid.y] = m1;
  GroupMemoryBarrierWithGroupSync();

  // ミップ 2: 2 つおきのスレッドが、隣の 2 x 2 を読む。
  float m2 = 0;
  if (all((gid % 2) == 0)) {
    m2 = DepthMipFilter(g_scratch[gid.x][gid.y], g_scratch[gid.x + 1][gid.y],
                        g_scratch[gid.x][gid.y + 1], g_scratch[gid.x + 1][gid.y + 1]);
    g_mip2[id / 2] = m2;
  }
  GroupMemoryBarrierWithGroupSync();
  if (all((gid % 2) == 0)) g_scratch[gid.x][gid.y] = m2;
  GroupMemoryBarrierWithGroupSync();

  // ミップ 3: 4 つおき。
  float m3 = 0;
  if (all((gid % 4) == 0)) {
    m3 = DepthMipFilter(g_scratch[gid.x][gid.y], g_scratch[gid.x + 2][gid.y],
                        g_scratch[gid.x][gid.y + 2], g_scratch[gid.x + 2][gid.y + 2]);
    g_mip3[id / 4] = m3;
  }
  GroupMemoryBarrierWithGroupSync();
  if (all((gid % 4) == 0)) g_scratch[gid.x][gid.y] = m3;
  GroupMemoryBarrierWithGroupSync();

  // ミップ 4: 8 つおき（1 グループに 1 つ）。
  if (all((gid % 8) == 0)) {
    g_mip4[id / 8] = DepthMipFilter(g_scratch[gid.x][gid.y], g_scratch[gid.x + 4][gid.y],
                                    g_scratch[gid.x][gid.y + 4], g_scratch[gid.x + 4][gid.y + 4]);
  }
}
```

ミップの作り方に重み付き平均を使うのが要点です。4 つの深度を単純に平均すると、物体の縁で前景と背景の間の「存在しない」深度ができて、そこから偽の影が出ます。そこで、いちばん奥の深度との差が大きいほど重みを下げます（`DepthMipFilter`）。重みは半径に 0.75 を掛けた範囲で 1 から 0 へ直線で下がります。0.75 は経験的な値だとコードのコメントが書いています。

グループの中のスレッドが `groupshared` の配列を使って、ミップ 2〜4 を順に作ります。ミップ 1 を各スレッドが書いたあとで、2 つおき 4 つおき 8 つおきのスレッドが、隣の値を読んで次のミップを作ります。深度は半精度の上限（65504）で切ります。無限遠の深度が半精度で inf にならないようにするためです。

## パス 2：法線とエッジ {#normals}

```hlsl
// ================= エッジ（法線の生成と、デノイズで使う）=================

// 中心と上下左右の深度差から、各方向が「同じ面」である度合い（0〜1）を出す。
// 傾いた面で深度が線形に変わるぶんは、傾きを補正して差し引く（slope-adjusted）。
float4 CalculateEdges(float center, float left, float right, float top, float bottom) {
  float4 e = float4(left, right, top, bottom) - center;
  float slope_lr = (e.y - e.x) * 0.5;                     // 左右の差から、傾きの見積もり
  float slope_tb = (e.w - e.z) * 0.5;
  float4 adjusted = e + float4(slope_lr, -slope_lr, slope_tb, -slope_tb);
  e = min(abs(e), abs(adjusted));                         // 傾きを引いた後のほうが小さければ、そちらを採る
  return saturate(1.25 - e / (center * 0.011));           // 中心の深度の 1.1 % 以上離れたら 0 に近づく
}

// 2 ビットずつ 4 方向を 1 バイトに詰める。値は 4 段階（0, 1/3, 2/3, 1）で、なめらかな遷移を保つ。
float PackEdges(float4 e) {
  e = round(saturate(e) * 2.9);
  return dot(e, float4(64.0, 16.0, 4.0, 1.0) / 255.0);
}
float4 UnpackEdges(float packed) {
  uint p = (uint)(packed * 255.5);
  return saturate(float4((p >> 6) & 3, (p >> 4) & 3, (p >> 2) & 3, p & 3) / 3.0);
}

// ================= ② 深度から法線 =================

Texture2D<float> g_view_depth : register(t1);             // ① で作った mip0 を読む（ミップ付き）
RWTexture2D<float4> g_normal_out : register(u5);          // ビュー空間の法線（xyz）

[numthreads(8, 8, 1)]
void NormalsCS(uint2 id : SV_DispatchThreadID) {
  if (any(id >= (uint2)g_size)) return;
  float2 uv = (id + 0.5) * g_pixel_size;
  float c = g_view_depth.Load(int3(id, 0));
  float l = g_view_depth.Load(int3(max((int2)id - int2(1, 0), 0), 0));
  float r = g_view_depth.Load(int3(min((int2)id + int2(1, 0), g_size - 1), 0));
  float t = g_view_depth.Load(int3(max((int2)id - int2(0, 1), 0), 0));
  float b = g_view_depth.Load(int3(min((int2)id + int2(0, 1), g_size - 1), 0));
  float4 edges = CalculateEdges(c, l, r, t, b);

  float3 pc = ViewSpacePosition(uv, c);
  float3 pl = normalize(ViewSpacePosition(uv - float2(g_pixel_size.x, 0), l) - pc);
  float3 pr = normalize(ViewSpacePosition(uv + float2(g_pixel_size.x, 0), r) - pc);
  float3 pt = normalize(ViewSpacePosition(uv - float2(0, g_pixel_size.y), t) - pc);
  float3 pb = normalize(ViewSpacePosition(uv + float2(0, g_pixel_size.y), b) - pc);

  // 4 つの象限の外積を、エッジで重み付けして足す。段差をまたぐ象限は重みが 0 に近づく。
  float4 w = saturate(float4(edges.x * edges.z, edges.z * edges.y, edges.y * edges.w, edges.w * edges.x) + 0.01);
  float3 n = w.x * cross(pl, pt) + w.y * cross(pt, pr) + w.z * cross(pr, pb) + w.w * cross(pb, pl);
  g_normal_out[id] = float4(normalize(n), 0);
}
```

エッジは中心と上下左右の深度の差から作ります。傾いた面では深度が線形に変わるだけで差が出ます。そこで、左右の差から傾きを見積もり引いたあとの差と元の差の小さいほうを採ります（`slope-adjusted`）。中心の深度の 1.1 % 以上離れたら、0 に近づきます。

法線は 4 つの象限（左と上、上と右、右と下、下と左）の外積をエッジで重み付けして足します。段差をまたぐ象限は重みが 0 に近づくので、物体の縁で法線が崩れません。重みに 0.01 を足すのは、4 方向すべてが段差のときも 0 割りにならないためです。

XeGTAO は法線を深度から作る処理をメインのパスの中に入れていた時期がありました。ところが、32 bit の深度が要るのに、全体を遅くするのでバージョン 1.20 で独立のパスに分けました。法線を他の効果と共有できるようになります。

## パス 3：メイン {#main}

画素ごとの手順を論文の疑似コードの行番号と対応させて、順に見ます。

```hlsl
// ================= ③ メイン パス =================

Texture2D<float> g_work_depth : register(t2);             // ビュー空間の Z（5 段のミップ付き）
Texture2D<float4> g_normals : register(t3);               // ビュー空間の法線
RWTexture2D<float> g_ao_out : register(u6);               // 可視性（1.5 で割って 0〜1 に収める前の値）
RWTexture2D<float> g_edges_out : register(u7);            // 詰めたエッジ

static const float kOcclusionScale = 1.5;                 // 生の値は 1 を超えうる。UNORM に詰めるために割る

// Hilbert 曲線の添字（64 x 64 の繰り返し）。隣の画素のノイズを、2D で遠く離すために使う。
uint HilbertIndex(uint px, uint py) {
  uint index = 0;
  for (uint level = 32; level > 0; level /= 2) {
    uint rx = (px & level) > 0 ? 1 : 0;
    uint ry = (py & level) > 0 ? 1 : 0;
    index += level * level * ((3 * rx) ^ ry);
    if (ry == 0) {
      if (rx == 1) { px = 63 - px; py = 63 - py; }       // 区画を反転
      uint tmp = px; px = py; py = tmp;                   // x と y を入れ替える
    }
  }
  return index;
}

// 空間 + 時間のノイズ（0〜1 の 2 値）。Hilbert 曲線の添字を R2 列に通す。
float2 SpatioTemporalNoise(uint2 pix) {
  uint index = HilbertIndex(pix.x % 64, pix.y % 64);
  index += 288 * ((uint)g_noise_index % 64u);                    // フレームごとに添字をずらす（288 は XeGTAO が試して選んだ値）
  return frac(0.5 + index * float2(0.75487766624669276, 0.56984029099805327));   // R2 列
}

// 区間 [-1, 1] の入力の acos の高速な近似（Lagarde）。XeGTAO と同じ。
float FastACos(float x) {
  float a = abs(x);
  float res = (-0.156583 * a + kHalfPi) * sqrt(max(1.0 - a, 0.0));
  return (x >= 0) ? res : kPi - res;
}

[numthreads(8, 8, 1)]
```

### 準備：中心、半径、ノイズ {#main-setup}

中心の画素の深度はごくわずか（0.99920 倍）カメラ側に寄せます。深度バッファの量子化誤差で自分自身を遮蔽物と見なしてしまうのを避けるためです。32 bit の深度なら 0.99999 倍です。

画面上の半径は `effect_radius / (1 画素がビュー空間でどれだけか)` です。1 画素のビュー空間の大きさは深度に比例します。C++ で 1080p・縦の画角 60 度の場合を数えると、深度 1 m で 681 px、5 m で 136 px、30 m で 23 px です。遠いほど画面上の半径は小さくなります。10 px 未満になると AO を弱めて 1 に寄せます（`(10 − 半径) / 100` の小さな値を足す）。ちらつきを避けるためです。

中心の画素を読んでも情報はないので、サンプルは 1.3 画素ぶん離れた所から始めます。

### スライスの向きと射影した法線 {#main-slice}

```hlsl
void MainPassCS(uint2 pix : SV_DispatchThreadID) {
  if (any(pix >= (uint2)g_size)) return;
  float2 uv = (pix + 0.5) * g_pixel_size;                 // 画素の中心

  // 1. 中心と、上下左右の深度。Gather で 2 回読めば足りる。
  float4 ul = g_work_depth.GatherRed(g_point_clamp, pix * g_pixel_size);
  float4 br = g_work_depth.GatherRed(g_point_clamp, pix * g_pixel_size, int2(1, 1));
  float view_z = ul.y;                                    // 中心
  float4 edges = CalculateEdges(view_z, ul.x, br.z, ul.z, br.x);   // 左・右・上・下
  g_edges_out[pix] = PackEdges(edges);                    // デノイズで使うので、ここで書いておく

  // 2. 中心を少しカメラ側に寄せる。深度バッファの量子化誤差で、自分自身を遮蔽物と見なすのを避ける。
  view_z *= 0.99920;                                      // 半精度の深度向け（32 bit なら 0.99999）
  float3 center = ViewSpacePosition(uv, view_z);
  float3 view_vec = normalize(-center);                   // 画素からカメラへ向かう単位ベクトル
  float3 normal = g_normals.Load(int3(pix, 0)).xyz;       // ビュー空間の法線

  // 3. 半径まわりの定数。
  float effect_radius = g_radius * g_radius_multiplier;
  float falloff_range = g_falloff_range * effect_radius;
  float falloff_from = effect_radius * (1.0 - g_falloff_range);
  float falloff_mul = -1.0 / falloff_range;               // 半径の端に向けて重みを 1 → 0 にする直線の傾き
  float falloff_add = falloff_from / falloff_range + 1.0;

  // 4. 画面上の半径 [px]。1 画素がビュー空間でどれだけか（view_z に比例）で割る。
  float2 pixel_size_at_z = view_z * g_ndc_mul_pixel;
  float screen_radius = effect_radius / pixel_size_at_z.x;

  float visibility = 0;
  // 画面上の半径が小さい（遠い）ところは、AO を弱く 1 に寄せて、ちらつきを避ける。
  visibility += saturate((10.0 - screen_radius) / 100.0) * 0.5;

  // 中心の画素そのものを読んでも情報がないので、最小の距離から始める。
  const float too_close = 1.3;                            // 1 画素ちょっとより近いサンプルは押し出す
  float min_s = too_close / screen_radius;

  float2 noise = SpatioTemporalNoise(pix);                // x = スライスの回転、y = ステップの位置

  [loop] for (int slice = 0; slice < g_slice_count; ++slice) {
    // 論文 5, 6 行: スライスの向き φ（0〜π を等分して、ノイズで回す）。
    float phi = (slice + noise.x) / g_slice_count * kPi;
    float cos_phi, sin_phi;
    sincos(phi, sin_phi, cos_phi);
    float2 omega = float2(cos_phi, -sin_phi) * screen_radius;   // 画面上の方向（y は下が正なので反転）。長さ = 画面上の半径

    // 論文 8〜11 行: スライスの面と、その面に射影した法線。
    float3 direction_vec = float3(cos_phi, sin_phi, 0);                       // スライスの向き
    float3 ortho_direction = direction_vec - dot(direction_vec, view_vec) * view_vec;   // 視線に直交させる
    float3 axis = normalize(cross(ortho_direction, view_vec));                // スライスの面の法線
    float3 projected_normal = normal - axis * dot(normal, axis);              // 法線を面に射影
```

スライスの向き φ は `(slice + noise.x) / スライス数 × π` です。0〜π を等分し画素ごとのノイズで回します。両側（±）を探すので 0〜π で全周を覆います。

論文の 8〜11 行はスライスの面を決めます。スライスの向き（画面上の方向）を視線に直交させ視線との外積で面の法線を作り、法線をその面に射影します。13〜15 行で射影した法線が視線から傾く角 `n`（符号つき）を求めます。符号はスライスの向きと同じ側へ傾くなら正です。

### 地平線を探す {#main-horizon}

```hlsl
    // 論文 13〜15 行: 射影した法線が、視線から傾く角 n（符号つき）。
    float sign_norm = sign(dot(ortho_direction, projected_normal));
    float projected_len = length(projected_normal);
    float cos_norm = saturate(dot(projected_normal, view_vec) / projected_len);
    float n = sign_norm * FastACos(cos_norm);

    // 地平線の下限: 法線の半球の外（n ± π/2）。-1 の代わりにこれを使う。
    float low_cos0 = cos(n + kHalfPi);
    float low_cos1 = cos(n - kHalfPi);
    float horizon_cos0 = low_cos0;                        // +方向の地平線の cos（大きいほど高い）
    float horizon_cos1 = low_cos1;                        // -方向

    [loop] for (int step = 0; step < g_steps_per_slice; ++step) {
      // 論文 20 行: ステップの位置。R1 列でスライスとステップごとにずらす。
      float step_noise = frac(noise.y + (slice + step * g_steps_per_slice) * 0.6180339887498948);
      float s = (step + step_noise) / g_steps_per_slice;  // 0〜1
      s = pow(max(s, 0.0), g_sample_power);                         // 手前に寄せる（2.0 なら二乗）
      s += min_s;                                         // 中心を避ける

      float2 sample_offset = s * omega;                   // 画面上のずらし量 [px]
      float offset_len = length(sample_offset);

      // 遠いサンプルほど粗いミップを読む。log2(距離) - 3.3 がミップ番号。
      float mip = clamp(log2(offset_len) - g_mip_offset, 0, 4);
      sample_offset = round(sample_offset) * g_pixel_size; // 画素の中心にそろえる（斜めの傾きが狂わないように）

      float2 uv0 = uv + sample_offset;
      float2 uv1 = uv - sample_offset;
      float3 pos0 = ViewSpacePosition(uv0, g_work_depth.SampleLevel(g_point_clamp, uv0, mip));
      float3 pos1 = ViewSpacePosition(uv1, g_work_depth.SampleLevel(g_point_clamp, uv1, mip));

      float3 delta0 = pos0 - center;
      float3 delta1 = pos1 - center;
      float dist0 = length(delta0);
      float dist1 = length(delta1);
      float3 horizon_vec0 = delta0 / dist0;               // 論文 23, 24 行
      float3 horizon_vec1 = delta1 / dist1;

      // 半径の外のサンプルは捨てる。端はなめらかに（重み 1 → 0）。
      float weight0 = saturate(dist0 * falloff_mul + falloff_add);
      float weight1 = saturate(dist1 * falloff_mul + falloff_add);

      float shc0 = dot(horizon_vec0, view_vec);           // サンプルの地平線の cos
      float shc1 = dot(horizon_vec1, view_vec);
      shc0 = lerp(low_cos0, shc0, weight0);               // 重みが 0 なら、下限に落とす（影響なし）
      shc1 = lerp(low_cos1, shc1, weight1);

      horizon_cos0 = max(horizon_cos0, shc0);             // 最も高い地平線を残す
      horizon_cos1 = max(horizon_cos1, shc1);
    }

    // 夜の暗がり対策: 高い傾きで少し暗すぎるので、射影した法線の長さを 5 % だけ 1 に寄せる（XeGTAO の補正）。
    projected_len = lerp(projected_len, 1.0, 0.05);

    // 論文 27 行: 地平線の角度と、内側の積分を解析的に求める（式 7）。
    float h0 = -FastACos(horizon_cos1);                   // -方向は角度が負
    float h1 = FastACos(horizon_cos0);
    float iarc0 = (cos_norm + 2.0 * h0 * sin(n) - cos(2.0 * h0 - n)) / 4.0;
    float iarc1 = (cos_norm + 2.0 * h1 * sin(n) - cos(2.0 * h1 - n)) / 4.0;
    visibility += projected_len * (iarc0 + iarc1);        // スライスの可視性（式 8: 射影した法線の長さを掛ける）
  }

  visibility /= g_slice_count;                            // スライスの平均
  visibility = pow(max(visibility, 0.0), g_final_power);  // コントラストの調整
  visibility = max(0.03, visibility);                     // 完全な遮蔽にはしない（画素は見えているので）
  g_ao_out[pix] = saturate(visibility / kOcclusionScale); // 1.5 で割って UNORM に収める
}
```

地平線の初期値は法線の半球の外 `cos(n ± π/2)` です。論文は −1 としていますが、XeGTAO は法線の半球の下に潜る値（意味が法線によって変わる）を避けるため、この値にしています。

ステップごとに R1 列（黄金比 0.618…）でノイズをずらし、`s = (step + noise) / ステップ数` を二乗して手前に寄せます。サンプルの画面上のずらし量は `s × omega`（`omega` はスライスの向き × 画面上の半径）です。この長さから読むミップを決めます。`mip = clamp(log2(長さ) − 3.3, 0, 4)` です。C++ で数えると深度 1 m と 2 m では最も遠いサンプルがミップ 4 の端に、5 m で 3.8、10 m で 2.8、30 m で 1.2 になります。ミップを粗くするほど速くなる反面、薄い物体が見落とされ時間的な安定も落ちると、ツールチップが書いています。

ずらし量は画素の中心に丸めます（`round`）。丸めないとサンプルの位置が深度テクセルの中心とずれて、斜めの傾きが狂うためです。サンプルが半径の外なら重みが 0 になり下限の地平線に落とします。端は 1 → 0 へなめらかに変えます。

そのあとで最も高い地平線の cos を残します。薄い物体への補正（thickness heuristic）は、論文の式 9 では地平線が下がるときに指数移動平均で混ぜる形です。XeGTAO はその補正を使わない版（上の単純な `max`）を既定にしています。

### 積分して平均する {#main-integrate}

論文の 27 行です。地平線の角度は `h0 = −acos(horizonCos1)`、`h1 = acos(horizonCos0)` です。内側の積分は解析的に閉じていて、式 7 です。

```text
iarc(h) = (cos γ + 2 h sin n − cos(2h − n)) / 4
スライスの可視性 = ‖射影した法線‖ × (iarc(h0) + iarc(h1))
```

C++ でこの式を確かめました。視線の軸のまわりに半角 h で一定の地平線（円錐の内側だけ開けている）を置き、法線を 0 / 30 / 60 度に傾けます。式の平均とコサイン重み付き半球のモンテカルロ（50 万本）を比べると、9 通りすべてで差が 0.001 以内に収まりました。論文の「高さ場の仮定のもとで、ground truth を解析的に解く」という主張が、数値で確かめられたことになります。

最後に、全スライスの平均を取り `FinalValuePower`（2.2）でべき乗し、0.03 を下限にします（完全な遮蔽にはしない。画素は実際に見えているため）。UNORM に詰めるために 1.5 で割ります。生の値は 1 を超えうるが平均すると 1 に収まるためです。

## パス 4：デノイズ {#denoise}

```hlsl
// ================= ④ デノイズ =================

Texture2D<float> g_ao_in : register(t4);                  // ③ の出力（÷1.5 済み）
Texture2D<float> g_edges_in : register(t5);               // ③ の出力
RWTexture2D<float> g_ao_final : register(u8);

[numthreads(8, 8, 1)]
void DenoiseCS(uint2 pix : SV_DispatchThreadID) {
  if (any(pix >= (uint2)g_size)) return;

  // 自分と上下左右の画素の、エッジ（4 方向）。
  float4 e_c = UnpackEdges(g_edges_in.Load(int3(pix, 0)));
  float4 e_l = UnpackEdges(g_edges_in.Load(int3(max((int2)pix - int2(1, 0), 0), 0)));
  float4 e_r = UnpackEdges(g_edges_in.Load(int3(min((int2)pix + int2(1, 0), g_size - 1), 0)));
  float4 e_t = UnpackEdges(g_edges_in.Load(int3(max((int2)pix - int2(0, 1), 0), 0)));
  float4 e_b = UnpackEdges(g_edges_in.Load(int3(min((int2)pix + int2(0, 1), g_size - 1), 0)));

  // エッジは左右で完全には対称にならない。隣の画素の反対側のエッジを掛けて、対称にそろえる（少しシャープになる）。
  e_c *= float4(e_l.y, e_r.x, e_t.w, e_b.z);

  // エッジが 3〜4 本あるとき、ごくわずかな漏れを許す（空間とフレーム間のエイリアスを減らす）。
  float leak_threshold = 2.5, leak_strength = 0.5;
  float edginess = saturate(4.0 - leak_threshold - dot(e_c, 1.0)) / (4.0 - leak_threshold) * leak_strength;
  e_c = saturate(e_c + edginess);

  // 近傍の AO。
  float ao_c = g_ao_in.Load(int3(pix, 0));
  float ao_l = g_ao_in.Load(int3(max((int2)pix - int2(1, 0), 0), 0));
  float ao_r = g_ao_in.Load(int3(min((int2)pix + int2(1, 0), g_size - 1), 0));
  float ao_t = g_ao_in.Load(int3(max((int2)pix - int2(0, 1), 0), 0));
  float ao_b = g_ao_in.Load(int3(min((int2)pix + int2(0, 1), g_size - 1), 0));

  // 重み付き平均: 中心（g_denoise_beta）+ 4 近傍（エッジの度合いが重み）。斜めは使わない簡略版。
  float sum_w = g_denoise_beta;
  float sum = ao_c * sum_w;
  sum += ao_l * e_c.x; sum_w += e_c.x;
  sum += ao_r * e_c.y; sum_w += e_c.y;
  sum += ao_t * e_c.z; sum_w += e_c.z;
  sum += ao_b * e_c.w; sum_w += e_c.w;

  g_ao_final[pix] = sum / sum_w * kOcclusionScale;        // 最後に 1.5 を戻す
}
```

メインのパスが書いたエッジ（4 方向 × 2 ビット）を使います。重みは自分と隣の画素の両方のエッジです。エッジの検出は左右で完全には対称ではないので、隣の画素の反対側のエッジを掛けて、対称にそろえます。少しシャープになり TAA とよく合うとコードのコメントが書いています。

エッジが 3〜4 本ある（孤立した画素）ときは、わずかな漏れを許します。空間と時間のエイリアスを減らすためです。XeGTAO は斜めの 4 近傍も使いますが、上のコードは上下左右の 4 近傍だけの簡略版です。TAA があれば 1 回で足りないときは 2〜3 回かけます。

## ノイズ：Hilbert 曲線と R2 列 {#noise}

メインのパスは 1 画素あたりのスライスとステップが少ない（Low で 1 スライス）ので、隣の画素どうしで違う値を使い画面全体で平均して正しい答えに近づけます。ところが、乱数だとノイズの粒が大きなかたまりになります。

XeGTAO は画素の位置を 64 × 64 の Hilbert 曲線の添字に写し、その添字を R2 列（2 次元の準乱数）に通します。Hilbert 曲線は 2D で近い画素が、添字でも近くなる曲線です。R2 列は添字が近いと値が離れるので、結果として隣の画素どうしのノイズが、2D で離れます。フレームごとに添字を 288 ずつずらします（288 は、XeGTAO の作者が試して選んだ値）。64 フレームで一巡します。

C++ で数えると隣り合う画素のノイズの距離は、平均 0.589、最小 0.035 でした（0〜1 の正方形の乱数なら平均 0.52）。同じ画素の 64 フレームのノイズは、最小距離が 0.086 で 64 点を一様な格子に置いたときの間隔 0.125 に近い値です。

## 品質プリセットとコスト {#quality}

<svg class="fig flow" viewBox="0 0 620 184" role="img" aria-label="品質プリセットのサンプル数"><defs><marker id="xe-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#94a3b8"/></marker></defs><text x="10" y="18" text-anchor="start" font-size="12" fill="currentColor">品質プリセットと 1 画素の深度の読み込み回数(スライス x ステップ x 2)</text><text x="102" y="52" text-anchor="end" font-size="11" fill="currentColor">Low (1 x 2)</text><rect x="110" y="34" width="28.1" height="24" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="144.14814814814815" y="51" text-anchor="start" font-size="11" fill="currentColor">4 回</text><text x="102" y="88" text-anchor="end" font-size="11" fill="currentColor">Medium (2 x 2)</text><rect x="110" y="70" width="56.3" height="24" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="172.2962962962963" y="87" text-anchor="start" font-size="11" fill="currentColor">8 回</text><text x="102" y="124" text-anchor="end" font-size="11" fill="currentColor">High (3 x 3)</text><rect x="110" y="106" width="126.7" height="24" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="242.66666666666666" y="123" text-anchor="start" font-size="11" fill="currentColor">18 回</text><text x="102" y="160" text-anchor="end" font-size="11" fill="currentColor">Ultra (9 x 3)</text><rect x="110" y="142" width="380.0" height="24" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="496.0" y="159" text-anchor="start" font-size="11" fill="currentColor">54 回</text></svg>

1 画素の深度の読み込み回数はスライス数 × ステップ数 × 2（両側）です。Low が 4 回、Medium が 8 回、High が 18 回、Ultra が 54 回です。

論文（GTAO）は半分の解像度で 1 方向/画素の空間 4 × 4 のバイラテラル再構成と、6 通りの回転の時間蓄積を組み合わせて、画素あたり 4 × 4 × 6 ＝ 96 方向の有効なサンプルを得ています。1080p の PS4 で 0.5 ms でした。XeGTAO の Low でもデノイズと TAA で数フレーム蓄積すれば、ずっと高い品質に収束します。

メモリは 1080p で深度ミップ 5 段（R16F）が 5.27 MiB（ミップ 0 の 1.33 倍）、AO とエッジと最終の R8 が 3 枚で 5.93 MiB、法線（R11G11B10）が 7.91 MiB です。

## 数字を出す C++ {#cpp}

式の検証、プリセット、画面上の半径とミップ、ノイズ、メモリを 1 本の C++ で出します。

MSVC（`/std:c++latest /W4`）でコンパイルして実行しました。HLSL は `fxc`（cs_5_0）でコンパイルして確かめました。実行して絵は確かめていません。

```cpp
// XeGTAO の式と設定を、数字で確かめる。
//  1. スライスの積分式（iarc）が、モンテカルロの正解と合うか（視線の軸のまわりに一定の地平線）
//  2. 品質プリセットの 1 画素あたりのサンプル数と、深度ミップの選ばれ方
//  3. Hilbert 曲線 + R2 列のノイズが、画素ごとに偏りなく散らばるか
//  4. メモリ（深度ミップ・作業用テクスチャ）
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <initializer_list>
#include <random>
#include <vector>

namespace {
constexpr double kPi = 3.14159265358979323846;

struct V3 { double x, y, z; };
V3 operator+(V3 a, V3 b) { return {a.x + b.x, a.y + b.y, a.z + b.z}; }
V3 operator-(V3 a, V3 b) { return {a.x - b.x, a.y - b.y, a.z - b.z}; }
V3 operator*(V3 a, double s) { return {a.x * s, a.y * s, a.z * s}; }
double Dot(V3 a, V3 b) { return a.x * b.x + a.y * b.y + a.z * b.z; }
V3 Cross(V3 a, V3 b) { return {a.y * b.z - a.z * b.y, a.z * b.x - a.x * b.z, a.x * b.y - a.y * b.x}; }
double Len(V3 a) { return std::sqrt(Dot(a, a)); }
V3 Norm(V3 a) { return a * (1.0 / Len(a)); }

// XeGTAO の 1 スライスの可視性（XeGTAO_MainPass の 536〜544 行を、そのまま書き直したもの）。
// view = 視線ベクトル（画素からカメラへ）、normal = 法線、dir = スライスの向き（view に直交）、
// horizon_cos0 / 1 = 両側の地平線の cos（視線ベクトルとのなす角）。
double SliceVisibility(V3 view, V3 normal, V3 dir, double horizon_cos0, double horizon_cos1) {
  const V3 axis = Norm(Cross(dir, view));                        // スライスの面の法線
  const V3 projected = normal - axis * Dot(normal, axis);        // 法線をスライスの面へ射影
  const double projected_len = Len(projected);
  const double sign_norm = Dot(dir, projected) >= 0 ? 1.0 : -1.0;
  const double cos_norm = std::clamp(Dot(projected, view) / projected_len, 0.0, 1.0);
  const double n = sign_norm * std::acos(cos_norm);              // 射影した法線が視線から傾く角

  // 地平線は、法線の半球（n ± π/2）の内側に収める。外側の値は、下限に切る。
  const double low0 = std::cos(n + kPi / 2), low1 = std::cos(n - kPi / 2);
  const double c0 = std::max(horizon_cos0, low0), c1 = std::max(horizon_cos1, low1);
  const double h0 = -std::acos(c1), h1 = std::acos(c0);          // コードの 536, 537 行
  auto iarc = [&](double h) { return (cos_norm + 2.0 * h * std::sin(n) - std::cos(2.0 * h - n)) / 4.0; };
  return projected_len * (iarc(h0) + iarc(h1));
}

// 正解: 視線の軸のまわりの円錐（半角 half_angle）の内側だけが開けている。
// 法線のまわりのコサイン重み付き半球で、開けている方向の割合をモンテカルロで求める。
double GroundTruthCone(V3 view, V3 normal, double half_angle, int samples, std::mt19937_64& rng) {
  std::uniform_real_distribution<double> u(0.0, 1.0);
  // 法線を z とする座標系。
  const V3 up = std::fabs(normal.z) < 0.99 ? V3{0, 0, 1} : V3{1, 0, 0};
  const V3 t = Norm(Cross(up, normal)), b = Cross(normal, t);
  int open = 0;
  for (int i = 0; i < samples; ++i) {
    const double r = std::sqrt(u(rng)), phi = 2 * kPi * u(rng);   // コサイン重み付き半球
    const V3 d = t * (r * std::cos(phi)) + b * (r * std::sin(phi)) + normal * std::sqrt(1 - r * r);
    if (std::acos(std::clamp(Dot(d, view), -1.0, 1.0)) <= half_angle) ++open;
  }
  return static_cast<double>(open) / samples;
}

// XeGTAO の Hilbert 曲線の添字（XeGTAO.h の HilbertIndex）。
uint32_t HilbertIndex(uint32_t px, uint32_t py) {
  uint32_t index = 0;
  for (uint32_t level = 32; level > 0; level /= 2) {            // 幅 64 = レベル 6
    const uint32_t rx = (px & level) > 0, ry = (py & level) > 0;
    index += level * level * ((3 * rx) ^ ry);
    if (ry == 0) {
      if (rx == 1) { px = 63 - px; py = 63 - py; }
      std::swap(px, py);
    }
  }
  return index;
}
}  // namespace

int main() {
  std::mt19937_64 rng(42);

  std::printf("== スライスの積分式と正解（視線の軸のまわりに一定の地平線）==\n");
  std::printf("法線の傾き gamma  半角 h   式(平均)   正解(MC 50 万)   差\n");
  for (double gamma_deg : {0.0, 30.0, 60.0}) {
    for (double h_deg : {30.0, 60.0, 80.0}) {
      const double gamma = gamma_deg * kPi / 180, h = h_deg * kPi / 180;
      const V3 view = {0, 0, 1}, normal = {std::sin(gamma), 0, std::cos(gamma)};
      double sum = 0;
      const int kSlices = 360;
      for (int i = 0; i < kSlices; ++i) {
        const double phi = (i + 0.5) / kSlices * kPi;           // スライスは 0〜π（両側で全周を覆う）
        sum += SliceVisibility(view, normal, {std::cos(phi), std::sin(phi), 0}, std::cos(h), std::cos(h));
      }
      const double formula = sum / kSlices;
      const double truth = GroundTruthCone(view, normal, h, 500000, rng);
      std::printf("%8.0f 度     %5.0f 度  %8.4f   %8.4f        %+.4f\n", gamma_deg, h_deg, formula, truth,
                  formula - truth);
    }
  }

  std::printf("\n== 品質プリセット（XeGTAO の vaGTAO.hlsl の値）==\n");
  std::printf("設定     スライス  ステップ/スライス  1 画素のサンプル数(両側)  深度の読み込み回数\n");
  const struct { const char* name; int slices, steps; } presets[] = {{"Low", 1, 2}, {"Medium", 2, 2}, {"High", 3, 3}, {"Ultra", 9, 3}};
  for (const auto& p : presets) {
    std::printf("%-7s  %4d      %4d             %6d                  %6d\n", p.name, p.slices, p.steps,
                p.slices * p.steps * 2, p.slices * p.steps * 2);
  }

  std::printf("\n== 画面上の半径と、深度ミップの選ばれ方（1080p、縦の画角 60 度）==\n");
  const double tan_half = std::tan(30.0 * kPi / 180.0);
  const double px_size_per_m = 2.0 * tan_half / 1080.0;         // 深度 1 m で 1 画素が覆う長さ [m]
  std::printf("既定 Radius 0.5 x RadiusMultiplier 1.457 = %.3f m\n", 0.5 * 1.457);
  std::printf("深度[m]  画面上の半径[px]  最も遠いサンプルのミップ(offset 3.3)\n");
  for (double z : {1.0, 2.0, 5.0, 10.0, 30.0}) {
    const double screen_radius = 0.5 * 1.457 / (z * px_size_per_m);
    const double mip = std::clamp(std::log2(screen_radius) - 3.3, 0.0, 5.0);
    std::printf("%6.0f    %12.1f        %.2f\n", z, screen_radius, mip);
  }

  std::printf("\n== Hilbert 曲線 + R2 列のノイズ ==\n");
  // 隣の画素のノイズが、2D でどれだけ離れているか（小さすぎると縞になる）。
  double min_d = 1e9, sum_d = 0;
  int count = 0;
  auto noise = [](uint32_t x, uint32_t y, uint32_t frame) {
    const uint32_t index = HilbertIndex(x % 64, y % 64) + 288 * (frame % 64);
    const double a = std::fmod(0.5 + index * 0.75487766624669276, 1.0);
    const double b = std::fmod(0.5 + index * 0.56984029099805327, 1.0);
    return std::pair<double, double>(a, b);
  };
  for (uint32_t y = 0; y < 63; ++y) {
    for (uint32_t x = 0; x < 63; ++x) {
      const auto p = noise(x, y, 0), r = noise(x + 1, y, 0), d = noise(x, y + 1, 0);
      for (const auto& q : {r, d}) {
        const double dist = std::hypot(p.first - q.first, p.second - q.second);
        min_d = std::min(min_d, dist);
        sum_d += dist;
        ++count;
      }
    }
  }
  std::printf("隣り合う画素のノイズの距離（0〜1 の正方形）: 平均 %.3f、最小 %.4f（乱数なら平均 0.52）\n", sum_d / count, min_d);
  // 同じ画素の 64 フレームの並びが、どれだけ一様か（64 点の最小距離）。
  double min_t = 1e9;
  for (uint32_t i = 0; i < 64; ++i) {
    for (uint32_t j = i + 1; j < 64; ++j) {
      const auto p = noise(10, 10, i), q = noise(10, 10, j);
      min_t = std::min(min_t, std::hypot(p.first - q.first, p.second - q.second));
    }
  }
  std::printf("同じ画素の 64 フレームのノイズの最小距離: %.4f（64 点を一様に置いた格子の間隔は 0.125）\n", min_t);

  std::printf("\n== メモリ（1920x1080）==\n");
  const double pixels = 1920.0 * 1080;
  double mips = 0;
  for (int m = 0; m < 5; ++m) mips += pixels / std::pow(4.0, m);
  std::printf("深度ミップ 5 段（R16F）: %.2f MiB（ミップ 0 の %.2f 倍）\n", mips * 2 / 1048576, mips / pixels);
  std::printf("AO の作業用 R8 (または法線つきなら R8G8B8A8) + エッジ R8 + 最終 R8: %.2f MiB（R8 を 3 枚）\n",
              3 * pixels / 1048576);
  std::printf("法線（R11G11B10）: %.2f MiB\n", pixels * 4 / 1048576);
  return 0;
}
```

```text title="実行結果"
== スライスの積分式と正解（視線の軸のまわりに一定の地平線）==
法線の傾き gamma  半角 h   式(平均)   正解(MC 50 万)   差
       0 度        30 度    0.2500     0.2492        +0.0008
       0 度        60 度    0.7500     0.7494        +0.0006
       0 度        80 度    0.9698     0.9695        +0.0003
      30 度        30 度    0.2165     0.2165        -0.0000
      30 度        60 度    0.6495     0.6502        -0.0007
      30 度        80 度    0.8641     0.8639        +0.0003
      60 度        30 度    0.1250     0.1252        -0.0002
      60 度        60 度    0.4196     0.4187        +0.0010
      60 度        80 度    0.6470     0.6477        -0.0007
```

```text title="実行結果（続き）"
== 品質プリセット（XeGTAO の vaGTAO.hlsl の値）==
設定     スライス  ステップ/スライス  1 画素のサンプル数(両側)  深度の読み込み回数
Low         1         2                  4                       4
Medium      2         2                  8                       8
High        3         3                 18                      18
Ultra       9         3                 54                      54
```

```text title="実行結果（続き）"
== 画面上の半径と、深度ミップの選ばれ方（1080p、縦の画角 60 度）==
既定 Radius 0.5 x RadiusMultiplier 1.457 = 0.729 m
深度[m]  画面上の半径[px]  最も遠いサンプルのミップ(offset 3.3)
     1           681.4        5.00
     2           340.7        5.00
     5           136.3        3.79
    10            68.1        2.79
    30            22.7        1.21
```

```text title="実行結果（続き）"
== Hilbert 曲線 + R2 列のノイズ ==
隣り合う画素のノイズの距離（0〜1 の正方形）: 平均 0.589、最小 0.0346（乱数なら平均 0.52）
同じ画素の 64 フレームのノイズの最小距離: 0.0863（64 点を一様に置いた格子の間隔は 0.125）
```

```text title="実行結果（続き）"
== メモリ（1920x1080）==
深度ミップ 5 段（R16F）: 5.27 MiB（ミップ 0 の 1.33 倍）
AO の作業用 R8 (または法線つきなら R8G8B8A8) + エッジ R8 + 最終 R8: 5.93 MiB（R8 を 3 枚）
法線（R11G11B10）: 7.91 MiB
```

## 組み込み方 {#integrate}

1. 公式のリポジトリ（GameTechDev/XeGTAO）の `XeGTAO.h` と `XeGTAO.hlsli` を取り込むか、このページのコードを元に自分で書く。
2. 深度のプリフィルタ、（法線）、メイン、デノイズのコンピュート シェーダーをコンパイルする。
3. 毎フレーム、順にディスパッチする。入力は深度（と法線）、出力は AO のテクスチャ。
4. ライティングで AO を間接光（アンビエント）に掛ける。直接光には掛けない。

論文は AO だけでなく近傍の間接光（`G(A, ρ)`、3 次多項式）と鏡面の遮蔽（GTSO）も扱います。ここでは触れません。

## よくあるミス {#mistakes}

??? failure "AO が物体の縁で光るまたは暗くなる（ハロ）"
    半径が大きいと手前の物体の縁で背景の深度を拾う。`FalloffRange` を上げるか半径を絞る。深度ミップの重み付き平均が壊れていないかも確かめる。

??? failure "フレームごとにちらつく"
    ノイズの種がフレームで変わるのに、時間蓄積がない。TAA と連携するか AO 専用の蓄積を入れる。TAA がないなら `noise_index` を 0 に固定する。

??? failure "平らな床が縞状に暗くなる"
    中心の画素のずらし（0.99920 倍）を入れていない、または深度の精度が足りない。16 bit の深度なら 0.99920、32 bit なら 0.99999 にする。

??? failure "AO が全体に暗すぎる／弱すぎる"
    半径がシーンの縮尺に合っていない。1 が 1 cm のシーンで 0.5 を使うとほぼ効かない。`Radius` を縮尺に合わせて決める。

??? failure "AO を直接光にも掛けた"
    AO は間接光の遮蔽。直接光は影で扱う。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 深度プリフィルタ、（法線）、メイン、デノイズの 4 つのコンピュート シェーダー。
    - [x] 品質はスライス数 × ステップ数。Low が 1 × 2、Ultra が 9 × 3。
    - [x] 遠いサンプルは粗いミップを読む。番号は `log2(画面上の距離) − 3.3`。
    - [x] ノイズは Hilbert 曲線 + R2 列。TAA で収束させる。
    - [x] AO は間接光にだけ掛ける。

## 参考

- Intel, XeGTAO (v1.30), <https://github.com/GameTechDev/XeGTAO>, MIT License.（`XeGTAO.h`、`XeGTAO.hlsli`、`vaGTAO.hlsl` を全部読んだ）
- Jorge Jimenez, Xian-Chun Wu, Angelo Pesce, Adrian Jarabo, "Practical Realtime Strategies for Accurate Indirect Occlusion", Activision Technical Memo ATVI-TR-16-01, 2016.（第 1〜7 節を読んだ。付録と結論は読んでいない）

## 関連ページ

- [GTAO](gtao.md)
- [AO Comparison](comparison.md)
- [Temporal AO](filtering/temporal.md)
- [HBAO+](hbao-plus.md)
