import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import pg  # noqa: E402

HILLAIRE = '''Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique", Computer Graphics Forum (Eurographics Symposium on Rendering 2020)'''
BRUNETON = '''Bruneton, Neyret, "Precomputed Atmospheric Scattering", Computer Graphics Forum (Eurographics Symposium on Rendering 2008)'''
BRUNETON17 = '''Bruneton, "A Qualitative and Quantitative Evaluation of 8 Clear Sky Models", IEEE Transactions on Visualization and Computer Graphics, Vol. 23, No. 12, 2017'''
NISHITA = '''Nishita, Sirai, Tadamura, Nakamae, "Display of the Earth Taking into Account Atmospheric Scattering", SIGGRAPH 1993'''
PREETHAM = '''Preetham, Shirley, Smits, "A Practical Analytic Model for Daylight", SIGGRAPH 1999'''
HOSEK = '''Hošek, Wilkie, "An Analytic Model for Full Spectral Sky-Dome Radiance", ACM Transactions on Graphics (SIGGRAPH 2012)'''
PEREZ = '''Perez, Seals, Michalsky, "All-Weather Model for Sky Luminance Distribution — Preliminary Configuration and Validation", Solar Energy, Vol. 50, No. 3, 1993'''
MEEUS = '''Meeus, "Astronomical Algorithms", Willmann-Bell, 1991（太陽・月の位置の計算）'''
RAMAMOORTHI = '''Ramamoorthi, Hanrahan, "An Efficient Representation for Irradiance Environment Maps", SIGGRAPH 2001（球面調和関数による、環境光）'''
WRONSKI = '''Wronski, "Volumetric Fog: Unified Compute Shader Based Solution to Atmospheric Scattering", SIGGRAPH 2014, Advances in Real-Time Rendering in Games'''
HILLAIRE15 = '''Hillaire, "Physically Based and Unified Volumetric Rendering in Frostbite", SIGGRAPH 2015, Advances in Real-Time Rendering in Games'''
RTR = '''Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018'''
ONEIL = '''O'Neil, "Accurate Atmospheric Scattering", GPU Gems 2, Chapter 16, 2005'''
BEER = '''Beer, "Bestimmung der Absorption des rothen Lichts in farbigen Flüssigkeiten", Annalen der Physik, 1852'''

# ================================================================ atmosphere model
pg.Dedup("atmosphere/scattering/atmosphere-model.md")
pg.Add("atmosphere/scattering/atmosphere-model.md", '''
## 大気を、どうモデル化するか

空の色や、遠景の、霞を、物理的に、計算するには、**大気を、層状の、媒質**として、モデル化します。**惑星は、球**、**大気は、その周りの、薄い殻**です。

```text
         大気の上端（半径 6460 km）
       ╭──────────────────╮
      ╱  ╭────────────╮    ╲
     │  ╱   惑星        ╲    │       大気の厚さ ≈ 100 km（地球の半径の、約 1.6%）
     │ │  （半径 6360 km）│    │
      ╲  ╲              ╱    ╱
       ╰──╰────────────╯───╯
```

| 要素 | 値の例（地球） |
| --- | --- |
| 惑星の半径（地表） | 6,360 km |
| 大気の上端 | 6,460 km（地表から、100 km） |
| 地表の、反射率（アルベド） | 0.3 程度（草地・土・海の平均） |

大気の厚さは、**惑星の半径に比べて、非常に、薄い**ので、**地表付近**では、**平らな層**と、みなせますが、**地平線の近く**や、**宇宙から**見るときは、**球の曲率**が、重要になります。

## 3 つの、成分

大気は、**光を、散乱・吸収**する、**3 種類の、成分**で、できています。

| 成分 | 大きさ | 散乱の性質 | 層の厚さ（スケール ハイト） |
| --- | --- | --- | --- |
| **空気の分子**（レイリー） | 波長より、**はるかに小さい** | **波長の 4 乗に、反比例**。前後に、均等に、散る | 8 km（厚い） |
| **エアロゾル**（ミー） | 波長と、**同程度** | 波長に、ほぼ、**無関係**（白っぽい）。**前方に、強く散る** | 1.2 km（地表近く） |
| **オゾン** | 分子 | **散乱せず、吸収のみ**。**赤〜緑の、一部を、吸収** | 高度 25 km 付近に、集中（帯状） |

### レイリー散乱：空が、青い理由

レイリー散乱の、強さは、**波長の 4 乗に、反比例**します。**青い光**（波長が、短い）は、**赤い光**（波長が、長い）の、**約 5〜6 倍**、強く散ります。**太陽の光**が、大気を通る間に、**青が、あらゆる方向へ、散り**、**空全体が、青く**見えます。

```text
散乱の強さ ∝ 1 / λ⁴
   青（450 nm）: 1 / 450⁴ ≈ 2.4e-11
   赤（650 nm）: 1 / 650⁴ ≈ 5.6e-12      → 青は、赤の約 4.3 倍
```

### ミー散乱：霞と、白い空

エアロゾルは、**波長に、依存せず**、**白く**散ります。**地平線の近く**で、**空が、白っぽく**なるのは、**視線が、地表近くの、濃いエアロゾルの層を、長く通る**ためです。

### オゾン：空の、深い青

オゾンは、**吸収だけ**を、行います。**赤〜緑の光**を、**少し吸う**ので、**日没の、太陽の光が、長い距離を、通ったとき**、**空の、深い青**（天頂付近）が、保たれます。**オゾンを、無視**すると、**夕方の空が、緑がかり**ます。

## 係数の値

Hillaire（2020）の、実装が、使っている、地球の、大気の係数です（単位は、**1 / km**）。

| 成分 | 散乱係数 | 吸収係数 | RGB |
| --- | --- | --- | --- |
| レイリー | (0.005802, 0.013558, 0.0331) | 0 | 青が、最大 |
| ミー | 0.003996 | 0.00444 | 白（RGB 同じ） |
| オゾン | 0 | (0.00065, 0.001881, 0.000085) | 赤・緑を、吸う |

```hlsl
// 係数の定義。単位は、1 / km。メートル単位で、計算するなら、1000 で割る。
static const float3 kRayleighScattering = float3(0.005802, 0.013558, 0.0331);
static const float kMieScattering = 0.003996;
static const float kMieAbsorption = 0.00444;
static const float3 kOzoneAbsorption = float3(0.00065, 0.001881, 0.000085);
```

レイリーの、`(0.0058, 0.0136, 0.0331)` は、**赤:緑:青 ≈ 1 : 2.3 : 5.7** で、**青が、約 6 倍**です。この、**比**が、空の、青さの、源です。

## 密度の、分布

各成分の、密度は、**高度の、関数**です。

```hlsl
// 高度 h（km）での、各成分の、密度（地表で 1）。
float RayleighDensity(float h_km) { return exp(-h_km / 8.0); }
float MieDensity(float h_km) { return exp(-h_km / 1.2); }
// オゾンは、高度 25 km を中心とした、三角形の分布（15 km 〜 35 km の、層）。
float OzoneDensity(float h_km) {
  return (h_km < 25.0) ? saturate(h_km / 15.0 - 2.0 / 3.0) : saturate(-h_km / 15.0 + 8.0 / 3.0);
}
```

**レイリーと、ミー**は、**指数関数**で、**高度とともに、薄く**なります。**オゾン**は、**特定の高度の、層**（25 km 付近）に、**集中**するので、**三角形の、関数**で、近似します。

## 消散係数の、合計

ある点での、**光を、失う割合**（消散係数）は、**各成分の、散乱と吸収の、合計**です。

```hlsl
// 点での、消散係数 σ_t（RGB）。散乱 + 吸収の、全成分。
float3 ExtinctionAt(float h_km) {
  float3 rayleigh = kRayleighScattering * RayleighDensity(h_km);
  float mie = (kMieScattering + kMieAbsorption) * MieDensity(h_km);
  float3 ozone = kOzoneAbsorption * OzoneDensity(h_km);
  return rayleigh + mie + ozone;
}
```

**散乱だけ**が、**視線の方向へ、光を足す**（**空の色**を、作る）のに、**使われる**一方、**消散**（散乱 + 吸収）は、**透過率**（光が、失われる量）に、使われます（[Transmittance](transmittance.md)）。

## 大気の、パラメーターを、変える

係数を、変えると、**別の惑星**や、**天候**を、表現できます。

| 変更 | 効果 |
| --- | --- |
| **ミー散乱を、増やす** | **霞んだ空**（スモッグ、湿気）。地平線が、白い |
| **ミー散乱を、減らす** | **澄んだ空**（高山、乾燥）。青が、濃く、遠くまで見える |
| **レイリーの、スケール ハイトを、変える** | 大気の、厚さの感じ |
| **オゾンを、ゼロに** | 夕方の空が、緑がかる |
| **惑星の半径を、変える** | 地平線の、見え方。**小さい惑星**は、地平線が、近く、曲がって見える |

火星の空（赤い塵が、多い）は、**ミー散乱が、強く**、**赤い**エアロゾルを、持つ、モデルで、表現できます。

''', before="## よくあるミス")
pg.Refs("atmosphere/scattering/atmosphere-model.md", [HILLAIRE, BRUNETON, BRUNETON17, NISHITA, ONEIL])

# ================================================================ hillaire
pg.Dedup("atmosphere/scattering/hillaire.md")
pg.Add("atmosphere/scattering/hillaire.md", '''
## 4 つの LUT の、役割分担

Hillaire（2020）の方式は、**空の、計算を、4 つの、小さな LUT に、分けて**、**毎フレーム、更新**します。**すべてが、リアルタイム**で、動くので、**時間帯の、変化、天候の、変化**に、即座に、追従できます。

| LUT | 大きさ | 軸 | 内容 | 更新 |
| --- | --- | --- | --- | --- |
| **透過率 LUT** | 256×64 | 高度、天頂角 | 大気の、上端までの、透過率 | 大気の、係数が、変わったときのみ |
| **多重散乱 LUT** | 32×32 | 高度、太陽の天頂角 | 多重散乱の、光（等方） | 大気の、係数、または、太陽の位置が、変わったとき |
| **Sky-View LUT** | 192×108 | 緯度・経度（空の、方向） | **カメラの位置から見た、空の色**（全方向） | 毎フレーム |
| **Aerial Perspective LUT** | 32×32×32 | 画面 xy、距離 | **カメラ前方の、各点までの、散乱光と、透過率** | 毎フレーム |

**重い計算を、小さな LUT に、集約**し、**画面の、全画素**では、**LUT を、読むだけ**にする、という、設計です。

```text
 [透過率 LUT] ─┬─→ [多重散乱 LUT] ─┬─→ [Sky-View LUT] ───→ 空の、各画素は、LUT を引くだけ
              │                    └─→ [Aerial Perspective LUT] ──→ 物体の、各画素は、LUT を引くだけ
              └─ 太陽の透過率に、使う（Sky-View、Aerial Perspective でも）
```

## 1：透過率 LUT

**高度と、天頂角**から、**大気の上端までの、透過率**を、事前に、計算します（詳細は、[Transmittance](transmittance.md)）。**太陽の光が、各点に、届く割合**を、**1 回の、テクスチャ読み込み**で、得るための、基礎です。

**更新の、頻度**は、**低く**（大気の係数が、変わらない限り、**1 回**で、済む）。

## 2：多重散乱 LUT

**高度と、太陽の、天頂角**から、**多重散乱の、光の量**を、事前に、計算します（詳細は、[Multiple Scattering](multiple-scattering.md)）。**32×32 の小さな、LUT** で、**透過率 LUT** を、使って、**各点で、64 方向**を、積分します。

## 3：Sky-View LUT

**カメラの位置**から見た、**空の、全方向の色**を、**1 枚の、小さな画像**に、描きます。**空は、ゆるやかに、変化する**ので、**192×108** という、**小さな解像度**で、十分です。

### 空の、方向を、画像に、割り当てる

**方向**（視線の向き）を、**画像の、座標**に、**割り当て**ます。**地平線の、近く**は、**色が、急に変わる**ので、**非線形**な、割り当てで、地平線の近くを、細かく取ります。

```hlsl
// Sky-View LUT の uv から、視線の方向（緯度 = 地平線からの角度、経度 = 太陽との、方位角の差）を求める。
void UvToSkyViewParams(float2 uv, float view_height, out float view_zenith_cos, out float light_view_cos) {
  // 地平線までの、角度。地平線の、すぐ上と、すぐ下を、細かく取る。
  float v_horizon = sqrt(view_height * view_height - g_bottom_radius * g_bottom_radius) / view_height;
  float beta = asin(g_bottom_radius / view_height);                    // 地平線の、俯角
  float zenith_horizon_angle = 3.14159265 - beta;                      // 天頂角の、地平線の値
```

まず、**カメラの高度**から、**地平線の、天頂角**（**地平線が、どこに、見えるか**）を、求めます。カメラが、**高い**ほど、**地平線は、下がり**（天頂角が、大きく）ます。

```hlsl
  float coord;
  if (uv.y < 0.5) {
    // 上半分: 地平線より、上（空）。地平線に近いほど、細かい（二乗で、詰める）
    coord = 1.0 - 2.0 * uv.y;
    coord *= coord;
    view_zenith_cos = cos(zenith_horizon_angle * (1.0 - coord) ...);
  } else {
    // 下半分: 地平線より、下（地面の方向）。同様に、地平線の近くを、細かく
    coord = uv.y * 2.0 - 1.0;
    coord *= coord;
    // ...
  }
```

**画像の、上下**で、**地平線の、上と下**を、分け、**それぞれ、地平線に向かって、`coord²`** で、**サンプルを、詰めます**。**地平線の近く**は、**色の変化が、急**（空と、地面、霞）なので、**ここに、解像度を、集める**のが、肝心です。

```hlsl
  // 横方向は、太陽との方位角の差（0 〜 π）。二乗で、詰める。
  float light_view_angle_cos = ...;      // 太陽と、視線の、水平方向での、角度の cos
  light_view_cos = light_view_angle_cos;
}
```

**横軸**は、**太陽との、方位角の差**にします。**太陽の、すぐ近く**（**ミー散乱が、強い、明るい輪**）を、**細かく**、取るためです。

```hlsl
// Sky-View LUT を描く: 各画素について、視線の方向に、1 回散乱 + 多重散乱を、積分する。
float4 SkyViewPS(float2 uv : TEXCOORD0) : SV_Target {
  float view_height = length(g_camera_position_from_planet_center);
  float view_zenith_cos, light_view_cos;
  UvToSkyViewParams(uv, view_height, view_zenith_cos, light_view_cos);

  float3 ray_dir = ...;                         // 求めた角度から、視線の向きを、復元
  float3 sun_dir = ...;
  float3 L = IntegrateScatteredLuminance(float3(0, view_height, 0), ray_dir, sun_dir, /*steps*/ 30);
  return float4(L, 1.0);
}
```

**積分は、1 回散乱の、ループ**（[Single-Scattering Integral](single-scattering.md)）に、**多重散乱 LUT**（[Multiple Scattering](multiple-scattering.md)）を、足した、ものです。**LUT の画素数が、少ない**（192×108 = 約 2 万）ので、**積分の、ステップ数を、多く**（30〜）しても、**軽い**です。

### 空を描く

**画面の、各画素**は、**視線の方向**から、**LUT の uv** を、求めて、**1 回読むだけ**です。

```hlsl
float3 SampleSkyView(float3 view_dir) {
  float2 uv = SkyViewDirToUv(view_dir);       // 先ほどの、割り当ての、逆変換
  return g_sky_view_lut.SampleLevel(g_linear_clamp, uv, 0).rgb;
}
```

**画面全体の、空が、テクスチャ 1 回の読み込み**になるので、**非常に、安い**です。

## 4：Aerial Perspective LUT

**空気遠近法**（遠くの物が、霞んで、青みを帯びる）を、**物体に**、適用するための、LUT です。**カメラの、前方の、空間**を、**32×32×32 の、3D テクスチャ**に、**分割**し（**froxel** と、同じ発想）、**各セルに、カメラから、そのセルまでの、散乱光と、透過率**を、**保存**します。

| 軸 | 内容 |
| --- | --- |
| x、y | **画面上の、位置**（カメラから見た、方向） |
| z | **カメラからの距離**（0 〜 32 km、**非線形**に分割、近くを細かく） |
| RGB | **カメラから、そのセルまでの、散乱光**（空気が、足す色） |
| A | **透過率**（カメラから、そのセルまでの、平均的な透過率） |

```hlsl
// Aerial Perspective LUT を、1 スライス（距離）ずつ、描く。各スライスは、カメラから、その距離までを、積分する。
float4 AerialPerspectivePS(float2 uv, uint slice) {
  float distance_m = SliceToDistance(slice);                         // スライス → 距離（近くを、細かく）
  float3 ray_dir = ScreenToViewDir(uv);
  float3 scattered; float3 transmittance;
  IntegrateScatteredLuminance(g_camera_position, ray_dir, g_sun_dir, distance_m, scattered, transmittance);
  float mean_t = dot(transmittance, float3(1, 1, 1)) / 3.0;           // 透過率の RGB の、平均
  return float4(scattered, 1.0 - mean_t);
}
```

### 物体に、適用する

物体を、描くとき、**その画素の、深度**から、**カメラまでの距離**を、求め、**LUT の、対応するセル**を、**読んで**、**散乱光を足し**、**透過率を掛けます**。

```hlsl
// 物体の色に、空気遠近法を、適用する（ピクセル シェーダーの、最後）。
float3 ApplyAerialPerspective(float3 scene_color, float2 screen_uv, float distance_m) {
  float slice = DistanceToSlice(distance_m);                          // 距離 → スライス（連続値）
  float4 ap = g_aerial_perspective_lut.SampleLevel(g_linear_clamp, float3(screen_uv, slice), 0);
  float3 inscatter = ap.rgb;                                          // 空気が、足す光
  float transmittance = 1.0 - ap.a;                                   // 物体の光が、届く割合
  return scene_color * transmittance + inscatter;
}
```

この、**1 行**で、**どんな物体にも、空気遠近法**が、かかります。**物体ごとに、大気の積分を、行う必要が、ありません**。**距離に応じた、霞と、青み**が、物理的な、**正しい値**で、**自然に、付きます**。

## 全体の、更新の、流れ

```text
起動時 / 大気の係数が、変わったとき:
  ① 透過率 LUT を、計算
  ② 多重散乱 LUT を、計算（①を使う）

毎フレーム:
  ③ Sky-View LUT を、計算（①②を使う）
  ④ Aerial Perspective LUT を、計算（①②を使う）
  ⑤ 空を描く（③を引く）
  ⑥ 各物体の、描画で、空気遠近法を、適用（④を引く）
```

| LUT | コスト（目安） |
| --- | --- |
| 透過率 | 起動時のみ（0.1 ms 未満） |
| 多重散乱 | 太陽が動くたび（0.05 ms 程度） |
| Sky-View | 毎フレーム 0.05〜0.1 ms |
| Aerial Perspective | 毎フレーム 0.1〜0.2 ms |

**合計で、毎フレーム、0.3 ms 未満**と、**非常に軽く**、**時間帯の、変化**にも、**リアルタイムに、追従**できます。

## 宇宙から、地上まで

この方式は、**カメラが、地上でも、空の高いところでも、宇宙でも**、**同じ仕組みで**、動きます。**カメラの高度**が、LUT の、**入力**になっているためです（Sky-View LUT の、地平線の計算が、高度から決まる）。**宇宙から、惑星を見る**とき（**大気の、青い縁**）には、**Sky-View LUT は、使わず**、**画面全体を、直接、積分**する、専用のパスを使います（[Ground and Space Views](ground-space.md)）。

''', before="## よくあるミス")
pg.Refs("atmosphere/scattering/hillaire.md", [HILLAIRE, BRUNETON, HILLAIRE15, RTR])

pg.Dedup("atmosphere/scattering/bruneton.md")
pg.Add("atmosphere/scattering/bruneton.md", '''
## 考え方：散乱を、丸ごと、事前計算する

Bruneton と Neyret（2008）の、方式は、**大気の、散乱の積分を、すべて、事前に、計算して、テクスチャに、保存**します。**実行時**は、**テクスチャを、引くだけ**です。**多重散乱**も、**事前計算の中で、正確に**、**反復して**、含められます。

| | Bruneton（2008） | Hillaire（2020） |
| --- | --- | --- |
| 事前計算 | **非常に大きい**（散乱の、4 次元のテクスチャ。数秒〜数十秒） | 小さい（透過率と、多重散乱の LUT のみ） |
| 実行時 | テクスチャを、引く（**安い**） | LUT を、毎フレーム、更新（**安いが、計算がある**） |
| 多重散乱 | **正確**（反復計算） | **近似**（等方性の仮定） |
| 大気の、変更 | 事前計算を、やり直し（**重い**）。**動的な、天候に、不向き** | **リアルタイムに、対応** |
| 太陽の、位置 | **テクスチャの軸**として、持つ（変化に、対応） | LUT に、太陽の角度を、軸として、持つ |
| 精度 | **高い**（参照用に、使える） | 十分（見た目を、重視） |

## 散乱テクスチャ

Bruneton の、方式の、核心は、**大気の、散乱を、4 つの変数**の、関数として、**テクスチャに、保存**することです。

```text
S(r, μ, μ_s, ν)        r: 高度、μ: 視線の天頂角の cos、μ_s: 太陽の天頂角の cos、ν: 視線と太陽の、間の角度の cos
```

| 変数 | 意味 |
| --- | --- |
| `r` | カメラの、**高度**（惑星の中心からの、距離） |
| `μ` | **視線の、天頂角の cos** |
| `μ_s` | **太陽の、天頂角の cos** |
| `ν` | **視線と、太陽の間の、角度の cos**（位相関数が、これに、依存する） |

**4 次元**は、**3D テクスチャ**に、**詰めて**保存します（例：**256×128×32** の 3D テクスチャを、`ν` の分割数だけ、横に並べる）。**実行時**は、**4 つの変数から**、**テクスチャ座標**を、求め、**4 次元の、線形補間**（**3D テクスチャの、2 回の読み込みを、補間**）で、**散乱を、読み取ります**。

```hlsl
// 4 変数 (r, mu, mu_s, nu) から、3D テクスチャの、座標を求め、2 回読んで、nu 方向に、補間する。
float3 GetScattering(float r, float mu, float mu_s, float nu) {
  float4 uvwz = GetScatteringTextureUvwzFromRMuMuSNu(r, mu, mu_s, nu);   // 参照実装の関数
  float tex_coord_x = uvwz.x * (kNuSize - 1);
  float tex_x = floor(tex_coord_x);
  float lerp_factor = tex_coord_x - tex_x;
  float3 uvw0 = float3((tex_x + uvwz.y) / kNuSize, uvwz.z, uvwz.w);
  float3 uvw1 = float3((tex_x + 1.0 + uvwz.y) / kNuSize, uvwz.z, uvwz.w);
  return g_scattering.SampleLevel(g_linear_clamp, uvw0, 0).rgb * (1.0 - lerp_factor)
       + g_scattering.SampleLevel(g_linear_clamp, uvw1, 0).rgb * lerp_factor;
}
```

`GetScatteringTextureUvwzFromRMuMuSNu` は、**非線形な、座標の、割り当て**です。**地平線の近く**を、**細かく**取るための、**参照実装**（Bruneton の、公開コード）が、**詳しい**式を、持っています。**自分で、導出せず**、**参照実装を、移植**するのが、現実的です。

## 事前計算の、流れ

多重散乱を、**正確に**、計算するために、**散乱の、次数を、反復**して、足します。

```text
① 透過率テクスチャ T を、計算
② 直接の、地面の、照度（irradiance）を、計算
③ 1 回散乱 S₁ を、計算（レイリーと、ミーを、別々のテクスチャに）
④ 次数 k = 2, 3, 4 について:
     (a) 「前の次数の、散乱光」から、各点の、**入射光の分布**を、計算
     (b) その入射光が、散乱する、**次の次数の、散乱** S_k を、計算
     (c) S_k を、合計 S に、足す
⑤ 完成した、S を、保存
```

**3〜4 次**まで、反復すれば、**ほぼ、収束**します（それ以降の、寄与は、小さい）。**各次数**で、**計算シェーダー（またはピクセル シェーダー）**を、数回、実行します。

## 実行時の、使い方

```hlsl
// 空の色: 視線の方向から、(r, mu, mu_s, nu) を求め、散乱テクスチャを引くだけ。
float3 SkyRadiance(float3 camera, float3 view_ray, float3 sun_dir) {
  float r = length(camera);
  float rmu = dot(camera, view_ray);
  float mu = rmu / r;
  float mu_s = dot(camera, sun_dir) / r;
  float nu = dot(view_ray, sun_dir);
  float3 rayleigh_scattering = GetScattering(r, mu, mu_s, nu);          // レイリー + 多重散乱
  float3 mie_scattering = GetMieScattering(r, mu, mu_s, nu);            // ミー（別テクスチャ）
  return rayleigh_scattering * RayleighPhase(nu) + mie_scattering * MiePhase(nu, kMieG);
}
```

**レイリーと、ミーを、別々**に、保存する理由は、**位相関数**が、違うためです。**実行時に、位相関数を、掛けて、足す**ことで、**ミー散乱の、`g` を、変えたり**、**位相関数を、差し替え**られます。

## 長所と短所

| | 内容 |
| --- | --- |
| 長所 | **実行時のコストが、非常に、小さい**（テクスチャの、読み込みのみ） |
| 長所 | **多重散乱が、正確** |
| 長所 | **参照実装が、公開**されている（検証に、使える） |
| 短所 | **事前計算が、重い**（大気の係数を、変えるたびに、やり直し）。**動的な、天候**（霞の濃さ、時々刻々）に、**不向き** |
| 短所 | **メモリ**（4 次元のテクスチャ）が、大きい（数十 MB） |
| 短所 | **実装が、複雑**（非線形な、座標の割り当て、反復計算） |
| 短所 | **雲、地形の影、volumetric な、効果**との、**組み合わせが、難しい**（空間的に、均一な大気を、前提） |

## 使いどころ

| 場面 | 判断 |
| --- | --- |
| **大気の、条件が、固定**（地球の、標準的な空）、**正確さを、重視** | Bruneton |
| **動的な、天候**（霞、湿度の、変化）、**カメラの、高度が、大きく変わる**（地上から宇宙） | **Hillaire**（[Hillaire 2020: Four LUTs](hillaire.md)） |
| 参照（正解）として、**自分の実装を、検証**したい | Bruneton の、**参照実装** |

''', before="## よくあるミス")
pg.Refs("atmosphere/scattering/bruneton.md", [BRUNETON, BRUNETON17, HILLAIRE, NISHITA])

pg.Dedup("atmosphere/scattering/ground-space.md")
pg.Add("atmosphere/scattering/ground-space.md", '''
## カメラの、高さで、見え方が、変わる

大気の、見え方は、**カメラが、どこにあるか**で、**まったく**違います。

| カメラの位置 | 見え方 | 空の描き方 |
| --- | --- | --- |
| **地上**（高度 0〜数 km） | 空は、**頭の上に、広がる**。地平線は、**ほぼ、水平** | **Sky-View LUT**（[Hillaire 2020: Four LUTs](hillaire.md)） |
| **高い山、飛行機**（高度 10 km 前後） | 地平線が、**少し下がり**、**わずかに、曲がって**見える | **Sky-View LUT**（高度が、LUT の、入力） |
| **宇宙**（高度 100 km 以上） | **惑星が、球として、見える**。**大気は、青い、薄い縁** | **画面全体を、直接、積分**（レイマーチ） |

## 地上から：Sky-View LUT

**カメラが、大気の中**にあるなら、**空は、カメラの周りの、全方向**に、広がります。**Sky-View LUT** に、**全方向の色**を、描いて、画面では、**LUT を、引くだけ**です。**空は、ゆるやかに変化する**ので、**低解像度**で、十分です。

## 宇宙から：球体を、レイマーチ

**カメラが、大気の外**にあるとき、**画面の、ほとんどは、宇宙**（黒）で、**惑星の、円盤**が、見えます。**大気は、惑星の、縁に、青く、細く**見えます。この場合、**Sky-View LUT**（カメラの周りの、全方向）は、**不適切**です。**画面の、各画素**から、**視線を、大気に向けて**、**直接**、積分します。

```hlsl
// 宇宙から見る: 画素ごとに、視線が、大気の球と、どう交わるかを、調べて、積分する。
float4 SpaceViewPS(float2 uv : TEXCOORD0) : SV_Target {
  float3 ray_dir = ScreenToViewDir(uv);
  float3 origin = g_camera_position_from_planet_center;

  // 視線と、大気の上端の球との、交点
  float2 t_top = RaySphere(origin, ray_dir, g_top_radius);
  if (t_top.y < 0.0) return float4(0, 0, 0, 0);                        // 大気に、当たらない（宇宙が、見える）
```

視線が、**大気の球と、交わらない**なら、**何も描きません**（星空や、背景が、見える）。

```hlsl
  float t_enter = max(t_top.x, 0.0);                                   // 大気に、入る距離（カメラが、すでに中なら 0）

  // 視線が、地面（惑星の本体）に、当たるなら、そこまで。当たらなければ、大気を、突き抜ける。
  float2 t_ground = RaySphere(origin, ray_dir, g_bottom_radius);
  float t_exit = (t_ground.x > 0.0) ? t_ground.x : t_top.y;

  float3 start = origin + ray_dir * t_enter;
  float ray_length = t_exit - t_enter;
  float3 L = IntegrateScatteredLuminance(start, ray_dir, g_sun_dir, ray_length, /*steps*/ 32);
```

**視線が、大気の中を、通る区間**（入口から、出口、または地面まで）だけを、積分します。

```hlsl
  // 視線が、地面に当たる → 惑星の、表面の色を、大気越しに、足す。
  if (t_ground.x > 0.0) {
    float3 hit_pos = origin + ray_dir * t_ground.x;
    float3 ground_albedo = SampleGroundAlbedo(hit_pos);
    float3 ground_lit = ground_albedo * SunTransmittance(hit_pos, g_sun_dir) * g_sun_illuminance * saturate(dot(normalize(hit_pos), g_sun_dir)) / 3.14159265;
    float3 view_t = Transmittance(start, ray_dir, ray_length);
    L += ground_lit * view_t;                                          // 地面の色が、大気を通って、届く
  }
  return float4(L, 1.0);
}
```

**惑星の、表面**（**地面、海、雲**）の、**色**を、**大気を通した**、**透過率**を、掛けて、**足し**ます。**昼側**では、**青い、大気を、通して**、**地面や海が、見え**、**夜側**は、**暗く**なります。

## 地面の、色

宇宙から、**惑星を、見る**とき、**地面の、色**が、必要です。

| 方法 | 内容 |
| --- | --- |
| **単色**（アルベド） | 簡単。**地球なら、青緑〜茶色**の、平均 |
| **テクスチャ**（惑星全体の、地図） | **大陸、海、雪、砂漠**を、**描く**。球面への、マッピング（キューブマップ） |
| **昼夜**で、変える | **夜側**に、**街の、光**（夜景テクスチャ）を、足す |

## 地上から、宇宙への、**連続的な、遷移**

**ゲームで、地上から、宇宙へ、上昇する**とき、**高度に応じて、2 つの、方式を、切り替え**ます。**切り替えの、境目**が、**目立たない**ように、**なめらかな、遷移**が、必要です。

| 高度 | 方式 |
| --- | --- |
| 〜50 km | **Sky-View LUT**（空は、頭上全体に、広がる） |
| 50〜150 km | **両方を、ブレンド**（空が、薄くなり、地平線が、曲がって、見え始める） |
| 150 km〜 | **宇宙ビュー**（画面全体を、直接、積分） |

**Sky-View LUT は、高度が、高くなる**と、**地平線が、画像の、下へ寄る**（地平線の角度が、大きくなる）ので、**連続的に、動きます**。**宇宙ビュー**との、**境目**では、**同じ値**になるはずですが、**LUT の、解像度**による、**わずかな差**が、あります。**ブレンド**で、目立たなくします。

## 大気の縁（リム）

宇宙から、惑星を見ると、**縁に、青い、細い、帯**が、見えます。**大気を、横から**（**接線方向**に）**通る視線**が、**長い距離**を、通り、**散乱が、積もる**ためです。

```text
 宇宙から、惑星の縁を、見る:
       視線 ─────────→   （大気を、長く、通る）
            ╲
        ╭─────╲─────╮
        │ 大気 ╲    │   ← 縁の青い帯（散乱光が、積もる）
        │  惑星     │
```

**視線が、大気を、通る長さ**が、**中心**（真正面から、見る）より、**縁**で、**非常に、長い**ので、**縁が、明るく、青い、リング**になります。**積分で、自然に、出る**ので、**特別な、処理は、不要**です。

''', before="## よくあるミス")
pg.Refs("atmosphere/scattering/ground-space.md", [HILLAIRE, BRUNETON, NISHITA, RTR])

# ================================================================ sky models
pg.Dedup("atmosphere/sky-models/index.md")
pg.Add("atmosphere/sky-models/index.md", '''
## 空を、描く、方法の、選択肢

空の色を、決める方法は、**単純な、グラデーション**から、**物理ベースの、大気散乱**まで、**幅**があります。

| 方式 | 内容 | 品質 | コスト | 向く場面 |
| --- | --- | --- | --- | --- |
| **グラデーション** | **天頂の色 → 地平線の色**を、補間する | 低 | 最小 | モバイル、ローポリ、スタイライズ |
| **解析的な、空の、モデル**（Preetham、Hošek-Wilkie） | **太陽の高さと、濁り**から、**空の色を、式で計算** | 中〜高 | 小 | 昼の空だけ。リアルな、昼空 |
| **事前計算の、大気散乱**（Bruneton） | 散乱を、**事前に、テクスチャへ** | 高 | 小（実行時） | 固定の大気 |
| **リアルタイムの、大気散乱**（Hillaire） | **4 つの小さな、LUT** を、毎フレーム、更新 | 高 | 小 | **時間帯の、変化**、**宇宙から地上まで** |
| **キューブマップ**（HDRI） | **撮影・作成した、空の画像**を、そのまま貼る | **最高**（実写なら） | 最小 | **固定の、空**。時間帯の変化は、**複数枚の、補間** |

## 選び方

| 状況 | おすすめ |
| --- | --- |
| まず、**空を、出したい** | グラデーション（[Gradient Sky](gradient.md)） |
| **昼の、リアルな空**（時間帯は、あまり、変えない） | 解析的モデル（[Analytic Sky Models](analytic.md)） |
| **時間帯が、変わる**（朝、昼、夕、夜）、**天候** | **Hillaire**（[Hillaire 2020: Four LUTs](../scattering/hillaire.md)） |
| **スタイライズ**（アニメ調の空） | グラデーション + ノイズの雲 + **太陽・月の、絵** |

## 空の、構成要素

空は、**1 つの、色**では、ありません。**複数の層**を、重ねます。

```text
奥     星空（夜）
 │     月、太陽の円盤（[Sun, Moon and Stars](celestial.md)）
 │     大気の散乱（空の青さ、夕焼け）
 │     雲（[Clouds](../clouds/index.md)）
手前   遠景（山）、空気遠近法（[Aerial Perspective and Fog](../aerial-fog/index.md)）
```

| 層 | 内容 | ページ |
| --- | --- | --- |
| 大気の散乱（空の色） | 空の背景の色 | このカテゴリ |
| 太陽・月・星 | 空に、**浮かぶ**天体 | [Sun, Moon and Stars](celestial.md) |
| 雲 | **空の中の、立体物** | [Clouds](../clouds/index.md) |
| 空気遠近法 | **地上の遠景の、霞** | [Aerial Perspective and Fog](../aerial-fog/index.md) |

## 空の、もう 1 つの、役割：ライティング

空は、**見た目**だけでなく、**光源**でもあります。**空全体が、シーンを、照らす**（環境光）ので、**空の色が、地面や物の色に、影響**します（[Using the Sky for Lighting](sky-lighting.md)）。**空の色を、変えたら、環境光も、変える**必要があります。

''', before="## よくあるミス")
pg.Refs("atmosphere/sky-models/index.md", [HILLAIRE, BRUNETON, PREETHAM, HOSEK, RTR])

pg.Dedup("atmosphere/sky-models/gradient.md")
pg.Add("atmosphere/sky-models/gradient.md", '''
## 最も、単純な、空

**グラデーション スカイ**は、**天頂の色**から**地平線の色**へ、**補間する**だけの、空です。**物理計算は、ありません**。**非常に、軽く**、**自由に、色を、決められる**ので、**スタイライズされた、ゲーム**や、**モバイル**で、よく使われます。

## 実装

視線の、**高さ**（上向きか、水平か）に、応じて、**天頂の色と、地平線の色を、混ぜます**。

```hlsl
// 視線の向き（正規化）から、空の色を求める。
float3 GradientSky(float3 view_dir) {
  float t = saturate(view_dir.y);                       // 0 = 水平、1 = 真上
```

`view_dir.y` は、**視線が、どれだけ上を、向いているか**（−1〜1）です。**地平線より、下**（負）は、**0 に、切り**ます（`saturate`）。

```hlsl
  // 地平線に近いところで、急に色が変わるように、べき乗で曲げる。
  t = pow(t, 0.5);
  return lerp(g_horizon_color, g_zenith_color, t);
}
```

**べき乗**（`pow(t, 0.5)` = 平方根）で、**地平線の近くを、広く**取ります。そうしないと、**地平線の色が、狭い帯**に、押し込まれ、**不自然**に見えます。**現実の空**でも、**地平線の、明るい帯は、幅が広い**です。

```hlsl
// 地面の方向（view_dir.y < 0）は、別の色で。
float3 sky = GradientSky(view_dir);
float3 ground = g_ground_color;
float3 color = (view_dir.y >= 0.0) ? sky : lerp(g_horizon_color, ground, saturate(-view_dir.y * 4.0));
```

**水平線より下**は、**地面の色**へ、移ります。**地面が、描かれていない**（水平線の、下が見える）なら、**ここで、補う**必要があります。

## 3 色以上の、グラデーション

**2 色だけ**では、**夕焼けの、複雑な色**を、表せません。**複数の色を、高さの、段階**で、**補間**します。

```hlsl
// 4 つの色（地平線の下、地平線、中間、天頂）を、高さで、区分線形に、補間する。
float3 MultiGradientSky(float y) {                      // y: −1（真下）〜 1（真上）
  float3 colors[4] = { g_below_horizon, g_horizon, g_mid, g_zenith };
  float stops[4] = { -0.1, 0.0, 0.3, 1.0 };
  for (int i = 0; i < 3; ++i) {
    if (y < stops[i + 1]) {
      float t = saturate((y - stops[i]) / (stops[i + 1] - stops[i]));
      return lerp(colors[i], colors[i + 1], t);
    }
  }
  return colors[3];
}
```

**色と、境目の高さ**を、**配列**に、並べ、**該当する、区間**を、探して、**その区間の、2 色を、補間**します。**色の数を、増やす**ほど、**自由な、グラデーション**が、描けます。**グラデーションを、1 次元の、テクスチャに、描いて**、**`SampleLevel` で、引く**方法も、あります（**アーティストが、画像で、編集できる**）。

## 太陽の方向への、変化

空は、**太陽の、近くが、明るく**、**反対側が、暗い**ので、**太陽の方向**を、反映すると、**ぐっと、それらしく**なります。

```hlsl
// 太陽の方向に近いほど、地平線の色を、太陽の色の方へ、寄せる。
float sun_amount = saturate(dot(view_dir, g_sun_dir));
float3 horizon = lerp(g_horizon_color, g_sun_glow_color, pow(sun_amount, 8.0));
```

`dot(view_dir, g_sun_dir)` は、**視線と、太陽の、近さ**です。**べき乗で、太陽の近くだけ**に、絞ります（`pow(…, 8.0)`）。これで、**太陽の周りの、ぼんやりした、明るさ**（**グロー**）が、出ます。

## 時間帯で、色を、変える

**1 日の、時間**に応じて、**色を、補間**します。**朝、昼、夕方、夜**の、**色のセット**（**天頂、地平線、太陽のグロー**）を、**用意**して、**時間で、混ぜます**。

```cpp
// 時間帯のキーフレーム（時刻、天頂の色、地平線の色）。
struct SkyKey { float time; float3 zenith; float3 horizon; };
std::vector<SkyKey> keys = {
    {0.0f,  {0.01f, 0.01f, 0.05f}, {0.02f, 0.02f, 0.08f}},     // 深夜
    {6.0f,  {0.20f, 0.30f, 0.60f}, {0.90f, 0.50f, 0.30f}},     // 朝焼け
    {12.0f, {0.10f, 0.30f, 0.80f}, {0.60f, 0.75f, 0.90f}},     // 昼
    {18.0f, {0.20f, 0.25f, 0.50f}, {1.00f, 0.40f, 0.20f}},     // 夕焼け
    {24.0f, {0.01f, 0.01f, 0.05f}, {0.02f, 0.02f, 0.08f}},     // 深夜（0 時と同じ）
};
// 現在の時刻が、どの 2 つの、キーの間にあるかを探し、線形補間する（時間帯の補間）。
```

**時刻**を、キーフレームの、**間で、補間**すると、**なめらかに、色が、変わる**空が、できます。**キーフレームを、アーティストが、編集**できる、データにしておくと、**調整が、楽**です（[Day-Night Cycle](day-night.md)）。

## 長所と短所

| | 内容 |
| --- | --- |
| 長所 | **最も、軽い**（数命令）。**アーティストが、完全に、制御**できる。**スタイライズ**に、最適 |
| 短所 | **物理的に、正しくない**。**夕焼けの、太陽の周りの、複雑な色**、**地平線の、霞**が、出ない |
| 短所 | **太陽の高さ**に応じた、色の、変化を、**手で**、設計する必要 |
| 短所 | **空気遠近法**（遠景の霞）と、**色が、合わない**ことがある（空の色と、霧の色を、合わせる。[Matching Fog Color to the Sky](../aerial-fog/color-match.md)） |

''', before="## よくあるミス")
pg.Refs("atmosphere/sky-models/gradient.md", [PREETHAM, HILLAIRE, RTR])

pg.Dedup("atmosphere/sky-models/analytic.md")
pg.Add("atmosphere/sky-models/analytic.md", '''
## 解析的な、空の、モデル

**解析的な、モデル**は、**観測や、シミュレーション**の、結果に、**数式を、当てはめた**ものです。**太陽の高さ**と、**大気の濁り（turbidity）**を、入れると、**空の、各方向の色**が、**式 1 つ**で、返ります。**積分も、LUT も、不要**です。

| モデル | 特徴 |
| --- | --- |
| **Perez の式**（1993） | 空の、**輝度の、分布**を、**5 つの係数**で、表す、古典的な式。**後続の、モデルの、土台** |
| **Preetham**（1999） | Perez の式の、**係数を、濁りの関数**として、決めた。**簡単で、広く使われた**。**昼の、空だけ**（太陽が、地平線より、上） |
| **Hošek–Wilkie**（2012） | Preetham より、**精度が、高く**、**太陽が、低いとき**（朝夕）も、**うまく動く**。**スペクトル全体**で、フィット |

## Perez の式

空の、**ある方向の、輝度**を、**天頂の輝度に、対する、割合**として、表します。

```text
F(θ, γ) = (1 + A × exp(B / cosθ)) × (1 + C × exp(D × γ) + E × cos²γ)

θ: 視線の、天頂角
γ: 視線と、太陽の、間の角度
A, B, C, D, E: 係数（天候・濁りで、決まる）
```

| 項 | 意味 |
| --- | --- |
| `(1 + A × exp(B / cosθ))` | **地平線に、近づくほど、明るく**（霞）。`A`、`B` が、**地平線の明るさ**を、決める |
| `(1 + C × exp(D × γ) + E × cos²γ)` | **太陽の周りが、明るい**（`C`、`D`）。**太陽と反対側の、わずかな、明るさ**（`E`） |

```hlsl
// Perez の式（天頂に対する、割合）。coefficients は、A..E の 5 つ。
float PerezFunction(float cos_theta, float gamma, float cos_gamma, float A, float B, float C, float D, float E) {
  return (1.0 + A * exp(B / max(cos_theta, 0.01))) * (1.0 + C * exp(D * gamma) + E * cos_gamma * cos_gamma);
}
```

`cos_theta` が、**0 に近い**（地平線）と、`B / cosθ` が、**大きな、値**になり、`exp` が、**暴走**するので、**下限**（`max(…, 0.01)`）を、設けます。

## Preetham の、使い方

Preetham は、**空の、色**を、**CIE xyY 色空間**で、**Perez の式**を、**3 回**（Y、x、y それぞれ）、計算して、得ます。**各係数**は、**濁り `T`** の、**1 次式**で、決まります。

```text
係数 A_Y = 0.1787 × T − 1.4630,  B_Y = −0.3554 × T + 0.4275,  C_Y = −0.0227 × T + 5.3251,
        D_Y = 0.1206 × T − 2.5771,  E_Y = −0.0670 × T + 0.3703
（x、y チャンネルにも、別の係数。論文の表を参照）
```

**天頂の色**（輝度 Y、色 x、y）も、**太陽の天頂角と、濁り**から、**式**で、決まります。**最終的な色**は、**天頂の値 × `F(θ, γ) / F(0, θ_s)`** です。

```hlsl
// Preetham の概略（輝度 Y のみ。色 x, y も、同様に、別の係数で計算する）。
float PreethamLuminance(float3 view_dir, float3 sun_dir, float turbidity) {
  float cos_theta = max(view_dir.y, 0.0);
  float cos_gamma = dot(view_dir, sun_dir);
  float gamma = acos(clamp(cos_gamma, -1.0, 1.0));
  float cos_theta_s = max(sun_dir.y, 0.0);

  // 濁り（turbidity）から、Perez の係数を求める（Y チャンネルの例）
  float A = 0.1787 * turbidity - 1.4630;
  float B = -0.3554 * turbidity + 0.4275;
  float C = -0.0227 * turbidity + 5.3251;
  float D = 0.1206 * turbidity - 2.5771;
  float E = -0.0670 * turbidity + 0.3703;

  float f_view = PerezFunction(cos_theta, gamma, cos_gamma, A, B, C, D, E);
  float f_zenith = PerezFunction(1.0, acos(cos_theta_s), cos_theta_s, A, B, C, D, E);
  float Y_zenith = ...;       // 天頂の輝度（太陽の天頂角と濁りから、論文の式で）
  return Y_zenith * f_view / f_zenith;
}
```

**濁り（turbidity）**は、**2（非常に、澄んだ）〜 10（霞んだ）**の範囲を、**使います**。**大きいほど、空が、白っぽく、霞んで**見えます。

## 長所と短所

| | 内容 |
| --- | --- |
| 長所 | **実行時の、コストが、小さい**（数十命令）。**事前計算も、LUT も、不要** |
| 長所 | **パラメーターが、少ない**（太陽の高さ、濁り）。**調整が、簡単** |
| 長所 | **昼の、リアルな、空**が、得られる |
| 短所 | **太陽が、低い**（朝夕）、**地平線の下**（薄明）では、**精度が、落ちる**（Preetham）。Hošek–Wilkie で、改善 |
| 短所 | **カメラが、地上に、固定**。**高い山、飛行機、宇宙**では、使えない |
| 短所 | **空気遠近法**（遠景の霞）を、**別の方法**で、与える必要がある（空の色と、**整合**させる） |
| 短所 | **大気の、パラメーターを、自由に、変えられない**（濁り以外） |

## 使いどころ

| 場面 | 判断 |
| --- | --- |
| **昼間の、地上**（時間帯が、あまり動かない） | **適している** |
| **時間帯が、動く**（朝夕、夜） | Hošek–Wilkie、または、**Hillaire**（[Hillaire 2020: Four LUTs](../scattering/hillaire.md)） |
| **宇宙、高高度** | **使えない**（大気散乱の方式を、使う） |
| 環境光（IBL）の、**元**に、使う | **空を、キューブマップに、描いて**、**ライティングの、元**にする（[Using the Sky for Lighting](sky-lighting.md)） |

''', before="## よくあるミス")
pg.Refs("atmosphere/sky-models/analytic.md", [PREETHAM, HOSEK, PEREZ, BRUNETON17])

pg.Dedup("atmosphere/sky-models/celestial.md")
pg.Add("atmosphere/sky-models/celestial.md", '''
## 太陽・月・星を、空に置く

大気の散乱で、空の色が、決まっても、**太陽の円盤**、**月**、**星**が、**無ければ**、空は、**のっぺり**しています。これらの、**天体**を、**空に、描き足します**。

## 太陽の、位置

太陽の、**方向**（空の、どこに、あるか）は、**時刻**と、**緯度**・**日付**から、決まります。

### 簡易版：ゲームの、時刻から

ゲームでは、**1 日を、数十分〜数時間**に、縮めて、**太陽を、一定の速さで、動かす**ことが、多いです。**時刻**（0〜24）から、**太陽の、天頂角と、方位角**を、決めます。

```hlsl
// 時刻（0〜24）から、太陽の方向（光が来る向き）を求める。単純化: 東から昇り、西に沈む、円軌道。
float3 SunDirection(float hour, float latitude_rad, float axial_tilt_rad) {
  float hour_angle = (hour - 12.0) * (2.0 * 3.14159265 / 24.0);       // 正午を 0 とした、時角
  float elevation_noon = 3.14159265 * 0.5 - latitude_rad + axial_tilt_rad;   // 正午の、太陽の高さ（概算）
```

**時角**（**正午を 0** とした、**時刻の、角度**）が、**地球の、自転**を、表します。**1 時間が、15°**（360° / 24）です。

```hlsl
  // 太陽の、赤緯（日付による、高さの変化）。ここでは、axial_tilt で、近似。
  float declination = axial_tilt_rad;
  float sin_elevation = sin(latitude_rad) * sin(declination) + cos(latitude_rad) * cos(declination) * cos(hour_angle);
  float elevation = asin(sin_elevation);                               // 地平線からの、高さ
  float cos_azimuth = (sin(declination) - sin(elevation) * sin(latitude_rad)) / (cos(elevation) * cos(latitude_rad));
  float azimuth = acos(clamp(cos_azimuth, -1.0, 1.0));
  if (hour_angle > 0.0) azimuth = 2.0 * 3.14159265 - azimuth;          // 午後は、西側
```

**緯度**、**赤緯**（**季節**）、**時角**から、**太陽の、高さ（仰角）と、方位**が、**天文学の、標準的な式**で、決まります。**ゲームでは、緯度や、赤緯を、固定**して、**時角だけを、動かす**のが、普通です。

```hlsl
  // 方位角・仰角から、方向ベクトルへ（右手系、Y 上）。方位角は、北を 0、東を +90° とする。
  return float3(sin(azimuth) * cos(elevation), sin(elevation), -cos(azimuth) * cos(elevation));
}
```

**天文学の、精密な、位置計算**（日付、時刻、緯度・経度から）は、Meeus の『Astronomical Algorithms』（1991）に、**詳しい式**があります。**リアルな、星空**（実在の星座）を、再現したいときに、必要です。

## 太陽の、円盤

太陽は、**視直径が、約 0.53°** の、**明るい円盤**です。**大気の、散乱**だけでは、**円盤が、描かれません**。**円盤**を、**明るさ**つきで、描き足します。

```hlsl
// 太陽の円盤: 視線と太陽の、角度が、太陽の視半径より、小さければ、非常に明るい。
float SunDisk(float3 view_dir, float3 sun_dir) {
  float cos_angle = dot(view_dir, sun_dir);
  const float kSunCosAngle = 0.99998;                    // cos(0.265°)。太陽の視半径は、約 0.265°
  // 縁を、少しだけ、なめらかにする（エイリアシング防止）。
  return smoothstep(kSunCosAngle - 0.00001, kSunCosAngle + 0.00001, cos_angle);
}
float3 sun_color = g_sun_luminance * SunDisk(view_dir, sun_dir);
```

`kSunCosAngle` の、`0.99998` は、**太陽の視半径**（約 0.265°）の、**cos** です。`smoothstep` で、**縁を、わずかに、ぼかして**、**ギザギザ**を、防ぎます。**太陽の、明るさは、非常に高い**（空の、数万倍）ので、**HDR で、描き**、**ブルーム**で、光らせます（[Post-Processing](../../postprocess/index.md)）。

### 大気を、通した、太陽の色

**太陽が、低い**（朝夕）と、**光が、大気を、長く通る**ので、**赤く、暗く**なります。**透過率**（[Transmittance](../scattering/transmittance.md)）を、**掛けて**、**円盤の色**を、決めます。

```hlsl
float3 sun_through_atmosphere = g_sun_luminance * SunTransmittance(g_camera_position, sun_dir);
float3 sun_disk_color = sun_through_atmosphere * SunDisk(view_dir, sun_dir);
```

**夕日が、赤い、橙の円盤**として、見えるのは、**この透過率**の、効果です。

## 月

月は、**太陽と、同じ**程度の、**視直径**（約 0.52°）ですが、**ずっと、暗く**（太陽の、約 40 万分の 1）、**満ち欠け**します。

| 要素 | 内容 |
| --- | --- |
| 円盤 | 太陽と、同じ方法。**テクスチャ**（月の表面の模様）を、貼る |
| **満ち欠け** | 月の、**照らされた部分**は、**太陽の、方向**で決まる。**球**として、描き、**太陽の光で、ライティング**する |
| 位置 | 太陽と、**独立**に、動く（約 29.5 日の周期で、太陽との角度が、一巡） |
| 明るさ | 太陽の、約 0.0000025（満月で）。**夜の空の、主な光源** |

```hlsl
// 月: 球として、太陽の光で、ライティング（満ち欠けは、自動的に、出る）。
float3 MoonColor(float3 view_dir, float3 moon_dir, float3 sun_dir, float moon_angular_radius) {
  float cos_angle = dot(view_dir, moon_dir);
  if (cos_angle < cos(moon_angular_radius)) return 0.0;               // 月の円盤の外
  // 円盤上の位置から、月の表面の法線を、復元する（球とみなす）。
  float3 moon_normal = MoonSurfaceNormal(view_dir, moon_dir, moon_angular_radius);
  float lit = saturate(dot(moon_normal, sun_dir));                     // 太陽に向いた面だけ、明るい
  float3 albedo = g_moon_texture.Sample(g_linear_clamp, MoonUv(moon_normal)).rgb;
  return albedo * lit * g_moon_luminance;
}
```

**球としての、法線**を、求めて、**太陽の光で、ライティング**するだけで、**満ち欠けが、自然に、再現されます**。**太陽と、月の、位置関係**（角度）が、**満ち欠けを、決める**からです。

## 星空

星は、**夜に、見える**、**無数の、点**です。

| 方法 | 内容 |
| --- | --- |
| **キューブマップ**（星空の画像） | **実在の、星図**（天球全体の画像）を、キューブマップに。**簡単で、高品質** |
| **ランダムな点** | **乱数で、点を**散らす。実在の星座は、再現できないが、**軽い** |
| **星表**（実在の、星の位置・明るさ） | **数千個の星**の、データから、**点**を描く。**星の明るさ・色**を、反映 |

```hlsl
// 星空のキューブマップに、夜の明るさを、掛けて、足す。昼は、見えない（空が、明るすぎる）。
float night_factor = saturate(-sun_dir.y * 5.0 + 0.2);                // 太陽が、地平線の下に行くほど、1
float3 stars = g_star_cubemap.Sample(g_linear_clamp, view_dir).rgb * night_factor;
// 星は、空の明るさに、負けるので、空の輝度で、隠す（空が、明るいほど、星が、消える）。
float3 final_color = sky_color + stars * saturate(1.0 - Luminance(sky_color) * 10.0);
```

**星が、昼間に、見えない**のは、**空の、明るさ**に、**かき消されるため**です。**空の輝度が、高い**ほど、**星を、弱める**と、**薄明**（夕暮れ）で、**明るい星から、順に、見え始める**様子が、再現できます。

### 星の、**回転**

**地球の、自転**で、星は、**1 日に 1 回**、**夜空を、回ります**。**星空の、キューブマップ**を、**時刻に応じて、回転**させます。**回転の、軸は、天の北極**（北極星の方向）で、**緯度**に、応じて、**傾き**ます。

```cpp
// 星空の、回転: 地球の自転（時角）と、観測者の緯度から、回転行列を作る。
Matrix star_rotation = Matrix::CreateRotationY(-hour_angle) * Matrix::CreateRotationX(latitude_rad - DirectX::XM_PIDIV2);
```

## 描く順序

| 順 | 描くもの |
| --- | --- |
| 1 | **星空**（最も、奥） |
| 2 | **大気の散乱**（空の色。星を、隠す） |
| 3 | **月**、**太陽の円盤** |
| 4 | **雲**（[Clouds](../clouds/index.md)） |

**星が、大気の、向こう**にあるので、**星を、先に描き**、**大気の、明るさで、隠します**。**太陽と月**は、**大気の、手前の、明るい点**として、足します。

''', before="## よくあるミス")
pg.Refs("atmosphere/sky-models/celestial.md", [MEEUS, HILLAIRE, "Bruneton, Neyret, \"Precomputed Atmospheric Scattering\", Computer Graphics Forum (EGSR 2008)", RTR])

pg.Dedup("atmosphere/sky-models/day-night.md")
pg.Add("atmosphere/sky-models/day-night.md", '''
## 時間帯が、変わると、何が変わるか

**昼から夜へ**、1 日を通して、変わるものを、整理します。

| 時間帯 | 太陽の高さ | 空 | 光 |
| --- | --- | --- | --- |
| **昼**（正午） | 高い | **明るい青** | 白〜やや黄色、強い |
| **朝・夕**（日の出・日の入り前後） | **低い** | **地平線付近が、橙・赤**。反対側は、青紫 | **橙〜赤**、影が、長い |
| **薄明**（日没後、約 30〜60 分） | 地平線の下（0〜−18°） | **深い青〜紫**。**地平線付近だけ、わずかに、明るい** | **ほぼ、空の光だけ**（太陽の、直接光は、無い） |
| **夜** | −18° 以下 | **暗い**。**星空** | **月**（あれば）、星 |

## 太陽の、高さと、光の、色

**太陽が、低い**ほど、**光が、大気を、長く、通り**、**青から、先に、散って、失われ**ます。**赤い光が、残る**ので、**朝夕の、太陽は、赤い**。

```hlsl
// 太陽の、高さ（天頂角の cos = sun_dir.y）から、地表での、太陽の光の色を求める（大気の透過率を、掛ける）。
float3 SunColorAtGround(float3 sun_dir) {
  float3 ground_pos = float3(0, g_bottom_radius + 1.0, 0);           // 地表に近い点
  return g_sun_illuminance * SunTransmittance(ground_pos, sun_dir);   // 透過率 LUT で、大気を通った、光の色
}
```

**透過率**は、**RGB ごと**に、違います（青が、よく散る）。**太陽の、高さ**に応じて、**自動的に**、**昼は白、夕方は橙、日没は赤**に、なります。**色を、手で、設定する必要は、ありません**。

## 光の、強さ

**太陽の、光の、強さ**は、**高さとともに、急に、変わります**。

| 太陽の高さ | 地表の照度（目安、lux） |
| --- | --- |
| 90°（真上） | 約 100,000 |
| 30° | 約 60,000 |
| 10° | 約 10,000 |
| 0°（地平線） | 約 1,000 |
| −6°（市民薄明の終わり） | 約 3 |
| −12° | 約 0.01 |
| 夜（満月） | 約 0.1〜0.3 |
| 夜（月なし） | 約 0.001 |

**対数的**に、**桁が、変わる**ので、**HDR と、露出の、自動調整**（[Auto Exposure](../../postprocess/tonemapping/auto-exposure.md)）が、**ほぼ、必須**です。**固定の露出**では、**昼が、白飛びするか、夜が、真っ暗**になります。

## 薄明（トワイライト）

**太陽が、地平線の、下に、沈んだ後**も、**空は、しばらく、明るい**です。**大気の、高い部分**（太陽の光が、まだ、当たっている）が、**光を、散乱して、地上へ、届ける**ためです。

| 太陽の高さ | 名前 | 見え方 |
| --- | --- | --- |
| 0° 〜 −6° | **市民薄明** | 空が、明るい。**屋外で、活動できる** |
| −6° 〜 −12° | **航海薄明** | **明るい星が、見える**。地平線が、**ぼんやり**見える |
| −12° 〜 −18° | **天文薄明** | ほぼ、夜。**かすかな、明るさ** |

大気散乱の、**物理計算**（[Hillaire 2020: Four LUTs](../scattering/hillaire.md)）は、**多重散乱**と、**オゾンの、吸収**を、含めると、**薄明も、自然に、再現**します（**1 回散乱だけでは、足りない**。[Multiple Scattering](../scattering/multiple-scattering.md)）。

## 1 日の、時間を、進める

ゲームでは、**1 日を、数十分**に、縮めます。**時刻**を、**一定の速さ**で、進めます。

```cpp
// ゲーム内の時刻（時）を、進める。1 日を day_length_minutes 分に、縮める。
float AdvanceTime(float hour, float dt_seconds, float day_length_minutes) {
  const float hours_per_second = 24.0f / (day_length_minutes * 60.0f);
  hour += dt_seconds * hours_per_second;
  if (hour >= 24.0f) hour -= 24.0f;
  return hour;
}
```

| 設計 | 内容 |
| --- | --- |
| 昼夜の、長さを、変える | **昼を、長く、夜を、短く**（プレイしやすい）など、**時間の進みを、時刻に応じて、変える** |
| 季節 | **日付**で、太陽の、**最大の高さ**（赤緯）が、変わる（夏は、高い） |
| 時刻の、**固定** | **ある場面だけ、夕方で、固定**（演出） |

## 夜への、移行で、変えるもの

時刻が、進むと、**複数の、システムを、連動**させます。

| システム | 変化 |
| --- | --- |
| **空**（大気散乱） | LUT を、太陽の位置で、**更新**（Hillaire の方式なら、**自動**） |
| **太陽の、光**（方向光） | 向き・色・強さを、**透過率**から、更新 |
| **月の光** | 夜は、**月を、方向光**に（太陽が、下がったら、**月の光に、切り替え**。または、**足す**） |
| **環境光**（空のライティング） | 空の色から、**再計算**（[Using the Sky for Lighting](sky-lighting.md)） |
| **星** | 夜に、**フェード イン**（[Sun, Moon and Stars](celestial.md)） |
| **霧**（空気遠近法） | **空の色に、合わせて**、色・強さを、変える（[Matching Fog Color to the Sky](../aerial-fog/color-match.md)） |
| **人工の光**（街灯、窓） | **夜に、点灯** |
| **影** | 太陽が、低いと、**影が、長く**（シャドウ マップの、範囲、バイアスの、調整が、必要） |
| **露出** | **自動露出**が、**数秒かけて、追従** |
| **色補正（カラー グレーディング）** | 夜は、**青みがかり、彩度が、下がる**（人間の目の、暗所での、見え方） |

''', before="## よくあるミス")
pg.Refs("atmosphere/sky-models/day-night.md", [HILLAIRE, MEEUS, BRUNETON17, RTR])

pg.Dedup("atmosphere/sky-models/sky-lighting.md")
pg.Add("atmosphere/sky-models/sky-lighting.md", '''
## 空は、光源でもある

空は、**見えるだけでなく**、**シーン全体を、照らす光源**です。**日陰**（太陽の光が、当たらない所）が、**真っ暗に、ならない**のは、**空全体が、青い光で、照らしている**ためです。この光を、**環境光**（アンビエント ライト）と呼びます。

| 光 | 内容 |
| --- | --- |
| **太陽の光**（直接光） | **1 方向から**の、強い光。影を作る |
| **空の光**（環境光） | **全方向から**の、弱い、青い光。**影の中を、照らす** |
| **地面からの、反射光** | 地面が、照らされて、**下から**、物を、照らす光 |

**昼の、日陰**が、**青っぽく**見えるのは、**空の青い光**が、当たっているためです。

## 環境光を、どう表すか

**空の光**を、**シェーディングに、使う**には、**あらゆる方向からの、光**を、**物の表面の、法線**に応じて、**足し合わせる**必要があります。これを、**直接、計算**する（**全方向を、積分**）のは、**重い**ので、**簡略化した、表現**を、使います。

| 方式 | 内容 | 表現力 | コスト |
| --- | --- | --- | --- |
| **単色**（定数） | **1 つの色**を、全面に、足す | 最低（方向性が、ない） | 最小 |
| **半球ライト**（2 色） | **上は、空の色、下は、地面の色**を、法線の上下で、補間 | **低**（上下だけ） | 小 |
| **球面調和関数（SH）** | **全方向の、光**を、**9 個の係数**（3 次）に、圧縮 | **中**（ゆるやかな、方向依存） | 小 |
| **キューブマップ**（IBL） | 環境マップを、**ぼかして**、**法線**で、引く | **高** | 中 |

## 半球ライト

最も、**簡単で、効果が、大きい**方法です。**法線が、上を向く**面は、**空の色**、**下を向く**面は、**地面の色**で、照らします。

```hlsl
// 半球ライト: 法線の上下で、空の色と、地面の色を、補間する。
float3 HemisphereAmbient(float3 normal, float3 sky_color, float3 ground_color) {
  float up = normal.y * 0.5 + 0.5;                      // 0（真下）〜 1（真上）
  return lerp(ground_color, sky_color, up);
}
float3 ambient = albedo * HemisphereAmbient(N, g_sky_ambient, g_ground_ambient);
```

`normal.y * 0.5 + 0.5` で、**法線の上下**を、0〜1 に、直して、**補間**の、重みに、します。**真上を向く面**は、**空の色**、**横**は、**中間**、**真下**は、**地面の色**になります。**物の、上面が、青く、下面が、地面の色**に、なり、**立体感**が、出ます。

## 球面調和関数（SH）

**空全体の、光の分布**を、**少数の係数**で、近似する、方法です（Ramamoorthi と Hanrahan、2001）。**3 次の SH**（**9 個の係数 × RGB**）で、**ゆるやかな、環境光**（拡散反射）を、**ほぼ、正確に**、表せます。

```hlsl
// 3 次の SH（9 係数）で、法線方向の、拡散な、環境光（放射照度）を、求める。
float3 EvaluateSH9Irradiance(float3 sh[9], float3 n) {
  // 論文（Ramamoorthi と Hanrahan 2001）の、放射照度の、式（cosine lobe を、畳み込んだ係数を、使う）。
  const float c1 = 0.429043, c2 = 0.511664, c3 = 0.743125, c4 = 0.886227, c5 = 0.247708;
  return c1 * sh[8] * (n.x * n.x - n.y * n.y) + c3 * sh[6] * n.z * n.z + c4 * sh[0] - c5 * sh[6]
       + 2.0 * c1 * (sh[4] * n.x * n.y + sh[7] * n.x * n.z + sh[5] * n.y * n.z)
       + 2.0 * c2 * (sh[3] * n.x + sh[1] * n.y + sh[2] * n.z);
}
```

**9 個の係数**を、**定数バッファ**に、持ち、**シェーダーが、法線から、環境光を、計算**します。**キューブマップを、引く**より、**はるかに、軽く**、**方向依存の、環境光**が、得られます。**SH の、詳細**は、[Spherical Harmonics (SH)](../../gi/theory/spherical-harmonics.md) を、参照してください。

### 空から、SH を、作る

**空を、キューブマップに、描き**（大気散乱の、結果）、**キューブマップを、SH の、係数に、投影**します（毎フレーム、または、空が、変わったとき）。

```text
① 空を、キューブマップ（32×32×6 程度の、小さな解像度）に、描く
② キューブマップの、各画素に、SH の、基底関数を掛けて、全画素で、合計する → 9 係数 × RGB
③ 係数を、定数バッファへ
```

```hlsl
// 計算シェーダー: キューブマップの 1 面を、SH の係数に、投影する（概略）。
// 各画素の、方向 d と、立体角 dΩ を求めて、基底関数 Y_lm(d) を、掛けて、合計する。
float3 sky = g_sky_cube.SampleLevel(g_linear_clamp, d, 0).rgb;
sh_coeff[0] += sky * 0.282095 * d_omega;                           // Y_00
sh_coeff[1] += sky * 0.488603 * d.y * d_omega;                     // Y_1-1
sh_coeff[2] += sky * 0.488603 * d.z * d_omega;                     // Y_10
sh_coeff[3] += sky * 0.488603 * d.x * d_omega;                     // Y_11
// ... Y_2m（5 個）も同様 ...
```

**小さな、キューブマップ**で、**十分**です（環境光は、**ゆるやかに、変わる**ため）。

## 鏡面反射の、環境光（IBL）

**光沢のある面**（金属、水面）は、**空の、細かい、景色**を、**映します**。**環境マップ**（キューブマップ）を、**反射ベクトルで、引き**、**粗さに応じて、ぼかした**ものを、使います（[Prefiltering (Split-Sum)](../../reflections/probes/prefilter.md)）。

| 反射 | 環境光の、表現 |
| --- | --- |
| **拡散**（ざらざらの面） | **SH**、または、**ぼかしたキューブマップ**（**法線**で引く） |
| **鏡面**（つるつるの面） | **環境マップ**（**反射ベクトル**で引く）。**粗さに応じて、ミップを選ぶ** |

## 空が、変わったら、環境光も、変える

**時刻が、進む**（空の色が変わる）、**天候が、変わる**と、**環境光も、更新**する必要があります。

| 更新の頻度 | 内容 |
| --- | --- |
| **毎フレーム** | **小さな、キューブマップ**（32×32）に、空を描き、**SH を、再計算**。**非常に、軽い** |
| **数フレームに、1 回** | **鏡面用の、大きな、キューブマップ**（128×128、ミップつき）を、**更新**。1 フレームに、**1 面ずつ**、など、**分割して**更新 |
| **時刻の、キーフレーム**ごと | **事前に、焼いた、環境マップ**を、補間（**固定の、時間帯**のみ） |

**空の、更新が、遅れる**と、**空は、夕焼けなのに、環境光は、昼の色**、という、**ずれ**が、出ます。**少なくとも、拡散用の、SH は、毎フレーム**、**更新**しておくと、**ずれが、目立ちません**。

''', before="## よくあるミス")
pg.Refs("atmosphere/sky-models/sky-lighting.md", [RAMAMOORTHI, HILLAIRE, "Karis, \"Real Shading in Unreal Engine 4\", SIGGRAPH 2013, Physically Based Shading in Theory and Practice（split-sum 近似による、IBL）", RTR])
pg.Refs("atmosphere/sky-models/index.md", [HILLAIRE, BRUNETON, PREETHAM, HOSEK, RTR])
print("ok")
