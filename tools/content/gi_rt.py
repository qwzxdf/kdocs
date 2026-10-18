import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import pg  # noqa: E402

SCHIED = '''Schied, Kaplanyan, Wyman, Patney, Chaitanya, Burgess, Liu, Dachsbacher, Lefohn, Salvi, "Spatiotemporal Variance-Guided Filtering: Real-Time Reconstruction for Path-Traced Global Illumination", High-Performance Graphics 2017（SVGF）'''
SCHIED18 = '''Schied, Peters, Dachsbacher, "Gradient Estimation for Real-Time Adaptive Temporal Filtering", High-Performance Graphics 2018（A-SVGF）'''
BITTERLI = '''Bitterli, Wyman, Pharr, Shirley, Lefohn, Jarosz, "Spatiotemporal Reservoir Resampling for Real-Time Ray Tracing with Dynamic Direct Lighting", ACM Transactions on Graphics (SIGGRAPH 2020)（ReSTIR）'''
OUYANG = '''Ouyang, Liu, Kettunen, Pharr, Pantaleoni, "ReSTIR GI: Path Resampling for Real-Time Path Tracing", Computer Graphics Forum (High-Performance Graphics 2021)'''
WYMAN23 = '''Wyman, Kettunen, Lin, Bitterli, Pantaleoni, Ouyang, Pharr, "A Gentle Introduction to ReSTIR: Path Reuse in Real-Time", SIGGRAPH 2023 Courses'''
LUMEN = '''Wright, Narkowicz, Kelly, "Lumen: Real-time Global Illumination in Unreal Engine 5", SIGGRAPH 2022, Advances in Real-Time Rendering in Games'''
SANNIKOV = '''Sannikov, "Radiance Cascades: A Novel Approach to Calculating Global Illumination", 2023（Radiance Cascades の、論文と、解説）'''
MAJERCIK = '''Majercik, Guertin, Nowrouzezahrai, McGuire, "Dynamic Diffuse Global Illumination with Ray-Traced Irradiance Fields", Journal of Computer Graphics Techniques, Vol. 8, No. 2, 2019（DDGI）'''
MAJERCIK21 = '''Majercik, Müller, Keller, Cline, McGuire, "Dynamic Diffuse Global Illumination Resampling", SIGGRAPH 2021 Talks'''
CRASSIN = '''Crassin, Neyret, Sainz, Green, Eisemann, "Interactive Indirect Illumination Using Voxel Cone Tracing", Computer Graphics Forum (Pacific Graphics 2011)'''
KAPLANYAN = '''Kaplanyan, Dachsbacher, "Cascaded Light Propagation Volumes for Real-Time Indirect Illumination", Symposium on Interactive 3D Graphics and Games 2010'''
RITSCHEL = '''Ritschel, Grosch, Seidel, "Approximating Dynamic Global Illumination in Image Space", Symposium on Interactive 3D Graphics and Games 2009（スクリーン スペースの、間接光）'''
STACHOWIAK = '''Stachowiak, "Stochastic All The Things: Raytracing in Hybrid Real-Time Rendering", Digital Dragons 2018（SEED のハイブリッド レイトレーシング）'''
DXR = '''Microsoft, "DirectX Raytracing (DXR) Functional Spec"'''
KARIS = '''Karis, "High Quality Temporal Supersampling", SIGGRAPH 2014, Advances in Real-Time Rendering in Games'''
RTR = '''Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（大域照明の章）'''
PBRT = '''Pharr, Jakob, Humphreys, "Physically Based Rendering: From Theory to Implementation", 4th Edition, MIT Press, 2023'''

# ================================================================ SSGI
pg.Dedup("gi/ssgi.md")
pg.Add("gi/ssgi.md", '''
## 画面の情報だけで、間接光を、求める

**SSGI**（Screen-Space Global Illumination）は、**画面に映っている、情報**（**色、深度、法線**）だけを、使って、**間接光**を、**近似**する方法です（Ritschel ら、2009）。**シーンの、形状を、持たず**、**G バッファと、深度バッファ**だけで、**ポスト プロセス**として、実行できるので、**導入が、簡単**です。

## 基本の考え方

**各画素**から、**半球の、ランダムな、方向**に、**画面空間で、レイを、飛ばし**（**レイマーチ**）、**当たった、画素の、色**を、**その方向から、来る光**として、**集めます**。

```text
画素 P から、法線の側の半球へ、ランダムな方向にレイを飛ばす（画面空間で、深度バッファを、辿る）
        ↓ 当たった画素 Q の「ライティング済みの色」を、P に届く光として、足す
```

**当たった画素 Q** は、**すでに、ライティングされた、画面の色**（直接光 + 前フレームの、間接光）です。**Q の色が、P を、照らす**ので、**1 回の、バウンス**の、間接光が、得られます。

## 画面空間の、レイマーチ

```hlsl
// 画素 P から、方向 dir へ、画面空間で、レイを進めて、最初に交わった画素の色を返す（交わらなければ、false）。
bool TraceScreenSpace(float3 origin_vs, float3 dir_vs, float2 pixel, out float3 hit_color) {
  const int kSteps = 16;
  float step_len = g_ssgi_max_distance / kSteps;
  float jitter = InterleavedGradientNoise(pixel);                      // 開始を、ずらして、縞を消す
  hit_color = 0;
  for (int i = 0; i < kSteps; ++i) {
    float3 p_vs = origin_vs + dir_vs * ((i + jitter) * step_len);      // ビュー空間での、レイ上の点
    float4 clip = mul(float4(p_vs, 1.0), g_proj);
    float2 uv = clip.xy / clip.w * float2(0.5, -0.5) + 0.5;
    if (any(uv < 0.0) || any(uv > 1.0)) return false;                  // 画面の外 → 情報がない
```

**ビュー空間で、レイを、進め**、各点を、**画面の、uv に、投影**します。**画面の外**に、出たら、**情報が、無い**ので、**打ち切ります**。

```hlsl
    float scene_depth = g_depth.SampleLevel(g_point_clamp, uv, 0);     // その画素の、深度（ビュー空間の、距離）
    float ray_depth = -p_vs.z;                                          // レイ上の点の、深度（右手系は、前方が -Z）
    float diff = ray_depth - scene_depth;
    if (diff > 0.0 && diff < g_thickness) {                             // レイが、面の「裏」に入った（交差した）。厚み以内なら、当たりとする。
      hit_color = g_lit_scene.SampleLevel(g_linear_clamp, uv, 0).rgb;   // 当たった画素の、ライティング済みの色
      return true;
    }
  }
  return false;
}
```

**レイ上の点の、深度**が、**その画素の、深度より、奥**（`diff > 0`）になった、瞬間が、**面との、交差**です。**厚み**（`g_thickness`）の、範囲内なら、**当たり**と、みなします（**薄い物の、裏を、通り抜ける**のを、避けるため。[Thickness](../reflections/ssr-basics/thickness.md)）。**当たった画素の、ライティング済みの色**（`g_lit_scene`）を、**間接光として、使います**。

## 間接光を、積算する

```hlsl
float3 SSGI(float2 pixel, float3 position_vs, float3 normal_vs, float3 albedo) {
  float3 sum = 0.0;
  const int kRays = 2;                                                  // 1 画素あたりの、レイ（少なく。デノイズで補う）
  for (int k = 0; k < kRays; ++k) {
    float2 u = Random2(pixel, g_frame_index * kRays + k);
    float3 dir = LocalToWorld(CosineHemisphere(u.x, u.y), normal_vs);   // 余弦重みづけ（[Monte Carlo Integration]）
    float3 hit_color;
    if (TraceScreenSpace(position_vs + normal_vs * 0.02, dir, pixel, hit_color)) {
      sum += hit_color;                                                  // 当たった → その色が、光
    } else {
      sum += g_sky_ambient;                                              // 当たらない → 空の環境光で、補う（画面の外は、不明）
    }
  }
  return albedo * sum / kRays;                                           // 余弦重みづけなので、albedo × 平均
}
```

**余弦重みづけの、サンプリング**（[Monte Carlo Integration](theory/monte-carlo.md)）で、**拡散の、間接光**は、**当たった色の、平均 × アルベド**に、なります。**当たらなかった**（画面の外、遠すぎる）場合は、**空の、環境光**など、**フォールバック**で、補います。

## 時間方向の、蓄積と、フィルタ

**1 画素あたり、1〜2 本の、レイ**では、**ノイズだらけ**です。**時間蓄積と、空間フィルタ**で、**なめらか**に、します（[Fighting Noise](rt-gi/noise.md)）。**前のフレームの、結果**と、**混ぜ**、**法線・深度が、近い、画素**どうしで、**ぼかします**。

## SSGI の、問題

| 問題 | 内容 | 対策 |
| --- | --- | --- |
| **画面の外の、光が、使えない** | **画面に、映っていない**光源・壁は、**間接光に、反映されない**。**カメラを、動かす**と、**明るさが、変わる**（画面の端で、光が、出入りする） | **フォールバック**（ライト プローブ、空の環境光）。**画面を、少し広く、描く** |
| **隠れた面が、使えない** | **手前の物の、裏**は、**見えていない**ので、**反射光が、出ない** | **深度の厚み**を、仮定。**限界として、許容** |
| **遠くの、光は、使えない** | **レイの、最大距離**を、短く（数 m）。**遠くからの、間接光**は、**無い** | **プローブ GI などと、併用** |
| **ノイズ** | 少ない、レイ | **時間蓄積 + 空間フィルタ** |
| **コスト** | **画面解像度に、比例** | **半分の解像度で、計算**して、アップサンプル |

## 長所と短所

| | 内容 |
| --- | --- |
| 長所 | **導入が、簡単**（ポスト プロセス）。**シーンの、形状・事前計算が、不要** |
| 長所 | **完全に、動的**（動く物、動くライトも、反映） |
| 長所 | **レイトレーシング ハードウェアが、不要** |
| 短所 | **画面の外の、情報が、無い**（カメラを、動かすと、**ちらつく**） |
| 短所 | **単独では、不十分**。**他の手法**（プローブ、ライトマップ）と、**併用**が、前提 |

## 使いどころ

| 場面 | 判断 |
| --- | --- |
| **補助**（**近距離の、間接光**、**色のにじみ**） | **向く**（プローブ GI の、**細かい部分を、補う**） |
| **GI の、主役** | **向かない**（画面の外の、情報が、無い） |
| **ハードウェア RT が、ない環境の、動的な GI** | **選択肢の、1 つ**（他の手法と、併用） |

''', before="## よくあるミス")
pg.Refs("gi/ssgi.md", [RITSCHEL, STACHOWIAK, SCHIED, "McGuire, Mara, \"Efficient GPU Screen-Space Ray Tracing\", Journal of Computer Graphics Techniques, Vol. 3, No. 4, 2014"])

# ================================================================ DDGI
pg.Dedup("gi/ddgi.md")
pg.Add("gi/ddgi.md", '''
## DDGI とは

**DDGI**（Dynamic Diffuse Global Illumination、Majercik ら、2019）は、**プローブ GI**（[Probe GI](probes/index.md)）の、**値を、毎フレーム、レイトレーシングで、更新**する方式です。**プローブを、空間に、置く**考え方は、**ライト プローブと、同じ**ですが、**ベイクではなく**、**実行時に、各プローブから、レイを、飛ばして**、**周りの光を、集め直します**。**動的な、ライト、動く物、扉の開閉**が、**すべて、反映**されます。

## 全体の流れ

```text
毎フレーム:
  ① 各プローブから、N 本（例 128 本）のレイを、飛ばす（レイトレーシング）
  ② レイが、当たった面の、色（ライティング済み）と、距離を、集める
  ③ 集めた値を、プローブの、放射照度マップ（8×8 の、八面体マップ）に、混ぜ込む（前の値と、ブレンド）
  ④ 物体の描画で、周りのプローブを、補間して、間接光を得る（[Interpolation Methods](probes/interpolation.md)）
```

## 八面体マップで、保存する

DDGI は、各プローブの、**放射照度**を、**SH ではなく**、**八面体マップ**（球面を、**1 枚の、正方形**に、展開した、小さなテクスチャ）に、**保存**します。**SH より、方向の、解像度が、高く**、**光の、変化**を、**より、細かく**、持てます。

| | SH L2 | 八面体マップ（8×8） |
| --- | --- | --- |
| 1 プローブの、データ | 9 係数 × RGB（27 個の数） | 64 画素 × RGB（192 個の数） |
| 方向の、表現 | **ごく、なめらか**（低周波） | **やや、細かい**（8×8 の、方向） |
| リンギング | **出る**（負の値） | **出ない** |
| 補間 | 係数を、足す | **テクスチャとして、ハードウェアの、補間**（双線形） |

### 八面体マッピング：球面 ↔ 正方形

**方向ベクトル**（単位ベクトル）を、**2D の、座標**（0〜1）に、変換します。

```hlsl
// 単位ベクトル（方向）→ 八面体マップの uv（0〜1）。
float2 OctEncode(float3 n) {
  n /= (abs(n.x) + abs(n.y) + abs(n.z));                                // 八面体の、表面に、投影（L1 ノルムで、正規化）
  float2 p = n.xy;
  if (n.z < 0.0) {                                                      // 下半球は、折り返して、四隅に、広げる
    p = (1.0 - abs(p.yx)) * (p.xy >= 0.0 ? 1.0 : -1.0);
  }
  return p * 0.5 + 0.5;
}

// 逆変換: uv → 方向。
float3 OctDecode(float2 uv) {
  float2 f = uv * 2.0 - 1.0;
  float3 n = float3(f.x, f.y, 1.0 - abs(f.x) - abs(f.y));
  if (n.z < 0.0) {
    n.xy = (1.0 - abs(n.yx)) * (n.xy >= 0.0 ? 1.0 : -1.0);
  }
  return normalize(n);
}
```

**八面体**（8 枚の、三角形で、できた、立体）の、表面に、方向を、**投影**し、**上半分**は、**そのまま**、**下半分**は、**四隅へ、折り返して**、**正方形**に、広げます。**球面の、全方向**が、**歪みが、少なく**、**1 枚の、正方形**に、収まります。

## プローブから、レイを、飛ばす

**各プローブ**が、**球面上の、N 本**（128〜256 本）の、**レイ**を、**飛ばし**、**当たった面の、ライティング**を、**集めます**。

```hlsl
// DXR の、レイ生成シェーダー: 各プローブについて、N 本のレイを、飛ばす。
[shader("raygeneration")]
void ProbeRayGen() {
  uint ray_index = DispatchRaysIndex().x;                               // このプローブの、何本目のレイか
  uint probe_index = DispatchRaysIndex().y;
  float3 probe_pos = g_probe_positions[probe_index];

  // 球面上に、均等に、散らす（毎フレーム、全体を、ランダムに回転させて、方向の偏りを、時間で、平均する）。
  float3 dir = mul(SphericalFibonacci(ray_index, kRaysPerProbe), g_random_rotation);

  RayDesc ray = { probe_pos, 0.0, dir, 1e27 };
  Payload payload = { float3(0, 0, 0), 0.0 };
  TraceRay(g_scene, RAY_FLAG_NONE, 0xFF, 0, 1, 0, ray, payload);

  g_ray_radiance[uint2(ray_index, probe_index)] = payload.radiance;      // 当たった面の、ライティング済みの色
  g_ray_distance[uint2(ray_index, probe_index)] = payload.hit_distance;  // 当たった距離（可視性の、計算用）
}
```

**球面フィボナッチ**で、**方向を、均等に、散らし**、**フレームごとに、全体を、回転**させます。**フレームを、またいで、平均**すると、**球面全体が、均等に、カバー**されます。**ヒット シェーダー**（当たった面での、ライティング）は、**当たった面の、直接光 + 前のフレームの、プローブの、間接光**を、計算します（**多重反射**が、フレームごとに、積み重なります）。

## 結果を、プローブに、混ぜる

**今フレームの、レイの結果**を、**プローブの、八面体マップ**に、**書き込み**ます。**前のフレームの値**と、**ブレンド**（指数移動平均）して、**ノイズを、減らします**。

```hlsl
// 計算シェーダー: プローブの、八面体マップの、各画素について、その方向に近い、レイの結果を、重みつきで集める。
[numthreads(8, 8, 1)]
void UpdateProbeIrradianceCS(uint3 id : SV_DispatchThreadID, uint probe_index : SV_GroupID) {
  float3 texel_dir = OctDecode((id.xy + 0.5) / 8.0);                     // この画素が、表す、方向
  float3 sum = 0.0;
  float weight_sum = 0.0;
  for (uint r = 0; r < kRaysPerProbe; ++r) {
    float3 ray_dir = RayDirection(r);
    float w = max(0.0, dot(texel_dir, ray_dir));                         // 方向が、近いレイほど、重い（余弦重み）
    sum += g_ray_radiance[uint2(r, probe_index)] * w;
    weight_sum += w;
  }
  float3 result = sum / max(weight_sum, 1e-4);

  // 前のフレームと、混ぜる（hysteresis）。値が、大きく変わったら、履歴を、弱める（光の変化に、追従）。
  float3 history = g_probe_irradiance[uint3(id.xy, probe_index)].rgb;
  float change = max3(abs(result - history)) / max(max3(history), 1e-3);
  float alpha = lerp(0.97, 0.7, saturate(change * 4.0));                 // 変化が大きいほど、今フレームを、強く
  g_probe_irradiance[uint3(id.xy, probe_index)] = float4(lerp(result, history, alpha), 1.0);
}
```

**八面体マップの、各画素**は、**1 つの、方向**を、表します。**その方向に、近い、レイ**（余弦重み）の、結果を、**集め**、**前のフレームと、混ぜます**。**混ぜる割合**（`alpha` = **履歴の、強さ**）を、**値の、変化の大きさ**に、**応じて、変える**（Majercik ら）と、**光が、急に変わる**（扉が、開く）とき、**素早く、追従**し、**静かな、とき**は、**なめらか**です。

## 可視性（光漏れ対策）

**プローブは、壁の、向こう**の、光を、**拾う**ことが、あります。**DDGI は**、**各プローブが、各方向の、「壁までの、距離」**（の、平均と、2 乗の平均）を、**別の、八面体マップに、保存**し、**補間のとき、物の位置が、壁の、手前にあるか**を、**チェビシェフの不等式**で、判定して、**光漏れを、抑えます**（[Interpolation Methods](probes/interpolation.md)）。

```hlsl
// 距離マップ: 各方向の、壁までの、距離の、平均と、2 乗の平均（VSM と、同じ考え方）。
float distance = g_ray_distance[uint2(r, probe_index)];
float2 moments = float2(distance, distance * distance);                  // 1 サンプルあたりの、(距離, 距離²)
// 放射照度と、同じ要領で、八面体マップに、混ぜる（余弦重みを、鋭くして、方向の、解像度を、保つ）。
```

## 長所と短所

| | 内容 |
| --- | --- |
| 長所 | **完全に、動的**（光、物、扉、壊れる壁）。**ベイク不要** |
| 長所 | **世界全体の、間接光**（画面の外の、光も、使える。SSGI の、弱点が、ない） |
| 長所 | **多重反射**が、**自然に、積み重なる**（フレームごとに、前のフレームの、プローブを、使うので） |
| 長所 | **コストが、画面解像度に、依存しない**（プローブの数と、レイの数で、決まる） |
| 短所 | **GPU レイトレーシング**（DXR）が、**必要** |
| 短所 | **低周波**（プローブ間隔の、解像度）。**細かい、接触の影**は、**出ない**（AO、コンタクト シャドウで、補う） |
| 短所 | **光の変化に、遅れる**（履歴との、ブレンド）。**急な変化**で、**少し、遅れて見える** |
| 短所 | **プローブの、配置**（[Probe Placement](probes/placement.md)）が、**品質を、左右**する |
| 短所 | **拡散のみ**（鏡面は、別の手法） |

## コスト

| 項目 | 目安 |
| --- | --- |
| プローブ数 | 数千〜数万個 |
| 1 プローブの、レイ数 | 128〜256 本 |
| 1 フレームの、レイ総数 | プローブ数 × レイ数 = 数十万〜数百万本 |
| 更新の、コスト | 約 0.5〜2 ms（GPU、世代による） |
| メモリ | 放射照度マップ（8×8 × RGBA16）+ 距離マップ（16×16 × RG16）で、プローブ 1 つあたり 約 1.5 KB |

**カメラの、近くの、プローブだけ**を、毎フレーム更新し、**遠くは、数フレームに、1 回**にする（**更新の、間引き**）と、**コストを、抑えられます**。**後続の、研究**（Majercik ら、2021、DDGI Resampling）は、**少ないレイでも、品質を、保つ**ための、**リサンプリング**を、提案しています。

''', before="## よくあるミス")
pg.Refs("gi/ddgi.md", [MAJERCIK, MAJERCIK21, DXR, RTR])

# ================================================================ voxel GI
pg.Dedup("gi/voxel-gi.md")
pg.Add("gi/voxel-gi.md", '''
## ボクセルで、シーンを、持つ

**ボクセル GI**（VXGI、Voxel Cone Tracing、Crassin ら、2011）は、**シーン全体を、3D の、格子（ボクセル）に、変換**し、**各ボクセルに、光と、形状の、情報**を、**持たせ**、**その、ボクセルを、辿って**、**間接光を、求めます**。**画面の外の、情報も、持てる**ので、**SSGI の、弱点が、ありません**。

## 全体の流れ

```text
① シーンを、ボクセル化（各ボクセルに、アルベド、法線、不透明度を、書き込む）
② ボクセルに、直接光を、注入（各ボクセルが、受けている、光 = 放射輝度）
③ ミップマップを、作る（ボクセルを、粗い解像度にまとめた、階層）
④ 各画素から、コーン（円錐）を、飛ばして、ミップを、辿り、間接光を、集める（コーン トレーシング）
```

## ① ボクセル化

**シーンの、三角形**を、**3D テクスチャの、ボクセル**に、**書き込み**ます。**ジオメトリ シェーダー**（または、**保守的ラスタライズ**）で、**三角形を、最も、面積が大きく、見える、軸**（X、Y、Z のどれか）に、投影して、**ラスタライズ**し、**ピクセル シェーダーで、ボクセルに、書き込みます**。

```hlsl
// ボクセル化のピクセル シェーダー: 三角形が、通る、ボクセルに、色と法線を、書き込む。
RWTexture3D<float4> g_voxel_albedo : register(u1);
RWTexture3D<float4> g_voxel_normal : register(u2);

void VoxelizePS(VoxelPSInput input) {
  // ワールド位置 → ボクセル格子の座標（整数）。
  int3 voxel = (int3)floor((input.world_position - g_voxel_origin) / g_voxel_size);
  float4 albedo = g_albedo.Sample(g_linear_wrap, input.uv);
  // 複数の三角形が、同じボクセルに、入る。ここでは、単純に、上書き（本来は、平均など）。
  g_voxel_albedo[voxel] = float4(albedo.rgb, 1.0);                      // a = 不透明度（ボクセルが、占められている）
  g_voxel_normal[voxel] = float4(input.world_normal * 0.5 + 0.5, 1.0);
}
```

**ボクセルの、大きさ**は、**10〜50 cm**（解像度は、128³〜512³）。**範囲が、広い**と、**ボクセルが、粗く**なるので、**カメラの周りに、追従する**（**カスケード**、クリップマップ）、**構造**に、します。

## ② 直接光の、注入

**ボクセル化した、シーン**の、**各ボクセル**に、**直接光**（太陽、ライト）を、**当てて**、**そのボクセルから、出ていく光**（**放射輝度**）を、**計算**して、**保存**します。**シャドウ マップ**を、引いて、**影の中の、ボクセル**は、**暗く**します。

```hlsl
// 計算シェーダー: 各ボクセルの、出射放射輝度を、直接光から、計算して、書き込む。
[numthreads(8, 8, 8)]
void InjectCS(uint3 id : SV_DispatchThreadID) {
  float4 albedo = g_voxel_albedo[id];
  if (albedo.a < 0.5) return;                                            // 空のボクセル
  float3 pos = g_voxel_origin + (float3(id) + 0.5) * g_voxel_size;       // ボクセル中心の、ワールド位置
  float3 N = g_voxel_normal[id].xyz * 2.0 - 1.0;
  float shadow = SampleShadow(pos);
  float3 radiance = albedo.rgb * g_sun_color * saturate(dot(N, -g_sun_dir)) * shadow;
  g_voxel_radiance[id] = float4(radiance, albedo.a);                     // 出射放射輝度 + 不透明度
}
```

**多重反射**は、**前のフレームの、ボクセルの、間接光**を、**今フレームの、ボクセルに、足し込む**ことで、**フレームを、またいで、積み重なり**ます。

## ③ ミップマップを、作る

**ボクセルの、3D テクスチャ**に、**ミップマップ**を、作ります。**ミップが、1 段**進むと、**ボクセルの、解像度が、半分**（8 つの、ボクセルを、1 つに、平均）になり、**広い範囲の、平均的な、光と、不透明度**を、表します。

```cpp
// 3D テクスチャの、ミップを、生成する（ミップごとに、計算シェーダーで、8 ボクセルを、平均する）。
// ミップ 0 = 128³、ミップ 1 = 64³、ミップ 2 = 32³ ...
```

**コーンが、遠くへ、進む**ほど、**広い範囲を、まとめて、見る**必要が、あり、**粗い、ミップ**を、読むのが、**効率的**です（コーン トレーシングの、核心）。

## ④ コーン トレーシング

**各画素**から、**円錐（コーン）**を、**複数、飛ばし**、**円錐の中の、光を、集めます**。**1 本の、細いレイ**でなく、**広がる、コーン**を、使うことで、**少ない本数**（**6 本**、法線の、周りに）でも、**拡散の、間接光**（半球の、全体）を、**カバー**できます。

```text
画素 P から、法線の周りの半球を、6 本のコーン（円錐）で、覆う

      ╱│╲      各コーン: 進むほど、広がる。広がった大きさに合う、ミップを読んで、光を集める
     ╱ │ ╲
    ╱  │  ╲
```

### コーンの、進み方

コーンは、**進むにつれて、直径が、広がり**ます。**その直径**に、**合った、ミップ**を、読みます。

```hlsl
// コーン 1 本を、トレースして、集めた光と、遮蔽（不透明度）を返す。
float4 TraceCone(float3 origin, float3 dir, float aperture, float max_distance) {
  float4 accum = 0.0;                                                    // rgb = 光、a = 累積した、不透明度
  float distance = g_voxel_size;                                         // 開始位置（自分の、ボクセルを、避けるため、少し進める）
  while (distance < max_distance && accum.a < 0.95) {
    float diameter = max(g_voxel_size, 2.0 * aperture * distance);       // この距離での、コーンの、直径
    float mip = log2(diameter / g_voxel_size);                           // 直径に、合う、ミップ
    float3 uvw = (origin + dir * distance - g_voxel_origin) / g_voxel_extent;
    float4 sample = g_voxel_radiance.SampleLevel(g_linear_clamp, uvw, mip);   // ミップから、光と不透明度を読む（3D テクスチャの、補間）
    // 手前から奥へ、前から後ろへの、合成（アルファ ブレンドと、同じ式）。
    float a = (1.0 - accum.a) * sample.a;
    accum.rgb += a * sample.rgb;
    accum.a += a;
    distance += diameter * 0.5;                                          // 直径の、半分ずつ進む
  }
  return accum;
}
```

**コーンの、直径**は、`2 × aperture × distance`（**開き角 × 距離**）で、**距離に、比例して、広がります**。**直径に、合う、ミップ**（`log2(直径 / ボクセル)`）を、読むので、**遠くは、粗い、ミップ**（広い範囲の、平均）を、読み、**コスト**が、**抑えられます**。**手前から、奥へ、光と、不透明度を、合成**し、**不透明度が、ほぼ 1**（**ふさがれた**）なら、**打ち切ります**。

### 拡散の、間接光

**法線の、周りの、半球**を、**数本の、コーン**（**1 本の真上 + 5 本の斜め**）で、**カバー**し、**余弦重み**で、**足し合わせます**。

```hlsl
float3 VoxelDiffuseGI(float3 position, float3 normal, float3 albedo) {
  float3 t, b;
  BuildBasis(normal, t, b);                                              // 法線から、直交基底（[Monte Carlo Integration]）
  // 6 本のコーン: 法線方向 + 斜め 5 本（60° の傾き）。重みは、余弦に、比例（合計 1）。
  const float3 kConeDirs[6] = { float3(0, 0, 1), float3(0, 0.866, 0.5), float3(0.823, 0.268, 0.5),
                                float3(0.509, -0.700, 0.5), float3(-0.509, -0.700, 0.5), float3(-0.823, 0.268, 0.5) };
  const float kConeWeights[6] = { 0.25, 0.15, 0.15, 0.15, 0.15, 0.15 };
  float3 sum = 0.0;
  for (int i = 0; i < 6; ++i) {
    float3 dir = t * kConeDirs[i].x + b * kConeDirs[i].y + normal * kConeDirs[i].z;
    sum += TraceCone(position + normal * g_voxel_size, dir, /*aperture*/ 0.577, 50.0).rgb * kConeWeights[i];
  }
  return albedo * sum;
}
```

**開き角**（`aperture`）が、**約 60° の、コーン**（`tan(30°) ≈ 0.577`）を、**6 本**で、半球を、ほぼ、覆います。**少ないコーン**で、**半球全体**を、**サンプル**できるのが、**コーン トレーシングの、効率の、良さ**です。

## 鏡面反射

**細い、コーン**（**開き角を、粗さに、応じて、小さく**）で、**反射方向**を、**トレース**すると、**鏡面の、間接光**も、**得られます**（**粗い、鏡面**）。**つるつるの鏡面**は、**ボクセルの、解像度が、足りず**、**ぼやけます**。

## 長所と短所

| | 内容 |
| --- | --- |
| 長所 | **動的**（光・物の、変化に、追従）。**GPU レイトレーシング**が、**不要** |
| 長所 | **世界全体の、光**（画面の外も）。**ボクセルの、範囲内** |
| 長所 | **拡散 + 粗い鏡面**の、**両方**が、**1 つの仕組み**で、得られる |
| 短所 | **メモリが、大きい**（ボクセルの 3D テクスチャ + ミップ。512³ で、数百 MB） |
| 短所 | **ボクセル化の、コスト**（動く物は、毎フレーム、**再ボクセル化**） |
| 短所 | **解像度が、粗い**（10〜50 cm）。**細かい、影、薄い壁**は、**表現できない**。**光漏れ**（薄い壁を、コーンが、すり抜ける） |
| 短所 | **コーンの、トレースが、重い**（画素あたり、数本のコーン × 数十ステップ） |
| 短所 | **範囲が、有限**。**カメラの、周りだけ**（クリップマップ）なので、**遠くの、間接光**は、**無い** |

### 光漏れ

**ボクセルが、粗い**と、**薄い壁**（ボクセル 1 つ分に、満たない）は、**ボクセルの、不透明度が、低く**（壁が、ボクセルの、一部しか、占めない）なり、**コーンが、壁を、すり抜けて**、**向こうの光**を、**拾います**。

| 対策 | 内容 |
| --- | --- |
| **ボクセルを、細かく** | **メモリ・コスト**が、増える |
| **不透明度を、強調**（薄い壁でも、ボクセルを、ほぼ不透明に） | ボクセル化で、**占有を、保守的**に |
| **方向性のある、ボクセル**（6 方向の、不透明度） | **ボクセルごとに、方向別の、不透明度**を、持つ。**壁の、向きを、考慮** |

''', before="## よくあるミス")
pg.Refs("gi/voxel-gi.md", [CRASSIN, KAPLANYAN, "Kaplanyan, \"Light Propagation Volumes in CryEngine 3\", SIGGRAPH 2009, Advances in Real-Time Rendering in 3D Graphics and Games", RTR])

# ================================================================ rt-gi
pg.Dedup("gi/rt-gi/index.md")
pg.Add("gi/rt-gi/index.md", '''
## レイトレーシングで、間接光を求める

**ハードウェア レイトレーシング**（DXR、[DirectX Raytracing](https://learn.microsoft.com/windows/win32/direct3d12/direct3d-12-raytracing)）が、**GPU で、使える**ようになり、**間接光を、実際に、レイを、飛ばして、求める**ことが、**リアルタイムで、可能**になりました。**シーンの、形状を、近似せず**（ボクセル、距離場、画面空間）、**本物の、三角形**に対して、**レイを、飛ばせます**。

## 基本の、考え方

**各画素**から、**半球の、ランダムな、方向**に、レイを、飛ばし（**モンテカルロ**、[Monte Carlo Integration](../theory/monte-carlo.md)）、**当たった面の、ライティング**を、**集め**ます。**1 回の反射**（1 バウンス）で、**間接光**を、**直接**、**サンプル**します。

```hlsl
// DXR: 各画素の、拡散の、間接光を、1 本のレイで、推定する（レイ生成シェーダー）。
[shader("raygeneration")]
void GIRayGen() {
  uint2 pixel = DispatchRaysIndex().xy;
  float3 position = g_gbuffer_position[pixel];
  float3 normal = g_gbuffer_normal[pixel];
  float3 albedo = g_gbuffer_albedo[pixel];

  float2 u = Random2(pixel, g_frame_index);
  float3 dir = LocalToWorld(CosineHemisphere(u.x, u.y), normal);         // 余弦重みづけ（拡散）

  RayDesc ray = { position + normal * 1e-3, 0.0, dir, 1e27 };
  Payload payload = { float3(0, 0, 0) };
  TraceRay(g_scene, RAY_FLAG_NONE, 0xFF, 0, 1, 0, ray, payload);         // 本物の三角形に対して、レイを飛ばす

  g_gi_raw[pixel] = float4(albedo * payload.radiance, 1.0);              // 余弦重みづけなので、albedo × 光（約分されている）
}
```

**ヒット シェーダー**（当たった面）で、**その面の、直接光**（太陽、ライト + 影レイ）と、**前のフレームの、間接光**（多重反射）を、**計算して**、**返します**。

## 問題：ノイズ

**1 画素あたり、1 本**の、レイでは、**ノイズだらけ**です（[Monte Carlo Integration](../theory/monte-carlo.md)：誤差は、`1/√N`）。**リアルタイム**では、**レイを、増やせない**ので、**デノイズ**（[Fighting Noise](noise.md)）、**再利用**（[ReSTIR GI](restir.md)）、**キャッシュ**（プローブ。[DDGI](../ddgi.md)）で、**補います**。

## 代表的な、アプローチ

| アプローチ | 内容 | ページ |
| --- | --- | --- |
| **画素ごとに、レイ + デノイズ** | **1 画素に、1 本**のレイ + **時空間フィルタ** | [Fighting Noise](noise.md) |
| **ReSTIR GI** | **隣の画素・前フレームの、レイの結果**を、**再利用** | [ReSTIR GI](restir.md) |
| **キャッシュ**（プローブ）に、レイ | **プローブ**から、レイを、飛ばし、**結果を、蓄積**（[DDGI](../ddgi.md)） | [DDGI](../ddgi.md) |
| **Lumen 型**（ハイブリッド） | **画面空間 + 距離場 + サーフェス キャッシュ**を、**組み合わせる** | [Lumen-Style Approaches](lumen-style.md) |
| **Radiance Cascades** | **カスケード状**に、レイを、**まとめて、再利用** | [Radiance Cascades](radiance-cascades.md) |

## 選び方

| 状況 | おすすめ |
| --- | --- |
| **ハードウェア RT が、使える**、**高品質** | **ReSTIR GI** + デノイズ、**DDGI** |
| **ハードウェア RT が、無い** | **Lumen 型**（ソフトウェア距離場）、**ボクセル GI**、**SSGI + プローブ** |
| **2D ゲーム**、**画面空間** | **Radiance Cascades** |
| **広い、オープン ワールド** | **Lumen 型**、**DDGI**（カスケードの、プローブ） |

詳しい、判断は、[Choosing a Method](choosing.md) を、見てください。

''', before="## よくあるミス")
pg.Refs("gi/rt-gi/index.md", [DXR, SCHIED, BITTERLI, OUYANG, LUMEN, MAJERCIK])

pg.Dedup("gi/rt-gi/noise.md")
pg.Add("gi/rt-gi/noise.md", '''
## レイを、1 本しか、飛ばせない

**リアルタイム**の、**レイトレーシング GI** では、**1 画素あたり、1 本**（多くて、数本）の、レイしか、飛ばせません。**1 本の、レイ**の、結果は、**非常に、ノイズが、大きい**（ある画素は、明るい壁に、当たり、隣は、暗い、影に、当たる）。**ノイズを、取り除く**（**デノイズ**）ことが、**リアルタイム GI の、ほぼ、すべて**と、言っても、過言ではありません。

## デノイズの、基本方針

**同じ、場所の、複数の、サンプル**を、**集めて、平均**することで、ノイズを、減らします。**集める方法**は、**2 つ**あります。

| 方法 | 内容 |
| --- | --- |
| **時間方向**（**時間蓄積**） | **前のフレームの、同じ場所の、結果**を、**混ぜる**。**数十フレーム分**の、サンプルが、集まる |
| **空間方向**（**空間フィルタ**） | **隣の、画素**を、**混ぜる**（ぼかす）。**法線・深度が、近い画素だけ**（エッジを、保つ） |

**両方を、組み合わせた**のが、**SVGF**（Schied ら、2017）に、代表される、**時空間フィルタ**です。

## ① 時間蓄積

**前のフレームの、結果**を、**再投影**（カメラの、動きを、補正して、前の画面の、位置を、求める）して、**今フレームと、混ぜます**。

```hlsl
// 今フレームの、ノイジーな、結果と、前フレームの、蓄積済みの結果を、混ぜる（指数移動平均）。
float2 prev_uv = Reproject(position_world, g_prev_view_proj);            // 前フレームの、画面上の位置
float4 history = g_history.SampleLevel(g_linear_clamp, prev_uv, 0);       // rgb = 前の結果、a = 蓄積した、サンプル数

// 履歴が、有効か（物が、動いて、別の面を、見ていないか）を、法線・深度で、確かめる。
bool valid = all(prev_uv >= 0.0) && all(prev_uv <= 1.0)
          && abs(history_depth - current_depth) < depth_threshold
          && dot(history_normal, current_normal) > 0.9;
float sample_count = valid ? min(history.a + 1.0, 32.0) : 1.0;             // 有効なら、増やす（上限 32）。無効なら、リセット
float alpha = 1.0 / sample_count;                                           // サンプルが、多いほど、今フレームの、影響が、小さい
float3 blended = lerp(history.rgb, current_gi, alpha);
g_history_out[pixel] = float4(blended, sample_count);
```

**蓄積した、サンプル数**を、**覚えて**おき、**混ぜる割合**を、**`1 / サンプル数`**にすると、**ちょうど、平均**（**全サンプルの、単純平均**）に、なります。**上限**（32）を、設けて、**古い履歴の、影響を、薄れさせ**、**光の変化**に、**追従**します。

### 履歴の、リジェクト（拒否）

**カメラ・物が、動く**と、**前のフレームの、同じ画素**が、**別の面**に、なる、ことがあります。**履歴を、そのまま、使う**と、**ゴースト**（残像）が、出ます。

| 判定 | 内容 |
| --- | --- |
| **画面の外** | 前のフレームの位置が、画面の外 → **履歴を、捨てる** |
| **深度の違い** | 前と今の、**深度が、大きく違う** → **別の物**（遮蔽が、解除された） → 捨てる |
| **法線の違い** | **法線が、大きく違う** → **別の面** → 捨てる |
| **物の ID**（任意） | **動く物の、ID が、違う** → 捨てる |

**履歴を、捨てた**画素は、**サンプル数が、1** に、戻り、**ノイズが、目立ちます**（数フレームで、また、蓄積される）。**空間フィルタ**が、**その間の、ノイズを、隠します**。

## ② 空間フィルタ：エッジを、保つ、ぼかし

**隣の画素**を、**混ぜて**、ノイズを、**ぼかします**。**ただし**、**物の、エッジ**（法線・深度が、違う画素）を、**越えて**、混ぜる**と、**にじむ**ので、**エッジで、止める**、**バイラテラル フィルタ**（[Bilateral Blur](../../ao/filtering/bilateral-blur.md)）を、使います。

### À-Trous ウェーブレット フィルタ

**SVGF** は、**À-Trous**（「穴あき」）**ウェーブレット フィルタ**を、使います。**同じ、小さな、5×5 のカーネル**を、**間隔を、広げながら**（1、2、4、8、16 画素おき）、**複数回、適用**します。**少ない読み込み**で、**広い範囲**を、ぼかせます。

```hlsl
// À-Trous フィルタの 1 回（step: 画素の間隔。1, 2, 4, 8, 16 と、繰り返す）。
float3 ATrous(uint2 pixel, int step_size, float3 center_color, float3 center_normal, float center_depth, float sigma_l) {
  const float kKernel[3] = { 1.0, 2.0 / 3.0, 1.0 / 6.0 };               // 5 タップの、B スプライン カーネル
  float3 sum = 0.0;
  float weight_sum = 0.0;
  for (int dy = -2; dy <= 2; ++dy)
    for (int dx = -2; dx <= 2; ++dx) {
      uint2 q = pixel + int2(dx, dy) * step_size;                         // 間隔を、空けて、読む
      float3 color = g_color[q];
      float3 normal = g_normal[q];
      float depth = g_depth[q];

      // 3 つのエッジ停止関数: 法線、深度、輝度（色）が、近いほど、重みが大きい。
      float w_normal = pow(saturate(dot(center_normal, normal)), g_sigma_normal);
      float w_depth = exp(-abs(center_depth - depth) / (g_sigma_depth * length(float2(dx, dy)) * step_size + 1e-4));
      float w_lum = exp(-abs(Luminance(center_color) - Luminance(color)) / sigma_l);
      float w = kKernel[abs(dx)] * kKernel[abs(dy)] * w_normal * w_depth * w_lum;
      sum += color * w;
      weight_sum += w;
    }
  return sum / max(weight_sum, 1e-4);
}
```

**5×5 の、25 タップ**を、**間隔を広げて**、**5 回**（1、2、4、8、16）、**適用**すると、**約 `(5 × 2⁴)` = 80 画素の幅**を、ぼかせます（**25 × 5 = 125 回の読み込み**で）。**普通の、大きなカーネル**（81×81 = 6,561 回）より、**はるかに、少ない**です。**3 つの、エッジ停止**（法線、深度、輝度）が、**エッジを、保ちます**。

### 分散で、フィルタの強さを、決める（SVGF の、核心）

**SVGF** は、**画素ごとの、分散**（ノイズの、大きさ）を、**推定**し、**ノイズが、大きい画素ほど**、**強く、ぼかします**。

```hlsl
// 時間蓄積で、輝度の、平均と、2 乗の平均を、持つ → 分散 = E[x²] − E[x]²。
float variance = max(0.0, moments.y - moments.x * moments.x);
float sigma_l = g_sigma_luminance * sqrt(variance) + 1e-4;               // 分散が、大きい → 輝度の差を、許す（強く、ぼかす）
```

**ノイズが、大きい**（分散が、大きい）画素は、**輝度の、差を、より、許して**、**強く、ぼかし**、**ノイズが、小さい**画素は、**弱く**ぼかして、**細部を、保ちます**。

## ③ ノイズを、減らす、工夫（入力側）

**デノイザーに、渡す前**に、**入力の、ノイズを、減らす**工夫も、**効果的**です。

| 工夫 | 内容 |
| --- | --- |
| **ブルー ノイズ**の、乱数 | サンプル方向を、**ブルー ノイズ**で、選ぶ。**ノイズの、粒が、均一**で、**フィルタが、効きやすい**（[Monte Carlo Integration](../theory/monte-carlo.md)） |
| **低食い違い量列** | Halton、Sobol、R2 など。**偏りの、少ない**サンプル |
| **余弦重み・重点サンプリング** | **寄与の、大きい方向を、多めに**（[Monte Carlo Integration](../theory/monte-carlo.md)） |
| **明るすぎる、サンプルを、切る**（ファイアフライ対策） | **明るい光源に、偶然、当たった**サンプルが、**白い点**（ファイアフライ）になる。**上限で、クランプ** |
| **半分の解像度で、レイ** | **画素の半分**にだけ、レイを、飛ばし、**アップサンプル** |

```hlsl
// ファイアフライ対策: 1 サンプルの、明るさに、上限を、設ける。
float lum = Luminance(radiance);
radiance *= min(1.0, g_max_radiance / max(lum, 1e-4));                    // 上限を超えたら、比率で、下げる
```

## デノイズの、限界

| 問題 | 内容 |
| --- | --- |
| **ぼやけ** | **強く、ぼかす**と、**細かい、陰影**（接触の、影）が、失われる |
| **ゴースト・遅れ** | **時間蓄積**が、**光の変化に、遅れる**（ライトが、動いた、数フレーム後に、反映） |
| **動く物の、ノイズ** | **履歴を、捨てる**ので、**動く物の、周りが、ノイズだらけ**になる |
| **ちらつき** | **デノイザーの、判断が、フレームごとに、揺れる** |

**ノイズと、ぼやけ・遅れ**は、**トレード オフ**です。**ReSTIR**（[ReSTIR GI](restir.md)）は、**入力の、質を、上げる**ことで、**デノイザーの、負担を、減らします**。

''', before="## よくあるミス")
pg.Refs("gi/rt-gi/noise.md", [SCHIED, SCHIED18, KARIS, STACHOWIAK, "Dammertz, Sewtz, Hanika, Lensch, \"Edge-Avoiding À-Trous Wavelet Transform for Fast Global Illumination Filtering\", High Performance Graphics 2010（À-Trous フィルタ）"])

pg.Dedup("gi/rt-gi/restir.md")
pg.Add("gi/rt-gi/restir.md", '''
## ReSTIR の、考え方

**ReSTIR**（Reservoir-based Spatio-Temporal Importance Resampling、Bitterli ら、2020）は、**少ない、サンプルから、良い、サンプルを、選び、再利用する**方法です。**ReSTIR GI**（Ouyang ら、2021）は、これを、**間接光**に、**適用**しました。**デノイズする前の、入力**の、**質を、上げる**ので、**ノイズが、はるかに、少ない**、**GI** が、得られます。

## 重要な、2 つの、アイデア

| アイデア | 内容 |
| --- | --- |
| **リザーバー サンプリング** | **多数の、候補**から、**重みに、比例した、確率で、1 つを、選ぶ**。**候補を、全部、覚えず**、**1 つだけ**（リザーバー）を、持てばよい |
| **空間・時間の、再利用** | **隣の画素**や、**前のフレーム**の、リザーバーの、サンプルを、**自分の候補に、加える** |

**隣の画素は、似た、光**を、受けている（**同じ、面、近い、位置**）ことが、多いので、**隣の画素が、見つけた、良いサンプル**（明るい方向）は、**自分にとっても、良い**サンプルの、可能性が、高い。**それを、使い回す**ことで、**実質的な、サンプル数が、何十倍にも、増えます**。

## リザーバー（貯水池）

**リザーバー**は、**ストリームの、要素**（候補）の中から、**重みに比例して、1 つを、選ぶ**、**小さな、データ構造**です。**要素を、1 つずつ、見て**、**選んだ、1 つ**と、**重みの、合計**だけを、**覚えます**。

```hlsl
// リザーバー: 選ばれた 1 つのサンプルと、見てきた候補の重みの合計・個数。
struct Reservoir {
  float3 hit_position;      // 選ばれたサンプル: レイが、当たった位置
  float3 hit_normal;        // 当たった面の、法線
  float3 radiance;          // 当たった面から、来る光（ライティング済み）
  float weight_sum;         // これまでに、見た、候補の重みの合計
  float M;                  // これまでに、見た、候補の数
  float W;                  // 選ばれたサンプルの、最終的な重み（バイアス補正用）
};

// 候補を、1 つ、リザーバーに、投入する。重みに比例した確率で、置き換える。
bool UpdateReservoir(inout Reservoir r, float3 position, float3 normal, float3 radiance, float weight, float u) {
  r.weight_sum += weight;
  r.M += 1.0;
  if (u * r.weight_sum < weight) {                       // 確率 weight / weight_sum で、新しい候補に、置き換える
    r.hit_position = position;
    r.hit_normal = normal;
    r.radiance = radiance;
    return true;
  }
  return false;
}
```

**重みが、大きい候補ほど、選ばれやすく**、**1 つだけ**を、**覚えれば、済みます**（メモリが、一定）。**重み**は、**その候補が、どれだけ、良いか**（**明るい、方向**ほど、大きい）を、表します。

## ReSTIR GI の、流れ

```text
① 初期サンプル: 各画素が、1 本のレイを飛ばし、当たった点を、リザーバーに入れる
② 時間的な再利用: 前のフレームの、同じ場所の、リザーバーと、マージ（候補を、混ぜる）
③ 空間的な再利用: 隣の画素（数個）の、リザーバーと、マージ
④ シェーディング: 最終的に、選ばれたサンプルで、間接光を、計算
```

### ① 初期サンプル

```hlsl
// 各画素: 1 本のレイを飛ばして、当たった点を、リザーバーの、最初の候補にする。
Reservoir r = (Reservoir)0;
float3 dir = LocalToWorld(CosineHemisphere(u1, u2), normal);
RayHit hit = TraceRay(position, dir);
float3 radiance = ShadeHit(hit);                                         // 当たった点の、ライティング
// 重み: 「目標となる、分布」（当たった点の、光の明るさ）/「実際に、サンプルした分布」（余弦重み）。
float target_pdf = Luminance(radiance);                                  // 目標: 明るい光を、多く
float source_pdf = CosinePdf(dir, normal);                               // 実際に、サンプルした、確率密度
UpdateReservoir(r, hit.position, hit.normal, radiance, target_pdf / source_pdf, u3);
```

**目標となる、分布**（明るい光ほど、**選びたい**）と、**実際に、サンプルした、分布**（余弦重み）の、**比**が、**重み**です。**明るい光を、見つけた**候補は、**重みが、大きく**、**リザーバーに、残りやすく**なります。

### ② 時間的な、再利用

```hlsl
// 前のフレームの、同じ場所の、リザーバーを、読んで、今のリザーバーに、マージする。
Reservoir prev = g_prev_reservoirs[prev_pixel];
prev.M = min(prev.M, 20.0 * r.M);                                        // 履歴の、影響に、上限（古すぎる、サンプルを、弱める）
// 前の、サンプルの、重みを、今のピクセルの、目標分布で、評価し直す（今の、位置・法線から、見た、明るさ）。
float prev_target = Luminance(prev.radiance) * max(0.0, dot(normal, normalize(prev.hit_position - position)));
// マージ: 前のリザーバーを、1 つの、候補として、今のリザーバーに、投入する。
UpdateReservoir(r, prev.hit_position, prev.hit_normal, prev.radiance, prev_target * prev.W * prev.M, u4);
r.M += prev.M - 1.0;                                                      // 見てきた、候補数を、足す
```

**前のフレームの、リザーバー**が、**数十フレーム分**の、**候補**を、**代表**しています。**今のリザーバーに、マージ**することで、**数十フレーム分**の、**サンプル**を、**使えます**。**今の位置・法線から、見直した**、**重み**（`prev_target`）で、**評価し直す**ことが、**偏りを、避ける**ために、**必要**です。

### ③ 空間的な、再利用

```hlsl
// 隣の画素（数個）の、リザーバーを、候補として、マージする。法線・深度が、近い画素だけ。
for (int k = 0; k < kSpatialSamples; ++k) {
  uint2 neighbor = pixel + RandomOffsetInDisk(k, radius);
  if (!SimilarSurface(neighbor, pixel)) continue;                         // 別の面（法線・深度が、違う）は、使わない
  Reservoir n = g_reservoirs[neighbor];
  float n_target = Luminance(n.radiance) * max(0.0, dot(normal, normalize(n.hit_position - position)));
  UpdateReservoir(r, n.hit_position, n.hit_normal, n.radiance, n_target * n.W * n.M, Random(k));
  r.M += n.M - 1.0;
}
```

**隣の画素が、見つけた、良い、サンプル**（明るい点）を、**自分の候補に、加えます**。**1 回の、空間的な、再利用**で、**実質的なサンプル数が、数倍**に、なります。**数回、繰り返す**（**ping-pong**）と、**さらに、増える**。

### ④ シェーディング

```hlsl
// 最終的に、選ばれたサンプルの、方向の、光で、間接光を、計算する。
float3 dir = normalize(r.hit_position - position);
float cos_term = max(0.0, dot(normal, dir));
float3 indirect = albedo / 3.14159265 * r.radiance * cos_term * r.W;     // r.W: バイアス補正の重み（1 / ターゲット × 重み合計 / M）
```

**r.W**（最終的な、重み）が、**偏りの、補正**です。`W = weight_sum / (M × target_pdf)` で、**リザーバー サンプリングの、公式**から、**導かれます**（Bitterli ら、2020）。

## 偏り（バイアス）の、問題

**空間的な、再利用**で、**隣の画素**の、サンプルを、**使う**と、**その方向が、自分から、見えるか**（**間に、壁が、あるか**）を、**確認していない**と、**間違った、光**を、**使います**（**光漏れ**）。**正しく**は、**隣の、サンプルの、方向に、影レイを、飛ばして**、**見えるかを、確認**します。

| 方式 | 内容 | コスト |
| --- | --- | --- |
| **偏りあり**（可視性を、確認しない） | **速い**。**光漏れ、暗くなる、バイアス** | 小 |
| **偏りなし**（可視性を、確認） | **正しい**。**影レイが、追加で、必要** | 中 |

実用では、**偏りを、許容**して、**類似した面**（法線・深度）だけ、再利用し、**必要な場面**だけ、**影レイで、確認**します。

## 長所と短所

| | 内容 |
| --- | --- |
| 長所 | **デノイザーに、渡す前の、質が、高い**。**同じレイ数で、ノイズが、はるかに、少ない** |
| 長所 | **明るい光を、見つけやすい**（重点サンプリング）。**小さく、明るい光源**（窓、ランプ）の、間接光が、**安定** |
| 長所 | **1 画素あたり、1 本のレイ**でも、**高品質** |
| 短所 | **リザーバーの、メモリ**（画素ごとに、リザーバーを、2 つ持つ、ping-pong） |
| 短所 | **実装が、複雑**。**偏りの、管理**が、**難しい** |
| 短所 | **動く物**・**急な、光の変化**で、**時間的な、再利用が、乱れる**（**ゴースト**） |
| 短所 | **GPU レイトレーシング**が、必要 |

## 他の、手法との、関係

| 手法 | ReSTIR との、関係 |
| --- | --- |
| **デノイザー**（SVGF など） | **ReSTIR の、後**に、**さらに、デノイズ**する（**併用**）。ReSTIR で、**入力の質が、上がる**ので、**デノイザーを、弱く**できる |
| **DDGI** | **別の、アプローチ**（プローブに、蓄積）。**ReSTIR は、画素ごと**。**併用**する場合も（**プローブで、遠くの光、ReSTIR で、近くの細部**） |

''', before="## よくあるミス")
pg.Refs("gi/rt-gi/restir.md", [BITTERLI, OUYANG, WYMAN23, "Talbot, Cline, Egbert, \"Importance Resampling for Global Illumination\", Eurographics Symposium on Rendering 2005（重要度リサンプリングの、源流）", SCHIED])

pg.Dedup("gi/rt-gi/lumen-style.md")
pg.Add("gi/rt-gi/lumen-style.md", '''
## 1 つの手法では、足りない

Unreal Engine 5 の **Lumen**（Wright ら、2022）は、**1 つの、手法**ではなく、**複数の、手法を、組み合わせた**、**ハイブリッド**です。**それぞれの、手法の、長所を、生かし**、**短所を、補い合います**。**ハードウェア レイトレーシングが、無くても、動き**、**有ると、品質が、上がります**。

| 手法 | 得意 | 苦手 |
| --- | --- | --- |
| **画面空間の、トレース**（SSGI、SSR） | **近距離で、最高精度**（画面の、実際の、ジオメトリ）。**安い** | **画面の外・隠れた面**が、無い |
| **距離場**（ソフトウェア、メッシュ SDF） | **世界全体**。**安い**、**遠くまで、レイを飛ばせる** | **細かい、形状**は、粗い（距離場の、解像度） |
| **ハードウェア レイトレーシング** | **本物の、三角形**に対して、**正確** | **重い**、GPU が、必要 |
| **サーフェス キャッシュ**（面ごとの、ライティングの、キャッシュ） | **当たった面の、ライティング**を、**高速に、引ける**（毎回、計算しない） | **キャッシュの、更新**が、必要 |

## 全体の構造（概要）

```text
各画素から、レイを、飛ばす
   ① まず、画面空間で、トレース（近距離。最も、正確）
        ↓ 当たらなければ
   ② 距離場（またはハードウェア RT）で、世界全体を、トレース（遠距離）
        ↓ 当たった点の、ライティングは
   ③ サーフェス キャッシュ（面ごとの、ライティングの、キャッシュ）から、引く（再計算しない）
        ↓ それでも、ノイジーなので
   ④ プローブ（スクリーン空間、ワールド空間）に、集めて、空間・時間で、フィルタ
```

### ① 近くは、画面空間

**画面に、映っている**、**近距離の、ジオメトリ**に、当たる、レイは、**画面空間の、レイマーチ**（[SSGI](../ssgi.md)）で、**高精度かつ、安く**、トレースできます。**深度バッファ**が、**そのまま、ジオメトリ**です。

### ② 遠くは、距離場

**画面空間で、当たらなかった**レイ（**画面の外・隠れた面**）は、**メッシュの、距離場**（各メッシュを、**距離場**に、変換した、データ。[Distance Field AO](../../ao/world-space/dfao.md)）で、**トレース**します。**距離場**は、**スフィア トレーシング**（距離が、分かるので、**大きく、進める**）で、**速く**、**世界全体**を、辿れます。

```hlsl
// 距離場の、スフィア トレーシング: 各点での、最も近い面までの、距離だけ、安全に、進める。
float3 p = origin;
for (int i = 0; i < kMaxSteps; ++i) {
  float d = SampleGlobalDistanceField(p);                                // 最も近い面までの距離（グローバル距離場）
  if (d < kHitThreshold) break;                                          // 面に、十分、近づいた → 当たり
  p += dir * d;                                                          // 距離だけ、安全に進む（面を、越えない）
}
```

**ソフトウェア**で、**動く**ので、**ハードウェア レイトレーシングが、無い、GPU** でも、使えます（**精度は、距離場の、解像度で、決まる**）。

### ③ サーフェス キャッシュ

**レイが、当たった、点の、ライティング**を、**毎回、計算する**と、**重い**（直接光、影、間接光）。**メッシュの、各面**に、**ライティングの、キャッシュ**（**サーフェス キャッシュ**、**カード**）を、**持ち**、**当たった、点の、ライティングは、キャッシュから、読むだけ**に、します。

| 項目 | 内容 |
| --- | --- |
| **カード** | メッシュを、**6 方向**（上下左右前後）から、見た、**小さな、平面の、画像**（アルベド、法線、深度、ライティング）の、**アトラス** |
| **更新** | **毎フレーム、一部**（優先度の、高い、カード）だけ、**ライティングを、再計算**して、**キャッシュを、更新** |
| **使い方** | レイが、当たった点を、**カードに、投影**し、**そこの、ライティングを、読む** |

### ④ 集めて、フィルタする

**画素ごとの、レイ**は、**ノイジー**なので、**プローブ**（**スクリーン空間に、並べた、プローブ**）に、**集め**、**時間・空間で、フィルタ**します（[Fighting Noise](noise.md)）。**プローブ**に、集める、ことで、**1 画素あたりの、コスト**を、**減らし**、**プローブの、補間**で、**全画素の、間接光**を、得ます。

## 長所と短所

| | 内容 |
| --- | --- |
| 長所 | **動的**（光・物の、変化に、追従）。**世界全体の、間接光** |
| 長所 | **ハードウェア RT が、無くても、動く**（距離場） |
| 長所 | **GI と、反射**（粗い鏡面）を、**同じ、仕組み**で、扱える |
| 短所 | **実装が、非常に、複雑**（距離場、サーフェス キャッシュ、プローブ、フィルタ）。**自作は、大変** |
| 短所 | **距離場の、解像度**による、**細かい形状の、欠落**、**光漏れ**（薄い壁） |
| 短所 | **メモリ**（距離場、カード アトラス、プローブ） |
| 短所 | **ハードウェア RT 版**では、**GPU の、世代**に、依存 |

## 自作する、場合の、現実的な、構成

**フル機能の、Lumen を、自作**するのは、**現実的ではありません**。**小規模**には、**必要な、機能を、絞った**構成が、**現実的**です。

| 目的 | 構成 |
| --- | --- |
| **動的な、環境光**（まず、これ） | **SSGI + ライト プローブ**（ベイク、または、空の SH） |
| **動的な、間接光を、広く**（RT 対応の GPU） | **DDGI**（[DDGI](../ddgi.md)） |
| **ソフトウェアで、世界全体の、間接光** | **ボクセル GI**（[Voxel GI](../voxel-gi.md)）、**距離場** |
| **高品質**（RT 対応の GPU） | **ReSTIR GI**（[ReSTIR GI](restir.md)）+ デノイザー |

''', before="## よくあるミス")
pg.Refs("gi/rt-gi/lumen-style.md", [LUMEN, STACHOWIAK, SCHIED, "Epic Games, \"Lumen Technical Details\", Unreal Engine 5 ドキュメント"])

pg.Dedup("gi/rt-gi/radiance-cascades.md")
pg.Add("gi/rt-gi/radiance-cascades.md", '''
## Radiance Cascades とは

**Radiance Cascades**（Sannikov、2023）は、**間接光**（グローバル イルミネーション）を、**ほぼ、ノイズなし**で、**一定の、コストで**、計算する、**新しい、アプローチ**です。**元々は、2D ゲームの、ライティング**（Path of Exile 2 などの、**画面空間**）で、使われ、**3D への、拡張**も、研究されています。

## 考え方：光の、見え方は、距離で、変わる

**点の周りの、光**を、**サンプル**するとき、**サンプルする、方向の、数**と、**距離**には、**関係**があります。

| 距離 | 必要な、方向の、数 | 必要な、位置の、細かさ |
| --- | --- | --- |
| **近い**（数画素） | **少ない**（角度が、粗くてよい。近くの、光は、**少ない方向で、十分**に、**捉えられる**） | **細かい**（近くの、変化は、急） |
| **遠い**（数百画素） | **多い**（遠くの、小さな光源を、**見つけるには**、**細かい角度**が、必要） | **粗い**（遠くの、光は、**位置の変化に、ゆるやか**） |

**近くは、位置を、細かく、方向を、粗く**、**遠くは、位置を、粗く、方向を、細かく**、サンプルすれば、**効率が、良い**、**という、観察**です。

## カスケード

**距離の、範囲ごと**に、**別の、解像度**（**位置の、密度と、方向の、数**）で、**光を、集めます**。**カスケード**（階層）と、呼びます。

```text
カスケード 0: 距離 0〜4 画素   位置: 全画素ごと   方向: 4 方向
カスケード 1: 距離 4〜16 画素  位置: 2 画素おき   方向: 16 方向（4 倍）
カスケード 2: 距離 16〜64 画素 位置: 4 画素おき   方向: 64 方向（4 倍）
カスケード 3: 距離 64〜256 画素 位置: 8 画素おき  方向: 256 方向（4 倍）
```

**次の、カスケードに、行く**ごとに、**位置の、密度が、1/4**（縦横、半分）に、**方向の数が、4 倍**に、なります。**どのカスケードも、サンプルの、総数が、ほぼ同じ**（位置 × 方向）なので、**コストが、一定**です。

## 各カスケードで、光を、集める

**各カスケードの、各プローブ**は、**自分の、担当する、距離の範囲**（たとえば、16〜64 画素）だけ、**各方向に、レイを、進め**、**そこに、ある、光と、遮蔽**を、**集めます**。**レイが、短い**（担当する範囲だけ）ので、**安く**、**同じ範囲を、どのレイも、見る**ため、**ノイズが、出ません**（**ランダムでなく、決まった、方向**）。

```hlsl
// カスケード n の、プローブ 1 つ: 担当する距離範囲（[start, end]）で、各方向に、短いレイを、進める。
float4 CastRayInterval(float2 origin, float2 dir, float start, float end) {
  float3 radiance = 0.0;
  float transmittance = 1.0;                                             // 遮蔽（光が、通り抜けたか）
  for (float t = start; t < end; t += 1.0) {
    float2 p = origin + dir * t;
    float4 scene = g_scene.SampleLevel(g_point_clamp, p / g_size, 0);    // rgb = その画素の、発光、a = 不透明度
    radiance += transmittance * scene.rgb * scene.a;                      // 光源に当たったら、足す
    transmittance *= (1.0 - scene.a);                                     // 遮蔽物に当たったら、光が、減る
    if (transmittance < 0.01) break;
  }
  return float4(radiance, transmittance);                                 // 担当範囲の、光と、通り抜ける割合
}
```

**各レイ**は、**自分の担当範囲**（`start` 〜 `end`）だけ、**進み**、**光（発光）と、遮蔽**を、**集めます**。**担当範囲の、外**は、**他の、カスケード**が、見ます。

## カスケードを、マージする

**遠いカスケード（粗い）の、結果**を、**近いカスケード（細かい）**に、**足し込みます**。**近いカスケードの、各レイ**は、**自分の、範囲の、先**（**遠く**）を、**次のカスケードに、問い合わせ**て、**遠くの光**を、**引き継ぎます**。

```hlsl
// カスケード n の、1 方向の結果 = 自分の範囲の結果 + 自分の範囲を、通り抜けた、割合 × 次のカスケードの、同じ方向の結果。
float4 near = CastRayInterval(origin, dir, start, end);                   // このカスケードの範囲
float4 far = SampleNextCascade(origin, dir);                              // 次の（遠い）カスケードの、同じ方向の、結果
float3 total_radiance = near.rgb + near.a * far.rgb;                      // 近くを通り抜けた分だけ、遠くの光が、届く
float total_transmittance = near.a * far.a;
```

**近い範囲で、遮られたら**（`near.a` が、小さい）、**遠くの光は、届かない**。**通り抜けたら**、**遠くの光が、足されます**。これを、**カスケード 0 まで**、**繰り返す**と、**全距離の、光**が、**1 つに**、まとまります。

**次の、カスケードの、結果の、読み出し**では、**4 つの近い、プローブ**を、**補間**（**双線形補間**）して、**方向も、補間**します（**4 倍の、方向の中から**、**対応する 4 方向**を、**平均**）。

## 長所と短所

| | 内容 |
| --- | --- |
| 長所 | **ノイズが、ほぼ、無い**（**ランダムでなく**、**決定的な、サンプル**）。**デノイズ不要** |
| 長所 | **コストが、一定**（シーンの、複雑さ、光源の数に、**依存しない**） |
| 長所 | **非常に、多くの、光源**（数千）でも、**同じコスト** |
| 長所 | **ソフトな影、間接光**が、**まとめて**得られる |
| 短所 | **主に、2D**（画面空間）向け。**3D への、拡張**は、**研究段階**（メモリ、コストが、増える） |
| 短所 | **画面の外の情報**が、無い（2D ゲームなら、画面が、世界全体） |
| 短所 | **カスケードの、継ぎ目**で、**アーティファクト**（リンギング、**ブロック状の、模様**）が、出ることがある |
| 短所 | **シーンの、解像度に、依存**（画素ごとの、不透明度・発光の、マップが、必要） |

## 使いどころ

| 場面 | 判断 |
| --- | --- |
| **2D ゲームの、ライティング**（ピクセル アート、トップダウン） | **非常に、向く**（動的な、ライトと、影を、ノイズなしで） |
| **3D の、間接光**（画面空間） | **研究段階**。**実験的に、試す価値** |
| **ハードウェア RT が、使えない、環境** | **選択肢**（ただし、2D が、前提） |

''', before="## よくあるミス")
pg.Refs("gi/rt-gi/radiance-cascades.md", [SANNIKOV, "Osborne, Sannikov ほか, Path of Exile 2 の、ライティングに関する、開発者の発表資料（Radiance Cascades の、実用例）", RTR])

pg.Dedup("gi/rt-gi/choosing.md")
pg.Add("gi/rt-gi/choosing.md", '''
## 手法を、選ぶ、基準

**リアルタイムの、レイトレーシング GI** には、**複数の手法**が、あります。**どれが、最良**ということは、なく、**ゲームの、条件**で、選びます。

| 基準 | 内容 |
| --- | --- |
| **ハードウェア RT の、有無** | **DXR 対応の GPU**を、**前提**にできるか |
| **ターゲットの、性能** | PC（高性能）、コンソール、**ハイエンド**のみ、**ミドル** |
| **シーンの、規模** | **狭い室内**、**広いオープン ワールド** |
| **光の、変化** | **静的**、**昼夜が、変わる**、**動く、ライト** |
| **品質の、要求** | **フォトリアル**、**スタイライズ** |
| **開発の、リソース** | **自作**、**エンジンの、機能を、使う** |

## 手法の、比較

| 手法 | RT 必要 | コスト | 品質 | ノイズ | 世界全体 | 実装の、難しさ |
| --- | --- | --- | --- | --- | --- | --- |
| **ライトマップ + プローブ**（ベイク） | **不要** | **最小** | **高**（静的） | なし | ○（事前） | 低〜中 |
| **SSGI** | 不要 | 小 | 中 | 中 | ×（画面のみ） | 低 |
| **ボクセル GI** | 不要 | 中〜大 | 中 | 小 | ○（範囲内） | 中〜高 |
| **DDGI** | **必要** | 中 | 中〜高（低周波） | 小 | ○ | 中 |
| **ReSTIR GI + デノイズ** | **必要** | 大 | **高** | 小〜中 | ○ | **高** |
| **Lumen 型** | 任意（距離場でも可） | 中〜大 | **高** | 小 | ○ | **非常に高** |
| **Radiance Cascades** | 不要 | 中 | 高（2D） | **なし** | ×（2D） | 中 |

## 状況別の、おすすめ

| 状況 | おすすめ | 理由 |
| --- | --- | --- |
| **静的な、場面**（室内、一本道）、**幅広い、ハード** | **ライトマップ + ライト プローブ** | **最高品質で、最安**。**どの GPU でも、動く** |
| **昼夜が、変わる、オープン ワールド**（RT なし） | **プローブの、動的更新** + **空の、環境光**、**SSGI で、補う** | RT 不要。**軽い** |
| **昼夜、動く物**（**DXR 対応の、ハイエンド PC**） | **DDGI**、または、**ReSTIR GI** | **完全に、動的**。**画面の外の、光も、使える** |
| **最高品質**（**DXR、ハイエンド**） | **ReSTIR GI + デノイザー**、**DDGI（遠く）+ ReSTIR（近く）** | **ノイズが、少なく**、**細部が、正確** |
| **2D ゲーム** | **Radiance Cascades** | **ノイズなし**、**光源数に、依存しない** |
| **自作の、小規模エンジン**（学習・インディー） | **ライト プローブ（SH）+ SSGI**、慣れたら、**DDGI** | **実装が、現実的** |

## 組み合わせる

**1 つに、絞らず**、**組み合わせる**のが、**現実的**です。

| 組み合わせ | 役割分担 |
| --- | --- |
| **DDGI + SSGI** | **DDGI** が、**世界全体の、低周波の、間接光**、**SSGI** が、**近距離の、細かい、陰影**（接触の、光のにじみ） |
| **ライトマップ + DDGI** | **静的な背景**は、**ライトマップ**（最高品質）、**動く物**は、**DDGI**（動的）。**DDGI の、レイが、ライトマップを、読む**（ヒット シェーダーで、ライトマップを、引く） |
| **ReSTIR GI + DDGI** | **近くは、ReSTIR**（画素ごと、高品質）、**遠くは、DDGI**（プローブ、安い） |
| **GI + AO + コンタクト シャドウ** | GI は、**低周波**。**細かい、接触の暗さ**は、**AO / コンタクト シャドウ**で、補う（[AO](../../ao/index.md)、[Contact Shadows](../../shadows/contact-shadows.md)） |

## 判断の、順序

```text
1. 光は、動くか？
     No  → ライトマップ + プローブ（ここで終わり。最も、安く、高品質）
     Yes ↓
2. ハードウェア RT を、前提にできるか？
     No  → プローブの動的更新 + SSGI（+ ボクセル GI）
     Yes ↓
3. 品質を、最優先か、それとも、安さか？
     最優先 → ReSTIR GI + デノイザー（+ DDGI）
     安さ   → DDGI
```

## 注意点

| 項目 | 内容 |
| --- | --- |
| **フォールバック** | **RT 非対応の、環境**に、**対応**するなら、**フォールバック**（ベイク + SSGI）を、**用意** |
| **品質設定** | **レイ数、プローブ数、デノイズの、強さ**を、**設定で、変えられる**ように |
| **デバッグ** | **間接光だけを、表示**する、**デバッグ ビュー**（直接光を、消す）を、**用意**。**GI の、バグは、見つけにくい** |
| **測る** | **プロファイラ**（[パフォーマンス プロファイラー](../../../vs/profiler.md)、PIX）で、**実際の、コスト**を、**測る**。**計算量の、見積もり**が、**当たらない**ことが、多い |

''', before="## よくあるミス")
pg.Refs("gi/rt-gi/choosing.md", [LUMEN, MAJERCIK, BITTERLI, OUYANG, RTR])

# ================================================================ comparison
pg.Dedup("gi/comparison.md")
pg.Refs("gi/comparison.md", [RTR, LUMEN, MAJERCIK, CRASSIN, OUYANG])
print("ok")
