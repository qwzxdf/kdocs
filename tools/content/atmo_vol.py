import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import pg  # noqa: E402

SCHNEIDER15 = '''Schneider, Vos, "The Real-Time Volumetric Cloudscapes of Horizon: Zero Dawn", SIGGRAPH 2015, Advances in Real-Time Rendering in Games'''
SCHNEIDER17 = '''Schneider, "Nubis: Authoring Real-Time Volumetric Cloudscapes with the Decima Engine", SIGGRAPH 2017, Advances in Real-Time Rendering in Games'''
HILLAIRE16 = '''Hillaire, "Physically Based Sky, Atmosphere and Cloud Rendering in Frostbite", SIGGRAPH 2016, Physically Based Shading in Theory and Practice'''
HILLAIRE20 = '''Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique", Computer Graphics Forum (Eurographics Symposium on Rendering 2020)'''
HILLAIRE15 = '''Hillaire, "Physically Based and Unified Volumetric Rendering in Frostbite", SIGGRAPH 2015, Advances in Real-Time Rendering in Games'''
WRONSKI = '''Wronski, "Volumetric Fog: Unified Compute Shader Based Solution to Atmospheric Scattering", SIGGRAPH 2014, Advances in Real-Time Rendering in Games'''
WRENNINGE = '''Wrenninge, "Art-Directable Multiple Volumetric Scattering", SIGGRAPH 2015 Talks'''
KARIS = '''Karis, "High Quality Temporal Supersampling", SIGGRAPH 2014, Advances in Real-Time Rendering in Games（TAA、履歴のクランプ）'''
MITCHELL = '''Mitchell, "Volumetric Light Scattering as a Post-Process", GPU Gems 3, Chapter 13, 2007（放射状ブラーによる、光の筋）'''
MITCHELL04 = '''Mitchell, "Light Shafts: Rendering Shadows in Participating Media", Game Developers Conference 2004'''
BEER = '''Beer, "Bestimmung der Absorption des rothen Lichts in farbigen Flüssigkeiten", Annalen der Physik, 1852（吸収の法則）'''
RTR = '''Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（参加媒質、雲、霧の章）'''
PERLIN = '''Perlin, "An Image Synthesizer", SIGGRAPH 1985'''
WORLEY = '''Worley, "A Cellular Texture Basis Function", SIGGRAPH 1996（Worley ノイズ。雲のもこもこに使う）'''
JIMENEZ = '''Jimenez, "Next Generation Post Processing in Call of Duty: Advanced Warfare", SIGGRAPH 2014（Interleaved Gradient Noise）'''
MCGUIRE = '''Mara, McGuire, Gribble, Lipton, Luebke, "Deep G-Buffers for Stable Global Illumination Approximation", High-Performance Graphics 2016'''
SOUSA = '''Sousa, "CryENGINE 3: Reaching the Speed of Light", SIGGRAPH 2010, Advances in Real-Time Rendering in Games'''

# ================================================================ aerial-fog
pg.Dedup("atmosphere/aerial-fog/fog-equation.md")
pg.Add("atmosphere/aerial-fog/fog-equation.md", '''
## 霧を、式で書く

**霧**（フォグ）は、**遠くの物の、色を、霧の色へ、近づける**効果です。**距離が、遠いほど、霧の色に、染まります**。式の、骨格は、**1 つ**です。

```text
最終の色 = 物の色 × 透過率  +  霧の色 × (1 − 透過率)
```

**透過率**（物の色が、**どれだけ残るか**）の、**決め方**が、方式ごとに、違います（[Fog Equations](#) の、上の図）。

## 3 つの、透過率の式

### ① 線形フォグ

**開始距離**から、**終了距離**まで、**直線的に**、霧が、濃くなります。

```hlsl
float LinearFog(float distance, float fog_start, float fog_end) {
  return saturate((fog_end - distance) / (fog_end - fog_start));       // 透過率: 開始で 1、終了で 0
}
```

`fog_start` より、近くでは、**透過率 1**（霧なし）、`fog_end` より、遠くでは、**透過率 0**（霧の色だけ）です。**最も、単純**で、**古い**方式ですが、**物理的には、正しくありません**（**霧の、濃さが、直線で、変わる**ことは、ない）。

### ② 指数フォグ

**物理に、近い**式です。**進んだ、距離に、比例して、同じ割合ずつ、光が、減る**（Beer の法則）。

```hlsl
float ExpFog(float distance, float density) {
  return exp(-density * distance);                                     // 透過率
}
```

`density` は、**霧の、濃さ**です。**距離が、2 倍**になると、**透過率が、2 乗**に（0.5 → 0.25）なります。**霧の、現実の、振る舞い**に、近い、**標準的な**式です。

### ③ 指数の 2 乗フォグ

**近くは、ほぼ、霧なし**、**ある距離から、急に、濃くなる**、**濃霧**の、見た目です。

```hlsl
float Exp2Fog(float distance, float density) {
  float f = density * distance;
  return exp(-f * f);
}
```

`exp(−(d × k)²)` は、**近くで、ほぼ 1**（霧が、ほとんど、見えない）で、**ある距離**（`1 / k` くらい）から、**急に、0 へ**落ちます。**霧の中に、入った**ような、**急な、視界の悪化**を、表現できます。

| 式 | 透過率 | 見た目 | 物理的な、正しさ |
| --- | --- | --- | --- |
| 線形 | 直線で、減る | 霧の、開始と終了が、はっきり | **正しくない** |
| 指数 | `exp(−kd)` | **自然な、霞** | **正しい**（Beer の法則） |
| 指数の 2 乗 | `exp(−(kd)²)` | **近くは、澄み、遠くで、急に、濃い** | 正しくない（見た目の、調整用） |

## 霧の、色を、適用する

```hlsl
// 物の色に、霧を、かける（ピクセル シェーダーの最後。距離は、カメラからの、実際の距離）。
float3 ApplyFog(float3 scene_color, float distance) {
  float transmittance = ExpFog(distance, g_fog_density);
  return scene_color * transmittance + g_fog_color * (1.0 - transmittance);
}
```

最初の式を、そのまま、コードにしたものです。`distance` は、**カメラから、その画素までの、距離**です。**深度**（視点の、奥行き）では、**視線が、斜めの画素で、霧が、薄く**なります（**距離が、実際より、短く**測られるため）。**視線方向の、距離**を、使います。

```hlsl
// 視線方向の距離: ワールド位置から、カメラまでの、実際の距離。
float distance = length(input.world_position - g_camera_position);
```

## RGB ごとの、減衰

**霧の、色が、青っぽい**（空気遠近法）のは、**青い光が、よく散る**ためで、**RGB ごとに、透過率が、違う**からです。**簡易な、霧**では、**1 つの、透過率**で、**霧の色を、混ぜます**。**物理ベース**の方式では、**RGB ごと**に、**別の、消散係数**を、持ちます（[Physically Based Aerial Perspective](physical.md)）。

```hlsl
float3 transmittance = exp(-g_extinction_rgb * distance);              // RGB ごとの、透過率
float3 result = scene_color * transmittance + g_inscatter_color * (1.0 - transmittance);
```

**赤は、遠くまで、残り**、**青は、先に、霧の色へ**染まる**ので、**霞む遠景が、青みがかる**、**空気遠近法**の、効果が、出ます。

## 密度の、決め方

`density`（`σ`）は、**「ここまでの、距離で、霧の色に、染まりきる」**という、**見た目の、要求**から、決められます。

```text
透過率が、ほぼ見えなくなる（5%）距離を D とすると:  exp(−σ D) = 0.05  →  σ = 3.0 / D
```

```hlsl
// 「視界が、D メートルで、ほぼ、霧の色になる」から、密度を求める。
float DensityFromVisibility(float visibility_m) { return 3.0 / visibility_m; }
```

| 視界の距離 | 霧の状態 | `σ`（1/m） |
| --- | --- | --- |
| 10 km | 澄んだ、昼 | 0.0003 |
| 2 km | 薄い、霞 | 0.0015 |
| 500 m | 霧 | 0.006 |
| 100 m | **濃霧** | 0.03 |

**ゲームの、視界を、制御**するのに、**「見える距離」で、指定**するほうが、**直感的**です。

## 注意点

| 項目 | 内容 |
| --- | --- |
| **HDR** | 霧の色は、**HDR の値**（空の、明るさ）に、**合わせる**。霧の色が、**暗すぎる**と、**遠景が、暗く沈み**、**明るすぎる**と、**白く浮く**（[Matching Fog Color to the Sky](color-match.md)） |
| **加算ブレンドの物** | **火や、光の、パーティクル**（加算）は、**霧で、暗くなる**が、**霧の色を、足してはいけない**（光の物が、霧で、白く、浮く）。**霧の、適用は、透過率の、掛け算だけ**に、する |
| **半透明** | 半透明の物にも、**霧を、かける**（透過率を、掛ける）。**かけ忘れる**と、**遠くの煙が、霧の中で、浮く** |
| **空** | 空にも、霧を、かけるかは、**場面**による。**霧の中**では、**空も、霧の色**に、近づく |

''', before="## よくあるミス")
pg.Refs("atmosphere/aerial-fog/fog-equation.md", [BEER, HILLAIRE20, RTR, WRONSKI])

pg.Dedup("atmosphere/aerial-fog/height-fog.md")
pg.Add("atmosphere/aerial-fog/height-fog.md", '''
## 高さで、濃さが、変わる、霧

**谷に、たまった、朝霧**、**地面に、近いほど、濃い、霧**のように、**霧の濃さは、高さで、変わります**。**高さフォグ**は、**霧の密度**を、**高さの関数**として、**扱います**。

```text
密度 ρ(h) = ρ₀ × exp( −k × h )          h: 霧の層の、基準からの、高さ。k: 減り方の速さ
```

**地面で、最も、濃く**、**高くなるほど、指数関数的に、薄く**なります。**大気そのものの、密度**（レイリー、ミー）と、**同じ、形**です。

## 光学的な、厚さを、解析的に、求める

視線に沿って、**密度を、積分した値**（**光学的な、厚さ**）が、透過率を、決めます。**密度が、指数関数**なら、**積分も、解析的に、求められます**。

```text
視線: 始点の高さ h₀、終点の高さ h₁、その間の、距離 d。高さは、直線的に変わる。

τ = ρ₀ × d × ( exp(−k h₀) − exp(−k h₁) ) / ( k × (h₁ − h₀) )       （h₁ ≠ h₀ のとき）
τ = ρ₀ × d × exp(−k h₀)                                              （h₁ = h₀ のとき。視線が、水平）
```

**透過率**は、`exp(−τ)` です。**積分を、ループで、数値計算せず**、**式 1 つ**で、求まります。

## 実装

```hlsl
// カメラから、ワールド位置までの、高さフォグの、透過率を、解析的に求める。
float HeightFogTransmittance(float3 camera, float3 world_pos) {
  float3 ray = world_pos - camera;
  float dist = length(ray);
  float h0 = camera.y - g_fog_base_height;                  // 霧の層の基準から見た、カメラの高さ
  float dh = ray.y;                                         // 視線に沿った、高さの変化
```

**カメラの高さ**と、**視線の上下方向の、変化**（`dh`）を、求めます。**霧の、基準の高さ**（`g_fog_base_height`）より、**上か下か**を、`h0` が、表します。

```hlsl
  float k = g_fog_falloff;                                  // 減り方の速さ（1/m）
  float exponent = k * dh;                                  // 視線に沿った、指数の、変化量
  float fog_at_camera = g_fog_density * exp(-k * h0);       // カメラの位置での、密度
```

**カメラの位置での、密度**（`fog_at_camera`）が、**積分の、出発点**です。

```hlsl
  // 積分の核: (1 − exp(−k·dh)) / (k·dh)。dh が、ほぼ 0 のとき（水平）は、1 に近づく。
  float integral = (abs(exponent) > 1e-4) ? (1.0 - exp(-exponent)) / exponent : 1.0;
  float optical_depth = fog_at_camera * dist * integral;
  return exp(-optical_depth);
}
```

`(1 − exp(−x)) / x` が、**積分の、解析解**で、**`x → 0`**（水平な視線）で、**1 に近づきます**。**ゼロ割を、避ける**ために、**`abs(x)` が、小さいときは、極限の値（1）**を、使います。これを、**距離に、掛ければ**、**光学的な、厚さ**が、求まります。

```hlsl
float3 ApplyHeightFog(float3 scene_color, float3 camera, float3 world_pos) {
  float t = HeightFogTransmittance(camera, world_pos);
  return scene_color * t + g_fog_color * (1.0 - t);
}
```

最後に、**通常の、霧と、同じ式**で、**物の色と、霧の色**を、混ぜます。

## 見た目の、特徴

| 状況 | 見え方 |
| --- | --- |
| カメラが、**霧の層の、中**（低い所） | **周りが、霧に、包まれる**。視界が、短い |
| カメラが、**層の、上**（高い所） | **下の方に、霧が、たまって見える**（雲海、谷の霧）。**上空は、澄んでいる** |
| 視線が、**上向き** | 高さが、上がるので、**霧が、薄く**（空は、霧が、少ない） |
| 視線が、**下向き**（地面） | **濃い、層**を、通るので、**霧が、濃い** |

**山の上から、谷を、見下ろす**と、**谷底に、霧が、たまっている**様子が、自然に、出ます。

## 他の霧との、組み合わせ

**高さフォグ**と、**距離フォグ**（[Fog Equations](fog-equation.md)）を、**足し合わせる**ことが、できます（**光学的な、厚さを、合計**）。

```hlsl
// 一様な、霧（遠景の、霞）と、高さフォグ（谷の、霧）を、光学的な厚さの、足し算で、組み合わせる。
float tau_uniform = g_uniform_density * dist;
float tau_height = ...;                                    // 上の式で求めた、高さフォグの、光学的な厚さ
float transmittance = exp(-(tau_uniform + tau_height));
```

**透過率の、掛け算**（`exp(−a) × exp(−b) = exp(−(a + b))`）なので、**足し算**で、**合成**できます。

## 注意点

| 項目 | 内容 |
| --- | --- |
| **視線が、地面を、貫く** | 視線が、**霧の層の下**（地面の、下）に、**潜る**場合は、**地面で、止める**（物の、位置が、終点） |
| **霧の層の、上端** | 指数関数は、**無限に続く**ので、**ある高さで、霧を、0 に**する、**クランプ**も、使う（**層の、上端が、はっきり**する、見た目） |
| **局所的な、霧**（沼地だけ） | **全体の、高さフォグ**では、できない。**ボリューム フォグ**（[Volumetric Fog](../volumetric-fog/index.md)）、または、**霧の、ボリューム**を、置く |

''', before="## よくあるミス")
pg.Refs("atmosphere/aerial-fog/height-fog.md", [HILLAIRE15, WRONSKI, RTR, BEER])

pg.Dedup("atmosphere/aerial-fog/physical.md")
pg.Add("atmosphere/aerial-fog/physical.md", '''
## 物理ベースの、空気遠近法

**簡易な霧**（[Fog Equations](fog-equation.md)）は、**霧の色と、濃さを、手で**決めます。**物理ベース**の、空気遠近法は、**大気の散乱**（[Atmosphere Model](../scattering/atmosphere-model.md)）から、**霧の色と、濃さを、計算**します。**時間帯**（朝、昼、夕）や、**カメラの高度**で、**自動的に、霧の色**が、変わります。

## 何が、物理的か

**遠くの物が、霞む**のは、**物から、カメラまでの、空気**が、**2 つのこと**を、行うためです。

| 効果 | 内容 |
| --- | --- |
| **減衰**（透過率） | 物から来た光が、**散乱・吸収**で、**一部、失われる**（**青の方が、減りやすい**） |
| **内向き散乱**（インスキャッター） | **太陽や空の光**が、**視線の途中で、カメラの方へ、散乱**して、**足される**（**空と、同じ色**） |

```text
カメラに届く色 = 物の色 × 透過率  +  内向き散乱（視線に沿って、足された、散乱光）
```

**1 つ目**は、**霧の式**と同じ（**物を、暗くし、色を、変える**）。**2 つ目**が、**霧の色**（霧の色に、近づく、部分）に、相当し、**物理ベースでは、計算で、求まります**。

## Aerial Perspective LUT

Hillaire（2020）の、方式は、**カメラの前方の、空間**を、**3D テクスチャ**（**32×32×32**）に、分割し、**各セルに**、**カメラから、そのセルまでの、内向き散乱と、透過率**を、**保存**します（[Hillaire 2020: Four LUTs](../scattering/hillaire.md)）。

```hlsl
// 物体の、色に、空気遠近法を、適用する（ピクセル シェーダーの、最後）。
float3 ApplyAerialPerspective(float3 scene_color, float2 screen_uv, float distance_m) {
  // 距離を、LUT の、奥行き方向の座標へ（近くを、細かく）。
  float slice = DistanceToSlice(distance_m);
  float4 ap = g_aerial_perspective_lut.SampleLevel(g_linear_clamp, float3(screen_uv, slice), 0);
```

画面上の、位置 `screen_uv` と、距離から、LUT の、**セル**を、引きます。**1 回の、テクスチャ読み込み**です。

```hlsl
  float3 inscatter = ap.rgb;                           // この距離までに、空気が、足した光
  float transmittance = 1.0 - ap.a;                    // 物体の光が、届く割合
  return scene_color * transmittance + inscatter;
}
```

**物体の色に、透過率を掛け**、**内向き散乱を、足す**。**霧の式と、同じ形**ですが、**LUT の値**は、**物理計算**の結果です。

## 距離の、割り当て

LUT の、奥行き方向の、**分割**は、**近くを、細かく**、**遠くを、粗く**します。**近くの、霞は、変化が、急**で、**遠くは、ゆるやか**なためです。

```hlsl
// 距離（m）→ スライス（0〜1）。距離の、平方根に比例させて、近くを、細かくする。
float DistanceToSlice(float distance_m) {
  const float kMaxDistance = 32000.0;                  // 32 km
  return sqrt(saturate(distance_m / kMaxDistance));
}
float SliceToDistance(float slice) {
  const float kMaxDistance = 32000.0;
  return slice * slice * kMaxDistance;
}
```

**平方根**で、**近くに、スライスを、集める**のが、**簡単で、効果的**な、割り当てです。

## 簡易な、霧との、違い

| | 簡易な霧 | 物理ベースの、空気遠近法 |
| --- | --- | --- |
| 霧の色 | **手で、決める** | **大気から、計算**（時間帯で、自動で、変わる） |
| 夕焼け | **手で、色を、変える** | **自動**（太陽が、低いと、赤い霞） |
| 太陽の方向 | 考慮しない | **太陽に、向かうと、明るい霞**（ミー散乱の、前方散乱） |
| 高度 | 考慮しない | **高い所**から見ると、**霧の、濃さが、変わる** |
| 空との、整合 | **手で、合わせる**（ずれやすい） | **自動**（同じ、大気の計算） |
| コスト | **最小** | 小（LUT の更新 + 1 回の読み込み） |

**空と、霧の、色が、自動で、合う**ことが、**最大の利点**です（[Matching Fog Color to the Sky](color-match.md)）。

## 太陽の、方向による、変化

物理ベースの、霧は、**太陽に、向かって見ると、明るく**、**太陽と、反対を見ると、暗い**です。**ミー散乱**が、**前方に、強く散る**ためです（[Phase Functions](../scattering/phase-function.md)）。

```text
太陽の方向を見る:   視線と太陽が、同じ向き  → 前方散乱が、強い → 霞が、明るく、白い
太陽の反対を見る:   視線と太陽が、逆向き   → 後方散乱は、弱い → 霞が、暗く、青い
```

この、**方向による、違い**が、**景色に、立体感**を、与えます。**簡易な霧**では、**全方向で、同じ色**になり、**平板**です。

## コスト

| 処理 | コスト |
| --- | --- |
| Aerial Perspective LUT の、更新 | 0.1〜0.2 ms |
| 物体ごとの、適用 | **テクスチャ 1 回**（物体の、ピクセル シェーダーに、数命令を、足すだけ） |

**物体の数に、関係なく**、**LUT を、1 回、更新**し、**各物体は、引くだけ**なので、**非常に、効率的**です。

''', before="## よくあるミス")
pg.Refs("atmosphere/aerial-fog/physical.md", [HILLAIRE20, HILLAIRE16, "Bruneton, Neyret, \"Precomputed Atmospheric Scattering\", Computer Graphics Forum (EGSR 2008)", RTR])

pg.Dedup("atmosphere/aerial-fog/sun-inscatter.md")
pg.Add("atmosphere/aerial-fog/sun-inscatter.md", '''
## 太陽の方向の、霞

太陽の、方を、見ると、**霞が、明るく、白く**、光ります。**霧の中で、太陽が、まぶしい**、あの見た目です。これは、**霧の粒子**（ミー散乱）が、**光を、前方に、強く散らす**ためで、**太陽の方向の、内向き散乱**を、**足す**ことで、**再現**できます。

## 内向き散乱を、足す

簡易な霧の、霧の色に、**太陽の、方向に応じた、項**を、足します。

```hlsl
// 太陽に、向かって見るほど、霧の色を、太陽の色へ、寄せる。
float3 FogColorWithSun(float3 view_dir, float3 sun_dir) {
  float sun_amount = saturate(dot(view_dir, sun_dir));             // 視線が、太陽の方を、向いているほど、1
```

`dot(view_dir, sun_dir)` は、**視線と、太陽の、近さ**です（1 のとき、太陽の、真正面）。

```hlsl
  // 前方散乱の、位相関数（HG）で、太陽の方向を、強調する。
  float phase = HenyeyGreenstein(sun_amount, 0.6);                 // g = 0.6: やや、前方に偏る
  float3 sun_glow = g_sun_color * phase;
  return g_fog_color + sun_glow * g_sun_inscatter_strength;
}
```

**HG 位相関数**（[Phase Functions](../scattering/phase-function.md)）で、**太陽の方向に、強く、偏った**、**明るさ**を、作ります。`g` が、大きい（0.8）ほど、**太陽の、すぐ近く**だけが、明るく、小さい（0.3）と、**広い範囲**が、ぼんやり、明るく**なります**。

## 適用する

```hlsl
float3 ApplyFogWithSun(float3 scene_color, float3 view_dir, float distance) {
  float3 fog_color = FogColorWithSun(view_dir, g_sun_dir);
  float transmittance = exp(-g_fog_density * distance);
  return scene_color * transmittance + fog_color * (1.0 - transmittance);
}
```

**霧の色**が、**視線の方向**によって、変わるので、**同じ霧でも、太陽の方向と、反対側で、色が違う**、**立体的な**霧に、なります。

## 太陽の、**影**を、考える

**霧の中**では、**太陽の光が、遮られた、場所**（建物、木の影）は、**霧も、暗く**なります。**影を、考慮しない**霧は、**影の中でも、一様に、明るい**ので、**光の筋**（ゴッド レイ）が、出ません（[God Rays](../god-rays/index.md)）。

| 方式 | 影の、扱い |
| --- | --- |
| この方式（霧の色に、太陽を足す） | **影を、無視**（全体が、一様） |
| **ボリューム フォグ**（froxel） | **シャドウ マップを、引いて**、**影の中は、暗い**（[Volumetric Fog](../volumetric-fog/index.md)） |
| **ゴッド レイ**（放射状ブラー、レイマーチ） | **影の、有無で、筋を、作る**（[God Rays](../god-rays/index.md)） |

**簡単な、霧に、太陽を、足す**方法は、**影を、無視**する代わりに、**非常に、軽い**ので、**遠景の、霞**に、向いています。**近景**の、**影つきの霧**は、**ボリューム**で、作ります。

## 物理ベースでは、自動

[Physically Based Aerial Perspective](physical.md) の、**LUT** は、**太陽の方向による、内向き散乱**を、**最初から**、含んでいます（ミー散乱の、位相関数を、積分に、含めているため）。**LUT を、使うなら**、**この項を、手で、足す必要は、ありません**。

''', before="## よくあるミス")
pg.Refs("atmosphere/aerial-fog/sun-inscatter.md", ["Henyey, Greenstein, \"Diffuse Radiation in the Galaxy\", Astrophysical Journal, Vol. 93, 1941", HILLAIRE20, RTR])

pg.Dedup("atmosphere/aerial-fog/color-match.md")
pg.Add("atmosphere/aerial-fog/color-match.md", '''
## 霧の色と、空の色が、ずれると

遠景の、**山や建物**は、**霧の色**に、向かって、霞んで、**消えて**いきます。その**霧の色**が、**空の、地平線の色**と、**違う**と、**山の、頂上の、すぐ上**で、**色の、境目**が、見えて、**不自然**です。

| 状況 | 見え方 |
| --- | --- |
| 霧の色 = 空の、地平線の色 | 遠景が、**空に、自然に、溶け込む** |
| 霧の色 ≠ 空の色 | 遠くの山が、**「貼り付いた、絵」**に見える。**輪郭が、浮く** |

## 方法 1：霧の色を、空から、取る

**視線の方向**の、**空の色**（**地平線**付近）を、**霧の色**として、使います。

```hlsl
// 霧の色を、視線の方向の、空の色から、取る（空を、キューブマップや、LUT に描いているとき）。
float3 FogColorFromSky(float3 view_dir) {
  // 地平線に近い方向の、空の色。視線が、上向きでも、地平線に、近い色を使う（霧は、地面近くの現象）。
  float3 horizon_dir = normalize(float3(view_dir.x, max(view_dir.y, 0.0) * 0.2, view_dir.z));
  return g_sky_cube.SampleLevel(g_linear_clamp, horizon_dir, 4).rgb;      // ぼかした（高いミップ）空の色
}
```

視線が、**上向きでも**、**水平方向の空の色**に、**寄せます**（`y` を、小さく）。**霧は、地面の近くの現象**なので、**上空の、青い空の色を、霧に使う**と、**霧が、青くなりすぎます**。**ミップの、高い（ぼやけた）段**を、読んで、**空の、細かい模様**（雲）を、**霧の色に**、持ち込まないようにします。

## 方法 2：空と、霧を、同じ大気から

**物理ベース**の方式（[Physically Based Aerial Perspective](physical.md)）では、**空と、霧が、同じ大気の計算**から、決まるので、**自動で、一致**します。**空の色を、霧の色に、コピー**する必要が、ありません。

## 方法 3：平均色を、定数に

**簡易な方法**は、**空の、地平線の、平均の色**を、**CPU で、計算**し、**定数バッファ**で、**霧の色**として、渡します。

```cpp
// 時間帯ごとに、地平線の色を、キーフレームで持ち、霧の色にも、同じキーフレームを、使う。
float3 horizon_color = SampleSkyKeyframes(time_of_day).horizon;
fog_color = horizon_color;                 // 空と、霧が、同じキーフレームから、決まる
```

**空と、霧が、同じデータ**（キーフレーム）から、決まるので、**必ず、揃います**。**グラデーション スカイ**（[Gradient Sky](../sky-models/gradient.md)）と、組み合わせる、**簡易**な構成で、よく使われます。

## 太陽の、方向の、考慮

空の、地平線は、**太陽の方向**で、**色が、変わります**（太陽側が、明るく、橙）。**霧の色も、方向で、変える**と、**遠景が、空に、自然に、溶け込みます**。

```hlsl
float3 horizon = lerp(g_horizon_color_away, g_horizon_color_sun, pow(saturate(dot(view_dir, g_sun_dir)), 4.0));
```

**太陽に、向かう**方向の、**霧の色**を、**空の、太陽側の、地平線の色**（橙、明るい）に、**寄せます**。**反対側**は、**青〜灰色**です。**空の、グラデーション**（[Gradient Sky](../sky-models/gradient.md)）の、**同じ式**を、**霧にも、使います**。

## HDR と、露出

**空の色**は、**HDR の値**（明るい）で、**霧の色**も、**同じ、スケール**でなければ、**霧が、浮きます**。**夜**は、**霧の色も、暗く**します。

| 問題 | 内容 |
| --- | --- |
| 霧が、**夜でも、明るい** | 霧の色が、**昼の、固定値**。**時間帯で、霧の色（と、明るさ）も、変える** |
| 霧が、**昼に、暗い** | 霧の色が、**LDR の、値**（1 以下）。HDR の、空の明るさに、**合わせる** |
| 遠景が、**空より、明るい** | 霧の色が、空の地平線より、**明るすぎ**。**霧の色を、空の、地平線の色に、そろえる** |

''', before="## よくあるミス")
pg.Refs("atmosphere/aerial-fog/color-match.md", [HILLAIRE20, "Preetham, Shirley, Smits, \"A Practical Analytic Model for Daylight\", SIGGRAPH 1999", RTR])

pg.Dedup("atmosphere/aerial-fog/where.md")
pg.Add("atmosphere/aerial-fog/where.md", '''
## 霧を、どこで、かけるか

霧は、**最終的に、画面に出る、色**に、かけます。**どの段階で、どの物に、かけるか**を、整理します。

| 方法 | タイミング | 内容 |
| --- | --- | --- |
| **各物体の、ピクセル シェーダー**の最後 | 物体を、描くとき | **物体ごとに、霧を計算**して、色に、かける。**フォワード レンダリング**の、標準 |
| **ポスト プロセス**（全画面） | 全部の物を、描いた後 | **深度バッファ**から、**各画素の、距離**を、求めて、**全画素に**、霧を、かける。**ディファード**の、標準 |

## 方法 1：物体ごとに、かける

**ピクセル シェーダー**の、最後で、**物体の色に、霧を、適用**します。

```hlsl
float4 main(PSInput input) : SV_Target {
  float3 color = ComputeLighting(input);                              // ライティング済みの色
  float distance = length(input.world_position - g_camera_position);
  color = ApplyFog(color, distance);                                  // 最後に、霧
  return float4(color, 1.0);
}
```

**長所**は、**半透明の物にも、そのまま、かけられる**ことです（半透明の物も、**自分の、ピクセル シェーダー**で、霧を、かける）。**短所**は、**すべての、マテリアルの、シェーダーに、霧の、コードを、入れる**必要があることです。

## 方法 2：ポスト プロセス

**全画面の、ピクセル シェーダー**で、**深度バッファ**から、**画素ごとの、距離**を、復元して、**霧を、かけます**。

```hlsl
float4 FogPostPS(float2 uv : TEXCOORD0) : SV_Target {
  float3 scene = g_scene_color.Sample(g_point_clamp, uv).rgb;
  float depth = g_scene_depth.Sample(g_point_clamp, uv).r;

  // 深度から、ワールド位置を、復元して、カメラまでの距離を、求める。
  float3 world_pos = ReconstructWorldPosition(uv, depth);
  float distance = length(world_pos - g_camera_position);

  return float4(ApplyFog(scene, distance), 1.0);
}
```

**長所**は、**マテリアルの、シェーダーを、変えなくて、よい**こと、**1 か所**で、**霧を、管理**できることです。**短所**は、**半透明の物**（**深度に、書かれない**）に、**霧が、かからない**ことです。

## 半透明の物を、どうするか

ポスト プロセスの、霧は、**不透明な物の、深度**だけを、見ます。**半透明の物**（煙、ガラス、パーティクル）は、**深度に、書かれない**ので、**霧が、かからず**、**霧の中で、浮いて**見えます。

| 対策 | 内容 |
| --- | --- |
| **半透明の物は、自分のシェーダーで、霧をかける** | ポスト プロセスの霧と、**同じ関数**を、半透明の、マテリアルの、ピクセル シェーダーでも、呼ぶ。**ポスト プロセスは、不透明にだけ、かかる**（半透明は、**かけた後に、描く**） |
| **描画順を、変える** | 1) 不透明を描く、2) **霧を、かける**、3) **半透明を描く**（半透明の、シェーダーに、霧が、組み込まれている） |

```text
① 不透明を描く（深度を書く）
② ポスト プロセスで、霧を、かける（不透明にだけ）
③ 半透明を描く（各自の、ピクセル シェーダーで、霧を、かける）
```

## 空に、かけるか

**空**は、**無限遠**で、**深度が、最大**です。**霧を、かける**と、**空が、すべて、霧の色**になって、**空が、消えます**。

| 方法 | 内容 |
| --- | --- |
| 空には、**霧を、かけない** | 深度が、最大（空）の画素は、**スキップ**。**空は、そのまま** |
| 空に、**少しだけ**、霧をかける | **地平線の近く**だけ、霧の色に、近づける（**空と、霧の、境目が、自然**に） |
| **濃霧**のとき | 空も、**霧の色に**（霧の中に、いる感じ） |

```hlsl
// 深度が、最大（空）の画素は、霧をかけない。または、方向に応じた、弱い霧にする。
if (depth >= 1.0) {
  // 地平線に近いほど、霧の色に近づける（空と、遠景の、霧が、つながる）。
  float horizon_blend = saturate(1.0 - abs(view_dir.y) * 3.0);
  return float4(lerp(scene, g_fog_color, horizon_blend * g_fog_sky_strength), 1.0);
}
```

## ディファード レンダリングでの、注意

**ディファード**では、**ライティングの後**に、ポスト プロセスで、霧を、かけます。**ライティングの、結果**（HDR の色）に、霧を、かけるので、**物理的に、正しい順序**です（**霧は、光の通り道の現象**）。

## 色の、順序

霧は、**ライティングの、後**、**トーン マッピングの、前**に、かけます。

```text
ライティング → 霧 → ポスト エフェクト（ブルーム） → トーン マッピング → ガンマ
```

**トーン マッピングの、後**に、霧を、かけると、**霧の、色が、LDR**（0〜1）に、**押し込まれ**、**明るい霧の、表現**（HDR）が、できません。**ブルーム**（霧の中の、光の、にじみ）も、**霧の後**に、かけるほうが、**自然**です。

''', before="## よくあるミス")
pg.Refs("atmosphere/aerial-fog/where.md", [RTR, HILLAIRE20, WRONSKI])
pg.Refs("atmosphere/aerial-fog/index.md", [HILLAIRE20, WRONSKI, BEER, RTR])

# ================================================================ god rays
pg.Dedup("atmosphere/god-rays/index.md")
pg.Add("atmosphere/god-rays/index.md", '''
## ゴッド レイとは

**雲の切れ間**、**木々の間**、**窓**から、**差し込む、光の筋**です（**光芒**、**クレパスキュラー レイ**とも）。**空気中の、細かい粒子**（霧、ほこり、水蒸気）が、**光の通り道を、散乱して、見えるようにする**現象です。**光が、遮られた場所**（影）は、**暗く**、**光が、通った、場所**だけが、**明るい筋**になります。

```text
        太陽
         ╲  ╲  ╲
          ╲  ╲  ╲          ← 光の筋（空気の粒子が、散乱して、光って見える）
    ██████╲  ╲██╲████       ← 遮蔽物（木、建物）の隙間を、光が、通る
          ╲   ╲
       ───────────── 地面
```

**光の筋が、見える、条件**は、**3 つ**です。

| 条件 | 内容 |
| --- | --- |
| **光源が、強い** | 太陽、強い、ライト |
| **空気中に、粒子**（霧、ほこり） | 散乱する、**媒質**が、必要。**澄んだ空気**では、筋が、見えない |
| **遮蔽物が、あり、光が、部分的に遮られる** | **光と影の、コントラスト**が、筋を作る |

## 実装方法の、一覧

| 方法 | 内容 | 品質 | コスト | ページ |
| --- | --- | --- | --- | --- |
| **放射状ブラー**（画面空間） | **太陽の、画面上の位置**から、**放射状**に、明るい部分を、**引き伸ばす** | 低〜中 | **小** | [Screen-Space Radial Blur](radial-blur.md) |
| **シャドウ マップ レイマーチ** | 視線に沿って、**各点が、光を受けているか**（シャドウ マップ）を、**積分** | **高** | 中〜大 | [Shadow Map Raymarching](shadowmap-march.md) |
| **ボリューム ライティング**（froxel） | 空間を、**3D グリッド**に、分割し、**光の、散乱を、格納** | **高**（**霧と、統合**） | 中 | [Volume-Based God Rays](volume.md)、[Volumetric Fog](../volumetric-fog/index.md) |
| **光の筋の、メッシュ** | **半透明の、板**を、置く | 低〜中（**アーティスト制御**） | 小 | [Light Shaft Meshes](mesh-shafts.md) |

## 選び方

| 状況 | おすすめ |
| --- | --- |
| **まず、出したい**、軽く | 放射状ブラー（[Screen-Space Radial Blur](radial-blur.md)） |
| **影の、正確さ**が、欲しい（木漏れ日） | シャドウ マップ レイマーチ |
| **霧の、全体**を、リアルにしたい | **ボリューム フォグ**（froxel。光の筋も、同時に、出る） |
| **特定の場所**（窓、洞窟の入口）に、**演出**として | 光の筋の、メッシュ |

近年の、ゲームでは、**ボリューム フォグ**（[Volumetric Fog](../volumetric-fog/index.md)）に、**統合**されることが、**多く**、**霧と、光の筋**が、**同じ、計算**で、出ます。

## 調整の、ポイント

| 項目 | 内容 |
| --- | --- |
| **強さ** | **強すぎる**と、**画面が、白く、もやもや**する。**控えめ**に |
| **色** | 太陽の色（**暖色**）。**朝夕は、橙**。**青い、空の光**は、筋に、ならない |
| **方向性** | **太陽の方を、見たとき**に、**強く**（前方散乱）。**太陽に、背を向ける**と、**弱い**（[Tuning the Look](tuning.md)） |
| **ちらつき** | **レイマーチの、ステップ数が、少ない**と、**縞**が、出る。**ノイズ + TAA** で、**ならす**（[Cloud Temporal Reprojection](../clouds/temporal.md)） |

''', before="## よくあるミス")
pg.Refs("atmosphere/god-rays/index.md", [MITCHELL, MITCHELL04, WRONSKI, HILLAIRE15, RTR])

pg.Dedup("atmosphere/god-rays/radial-blur.md")
pg.Add("atmosphere/god-rays/radial-blur.md", '''
## 画面空間の、放射状ブラー

**放射状ブラー**（Mitchell、2007）は、**画面に、描かれた、画像**を、**太陽の画面上の位置**から、**放射状**に、**ぼかして**（引き伸ばして）、**光の筋**を、作ります。**3D の、シーンを、再計算せず**、**画面の、画像だけ**で、行うので、**非常に、軽い**です。

```text
 画面:  太陽（画面上の点）●
         ╲   ╲   ╲
          ╲   ╲   ╲        各画素から、太陽に向かって、何回か読んで、明るさを足す
           ・   ・   ・
```

## 手順

| 手順 | 内容 |
| --- | --- |
| ① **光の、マスク**を作る | **太陽の、円盤**と、**明るい空**を、**白**、**遮蔽物**（木、建物）を、**黒**にした画像（**低解像度**） |
| ② **放射状に、ぼかす** | **各画素**から、**太陽の画面位置**へ向かって、**数十回、読んで、足す**。**明るい部分が、太陽から、放射状に、伸びる** |
| ③ **合成** | ぼかした結果を、**加算ブレンド**で、シーンに、足す |

## ① 光の、マスク

**シーンを、白黒に**します。**空（太陽）は、明るく**、**物体は、黒**にします。**物体の、隙間から、空が、見える所**だけが、**明るく**残ります。

```hlsl
// 光のマスク: 深度が最大（空）の画素は、シーンの色を、そのまま。物体の画素は、黒。
float3 LightMaskPS(float2 uv : TEXCOORD0) : SV_Target {
  float depth = g_scene_depth.Sample(g_point_clamp, uv).r;
  float3 color = g_scene_color.Sample(g_linear_clamp, uv).rgb;
  float is_sky = step(0.9999, depth);                    // 深度が、ほぼ最大 = 空
  // 太陽の円盤、明るい空だけを、取り出す。しきい値で、明るい部分に、絞ってもよい。
  return color * is_sky;
}
```

`step(0.9999, depth)` で、**空の画素だけ**を、**1**、**物体の画素**を **0** にします。**空の色**（太陽の、周りの明るさ）が、**マスク**の、**明るさ**になります。**画面の、半分または、1/4 の、解像度**で、描くと、**後の、ぼかしが、軽く**なります。

## ② 放射状に、ぼかす

```hlsl
// 太陽の画面上の位置（0〜1 の uv）から、各画素に向かって、何度か読んで、足す。
float4 RadialBlurPS(float2 uv : TEXCOORD0) : SV_Target {
  const int kSamples = 48;
  float2 delta = (uv - g_sun_screen_uv) * (g_density / kSamples);   // 太陽から、この画素への、向きと、1 歩の長さ
```

`delta` は、**この画素から、太陽へ向かう、1 歩**です（**逆向き**に進むので、符号は、`uv − sun`）。`g_density` が、**筋の、長さ**（大きいほど、**遠くまで、読む**）を、決めます。

```hlsl
  float2 sample_uv = uv;
  float illumination_decay = 1.0;                                    // 減衰（遠くを、読んだ分ほど、弱く）
  float3 sum = 0.0;
  for (int i = 0; i < kSamples; ++i) {
    sample_uv -= delta;                                              // 太陽に向かって、1 歩進む
    float3 s = g_light_mask.SampleLevel(g_linear_clamp, sample_uv, 0).rgb;
    sum += s * illumination_decay * g_weight;
    illumination_decay *= g_decay;                                   // 1 回ごとに、弱める（0.95〜0.99）
  }
  return float4(sum, 1.0);
}
```

**太陽に向かって**、**48 回**、**マスクを読み**、**明るさを、足し合わせます**。**途中に、遮蔽物**（黒）が、あれば、**その分、暗く**なり、**空が、見える方向**は、**明るい**ので、**光の筋と、影**が、**放射状に**、現れます。`g_decay`（減衰）は、**遠くを読むほど、弱く**する、重みです。**1 に近い**ほど、**筋が、長く**伸びます（[Tuning the Look](tuning.md)）。

## ③ 合成

```hlsl
// 放射状ブラーの結果を、太陽の色で着色して、シーンに加算する。
float3 rays = g_radial_blur.Sample(g_linear_clamp, uv).rgb * g_sun_color * g_intensity;
float3 final_color = scene_color + rays;
```

**加算ブレンド**で、**シーンに、足す**だけです。**HDR で、足す**と、**ブルーム**（[Bloom](../../postprocess/bloom/index.md)）と、**組み合わさって**、**まぶしい**筋になります。

## 太陽が、画面の外にある

**太陽が、画面の外**（背後、または、画面の端の外）にあるとき、**放射状ブラー**の、**起点**が、**画面の外**になり、**計算が、不安定**になります。

| 状況 | 対策 |
| --- | --- |
| 太陽が、**カメラの、背後** | 筋を、**消す**（太陽の方向と、視線の、内積が、負なら、強さ 0） |
| 太陽が、**画面の外**（横） | **画面の、端の外まで、計算**する（起点は、uv の範囲外でも、よい）。**太陽に、近いほど、強く**、**離れるほど、フェード** |
| 太陽が、**真上**や、**地平線の下** | 太陽が、地平線の下なら、**筋を、消す** |

```hlsl
// 太陽の方向に応じた、フェード。視線が、太陽の方を、向いているほど、強い。
float facing = saturate(dot(g_camera_forward, g_sun_dir));
float intensity = g_intensity * pow(facing, 3.0);
```

## 長所と短所

| | 内容 |
| --- | --- |
| 長所 | **軽い**（低解像度の、後処理。**数十回の、テクスチャ読み込み**） |
| 長所 | **実装が、簡単** |
| 短所 | **画面の中に、太陽（または、明るい空）が、映って**いないと、**出ない**（光が、**画面の外から**、**差し込む**場合は、**不正確**） |
| 短所 | **影の、正確さ**が、無い（**画面に、映った、明るい空**しか、使えない） |
| 短所 | **視点（カメラの向き）に、依存**し、**視線を、動かすと、筋が、ずれる** |
| 短所 | **読み込みの、回数が、少ない**と、**縞**が、出る |

''', before="## よくあるミス")
pg.Refs("atmosphere/god-rays/radial-blur.md", [MITCHELL, MITCHELL04, RTR])

pg.Dedup("atmosphere/god-rays/shadowmap-march.md")
pg.Add("atmosphere/god-rays/shadowmap-march.md", '''
## シャドウ マップで、光の通り道を、調べる

**放射状ブラー**（[Screen-Space Radial Blur](radial-blur.md)）は、**画面の画像**だけを、使うので、**影の正確さ**が、ありません。**シャドウ マップ**を、使うと、**視線に沿った、各点が、太陽の光を、受けているか**が、**正確に**、分かります。

## 考え方

**カメラから、各画素へ向かう、視線**を、**細かく、区切って**、**各点で、2 つのこと**を、調べます。

| 調べること | 内容 |
| --- | --- |
| **光が、届いているか** | その点は、**シャドウ マップ**で、**影の外**か（**太陽の光が、届く**） |
| **どれだけ、散乱するか** | **霧の密度** × **位相関数**（太陽の方向への、前方散乱） |

**光が、届いている点の、散乱光だけ**を、**足し合わせる**と、**光の筋**（**光が、通る、道筋**）が、**現れます**。

```text
視線 ●────●────●────●────●────●
カメラ   光   影   影   光   光       ← 各点で、影かどうかを、シャドウ マップで調べる
         ↑                          光の点だけ、散乱光を、足す
```

## 実装

```hlsl
// 視線に沿って、シャドウ マップを引きながら、散乱光を、積分する。
float3 GodRays(float3 camera, float3 world_pos, float2 screen_pos) {
  const int kSteps = 32;
  float3 ray = world_pos - camera;
  float ray_length = length(ray);
  float3 ray_dir = ray / ray_length;
  float step_len = ray_length / kSteps;
```

**カメラから、その画素の、物体まで**の、視線を、**32 区間**に、分けます。**物体より、奥は、積分しません**（物体で、視線が、止まる）。

```hlsl
  // ステップの開始位置を、ノイズで、ずらす（縞を、細かいノイズに、変える）。
  float jitter = InterleavedGradientNoise(screen_pos);
  float3 sum = 0.0;
  float cos_theta = dot(ray_dir, g_sun_dir);
  float phase = HenyeyGreenstein(cos_theta, 0.7);               // 太陽の方向への、前方散乱
```

**開始位置を、ノイズで、ずらす**（ジッター）と、**縞（バンディング）**が、**細かいノイズ**に、変わり、**TAA** で、**なめらか**に、ならされます（[Cloud Temporal Reprojection](../clouds/temporal.md)）。**位相関数**は、**視線に沿って、一定**なので、**ループの外**で、1 回です。

```hlsl
  for (int i = 0; i < kSteps; ++i) {
    float3 p = camera + ray_dir * ((i + jitter) * step_len);
    float shadow = SampleShadowMap(p);                          // 1 = 光が届く、0 = 影
    sum += shadow;
  }
```

**各点の、ワールド位置**を、**シャドウ マップの座標**へ、変換して、**影かどうか**を、調べます（[Comparison Samplers](../../shadows/shadow-map-basics/comparison-sampler.md)）。**光が、届く点**（`shadow = 1`）だけが、**足される**ので、**影に、入った、区間は、足されません**。

```hlsl
  // 平均を取り、散乱の量（霧の密度 × 距離）と、位相関数、太陽の色を、掛ける。
  float scatter_amount = 1.0 - exp(-g_fog_density * ray_length);     // 霧の、全体の、厚み
  return (sum / kSteps) * scatter_amount * phase * g_sun_color;
}
```

**光が、届いた区間の、割合**（`sum / kSteps`）に、**霧の厚み**と、**位相関数**、**太陽の色**を、掛けます。**光が、多く届く**（影が、少ない）視線ほど、**明るい**筋に、なります。

## シャドウ マップの、読み方

**視線に沿った、各点**は、**空間の、あらゆる場所**にあるので、**シャドウ マップ**（カスケード）の、**どの範囲に、入るか**を、**判定**して、**適切な、カスケード**を、引きます（[CSM](../../shadows/cascaded.md)）。**遠い点**は、**カスケードの、外**に、なることが、あり、**影なし**（光が、届く）と、みなします。

```hlsl
float SampleShadowMap(float3 world_pos) {
  // どのカスケードに入るかを調べ、そのカスケードの、シャドウ マップを、比較サンプラーで引く。
  int cascade = SelectCascade(world_pos);
  if (cascade < 0) return 1.0;                                   // 範囲の外 → 影なし
  float4 shadow_coord = mul(float4(world_pos, 1.0), g_cascade_matrix[cascade]);
  return g_shadow_map.SampleCmpLevelZero(g_shadow_sampler, float3(shadow_coord.xy, cascade), shadow_coord.z);
}
```

## 計算量と、最適化

**画面の全画素**に対して、**32 ステップ**の、ループを、回すと、**非常に、重い**です（1080p で、約 6,600 万回の、シャドウ マップ読み込み）。

| 最適化 | 内容 |
| --- | --- |
| **低解像度**（半分、1/4）で計算 | 画素数が、1/4〜1/16。**アップサンプル**（深度を、考慮した、バイラテラル）で、元の、解像度へ |
| **ステップ数を、減らす** + **ジッター** + **TAA** | 16 ステップでも、**ノイズ + 時間方向の、平均**で、**なめらか**に |
| **近い範囲のみ** | **カメラの、近くだけ**（数十メートル）を、レイマーチ。遠くは、**簡易な霧** |
| **ボリューム テクスチャ**（froxel）に、まとめる | **画素ごとに、レイマーチ**する代わりに、**3D グリッド**に、**1 回だけ計算**（[Volumetric Fog](../volumetric-fog/index.md)） |

## 長所と短所

| | 内容 |
| --- | --- |
| 長所 | **影の、形が、正確**に、光の筋に、反映される（**木漏れ日**、窓の形） |
| 長所 | **太陽が、画面の外**でも、**動く** |
| 長所 | **霧の、密度を、場所で、変えられる**（霧の、**濃淡**が、光に、反映） |
| 短所 | **重い**（**画素 × ステップ**） |
| 短所 | **ノイズ**（ステップが、少ないとき） |
| 短所 | **シャドウ マップの、解像度**に、依存する（**遠くは、粗い**） |

''', before="## よくあるミス")
pg.Refs("atmosphere/god-rays/shadowmap-march.md", [MITCHELL04, WRONSKI, HILLAIRE15, JIMENEZ, RTR])

pg.Dedup("atmosphere/god-rays/volume.md")
pg.Add("atmosphere/god-rays/volume.md", '''
## ボリュームで、ゴッド レイを、作る

**ボリューム ライティング**（**froxel**、[Froxels](../volumetric-fog/froxel.md)）は、**カメラの、前方の、空間**を、**3D グリッド**に、分割し、**各セルに、光の、散乱**を、**事前に、計算**しておきます。**画素ごとの、レイマーチ**（[Shadow Map Raymarching](shadowmap-march.md)）を、**セルごとの、計算に、置き換える**ので、**効率的**です。**ゴッド レイは、このボリュームの、副産物**として、**自動で**、現れます。

## 考え方

**カメラから見て、奥行き方向に、分割された、セル**（froxel、「フラスタム」+「ボクセル」）の、各セルで、**光の、散乱**（太陽の、光が、そのセルで、**カメラの方へ、散る**量）を、**計算**して、**3D テクスチャ**に、**格納**します。**画面の、各画素**は、**視線に沿って、セルを、順に、足して**、**散乱光を、合計**します。

```text
3D テクスチャ（froxel）: 横 × 縦 × 奥行き（160 × 90 × 64 など）

カメラ ●─────→ 奥行き方向に、セルを、足していく（積分）
        [セル0][セル1][セル2]...[セル63]
```

## ボリュームを、作る：光の、注入

**各セル**に、**太陽の光**を、**注入**します。**セルの、位置が、影の中か**を、**シャドウ マップ**で、調べ、**光が、届くセルだけ**、**散乱光**を、格納します。

```hlsl
// 計算シェーダー: 各セルに、太陽の光の、散乱を、書き込む。
[numthreads(8, 8, 4)]
void InjectLightCS(uint3 id : SV_DispatchThreadID) {
  float3 cell_world = FroxelToWorld(id);                         // セルの中心の、ワールド位置
  float density = SampleFogDensity(cell_world);                   // そのセルの、霧の密度

  // 太陽の光が、届いているか（シャドウ マップ）。1 = 届く、0 = 影。
  float shadow = SampleShadowMap(cell_world);

  // 視線の方向（カメラから、セルへ）と、太陽の、間の位相関数。
  float3 view_dir = normalize(cell_world - g_camera_position);
  float phase = HenyeyGreenstein(dot(view_dir, g_sun_dir), g_phase_g);

  // 散乱光 = 密度 × 光が届く割合 × 位相関数 × 太陽の光
  float3 scattering = g_sun_color * shadow * phase * density;
  g_froxel_scatter[id] = float4(scattering, density);              // 散乱光と、消散（密度）を、格納
}
```

**シャドウ マップの、読み込み**は、**セルごとに、1 回**です。**画素ごと、ステップごと**の、レイマーチ（[Shadow Map Raymarching](shadowmap-march.md)）より、**はるかに、少ない回数**で、済みます（160×90×64 = 約 92 万セル）。

## ボリュームを、積分する

**奥行き方向**に、**手前から奥へ**、**散乱光を、累積**しながら、**透過率**を、**更新**します。

```hlsl
// 計算シェーダー: 各 (x, y) の列について、奥行き方向に、散乱光を、累積する。
[numthreads(8, 8, 1)]
void IntegrateCS(uint3 id : SV_DispatchThreadID) {
  float3 accumulated = 0.0;
  float transmittance = 1.0;
  for (uint z = 0; z < kFroxelDepth; ++z) {
    float4 cell = g_froxel_scatter[uint3(id.xy, z)];              // xyz = 散乱光、w = 密度（消散）
    float step_len = SliceThickness(z);                           // このスライスの、厚み（メートル）
    float cell_transmittance = exp(-cell.w * step_len);           // このセルを、通る、透過率

    // 区間内の積分（解析的）: 散乱光 × (1 − 透過率) / 消散
    float3 integral = cell.xyz * (1.0 - cell_transmittance) / max(cell.w, 1e-5);
    accumulated += transmittance * integral;                       // ここまでの、透過率を、掛けて、足す
    transmittance *= cell_transmittance;

    g_froxel_integrated[uint3(id.xy, z)] = float4(accumulated, transmittance);   // 「カメラから、スライス z まで」の結果
  }
}
```

**奥行き方向の、累積**を、**各スライス**に、**保存**しておくと、**画面の画素**は、**自分の、深度に、対応するスライス**を、**1 回読む**だけで、**カメラから、その物体までの、散乱光と、透過率**を、**得られます**。

## 画面に、適用する

```hlsl
// 物体の色に、ボリューム ライティングを、適用する。
float3 ApplyVolumetric(float3 scene_color, float2 screen_uv, float distance_m) {
  float slice = DistanceToSlice(distance_m);
  float4 v = g_froxel_integrated.SampleLevel(g_linear_clamp, float3(screen_uv, slice), 0);
  return scene_color * v.a + v.rgb;                                // 物の色 × 透過率 + 散乱光
}
```

**物体の色に、透過率を掛け**、**散乱光を足す**。**霧の式と、同じ形**ですが、**散乱光に、影と、光の筋が、含まれている**点が、違います。

## 長所と短所

| | 内容 |
| --- | --- |
| 長所 | **画素ごとの、レイマーチより、効率的**（**セルごとに、1 回**） |
| 長所 | **霧の密度**（場所で、変わる）、**局所光**（ランプ、ライトの、散乱）も、**同じ仕組みで、扱える**（[Light Injection](../volumetric-fog/injection.md)） |
| 長所 | **半透明の物**にも、**同じ、ボリュームを、引くだけ**で、適用できる |
| 長所 | **時間方向の、フィルタ**（TAA）で、品質を、上げられる（[Temporal Accumulation](../volumetric-fog/temporal.md)） |
| 短所 | **解像度が、低い**（画面の 1/8 程度）。**細かい、光の筋は、ぼやける** |
| 短所 | **奥行き方向の、分割**による、**縞**（[Quality and Performance](../volumetric-fog/quality.md)） |
| 短所 | **メモリ**（3D テクスチャ数枚） |

''', before="## よくあるミス")
pg.Refs("atmosphere/god-rays/volume.md", [WRONSKI, HILLAIRE15, HILLAIRE16, RTR])

pg.Dedup("atmosphere/god-rays/mesh-shafts.md")
pg.Add("atmosphere/god-rays/mesh-shafts.md", '''
## 光の筋を、メッシュで、描く

**計算で、光の筋を、作る**代わりに、**半透明の、板（メッシュ）**を、**光の通り道に、置き**、**光の筋に、見える、テクスチャ**を、貼る方法です。**アーティストが、完全に、制御**でき、**非常に、軽い**ので、**特定の場所**（窓、洞窟の、入口、森の、木漏れ日）の、**演出**に、使われます。

## 作り方

| 要素 | 内容 |
| --- | --- |
| **メッシュ** | 光の筋の、方向（**太陽の方向**）に、沿って、**細長い、板**（または、円錐、箱）を、置く |
| **テクスチャ** | **縦方向に、薄れる**グラデーション。**横方向**に、**縁が、なめらか**。**縞（細かい筋）**を、描いてもよい |
| **ブレンド** | **加算**ブレンド（光の、足し算）。**重なる所が、明るく**なる |
| **ライト** | **ない**（自己発光）。**太陽の色**を、**マテリアルの色**で、与える |

```text
窓から、差し込む、光の筋（横から見た図）:

   窓
   │ ╲    ← 板（光の筋）。窓から、床に向かって、広がる
   │  ╲
   │   ╲
   └────╲──── 床
```

## シェーダー

```hlsl
float4 main(PSInput input) : SV_Target {
  // 縞のテクスチャ（縦方向に、細かい筋）。
  float stripes = g_shaft_tex.Sample(g_linear_wrap, input.uv * float2(4.0, 1.0)).r;

  // 長さ方向（窓 → 床）に、薄れる。0（窓）で 1、1（床）で 0。
  float along = 1.0 - input.uv.y;

  // 横方向（板の幅）に、縁を、なめらかに。中心で 1、縁で 0。
  float across = 1.0 - abs(input.uv.x * 2.0 - 1.0);
  across = smoothstep(0.0, 0.5, across);

  float intensity = stripes * along * across * g_intensity;
  return float4(g_sun_color * intensity, 1.0);                    // 加算ブレンドで、描く
}
```

**3 つの要素**（縞、長さ方向の、減衰、横方向の、縁）を、**掛け合わせて**、**光の筋の、形**を、作ります。**縞のテクスチャ**で、**細かい筋**（空気中の、ほこりが、作る、不均一さ）を、与えます。

### ゆらぎ

**光の筋が、ゆらゆら、動く**と、**生きた、空気**に、見えます。**縞の、UV を、時間で、ずらす**、**強さを、ゆっくり、脈打たせる**。

```hlsl
float flicker = 0.85 + 0.15 * sin(g_time * 0.7 + input.world_position.x * 0.3);   // ゆっくり、脈打つ
float2 scroll = float2(g_time * 0.02, 0.0);
float stripes = g_shaft_tex.Sample(g_linear_wrap, input.uv * float2(4.0, 1.0) + scroll).r;
```

## 近くで、見たとき

**板**は、**平らな面**なので、**カメラが、近づく**と、**板の、縁**が、見え、**不自然**になります。

| 問題 | 対策 |
| --- | --- |
| 板の、**縁が、見える** | **視線に平行な向き**（板を、真横から見る）で、**縁が、薄く**なるよう、**法線と視線の、内積**で、**フェード** |
| 板に、**近づきすぎる** | **カメラに、近い**ほど、**フェード アウト**（ソフト パーティクルと、同じ。[Soft Particles](../../translucency/blending-sorting/soft-particles.md)） |
| 床や壁との、**交差線** | **深度の差**で、**フェード**（[Soft Particles](../../translucency/blending-sorting/soft-particles.md)） |

```hlsl
// 板が、視線と、ほぼ平行（縁が見える角度）のとき、薄くする。
float facing = abs(dot(normalize(input.world_normal), normalize(g_camera_position - input.world_position)));
intensity *= smoothstep(0.0, 0.4, facing);
```

## 長所と短所

| | 内容 |
| --- | --- |
| 長所 | **非常に、軽い**（半透明の、板を、数枚、描くだけ） |
| 長所 | **アーティストの、完全な、制御**（形、色、動き） |
| 長所 | **カメラ・太陽の、位置に、依存しない**（常に、同じ形で、見える） |
| 短所 | **影や、遮蔽物と、連動しない**（**動く物**が、光を、遮っても、筋が、変わらない） |
| 短所 | **太陽が、動く**（時間帯）と、**板の向き**を、**合わせる**必要がある（**手動**） |
| 短所 | **近くで、見ると、板だと、分かる** |
| 短所 | **配置が、手作業**（レベルデザイナーが、置く） |

## 使いどころ

| 場面 | 判断 |
| --- | --- |
| **固定の、演出**（教会の窓、洞窟の穴） | **適している**（光の筋が、**変わらない**） |
| **動く、太陽**で、**屋外全体** | **不向き**（[Volume-Based God Rays](volume.md) など） |
| **モバイル、低スペック** | **有効**（計算が、ほぼ、不要） |

''', before="## よくあるミス")
pg.Refs("atmosphere/god-rays/mesh-shafts.md", [MITCHELL, RTR, "Microsoft Learn, \"D3D11_RENDER_TARGET_BLEND_DESC\"（加算ブレンド）"])

pg.Dedup("atmosphere/god-rays/tuning.md")
pg.Add("atmosphere/god-rays/tuning.md", '''
## 調整の、パラメーター

ゴッド レイは、**強すぎると、画面が、白く、もやもや**し、**弱すぎると、見えません**。**主要な、パラメーター**の、**意味と、効き方**を、整理します。

| パラメーター | 意味 | 大きくすると | 目安 |
| --- | --- | --- | --- |
| **強さ**（intensity） | 光の筋の、明るさ | **明るく**、画面が、白っぽく | 0.1〜1 |
| **密度**（density） | 放射状ブラーで、**どこまで**、遠くを読むか | **筋が、長く**伸びる | 0.5〜1 |
| **減衰**（decay） | **遠くの、サンプル**の、重み（読むたびに、掛ける） | **筋が、遠くまで**（1 に近い） | 0.95〜0.99 |
| **重み**（weight） | **1 回の、サンプル**の、寄与 | 全体が、**明るく** | 0.01〜0.1 |
| **位相関数の `g`** | **太陽の方向への、偏り** | **太陽の近く**だけが、明るく | 0.6〜0.9 |
| **霧の密度** | 散乱する、**粒子の、濃さ** | **筋が、はっきり**（濃い霧で、強く） | 場面による |
| **サンプル数** | 放射状ブラー / レイマーチの、読み込み回数 | **なめらか**（ノイズ・縞が、減る） | 32〜64 |

## 見た目を、決める、3 つの、考え方

### ① 太陽の、方向を、強調する

光の筋は、**太陽の方を、見たとき**に、**最も、はっきり**見えます（**前方散乱**）。**太陽に、背を向けた**ときは、**ほぼ、見えません**。**位相関数**（[Phase Functions](../scattering/phase-function.md)）と、**視線と太陽の、角度**で、**強さを、変えます**。

```hlsl
// 太陽を、向いているほど、強く。背を向けたら、ほぼ 0。
float facing = saturate(dot(g_camera_forward, g_sun_dir));
float strength = g_intensity * pow(facing, 2.0);
```

### ② 色を、太陽に、合わせる

光の筋の色は、**太陽の色**（**大気を通った後の、色**）です。**昼は、白〜淡い黄色**、**朝夕は、橙〜赤**。**空の、青**を、使うと、**筋が、見えません**（**青い光の筋**は、**不自然**）。

```hlsl
float3 ray_color = SunColorAtGround(g_sun_dir) * g_intensity;       // 大気の透過率を、掛けた、太陽の色
```

### ③ 時間帯で、強さを、変える

| 時間帯 | 光の筋 |
| --- | --- |
| 正午（太陽が、高い） | **弱い**（光が、**ほぼ、真上から**、筋が、**短い**。空気も、**澄んでいる**） |
| **朝・夕**（太陽が、低い） | **強い**（光が、**斜めに、長く**、通る。**霧・もやも、多い**） |
| 夜 | **なし**（太陽が、地平線の下） |

**ゴッド レイが、最も、美しいのは、朝夕**です。**太陽の高さ**に応じて、**強さを、変える**と、**時間帯の、雰囲気**が、**ぐっと、増します**。

```hlsl
float sun_height = g_sun_dir.y;                                       // 1 = 真上、0 = 地平線
float time_of_day_factor = lerp(1.0, 0.3, saturate(sun_height * 2.0));   // 低いほど、強く
```

## 品質を、損なう、問題

| 症状 | 原因 | 対策 |
| --- | --- | --- |
| **縞**（バンディング） | サンプル数が、**少ない** | **ジッター**（ノイズで、開始位置を、ずらす）+ **TAA**。サンプル数を、増やす |
| **画面全体が、白く、もやもや** | **強さが、強すぎる**、**重み・減衰の、設定** | 強さを、**下げる**。**しきい値**で、**非常に、明るい部分**だけを、光源に |
| **筋が、画面の、端で、途切れる** | 放射状ブラーの、**起点が、画面の外** | 起点が、画面の外でも、**計算**し、**端で、フェード** |
| **太陽の周りに、四角い、アーティファクト** | 低解像度の、マスクの、**補間** | マスクを、**バイラテラル**で、アップサンプル、解像度を、上げる |
| **筋が、ちらつく** | **TAA の、履歴**が、**不安定** | **履歴の、クランプ**（[Cloud Temporal Reprojection](../clouds/temporal.md)） |
| 木の**葉の、隙間**が、**ざらざら** | アルファ テストの、**ジャギー** | 光のマスクを、**ぼかして**から、放射状ブラーへ |

## ブルームと、組み合わせる

**まぶしい**、光の筋は、**ブルーム**（[Bloom](../../postprocess/bloom/index.md)）と、**一緒**に、使うと、**映えます**。**ゴッド レイを、足した後**に、ブルームを、かけます。

```text
シーン + ゴッド レイ（加算） → ブルーム → トーン マッピング
```

## 目的に、合わせた、設定

| 目的 | 設定の、方向性 |
| --- | --- |
| **自然な、控えめな**光の筋 | 強さ **小**、**霧の密度**は、場面の霧に、合わせる、**位相関数 `g` = 0.7** |
| **ドラマチックな、演出**（神殿、洞窟） | 強さ **大**、**局所的な、霧**（その場所だけ、濃く）、**筋の、方向**を、固定 |
| **スタイライズ**（アニメ調） | **くっきりした、筋**（ぼかしを、弱く）、**色を、暖色に**、強め |

''', before="## よくあるミス")
pg.Refs("atmosphere/god-rays/tuning.md", [MITCHELL, HILLAIRE15, RTR])

pg.Dedup("atmosphere/god-rays/underwater.md")
pg.Add("atmosphere/god-rays/underwater.md", '''
## 水中の、光の筋

**水中**で、**水面から、差し込む、太陽の光**は、**光の筋**に、なります。**水中の、細かい粒子**（プランクトン、泥）が、**光を、散乱**して、**光の通り道を、見せる**ためです。**空気中の、ゴッド レイ**と、**同じ原理**ですが、**水の、吸収**（**赤が、先に消える**）と、**波による、揺れ**が、加わります。

詳しい、実装は、**水の、セクション**で、扱っています（[Underwater God Rays](../../water/underwater/god-rays.md)）。ここでは、**空気中との、違い**を、整理します。

## 空気中との、違い

| 項目 | 空気中 | 水中 |
| --- | --- | --- |
| **光の、色** | 太陽の色（白、橙） | **青緑**（**赤が、吸収**される） |
| **減衰** | **ゆるやか**（数 km） | **急**（**数十 m** で、消える） |
| **光の筋の、揺れ** | ほぼ、無し（霧の、ゆらぎ） | **波**による、**強い、揺れ**（**コースティクス**） |
| **光の向き** | 太陽の方向 | **水面で、屈折**して、**真下に、近づく**（最大で、約 48.6°） |
| **見える、距離** | **長い** | **短い**（水の濁りで、数 m〜数十 m） |

## 色と、減衰

**水中の、光の筋の色**は、**水面から、そこまでの、深さ**に応じて、**赤から、順に、吸収**されます。**浅い所**は、**明るい青緑**、**深くなる**ほど、**暗い青**です。

```hlsl
// 水中の光の筋: 水面からの深さと、カメラまでの距離の、両方で、減衰させる。
float3 UnderwaterSunColor(float depth_below_surface, float distance_to_camera) {
  float3 sun_at_depth = g_sun_color * exp(-g_absorption * depth_below_surface);       // 水面 → この点（太陽の光）
  float3 to_camera = exp(-g_absorption * distance_to_camera);                          // この点 → カメラ（散乱した光）
  return sun_at_depth * to_camera;
}
```

**2 回の減衰**（**太陽 → 点**、**点 → カメラ**）が、**両方**、効きます。**どちらも、Beer の法則**です。**深く、遠い**光の筋は、**ほぼ見えません**。

## 光の向き（屈折）

**太陽の光**は、**水面で、屈折**して、**水中へ**入ります。**水中での、光の向き**は、**空気中**と**違います**。

```hlsl
// 水中での、太陽の光の向き。水面の法線は、真上 (0, 1, 0) とする（波は、無視）。
float3 UnderwaterLightDir(float3 sun_dir) {
  // sun_dir は、光が来る向き（太陽へ向かう）。進む向きは、逆。
  return refract(-sun_dir, float3(0, 1, 0), 1.0 / 1.33);
}
```

**太陽が、地平線に近い**（斜めの、光）ほど、**水中では、真下に近づく**（**スネルの法則**）ので、**光の筋は、常に、ほぼ、下向き**です。

## 波による、揺れ

**水面の、波**は、**レンズ**のように、光を、**集めたり、散らしたり**します（**コースティクス**）。**光の筋の、強さ**を、**コースティクスの模様**で、**変調**します（[Caustics](../../water/underwater/caustics.md)）。

```hlsl
// 光の筋の強さに、コースティクスの模様を、掛ける。波が、動くと、光の筋も、ゆらぐ。
float caustic = SampleCaustic(p);                                     // 水面の波が作る、光の濃淡
scatter *= caustic;
```

**水面が、揺れる**と、**水中の、光の筋が、ゆらゆらと、揺れ動き**ます。**水中らしさ**を、**強く**与える、**重要な、効果**です。

## 手法の、選択

| 手法 | 水中での、使い方 |
| --- | --- |
| **放射状ブラー** | **水面（明るい、窓）**を、光源として、**放射状に、ぼかす**。**簡単**で、**軽い** |
| **シャドウ マップ レイマーチ** | **岩や、船の、影**で、光の筋が、**遮られる**。**波の、コースティクス**で、**変調**。**正確**（重い） |
| **光の筋の、メッシュ** | **水面から、下へ**、**板**を置く。**アーティスト制御**。**軽い** |
| **ボリューム フォグ** | **水中を、ボリュームとして**、扱い、**吸収と散乱**を、**同時に**、計算 |

''', before="## よくあるミス")
pg.Refs("atmosphere/god-rays/underwater.md", [MITCHELL04, "Guardado, Sánchez-Crespo, \"Rendering Water Caustics\", GPU Gems, Chapter 2, 2004", "Pope, Fry, \"Absorption Spectrum (380–700 nm) of Pure Water. II. Integrating Cavity Measurements\", Applied Optics, Vol. 36, No. 33, 1997", RTR])
print("ok")
