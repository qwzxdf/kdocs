import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import pg  # noqa: E402

SCHNEIDER15 = '''Schneider, Vos, "The Real-Time Volumetric Cloudscapes of Horizon: Zero Dawn", SIGGRAPH 2015, Advances in Real-Time Rendering in Games'''
SCHNEIDER17 = '''Schneider, "Nubis: Authoring Real-Time Volumetric Cloudscapes with the Decima Engine", SIGGRAPH 2017, Advances in Real-Time Rendering in Games'''
HILLAIRE16 = '''Hillaire, "Physically Based Sky, Atmosphere and Cloud Rendering in Frostbite", SIGGRAPH 2016, Physically Based Shading in Theory and Practice'''
HILLAIRE15 = '''Hillaire, "Physically Based and Unified Volumetric Rendering in Frostbite", SIGGRAPH 2015, Advances in Real-Time Rendering in Games'''
WRONSKI = '''Wronski, "Volumetric Fog: Unified Compute Shader Based Solution to Atmospheric Scattering", SIGGRAPH 2014, Advances in Real-Time Rendering in Games'''
WRENNINGE = '''Wrenninge, "Art-Directable Multiple Volumetric Scattering", SIGGRAPH 2015 Talks'''
KARIS = '''Karis, "High Quality Temporal Supersampling", SIGGRAPH 2014, Advances in Real-Time Rendering in Games'''
PERLIN = '''Perlin, "An Image Synthesizer", SIGGRAPH 1985'''
WORLEY = '''Worley, "A Cellular Texture Basis Function", SIGGRAPH 1996（Worley ノイズ。雲のもこもこに使う）'''
JIMENEZ = '''Jimenez, "Next Generation Post Processing in Call of Duty: Advanced Warfare", SIGGRAPH 2014（Interleaved Gradient Noise）'''
RTR = '''Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（参加媒質、雲、霧の章）'''
BEER = '''Beer, "Bestimmung der Absorption des rothen Lichts in farbigen Flüssigkeiten", Annalen der Physik, 1852'''
HENYEY = '''Henyey, Greenstein, "Diffuse Radiation in the Galaxy", Astrophysical Journal, Vol. 93, 1941'''
D3D11_TEX3D = '''Microsoft Learn, "D3D11_TEXTURE3D_DESC"（3D テクスチャ、`D3D11_BIND_UNORDERED_ACCESS`）'''

# ================================================================ clouds
pg.Dedup("atmosphere/clouds/density-model.md")
pg.Add("atmosphere/clouds/density-model.md", '''
## 雲の、密度を、どう作るか

**ボリューム レンダリング**で、雲を描くには、**空間の、各点での、雲の密度**（どれだけ、濃いか）が、必要です。**3D の、密度の、データ**を、**そのまま**、持つ（**ボクセル**）と、**巨大**になるので、**ノイズ テクスチャを、組み合わせて**、**実行時に、密度を、作ります**（Schneider と Vos、2015）。

| 材料 | 内容 |
| --- | --- |
| **天気マップ**（2D） | **どこに、雲があるか**（カバレッジ）、**どんな種類か**。**大きなスケールの、配置** |
| **基本の形**（3D ノイズ、低周波） | 雲の、**大きな、もこもこの形** |
| **細部**（3D ノイズ、高周波） | 雲の縁の、**細かい、ちぎれ・渦** |
| **高さの、グラデーション** | 雲の種類ごとの、**高さ方向の、密度の、山** |

## 密度を、組み立てる、手順

**5 つの手順**で、密度が、決まります。**1 つずつ、コード**を、追います。

### ① 天気マップから、カバレッジと、種類を読む

```hlsl
// 天気マップ: R = 雲の量（カバレッジ）、G = 雨の確率、B = 雲の種類（0 = 層雲、0.5 = 積雲、1 = 積乱雲）。
float3 weather = g_weather_map.SampleLevel(g_linear_wrap, position.xz * g_weather_scale, 0).rgb;
float coverage = weather.r;
float cloud_type = weather.b;
```

**天気マップ**は、**空を、真上から見た、2D の画像**です。**どこに、雲があるか**（R）、**どんな種類か**（B）を、**画素ごとに、決める**ので、**アーティストが、空の、雲の配置を、描けます**。**位置**（`position.xz`）から、**UV** を、作って、読みます。

### ② 高さの、グラデーション

```hlsl
// 雲の層の中での、高さの割合（0 = 底、1 = 上端）。
float height_fraction = (length(position) - g_cloud_bottom_radius) / (g_cloud_top_radius - g_cloud_bottom_radius);
float gradient = HeightGradient(height_fraction, cloud_type);        // 種類ごとの、高さ方向の、密度の山
```

雲の、**層**（惑星の周りの、球殻）の中で、**どの高さか**を、**0〜1** で、求めます。**種類ごとの、グラデーション**（[Cloud Layers](layers.md)）を、掛けて、**底は、平ら、上端は、丸い**形に、します。

### ③ 基本の、形

```hlsl
// 低周波の 3D ノイズ（Perlin-Worley）: 雲の、大きなもこもこ。R = Perlin-Worley、GBA = 異なる周波数の Worley。
float4 low = g_base_noise.SampleLevel(g_linear_wrap, position * g_base_scale + g_wind_offset, 0);
float low_freq_fbm = low.g * 0.625 + low.b * 0.25 + low.a * 0.125;     // Worley の 3 オクターブを、足す
float base_cloud = Remap(low.r, -(1.0 - low_freq_fbm), 1.0, 0.0, 1.0); // Perlin-Worley を、Worley の fBm で、持ち上げる
base_cloud *= gradient;                                                 // 高さの、グラデーションを、掛ける
```

**基本の形**は、**128³ の、3D テクスチャ**から、読みます。**R チャンネル**は、**Perlin ノイズ**（なめらかな、うねり）に、**Worley ノイズ**（もこもこの、粒）を、**混ぜた**もので、**GBA** は、**周波数の違う、Worley ノイズ**です。**Worley の fBm で、Perlin-Worley を、持ち上げる**（`Remap` の、下限を、動かす）ことで、**雲の、もこもこした、輪郭**が、できます。

```hlsl
// Remap: 値 v を、範囲 [l0, h0] から、範囲 [l1, h1] へ、線形に、写す（範囲の外は、そのまま、外挿）。
float Remap(float v, float l0, float h0, float l1, float h1) {
  return l1 + (v - l0) * (h1 - l1) / (h0 - l0);
}
```

`Remap` は、**この方式の、基本の道具**です。**ノイズの値の、範囲を、動かして**、**雲の量**（カバレッジ）や、**輪郭の、細かさ**を、**調整**します。

### ④ カバレッジを、適用する

```hlsl
// カバレッジ（0〜1）で、雲の量を決める。カバレッジが、大きいほど、下限が、下がり、雲が、増える。
float base_with_coverage = Remap(base_cloud, coverage, 1.0, 0.0, 1.0);
base_with_coverage *= coverage;                                          // カバレッジが、小さいとき、密度も、薄く
```

**カバレッジ**以下の、ノイズの値は、**0**（雲なし）に、切られ、**それより上**が、**雲**になります。**カバレッジが、大きい**ほど、**切られる部分が、減って**、雲が、**増えます**。最後に、**カバレッジを掛けて**、**少ない雲が、薄く**なるようにします。

### ⑤ 細部で、縁を、削る（エロージョン）

```hlsl
// 高周波の 3D ノイズ（Worley の fBm）で、雲の縁を、削って、細かいちぎれを、作る。
float3 high = g_detail_noise.SampleLevel(g_linear_wrap, position * g_detail_scale + g_wind_offset * 0.3, 0).rgb;
float high_freq_fbm = high.r * 0.625 + high.g * 0.25 + high.b * 0.125;
// 底（height_fraction が小さい）では、ノイズを、反転して、ふわっとした底に。上は、そのまま。
float detail_modifier = lerp(high_freq_fbm, 1.0 - high_freq_fbm, saturate(height_fraction * 10.0));
float density = Remap(base_with_coverage, detail_modifier * 0.2, 1.0, 0.0, 1.0);
```

**細部のノイズ**（**32³**）で、**基本の形の、縁**を、**削ります**。**雲の、内側**（密度が、高い所）は、**ほとんど、削られず**、**縁**（密度が、低い所）が、**大きく、削られる**ので、**縁だけ**が、**ちぎれたような、細かい形**に、なります。`height_fraction` で、**底**と**上端**の、削り方を、**変えて**、**底は、ふわっと、上は、もこもこ**に、します。

```hlsl
return max(density, 0.0) * g_density_scale;                              // 負の値を、切り、全体の濃さの、係数を、掛ける
```

## ノイズ テクスチャの、作り方

**ノイズ テクスチャ**は、**事前に、ツールで、作って**、**3D テクスチャ**として、読み込みます（実行時には、作りません）。

| テクスチャ | 大きさ | 内容 |
| --- | --- | --- |
| **基本の形** | 128×128×128（`R8G8B8A8`） | R = Perlin-Worley、G/B/A = Worley（周波数 1×、2×、4×） |
| **細部** | 32×32×32（`R8G8B8A8`） | R/G/B = Worley（周波数 2×、4×、8×） |

```hlsl
// Worley ノイズ（セル ノイズ）: 各セルに、ランダムな点を置き、最も近い点までの、距離を、返す。1 から引いて、「もこもこ」にする。
float Worley3D(float3 p, float frequency) {
  float3 q = p * frequency;
  float3 cell = floor(q);
  float3 f = frac(q);
  float min_dist = 1.0;
  for (int z = -1; z <= 1; ++z)
    for (int y = -1; y <= 1; ++y)
      for (int x = -1; x <= 1; ++x) {
        float3 neighbor = float3(x, y, z);
        float3 point = Hash33(fmod(cell + neighbor, frequency));       // 周期的になるように、frequency で、折り返す
        float d = length(neighbor + point - f);
        min_dist = min(min_dist, d);
      }
  return 1.0 - saturate(min_dist);                                     // 点の近くが、明るい（雲の、もこもこ）
}
```

**Worley ノイズ**（Worley、1996）は、**各セルに、1 つ、ランダムな点**を置き、**各位置から、最も近い点までの、距離**で、**値**を決めます。**1 から引く**と、**点の周りが、明るい、丸い塊**に、なり、**雲の、もこもこ**に、似ます。`fmod(cell + neighbor, frequency)` で、**周期的**に（**端で、つながる**）、**3D テクスチャを、繰り返して、使える**ようにします。

## 風で、動かす

**ノイズの、読み込み位置**を、**時間とともに、ずらす**と、**雲が、風で、流れます**。

```hlsl
float3 wind_offset = g_wind_direction * g_time * g_wind_speed;          // 風の向きに、時間とともに、ずらす
// 基本の形は、ゆっくり、細部は、少し速く（細部が、基本の形の中を、流れる、ように見える）。
float4 low = g_base_noise.SampleLevel(g_linear_wrap, position * g_base_scale + wind_offset, 0);
float3 high = g_detail_noise.SampleLevel(g_linear_wrap, position * g_detail_scale + wind_offset * 1.5, 0).rgb;
```

**基本の形と、細部の、動く速さを、少し、変える**と、**雲が、変形しながら、流れる**ように、見えます（**ただ、並行移動する、だけ**だと、**平板**）。

## 密度の、使い方

ここで、求めた、**密度**は、**レイマーチの、各サンプル**で、**散乱・吸収**の、計算に、使います（[Cloud Raymarching](raymarch.md)）。**密度が、高い所**ほど、**光を、よく散らし、よく、遮ります**。

''', before="## よくあるミス")
pg.Refs("atmosphere/clouds/density-model.md", [SCHNEIDER15, SCHNEIDER17, WORLEY, PERLIN, HILLAIRE16])

pg.Dedup("atmosphere/clouds/layers.md")
pg.Add("atmosphere/clouds/layers.md", '''
## 雲の、種類と、高さ

雲には、**種類**があり、**高さ**と、**形**が、違います。**同じ、ノイズ**から、**種類ごとの、雲**を、作るには、**高さ方向の、密度の、山**（**高さのグラデーション**）を、**変えます**。

| 種類 | 高さ | 形 | 見た目 |
| --- | --- | --- | --- |
| **層雲**（stratus） | 低い（0〜2 km） | **薄く、平ら** | **空を、覆う、灰色の、層**。霧の、持ち上がった、ような |
| **積雲**（cumulus） | 中（1〜3 km） | **もこもこ**。底は、平ら、上は、丸い | **晴れた日の、綿雲** |
| **積乱雲**（cumulonimbus） | 低〜高（1〜12 km） | **非常に高く、伸びる**。上端が、**かなとこ**状 | **入道雲、雷雲** |

## 高さの、グラデーション

**雲の層**（惑星を、覆う、球殻）の中で、**高さの割合**（`h`: 0 = 底、1 = 上端）に応じて、**密度に、掛ける、係数**です。

```hlsl
// 高さの割合 h と、種類 type（0 = 層雲、0.5 = 積雲、1 = 積乱雲）から、高さ方向の、密度の山を返す。
float HeightGradient(float h, float type) {
  // 層雲: 低い位置に、薄い層。0〜0.1 で立ち上がり、0.2〜0.3 で、消える。
  float stratus = Remap(h, 0.0, 0.1, 0.0, 1.0) * Remap(h, 0.2, 0.3, 1.0, 0.0);
  // 積雲: 0〜0.1 で、立ち上がり（底は、はっきり）、0.6〜0.95 で、ゆるやかに、消える（上は、丸い）。
  float cumulus = Remap(h, 0.0, 0.1, 0.0, 1.0) * Remap(h, 0.6, 0.95, 1.0, 0.0);
  // 積乱雲: 0〜0.1 で、立ち上がり、0.9〜1.0 まで、ほぼ、一定（高く、伸びる）。
  float cumulonimbus = Remap(h, 0.0, 0.07, 0.0, 1.0) * Remap(h, 0.9, 1.0, 1.0, 0.0);
```

**3 つの、関数**は、**どれも、`Remap` で、立ち上がり**（底）と、**消え方**（上端）を、**作ります**。

- **層雲**は、**高さ 0.2〜0.3** で、**もう、消える**（**薄い層**）
- **積雲**は、**0.6 から、ゆっくり**消えて、**上端が、丸い**
- **積乱雲**は、**ほぼ、上端まで**、**密度が、続く**（**高く、伸びる**）

```hlsl
  // 種類に応じて、3 つを、補間する（0〜0.5 で、層雲 → 積雲、0.5〜1 で、積雲 → 積乱雲）。
  float a = lerp(stratus, cumulus, saturate(type * 2.0));
  return lerp(a, cumulonimbus, saturate(type * 2.0 - 1.0));
}
```

**種類**（0〜1）で、**3 つの関数を、なめらかに、補間**します。**天気マップ**（[Cloud Density Model](density-model.md)）の、**B チャンネル**に、**種類**を、描いておけば、**場所ごとに、雲の種類が、変わります**。

## 雲の、層の、構成

**雲を、描く範囲**は、**惑星の周りの、2 つの球**（**底の、球と、上端の、球**）に、**挟まれた、殻**です。

```text
         上端の球（半径 = 惑星 + 雲の上端の、高さ）
       ╭─────────────╮
      ╱  ╭─────────╮  ╲        ← 雲は、この殻の中だけに、ある
     │  ╱  惑星     ╲  │
      ╲  ╲  ╱        ╱ ╱
       ╰──╰─────────╯──╯
         底の球（半径 = 惑星 + 雲の、底の高さ）
```

| 値 | 例 |
| --- | --- |
| 惑星の半径 | 6,360 km |
| 雲の、底の高さ | 1,500 m |
| 雲の、上端の高さ | 4,000 m |
| 殻の厚さ | 2,500 m |

```hlsl
// 視線が、雲の殻と、交わる区間（入口と、出口）を、求める。レイマーチは、この区間だけ。
float2 CloudLayerIntersect(float3 origin, float3 dir) {
  float2 t_bottom = RaySphere(origin, dir, g_planet_radius + g_cloud_bottom);
  float2 t_top = RaySphere(origin, dir, g_planet_radius + g_cloud_top);
  float height = length(origin) - g_planet_radius;
  float t_start, t_end;
  if (height < g_cloud_bottom) {                         // カメラが、雲の下
    t_start = t_bottom.y;                                // 底の球の、出口
    t_end = t_top.y;                                     // 上端の球の、出口
  } else if (height > g_cloud_top) {                     // カメラが、雲の上
    t_start = t_top.x;                                   // 上端の球の、入口
    t_end = t_bottom.x;                                  // 底の球の、入口
  } else {                                               // カメラが、雲の中
    t_start = 0.0;
    t_end = (t_bottom.x > 0.0) ? t_bottom.x : t_top.y;
  }
  return float2(t_start, t_end);
}
```

**カメラの位置**（**雲の下、中、上**）で、**入口と出口の、組み合わせが、変わります**。**この区間**だけを、**レイマーチ**します（[Cloud Raymarching](raymarch.md)）。

## 複数の、層

**低い雲**（層雲、積雲）と、**高い雲**（巻雲）を、**別の層**として、**重ねる**ことも、できます。

| 層 | 高さ | 描き方 |
| --- | --- | --- |
| **低い雲**（積雲、層雲） | 1〜4 km | **ボリューム**（レイマーチ。本物の、立体感） |
| **高い雲**（巻雲、巻層雲） | 6〜10 km | **2D の、テクスチャ**（空に、貼る。立体感は、不要。**安い**） |

**高い雲**は、**遠く、薄く**、**立体感が、見えない**ので、**ボリュームで、描く必要は、ありません**。**レイマーチ**は、**低い雲だけ**に、使います（[Cheap Alternatives](cheap.md)）。

## 雲の、遠近

**地平線の、近く**では、**視線が、雲の殻を、非常に、長く、通り**ます。**レイマーチの、距離が、長くなり**、**重い**です。

| 工夫 | 内容 |
| --- | --- |
| **最大距離を、決める** | 一定の距離（50 km）で、**打ち切る**。**それ以上**は、**霧の色**に、**フェード** |
| **ステップを、距離で、広げる** | **遠いほど**、**ステップを、大きく**する（遠くの、細部は、見えない） |
| **遠景は、低解像度** | 遠くの雲は、**粗い**（ノイズの、ミップを、読む） |

''', before="## よくあるミス")
pg.Refs("atmosphere/clouds/layers.md", [SCHNEIDER15, SCHNEIDER17, HILLAIRE16, RTR])

pg.Dedup("atmosphere/clouds/raymarch.md")
pg.Add("atmosphere/clouds/raymarch.md", '''
## レイマーチで、雲を、描く

**雲**は、**空間に、密度が、分布する、ボリューム**です。**画面の、各画素**から、**視線**を、**雲の殻**（[Cloud Layers](layers.md)）の中へ、**少しずつ進み**、**各点で、密度と、光**を、調べて、**色を、積算**します。**レイマーチ**です。

## 全体の、骨格

```hlsl
float4 CloudPS(float2 uv : TEXCOORD0) : SV_Target {
  float3 ray_dir = ScreenToWorldDir(uv);
  float3 origin = g_camera_position_from_planet_center;
  float2 range = CloudLayerIntersect(origin, ray_dir);                  // 雲の殻との、交わる区間
  if (range.y <= range.x) return float4(0, 0, 0, 1);                    // 交わらない → 雲なし（透過率 1）
```

まず、**視線が、雲の殻と、交わる区間**（入口と出口）を、求めます（[Cloud Layers](layers.md)）。**交わらなければ**、**雲は、ありません**（色 0、透過率 1）。

```hlsl
  const int kSteps = 64;
  float distance_range = min(range.y - range.x, g_max_march_distance);  // 遠すぎる区間は、打ち切る
  float step_len = distance_range / kSteps;
  float t = range.x + step_len * InterleavedGradientNoise(uv * g_screen_size);   // 開始位置を、ノイズで、ずらす（ジッター）
```

**区間を、64 に分け**、**開始位置を、ノイズで、ずらします**（**ジッター**）。**画素ごとに、違う位置**から、始まるので、**縞（バンディング）**が、**細かいノイズ**に、変わり、**TAA** で、**なめらか**に、ならされます（[Cloud Temporal Reprojection](temporal.md)）。

```hlsl
  float3 scattered = 0.0;                                               // 積算した、散乱光
  float transmittance = 1.0;                                            // ここまでの、透過率
  for (int i = 0; i < kSteps; ++i) {
    float3 p = origin + ray_dir * t;
    float density = CloudDensity(p);                                    // 密度（[Cloud Density Model]）
    if (density > 0.001) {
```

各ステップで、**その点の、密度**を、求めます。**密度が、ほぼ 0**（雲の、外）の点は、**何も、しません**（**空の、部分は、スキップ**）。

```hlsl
      float3 light = CloudLighting(p, ray_dir, density);                // その点で、視線の方向へ、散る光（[Cloud Lighting]）
      float sigma_t = density * g_extinction;                           // 消散係数
      float step_transmittance = exp(-sigma_t * step_len);
      // 区間内の、積分（解析的）: エネルギーを、保つ、形。
      float3 integral = (light - light * step_transmittance) / max(sigma_t, 1e-5);
      scattered += transmittance * integral;
      transmittance *= step_transmittance;
```

**散乱光**を、**積算**します。**区間の中でも、光は、減る**ので、**解析的な、積分**（`(1 − exp(−σΔs)) / σ`）を、使うと、**ステップが、粗くても、安定**します（[Single-Scattering Integral](../scattering/single-scattering.md)）。**透過率**は、**区間ごとに、掛けて**、**更新**します。

```hlsl
      if (transmittance < 0.01) break;                                  // ほぼ、不透明になったら、打ち切る（以降は、見えない）
    }
    t += step_len;
  }
  return float4(scattered, transmittance);
}
```

**透過率が、ほぼ 0**（雲が、濃く、**向こうが、見えない**）なら、**それ以上進んでも、結果が、変わらない**ので、**打ち切ります**（**早期終了**）。最後に、**散乱光**と、**透過率**を、**返し**、**空の色**（背景）を、**透過率で、重ねます**。

```hlsl
// 呼び出し側: 空の色（背景）に、雲を重ねる。
float4 cloud = CloudPS(uv);
float3 final_color = sky_color * cloud.a + cloud.rgb;                   // 背景 × 透過率 + 雲の散乱光
```

## ステップの、工夫（速くする）

64 ステップを、**全画素**で、回すと、重いです。**無駄**を、減らす、工夫です。

### ① 空の部分は、大きく進む

**雲が、ない、空間**（密度 0）では、**細かく、進む必要が、ありません**。**粗い、サンプル**（安い）で、**密度を、調べ**、**雲に、入ったら**、**細かい、サンプル**（重い）に、**切り替えます**。

```hlsl
// 2 段階: 最初は、粗い歩幅で、安い密度（基本の形だけ）を、調べる。雲に入ったら、細かい歩幅で、細部まで。
bool in_cloud = false;
float coarse_step = step_len * 2.0;
for (int i = 0; i < kSteps; ++i) {
  float3 p = origin + ray_dir * t;
  if (!in_cloud) {
    float coarse = CloudDensityCheap(p);                                // 基本の形だけ（細部のノイズを、読まない。安い）
    if (coarse > 0.0) { in_cloud = true; t -= coarse_step; continue; }  // 雲に入った → 1 歩戻って、細かく
    t += coarse_step;
  } else {
    // ... 通常の、細かい計算 ...
  }
}
```

**空の部分**は、**基本の形だけの、安い密度**で、**大きな歩幅**で、進み、**雲に、当たったら、1 歩戻って**、**細かく**、進みます。**雲が、少ない画素**では、**大幅に**、**速く**なります。

### ② 遠くほど、歩幅を、広げる

**遠くの雲の、細部**は、**画面上で、小さく**、**見えません**。**距離に応じて**、**歩幅を、広げ**ます。

```hlsl
float step_len = lerp(g_min_step, g_max_step, saturate((t - range.x) / g_step_growth_distance));
```

### ③ 低解像度で、描く

**雲は、ふわふわ**で、**細かい、エッジが、少ない**ので、**画面の、1/4 の解像度**（**縦横、半分**）で、描いて、**アップサンプル**しても、**目立ちません**（[Cloud Temporal Reprojection](temporal.md)）。

| 工夫 | 効果（目安） |
| --- | --- |
| 空の部分を、大きく進む | **2〜3 倍** 速い（雲が、疎な画素で） |
| 遠くで、歩幅を、広げる | 約 **1.5 倍** |
| **低解像度**（1/4 の画素数） | **4 倍** |
| **時間方向の、更新の、間引き**（1/16 の画素だけ、毎フレーム） | **16 倍**（[Cloud Temporal Reprojection](temporal.md)） |
| 早期終了（透過率が、小さい） | 濃い雲で、**大幅** |

## 視線の、起点

**カメラが、雲の殻の中**（飛行機）や、**上**（宇宙）にある場合、**入口の位置**が、変わります（[Cloud Layers](layers.md)）。**どの場合でも**、**入口から、出口までの、区間**を、**マーチ**する、**1 つの、コード**で、**書けます**。

''', before="## よくあるミス")
pg.Refs("atmosphere/clouds/raymarch.md", [SCHNEIDER15, SCHNEIDER17, HILLAIRE16, JIMENEZ, RTR])

pg.Dedup("atmosphere/clouds/lighting.md")
pg.Add("atmosphere/clouds/lighting.md", '''
## 雲の、光の、特徴

**雲が、白く、ふわふわして、立体的**に、見えるのは、**光の、散らばり方**に、**特徴**が、あるためです。

| 現象 | 見え方 |
| --- | --- |
| **前方散乱**（ミー散乱が、強い） | **太陽の方向**の、**雲の縁**が、**明るく、銀色に、光る**（シルバー ライニング） |
| **多重散乱** | **雲の、内側**まで、**光が、届き**、**真っ黒に**ならない |
| **吸収と、散乱の、バランス** | **厚い**雲は、**暗い、底**（光が、届かない）、**薄い**縁は、**明るい** |
| **粉っぽさ（Powder）** | **雲の、縁**は、**暗く、縁取られ**て見える（光が、散乱しきっていない） |

## 1 点での、光の、計算

レイマーチの、**各サンプル点**で、**太陽の光が、その点に、どれだけ、届くか**を、求め、**位相関数**を、掛けて、**視線の方向へ、散る光**を、得ます。

```hlsl
float3 CloudLighting(float3 p, float3 view_dir, float density) {
  // ① 太陽の光が、この点まで、どれだけ届くか（太陽方向へ、密度を積分して、Beer の法則で、減衰）。
  float light_optical_depth = LightMarchDensity(p, g_sun_dir);
  float beer = exp(-light_optical_depth * g_extinction);
```

**太陽の方向**へ、**短く、レイマーチ**し（**6〜8 ステップ**）、**途中の、密度を、積分**します。**Beer の法則**（`exp(−τ)`）で、**太陽の光が、点まで、届く割合**を、求めます。**雲の、厚い部分を、通った**光ほど、**弱く**なります。

```hlsl
  // ② 位相関数（前方散乱 + 後方散乱の、2 つの HG）。太陽の方向を、向いているとき、強く光る。
  float cos_theta = dot(view_dir, g_sun_dir);
  float phase = lerp(HenyeyGreenstein(cos_theta, -0.3), HenyeyGreenstein(cos_theta, 0.8), 0.7);
```

**2 つの、HG**（**前方の、強い山**と、**後方の、弱い山**）を、**混ぜた**位相関数です（[Phase Functions](../scattering/phase-function.md)）。**太陽の方を、向く**と、**前方散乱**で、**縁が、強く、光ります**。

```hlsl
  // ③ 粉っぽさ（Powder）: 薄い所（密度が低い所）では、光が、まだ、散乱しきらず、暗く見える。
  float powder = 1.0 - exp(-density * g_extinction * 2.0);
  float beer_powder = 2.0 * beer * powder;
```

**Beer の法則**だけだと、**雲の縁（薄い所）が、明るすぎ**ます。**Powder 効果**（**1 − exp(−2τ)**）を、掛けると、**縁が、暗く縁取られ**、**ふわふわした、雲らしさ**が、出ます（[Cloud Beer-Powder]の、図、参照）。**太陽の方向を、向く**ときは、**Powder の影響を、弱めます**（**縁が、輝く**ので）。

```hlsl
  // ④ 太陽の方を向くほど、Powder を弱める（縁が、輝くので）。
  float powder_blend = lerp(beer_powder, beer, saturate(cos_theta * 0.5 + 0.5));
  float3 sun_light = g_sun_color * powder_blend * phase;
```

**太陽に、背を向ける**ときは、**Powder を、強く**（縁が、暗く）、**太陽に、向かう**ときは、**Beer だけ**（縁が、明るい）、と、**補間**します。

```hlsl
  // ⑤ 環境光（空の光）: 雲の、上は、空の光で、明るく、底は、地面からの、暗い反射光だけ。
  float height_fraction = HeightFractionAt(p);
  float3 ambient = lerp(g_ambient_bottom, g_ambient_top, saturate(height_fraction));
  return sun_light + ambient * 0.5;
}
```

**環境光**は、**高さ**で、変えます。**雲の、上の方**は、**空の光**で、**明るく**、**底**は、**地面から、反射した、暗い光**だけです。**雲の底が、暗い**（影っぽい）のは、**雲の、厚みで、太陽の光が、届かず**、**環境光も、弱い**ためです。

## 光の、方向への、レイマーチ

**太陽の方向**へ、**短く、レイマーチ**して、**密度を、積分**します。**この計算が、レイマーチの、各サンプルで、必要**なので、**ステップ数は、少なく**（**6〜8**）します。

```hlsl
// 太陽方向への、密度の、積分（光学的な厚さ）。少ないステップ数で、近似する。
float LightMarchDensity(float3 p, float3 sun_dir) {
  const int kLightSteps = 6;
  float step_len = g_light_march_length / kLightSteps;
  float sum = 0.0;
  for (int i = 1; i <= kLightSteps; ++i) {
    // ステップを、だんだん、大きく（遠い所は、粗くてよい）。ランダムな、円錐状のずれを、足す（ノイズ）。
    float t = step_len * i * i * 0.3;
    float3 sample_pos = p + sun_dir * t + RandomConeOffset(i) * t * 0.1;
    sum += CloudDensityCheap(sample_pos) * step_len;                 // 安い密度（細部のノイズは、読まない）
  }
  return sum;
}
```

**光の方向の、積分**は、**細部が、不要**（**ぼんやり、減衰する**だけ）なので、**安い密度**（基本の形だけ）で、十分です。**ステップを、だんだん大きく**し、**円錐状に、少しずらす**（ノイズ）と、**少ないステップでも、なめらか**に、なります。

## 多重散乱の、近似

**1 回散乱**（太陽 → 点 → 目）だけでは、**雲の、内部が、暗すぎ**ます。**光は、雲の中で、何度も、散乱**して、**奥まで、届く**ためです。**オクターブによる、近似**（[Multiple Scattering](../scattering/multiple-scattering.md)）で、**足します**。

```hlsl
// 多重散乱: 散乱量 a を、半分ずつ、減衰 b を、弱く、位相の偏り c を、弱く（等方に、近づける）、4 回、足す。
float3 multi = 0.0;
float a = 1.0, b = 1.0, c = 1.0;
for (int octave = 0; octave < 4; ++octave) {
  float ph = DualLobePhase(cos_theta, 0.8 * c, -0.3 * c, 0.7);
  multi += a * ph * exp(-light_optical_depth * g_extinction * b);
  a *= 0.5; b *= 0.25; c *= 0.5;
}
float3 sun_light = g_sun_color * multi;
```

**オクターブが、進むほど**、**散乱量が、半分**に、**減衰が、弱まり**（**深くまで、届く**）、**位相関数が、等方に近づく**（**散らばる**）。これで、**厚い雲の、内部**でも、**光が、ほどよく、届き**、**ふわっとした、明るさ**が、出ます。

## 長所と、調整

| 要素 | 効果 | 調整 |
| --- | --- | --- |
| 前方散乱（`g_forward`） | **太陽側の、縁が、光る** | 0.6〜0.9。大きいほど、**太陽の近くだけ**、強く光る |
| 後方散乱（`g_back`） | **太陽の反対側**の、うっすらとした、明るさ | −0.2〜−0.5 |
| Powder | **縁の、暗い縁取り** | 強すぎると、**雲が、ごつごつ**する |
| 消散係数 | 雲の、**濃さ**（暗さ） | 大きいと、**暗く、濃い** |
| 環境光 | **底の、明るさ** | 底が、**黒すぎ**ないよう、**少し、足す** |

''', before="## よくあるミス")
pg.Refs("atmosphere/clouds/lighting.md", [SCHNEIDER15, WRENNINGE, HENYEY, BEER, HILLAIRE16, RTR])

pg.Dedup("atmosphere/clouds/shadows.md")
pg.Add("atmosphere/clouds/shadows.md", '''
## 雲の、影

**雲は、光を、遮る**ので、**地面に、雲の影**が、落ちます。**雲の影が、地面を、ゆっくり、流れていく**様子は、**風景に、生命感と、スケール感**を、与えます。**雲の、影を、地面に、落とす**には、**地面の各点が、太陽の方向に、雲を、どれだけ、通るか**を、知る必要が、あります。

## 方法 1：雲の、**影マップ**

**太陽の方向から**、**雲の殻**を、**見下ろして**、**各位置での、雲の、光学的な厚さ**（密度の積分）を、**テクスチャ**（**雲の影マップ**）に、描きます。**地面の、各点**は、**このマップを、引くだけ**で、**雲の影の、濃さ**が、分かります。

```text
        太陽
         ↓ ↓ ↓          ← 太陽の方向に、投影した、正射影
     ░░▓▓▓░░░▓▓░░       ← 雲の層（上から見た、厚さ）
   ──────────────────── 地面
   ↓ ↓ ↓ ↓              ← 影マップを、地面の各点で、引く
```

### 影マップを、描く

```hlsl
// 計算シェーダー: 影マップの各画素について、太陽の方向に、雲の殻を、通る、光学的な厚さを求める。
[numthreads(8, 8, 1)]
void CloudShadowMapCS(uint3 id : SV_DispatchThreadID) {
  // 画素に対応する、地面（または、雲の底の下）の、位置を、太陽の向きに、垂直な平面上の、座標から、求める。
  float3 plane_pos = ShadowMapToWorld(id.xy);                       // 影マップの画素 → ワールド位置（太陽に、垂直な平面）
  // この位置から、太陽へ向かって、雲の殻を、通過する区間を、求める。
  float2 range = CloudLayerIntersect(plane_pos, g_sun_dir);
  float optical_depth = 0.0;
  const int kSteps = 16;
  float step_len = (range.y - range.x) / kSteps;
  for (int i = 0; i < kSteps; ++i) {
    float3 p = plane_pos + g_sun_dir * (range.x + (i + 0.5) * step_len);
    optical_depth += CloudDensityCheap(p) * g_extinction * step_len;   // 安い密度（細部は、不要）
  }
  g_cloud_shadow_map[id.xy] = exp(-optical_depth);                     // 透過率（1 = 影なし、0 = 完全な影）
}
```

**太陽の方向**に、**雲の殻を、貫く、光線**を、**画素ごとに**、飛ばし、**密度を積分**して、**透過率**（**光が、地面まで、届く割合**）を、書き込みます。**安い密度**（**基本の形だけ**）で、十分です（**影は、ぼんやり**している）。**解像度**は、**256×256 〜 1024×1024** で、**広い範囲**を、覆います。**雲は、ゆっくり、動く**ので、**数フレームに、1 回、更新**すれば、十分です。

### 地面で、引く

```hlsl
// 地面（または、物体）の、ライティングで、雲の影を、太陽の光に、掛ける。
float CloudShadow(float3 world_pos) {
  // ワールド位置を、影マップの座標へ（太陽の向きに、垂直な平面に、投影）。
  float2 uv = WorldToCloudShadowUv(world_pos);
  return g_cloud_shadow_map.SampleLevel(g_linear_clamp, uv, 0);
}
float3 sun = g_sun_color * CloudShadow(world_pos) * ShadowMapShadow(world_pos);   // 雲の影 × 通常のシャドウ マップ
```

**太陽の直接光**に、**雲の影の透過率**を、**掛け**ます。**通常の、シャドウ マップ**（[Shadows](../../shadows/index.md)）と、**掛け合わせて**、使います。**雲の下**では、**太陽の光が、弱まり**、**地面が、暗く**なります。

## 方法 2：天気マップを、直接、引く

**雲の影の、簡易な、近似**です。**雲は、薄い層**なので、**天気マップ**（[Cloud Density Model](density-model.md)）の、**カバレッジ**を、**そのまま、影の濃さ**に、使います。

```hlsl
// 天気マップの、カバレッジを、太陽の方向に、ずらして、影として使う。
float2 shadow_uv = (world_pos.xz + g_sun_dir.xz * (g_cloud_height / max(g_sun_dir.y, 0.1))) * g_weather_scale;
float coverage = g_weather_map.SampleLevel(g_linear_wrap, shadow_uv, 0).r;
float shadow = 1.0 - coverage * g_cloud_shadow_strength;
```

**雲の、高さだけ**、**太陽の方向に、位置を、ずらして**、**天気マップを、読む**（**雲の層が、地面の、上空にある**ため、**影は、太陽と、反対の、向きに、ずれる**）。**計算は、1 回の、テクスチャ読み込み**で、**非常に、軽い**です。**雲の、厚みの、細かい、濃淡**は、**出ません**。

| 方式 | 精度 | コスト |
| --- | --- | --- |
| **影マップ**（雲の殻を、積分） | **高**（雲の、実際の、密度を、反映） | 中（数フレームに、1 回の、更新） |
| **天気マップを、引く** | 低（**カバレッジだけ**） | 最小 |

## 雲の影を、**ボリューム**にも

**霧や、大気**（[Volumetric Fog](../volumetric-fog/index.md)）の、**ライティング**でも、**雲の影**を、使います。**光の筋**（[God Rays](../god-rays/index.md)）が、**雲の隙間**から、**差し込む**様子が、出ます。

```hlsl
// ボリューム フォグの、太陽の光の注入で、雲の影も、掛ける。
float3 sun_in_cell = g_sun_color * shadow_map_visibility * CloudShadow(cell_world_pos);
```

## 注意点

| 項目 | 内容 |
| --- | --- |
| **雲の、動き** | 雲が、風で、動くと、**影マップも、変わる**。**更新を、間引く**と、**影が、カクカク**する。**前の、影マップと、補間** |
| **太陽の、角度が、浅い**（朝夕） | 影が、**非常に、長く**伸びる。**影マップの、範囲**が、足りなくなる。**範囲を、広げる**、**カスケード化** |
| **影の、濃さ** | 雲の影は、**柔らかく、薄い**。**濃すぎる**と、**不自然**（暗すぎる）。**透過率の、下限**を、設ける（**0.3** など） |
| **ボリュームと、地面の、整合** | **雲の影**を、**地面**にも、**霧にも、同じ影マップ**で、適用して、**ずれ**が、ないように |

''', before="## よくあるミス")
pg.Refs("atmosphere/clouds/shadows.md", [SCHNEIDER15, SCHNEIDER17, HILLAIRE16, RTR])

pg.Dedup("atmosphere/clouds/temporal.md")
pg.Add("atmosphere/clouds/temporal.md", '''
## なぜ、時間方向の、処理か

雲の、レイマーチ（[Cloud Raymarching](raymarch.md)）は、**重い**です。**全画素**で、**毎フレーム**、**数十ステップ**を、行うと、**数ミリ秒**〜**十数ミリ秒**かかります。そこで、**時間方向に、計算を、分散**します。**1 フレームで、一部の画素だけ**を、**計算**し、**残りは、前のフレームの結果**を、**使い回します**。

## 2 つの、工夫

| 工夫 | 内容 | 効果 |
| --- | --- | --- |
| **低解像度で、描く** | 画面の、**1/4**（縦横、各 1/2）の、解像度で、レイマーチ | 画素数が、**1/4** |
| **更新する画素を、間引く** | **1 フレームに、16 画素に 1 つ**（4×4 の、1 つ）だけ、**レイマーチ**。残りの、15 は、**前のフレームから、再投影** | さらに、**1/16** |

**組み合わせる**と、**画面の、約 1/64** の画素しか、**毎フレーム、レイマーチしません**。**64 倍**、軽くなります。

## 4×4 の、更新パターン

**4×4 のブロック**（16 画素）の、**どの 1 つを、更新するか**を、**フレームごとに、順番に**、変えます。**16 フレームで**、**全画素が、1 回ずつ、更新**されます（[Cloud Bayer の図、参照]）。

```hlsl
// 4×4 の、更新順（Bayer 行列）。0〜15。フレーム番号 % 16 と、一致する画素が、今フレームの、更新対象。
static const int kBayer4x4[16] = { 0, 8, 2, 10,  12, 4, 14, 6,  3, 11, 1, 9,  15, 7, 13, 5 };

bool ShouldUpdate(uint2 pixel, uint frame_index) {
  uint2 p = pixel & 3;                                          // 4×4 ブロック内の位置
  return kBayer4x4[p.y * 4 + p.x] == (frame_index & 15);
}
```

**ベイヤー行列の、順序**で、**離れた画素**を、**次々に**、更新します。**隣り合う画素**が、**同じフレーム**で、**更新されない**ので、**更新の、むらが、目立ちません**（[Dithered Transparency](../../translucency/alpha-test/dither.md) と、同じ、順序）。

## 再投影：前のフレームを、使う

**更新しない画素**は、**前のフレームの、結果**を、**使い回します**。**カメラが、動いている**ので、**前のフレームの、どの画素**が、**今の画素**に、**対応**するか（**再投影**）を、求めます。

```hlsl
// 今フレームの画素に対応する、前フレームの uv を求める（カメラの動きを、考慮）。
float2 ReprojectToPrevious(float2 uv, float depth_distance) {
  // 雲は、遠いので、深度は、遠景の距離として、扱う（視線方向 × 距離 → ワールド位置）。
  float3 ray_dir = ScreenToWorldDir(uv);
  float3 world_pos = g_camera_position + ray_dir * depth_distance;
  float4 prev_clip = mul(float4(world_pos, 1.0), g_prev_view_proj);
  return prev_clip.xy / prev_clip.w * float2(0.5, -0.5) + 0.5;
}
```

**今の、画素の位置**（**距離つき**）から、**ワールド位置**を、復元し、**前フレームの、ビュー・射影行列**で、**前の、画面の位置**を、求めます。**雲は、遠く**にあるので、**距離は、大きな、固定値**（雲の殻までの、距離）で、**近似**できます。

```hlsl
float4 CloudTemporalPS(float2 uv : TEXCOORD0, float4 pos : SV_Position) : SV_Target {
  uint2 pixel = (uint2)pos.xy;
  float2 prev_uv = ReprojectToPrevious(uv, g_cloud_reference_distance);
  float4 history = g_cloud_history.Sample(g_linear_clamp, prev_uv);      // 前フレームの結果（色 + 透過率）

  if (ShouldUpdate(pixel, g_frame_index)) {
    float4 current = RaymarchCloud(uv);                                  // 今フレームに、更新する画素: レイマーチ
    return lerp(history, current, 0.1 + ...);                            // 履歴と、混ぜる（下記）
  }
  return history;                                                        // 更新しない画素: 履歴を、そのまま
}
```

**更新する画素**は、**レイマーチ**した結果を、**履歴に、混ぜ**、**更新しない画素**は、**履歴を、そのまま**、**返します**。

## 履歴の、クランプ（ゴースト対策）

**カメラや、雲が、動く**と、**前のフレームの結果が、今の状態と、合わなく**なり、**ゴースト**（残像）が、出ます。**履歴の色**を、**今フレームの、周囲の色の、範囲**に、**クランプ**します（Karis、2014、TAA と、同じ考え方）。

```hlsl
// 周囲 3×3 の、今フレームの結果の、最小・最大の範囲に、履歴を、クランプして、ゴーストを抑える。
float4 min_c = 1e9, max_c = -1e9;
for (int y = -1; y <= 1; ++y)
  for (int x = -1; x <= 1; ++x) {
    float4 c = g_cloud_current_lowres.Load(int3(pixel / 4 + int2(x, y), 0));
    min_c = min(min_c, c); max_c = max(max_c, c);
  }
history = clamp(history, min_c, max_c);
```

**履歴が、今の周囲の色の範囲から、外れて**いたら、**範囲の中に、押し込みます**。**雲が、動いた**ことで、**古い値が、残る**場合に、**ゴーストが、消えます**。

| 履歴の、混ぜ方 | 効果 |
| --- | --- |
| **混ぜる割合を、小さく**（履歴を、強く） | **なめらか**、ノイズが、少ない。**ゴースト**が、出やすい |
| **混ぜる割合を、大きく**（履歴を、弱く） | **ゴースト**が、少ない。**ノイズ**が、目立つ |
| **速い動き**のときは、**割合を、大きく** | カメラの、動きの、**速度**で、**混ぜる割合を、変える** |

```hlsl
float camera_motion = length(g_camera_position - g_prev_camera_position);
float blend = saturate(0.05 + camera_motion * g_motion_blend_scale);     // 速く動くほど、今フレームを、強く
```

## ジッターと、組み合わせる

**レイマーチの、開始位置**に、**フレームごとに、違うノイズ**を、使うと、**16 フレームの、平均**で、**ノイズが、均され**、**なめらか**な、雲に、なります（[Cloud Raymarching](raymarch.md) の、ジッター）。

```hlsl
float jitter = InterleavedGradientNoise(pixel + g_frame_index * 5.588238);   // フレームごとに、ずらす
```

## 品質と、コストの、トレードオフ

| 設定 | コスト | 品質 |
| --- | --- | --- |
| **フル解像度、毎フレーム、全画素** | 非常に、重い | 最高 |
| **1/4 解像度、毎フレーム、全画素** | 重い | 高 |
| **1/4 解像度、4×4 で、1/16 更新** | **軽い** | 中〜高（カメラが、止まっていれば、高い） |
| **1/4 解像度、2×2 で、1/4 更新** | 中 | 高 |

**カメラが、速く、動く**と、**ゴースト、ノイズ**が、増えます。**動きの、速さに応じて**、**更新の、割合**を、**変える**（**速いときは、多く、更新**）と、**品質が、保たれ**ます。

''', before="## よくあるミス")
pg.Refs("atmosphere/clouds/temporal.md", [KARIS, SCHNEIDER15, HILLAIRE16, JIMENEZ])

pg.Dedup("atmosphere/clouds/cheap.md")
pg.Add("atmosphere/clouds/cheap.md", '''
## ボリューム雲は、**重い**

レイマーチの、ボリューム雲（[Cloud Raymarching](raymarch.md)）は、**美しい**が、**重く**、**実装も、複雑**です。**モバイル**、**低スペック**、**カメラが、雲に、近づかない**ゲームでは、**もっと、安い方法**が、**十分**です。

| 方式 | 立体感 | コスト | 向く場面 |
| --- | --- | --- | --- |
| **ボリューム（レイマーチ）** | 完全 | **重い** | 高品質、飛行、カメラが、雲に、近づく |
| **スカイドーム テクスチャ** | **なし**（平面） | **最小** | モバイル、遠景だけ |
| **2D の、層**（視差） | わずか（視差） | **小** | 中程度の品質 |
| **雲の、板（ビルボード）** | 中（個々の、雲は、立体的に、見える） | 小〜中 | 空の、雲が、**少なく**、**近づける** |
| **フリップブック**（アニメーションする、雲の板） | 中 | 中 | 動きのある、**局所的な**雲 |

## 方法 1：スカイドーム テクスチャ

**空全体**を、**1 枚の（または、数枚の）、画像**で、**覆います**。**雲が、描かれた、画像**を、**空の、ドーム**に、貼るだけです。

```hlsl
// 空の方向（球面）を、平面の UV に、割り当てて、雲のテクスチャを、引く。
float2 CloudUv(float3 view_dir, float time) {
  // 平面への投影: 視線が、水平に近づくほど、遠くに、投影される（雲が、地平線に向かって、縮む）。
  float2 uv = view_dir.xz / max(view_dir.y + 0.1, 0.05);
  return uv * g_cloud_scale + g_wind_direction * time * g_wind_speed;
}
float4 cloud = g_cloud_tex.Sample(g_linear_wrap, CloudUv(view_dir, g_time));
float3 sky_with_cloud = lerp(sky_color, cloud.rgb, cloud.a);
```

**視線の、`y` で、割る**ことで、**平らな、雲の層**を、**見上げた、ような、遠近感**（**地平線に、近い雲ほど、小さく、密**）が、出ます。**風で、UV を、ずらす**と、**雲が、流れます**。**最も、安く**、**どんな、プラットフォーム**でも、動きます。**立体感は、ありません**。

### 太陽の方向での、色づけ

**雲の絵**を、**そのまま**、貼ると、**太陽の方向**と、**関係なく、同じ色**で、**平板**です。**太陽の、方向を、見る**ほど、**雲の縁が、明るく、光る**ように、**色を、補う**と、**立体感**が、増します。

```hlsl
float sun_glow = pow(saturate(dot(view_dir, g_sun_dir)), 8.0);
float3 cloud_color = cloud.rgb * (1.0 + sun_glow * 2.0);                // 太陽の方を見ると、雲が、明るくなる
```

## 方法 2：2D の層を、重ねる（視差）

**雲の、テクスチャの層を、2〜3 枚**、**高さを、変えて**、**重ねます**。**カメラが、動く**と、**層ごとに、見える位置が、ずれる**（**視差**）ので、**奥行き**が、感じられます。

```hlsl
// 3 層の、雲。各層は、異なる高さ（= 異なる、投影スケール）と、風の速さを、持つ。
float4 c0 = SampleCloudLayer(view_dir, /*height*/ 1.0, /*speed*/ 0.010);
float4 c1 = SampleCloudLayer(view_dir, /*height*/ 1.5, /*speed*/ 0.015);
float4 c2 = SampleCloudLayer(view_dir, /*height*/ 2.2, /*speed*/ 0.022);
// 奥の層から、順に、重ねる。
float3 color = sky_color;
color = lerp(color, c2.rgb, c2.a);
color = lerp(color, c1.rgb, c1.a);
color = lerp(color, c0.rgb, c0.a);
```

**手前の層**ほど、**速く動き**、**大きく**見えます。**奥行きの、手がかり**（**視差**）が、**増え**、**平板さ**が、減ります。

### 雲の、厚みの、近似（疑似的な、立体感）

**1 枚の、テクスチャ**から、**光の、方向へ、少し、ずらして、もう 1 回読み**、**厚みを、近似**する、**方法**が、あります。

```hlsl
// 光の方向へ、UV を、少しずらして、もう一度読む。その差から、雲の、明暗（厚みの手がかり）を、作る。
float density = g_cloud_tex.Sample(g_linear_wrap, uv).a;
float density_toward_sun = g_cloud_tex.Sample(g_linear_wrap, uv + sun_dir_uv * 0.02).a;
float shade = saturate(1.0 - (density_toward_sun - density) * 3.0);      // 太陽側に、雲が、続いているほど、暗い（影の中）
float3 lit_cloud = lerp(g_cloud_shadow_color, g_cloud_lit_color, shade);
```

**太陽の方向に、雲が、続いている**（**光を、遮る**）なら、**暗く**、**続いていない**（縁）なら、**明るく**します。**1 回の、余計な、テクスチャ読み込み**で、**雲の、陰影**が、出ます。

## 方法 3：雲の板（ビルボード）

**個々の、雲**を、**カメラを、向く、板**に、**雲の絵**を、貼って、**空に、点在**させます。**積雲**（もこもこ）の、**数個**だけ、**空に、浮かべる**用途に、向きます。

| 要素 | 内容 |
| --- | --- |
| 板の数 | 数十〜数百 |
| 絵 | **ライティング済み**の、雲の画像（**複数の、バリエーション**） |
| 向き | **常に、カメラを向く**（ビルボード） |
| 太陽の方向 | **画像の明暗**を、太陽の位置に応じて、**切り替える**、または、**法線マップ**で、ライティング |
| ソート | **奥から手前**（半透明）。**加算でなく、アルファ ブレンド**（[Sorting](../../translucency/blending-sorting/sorting.md)） |

**近づく**と、**板だと、分かる**ので、**近づけない**場面（**遠景の、雲**）に、限ります。

## 方法 4：雲の、事前計算（フリップブック）

**ボリューム雲**を、**事前に、レンダリング**して、**複数の角度から**、**画像**にしておき、**カメラの向きに、近い画像**を、**板に、貼る**方法です（**インポスター**。[Trees](../../terrain/vegetation/trees.md) の、インポスターと、同じ）。**実時間の、レイマーチ**なしで、**ボリュームらしい、見た目**が、得られます。

## 切り替え：近くは、ボリューム、遠くは、安く

**近く**（**カメラの周り**）の、雲だけ、**ボリューム**で、**遠く**は、**安い方法**に、**切り替える**、**ハイブリッド**です。

| 距離 | 方式 |
| --- | --- |
| 〜10 km | **ボリューム**（レイマーチ。**低解像度** + **時間方向の、更新**） |
| 10 km〜 | **2D の層**、スカイドーム テクスチャ |
| 超遠景（地平線） | **霧の色**に、フェード |

**境目**は、**フェード**で、**なめらかに**、つなぎます。**ボリュームの、遠景**が、**重い**（視線が、殻を、長く通る）ので、**遠景を、安い方法に、する**ことで、**大幅に**、軽くなります。

''', before="## よくあるミス")
pg.Refs("atmosphere/clouds/cheap.md", [SCHNEIDER15, HILLAIRE16, RTR])
pg.Refs("atmosphere/clouds/index.md", [SCHNEIDER15, SCHNEIDER17, HILLAIRE16, WRENNINGE, WORLEY])

# ================================================================ volumetric fog
pg.Dedup("atmosphere/volumetric-fog/index.md")
pg.Add("atmosphere/volumetric-fog/index.md", '''
## ボリューム フォグとは

**通常の霧**（[Fog Equations](../aerial-fog/fog-equation.md)）は、**距離だけ**で、**霧の濃さ**を、決めます。**ボリューム フォグ**は、**空間の、各点の、霧の濃さ・光の当たり方**を、**ボリューム（3D グリッド）**として、**計算**します。

| | 通常の霧 | ボリューム フォグ |
| --- | --- | --- |
| 濃さ | **距離**と、**高さ**だけ | **空間の、各点**（**局所的な、霧の塊**） |
| **光の筋**（ゴッド レイ） | 出ない | **出る**（影の中は、暗い） |
| **局所光の、散乱**（ランプの周りの、光の玉） | 出ない | **出る** |
| **動く霧**（ノイズで、動く） | 難しい | **簡単**（密度を、ノイズで、変える） |
| コスト | **最小** | 中（毎フレーム、ボリュームを、計算） |

**ライトの、周りの、光の玉**、**窓から、差し込む、光の筋**、**霧の、渦**など、**リアルな、大気の、表現**が、**1 つの、仕組み**で、得られます。Wronski（2014）の、方式が、**多くの、ゲームの、標準**です。

## 4 つの、段階

ボリューム フォグは、**4 つの段階**で、できています。

| 段階 | 内容 | ページ |
| --- | --- | --- |
| ① **密度** | **各セルの、霧の濃さ**を、決める（一様、高さ、ノイズ、局所の、ボリューム） | [Step 1: Density](density.md) |
| ② **ライトの、注入** | **各セルに、ライトの光**を、**散乱光**として、**書き込む**（影も、考慮） | [Step 2: Light Injection](injection.md) |
| ③ **積分** | **奥行き方向**に、**散乱光を、累積**する（**カメラから、各距離までの、結果**） | [Steps 3 and 4: Integration and Application](integration.md) |
| ④ **適用** | **物体の、色**に、**霧の効果**を、**かける** | [Steps 3 and 4: Integration and Application](integration.md) |

## froxel：カメラに、合わせた、グリッド

**ボリュームは、カメラの視錐台**に、**合わせた、3D グリッド**です（**froxel** = **fr**ustum + vo**xel**）。**画面の、横・縦**と、**奥行き**で、**分割**します。

```text
横（画面）160 × 縦（画面）90 × 奥行き 64   =  約 92 万セル

カメラ ●──→ 奥行き（近いところは、細かく、遠いところは、粗く）
```

| 軸 | 分割数の例 | 意味 |
| --- | --- | --- |
| x | 160 | 画面の横（画素の 1/12 程度） |
| y | 90 | 画面の縦 |
| z | 64 | 奥行き（**指数的に**、分割。**近くを、細かく**） |

詳しくは、[Froxels](froxel.md) を、参照してください。

## 毎フレームの、流れ

```text
① 密度ボリュームを、書く         （計算シェーダー）
② ライトを、注入する              （計算シェーダー。シャドウ マップを引く）
③ 奥行き方向に、積分する          （計算シェーダー）
④ 物体を描くとき、ボリュームを、引いて、霧を、かける   （ピクセル シェーダー）
```

**毎フレームの、コスト**は、**約 0.5〜1.5 ms**（解像度、ライトの数による）です。**時間方向の、平均**（[Temporal Accumulation](temporal.md)）で、**低い解像度でも**、**なめらか**に、なります。

''', before="## よくあるミス")
pg.Refs("atmosphere/volumetric-fog/index.md", [WRONSKI, HILLAIRE15, HILLAIRE16, RTR])

pg.Dedup("atmosphere/volumetric-fog/froxel.md")
pg.Add("atmosphere/volumetric-fog/froxel.md", '''
## froxel の、グリッドを、作る

**froxel** は、**カメラの視錐台**を、**細かく**分割した、**3D グリッド**です（frustum + voxel）。**カメラから見た、画面の、横・縦**と、**奥行き**で、**セルを、並べ**ます。**ボクセル**（立方体の、グリッド）と、違い、**セルの、形が、遠いほど、大きい**（視錐台は、遠くで、広がるため）。

```text
  カメラ ●
          ╲╲
           ╲ ╲      奥行き方向に、スライス（スライス = 奥行きの 1 段）
            ╲  ╲
             [z=0][z=1][z=2]...[z=63]
```

## 3D テクスチャで、持つ

**3D テクスチャ**に、**各セルの、値**を、**書き込みます**。

```cpp
// 160×90×64 の、3D テクスチャを、2 枚（散乱と、積分結果）作る。計算シェーダーが、書き込む。
D3D11_TEXTURE3D_DESC desc = {};
desc.Width = 160;
desc.Height = 90;
desc.Depth = 64;
desc.MipLevels = 1;
desc.Format = DXGI_FORMAT_R16G16B16A16_FLOAT;               // 散乱光（RGB）+ 消散（A）
desc.Usage = D3D11_USAGE_DEFAULT;
desc.BindFlags = D3D11_BIND_SHADER_RESOURCE | D3D11_BIND_UNORDERED_ACCESS;   // 読む + 計算シェーダーで書く
device->CreateTexture3D(&desc, nullptr, &froxel_tex);
```

`R16G16B16A16_FLOAT` は、**HDR の色**（明るい光）を、**収める**ためです。`BIND_UNORDERED_ACCESS` は、**計算シェーダーが、書き込む**ために、必要です。**3D テクスチャの、1 つの値**が、**1 つの、froxel**です。

## セル ↔ ワールド座標

**セルの、番号**から、**ワールド位置**を、求める変換が、**すべての段階**（密度、ライト、積分、適用）で、**必要**です。

```hlsl
// froxel の番号 (x, y, z) から、ワールド位置を求める。z は、スライス番号（小数も可）。
float3 FroxelToWorld(float3 froxel_id) {
  float2 uv = (froxel_id.xy + 0.5) / float2(160, 90);                    // 画面上の位置（0〜1）
  float view_depth = SliceToViewDepth(froxel_id.z / 64.0);              // スライス → カメラからの、奥行き（メートル）
  // 画面の位置と、奥行きから、ビュー空間の位置 → ワールド空間へ
  float2 ndc = uv * float2(2, -2) + float2(-1, 1);
  float3 view_pos = float3(ndc.x * view_depth / g_proj_x, ndc.y * view_depth / g_proj_y, -view_depth);   // 右手系: 前方が −Z
  return mul(float4(view_pos, 1.0), g_inv_view).xyz;
}
```

**画面上の位置**（`x`、`y`）と、**奥行き**（`z`）から、**ビュー空間の位置**を、作り、**逆ビュー行列**で、**ワールド**へ、戻します。**奥行き**の、割り当て（`SliceToViewDepth`）が、次の節です。

## 奥行きの、割り当て

**奥行き方向**は、**均等に**分割**しません**。**近くは、細かく**、**遠くは、粗く**します。**近くの、霧の変化は、画面上で、大きく**、**遠くは、小さい**ためです。

```hlsl
// 奥行きの割り当て: 指数的に（近くを、細かく）。near から far まで、64 スライス。
float SliceToViewDepth(float slice01) {                                  // slice01: 0〜1
  // slice01 = 0 で near、1 で far。指数的に、広がる。
  return g_near * pow(g_far / g_near, slice01);
}
float ViewDepthToSlice(float view_depth) {
  return log(view_depth / g_near) / log(g_far / g_near);
}
```

**対数**（`log`）の、割り当てで、**スライスの、厚さ**が、**距離に、比例**します（**近くは、薄く、遠くは、厚い**）。**画面上で、各スライスが、ほぼ、同じ、見た目の厚さ**に、なります。

| 割り当て | 内容 |
| --- | --- |
| **均等** | 簡単だが、**近くが、粗く**、**縞**が、目立つ |
| **指数（対数）** | **近くを、細かく**。標準 |
| **べき乗**（`slice²`） | 指数より、**ゆるやか**。近くを、細かく、**簡単な、式** |

## 近・遠の、範囲

**froxel** は、**カメラの、近くから、一定の、距離**（**数十〜数百メートル**）までを、覆います。**それより、遠く**の、霧は、**別の方法**（**高さフォグ**、**空気遠近法**）で、**補います**。

| 範囲 | 方式 |
| --- | --- |
| 〜 64 m 〜 200 m（froxel の、範囲） | **ボリューム フォグ** |
| それより遠く | **空気遠近法**（[Physically Based Aerial Perspective](../aerial-fog/physical.md)）、高さフォグ |

**境目**では、**froxel の、最後のスライスの、値**を、**遠景の霧**へ、**フェード**して、**つなぎます**。

## 解像度の、選び方

| 解像度 | セル数 | 品質 | コスト |
| --- | --- | --- | --- |
| 80×45×32 | 約 11 万 | 低（ぼやける、縞） | **最小** |
| **160×90×64** | **約 92 万** | **標準** | 中 |
| 320×180×128 | 約 740 万 | 高（細かい光の筋） | **重い** |

**画面の、解像度**（1920×1080）の、**1/12**（160×90）が、**標準的**です。**霧は、ゆるやかに変化する**ので、**低解像度でも、十分**です。**時間方向の、平均**（[Temporal Accumulation](temporal.md)）で、**品質を、補います**。

''', before="## よくあるミス")
pg.Refs("atmosphere/volumetric-fog/froxel.md", [WRONSKI, HILLAIRE15, D3D11_TEX3D, RTR])

pg.Dedup("atmosphere/volumetric-fog/density.md")
pg.Add("atmosphere/volumetric-fog/density.md", '''
## ステップ 1：各セルの、霧の、濃さ

**ボリューム フォグ**の、最初の段階は、**froxel の、各セルの、霧の密度**（**消散係数**、`σ_t`）を、**決める**ことです。**密度が、高い**セルほど、**光を、よく、散らし、遮ります**。

## 密度の、材料

**複数の、材料を、足し合わせて**、**最終的な、密度**を、作ります。

| 材料 | 内容 | 例 |
| --- | --- | --- |
| **一様な、密度** | **空間全体**に、**一定の、薄い霧** | 空気の、霞 |
| **高さによる、密度** | **地面に、近いほど、濃い**（[Height Fog](../aerial-fog/height-fog.md)） | 谷の霧、朝霧 |
| **ノイズ** | **3D ノイズ**で、**霧に、むら**を、与える。**時間で、動かす** | 渦を巻く、霧 |
| **局所的な、霧の、ボリューム** | **箱や、球**の中だけ、**濃い霧** | 沼、洞窟の入口、魔法の霧 |
| **パーティクル** | **煙や、爆発**が、霧の密度を、**足す** | 煙幕 |

## 計算シェーダーで、書く

```hlsl
RWTexture3D<float4> g_froxel_scatter : register(u0);       // xyz = 散乱係数 × アルベド、w = 消散係数（密度）

[numthreads(8, 8, 4)]
void DensityCS(uint3 id : SV_DispatchThreadID) {
  float3 world = FroxelToWorld(float3(id) + JitterOffset());              // セルの、ワールド位置（ジッター付き。下記）
```

まず、**セルの中心**の、ワールド位置を、求めます（[Froxels](froxel.md)）。`JitterOffset()` は、**フレームごとの、わずかな、ずらし**で、**時間方向の平均**で、**縞を、消す**ために、使います（[Temporal Accumulation](temporal.md)）。

```hlsl
  // ① 一様な密度 + 高さによる密度。
  float h = world.y - g_fog_base_height;
  float density = g_uniform_density + g_height_density * exp(-g_height_falloff * max(h, 0.0));
```

**基本の、霧**です。**一様な部分**と、**高さで、指数的に、薄くなる**部分を、足します。

```hlsl
  // ② ノイズで、むらを与える。3D ノイズを、風で、流す。
  float3 noise_pos = world * g_noise_scale + g_wind_direction * g_time * g_wind_speed;
  float noise = g_noise_3d.SampleLevel(g_linear_wrap, noise_pos, 0).r;           // 0〜1
  density *= lerp(1.0, noise * 2.0, g_noise_strength);                            // ノイズで、濃さを、変える
```

**3D ノイズ**（**Perlin**、**Worley**）で、**霧の濃さに、むら**を、与え、**風で、流す**と、**霧が、動いて**見えます。**ノイズの値**（平均 0.5）に **2** を、掛けて、**平均を、1 に**そろえ、**全体の、濃さを、変えず**、**むら**だけを、足します。

```hlsl
  // ③ 局所的な、霧のボリューム（箱）を、足す。各ボリュームの、中だけ、密度を、足す。
  for (uint i = 0; i < g_fog_volume_count; ++i) {
    FogVolume v = g_fog_volumes[i];
    float3 local = mul(float4(world, 1.0), v.world_to_local).xyz;                 // ボリュームの、ローカル座標（-0.5〜0.5 の箱）
    float inside = all(abs(local) < 0.5) ? 1.0 : 0.0;
    // 箱の縁を、なめらかに（端で、密度が、0 に落ちる）
    float edge = saturate(min(min(0.5 - abs(local.x), 0.5 - abs(local.y)), 0.5 - abs(local.z)) / v.edge_softness);
    density += v.density * inside * edge;
  }
```

**局所的な、霧**（沼、洞窟）は、**箱（または、球）**の形の、**ボリューム**として、**置きます**。**セルが、箱の中**にあれば、**密度を、足し**、**縁**は、**なめらかに、薄く**します。**ボリュームを、アーティストが、レベルに、置く**（**霧の、ボリューム アクター**）ことで、**場所ごとの、霧**を、作れます。

```hlsl
  // 散乱係数と、吸収（アルベド）。霧は、ほぼ散乱だけ（アルベドが、高い）。消散 = 散乱 + 吸収。
  float3 scattering = g_fog_albedo * density;              // 散乱係数（RGB）
  float extinction = density;                              // 消散係数（散乱 + 吸収）。アルベドが 1 なら、散乱と、同じ。
  g_froxel_scatter[id] = float4(scattering, extinction);
}
```

最後に、**散乱係数**（`σ_s`、光を、曲げる）と、**消散係数**（`σ_t`、光を、失う）を、**書き込みます**。**アルベド**（**散乱 / 消散**）は、**霧の色**に、**相当**し、**1 に近い**と、**白い霧**、**小さい**と、**暗い、煤けた霧**になります。

## 単位と、スケール

| 値 | 意味 | 例 |
| --- | --- | --- |
| **消散係数**（1/m） | **1 m 進むと、光が、失われる割合** | 薄い霞 0.0005、霧 0.01、濃霧 0.05 |
| **視界の距離** | 約 `3 / 消散係数` | 0.01 → 約 300 m |

**ゲームの、空間の、スケール**に、合わせて、**消散係数**を、決めます。**視界が、300 m の霧**は、**0.01** 程度です（[Fog Equations](../aerial-fog/fog-equation.md)）。

## 事前に、決める、データ

**局所的な、霧の、ボリューム**は、**CPU 側**で、**リスト**にして、**定数バッファ**（または、構造化バッファ）で、**渡します**。**カメラの、近くに、ある、ボリュームだけ**を、**絞って**、渡すと、**ループが、短く**なります。

```cpp
struct FogVolume {
  Matrix world_to_local;     // ワールド → ボリュームの、ローカル（箱が、-0.5〜0.5 になる）
  float density;
  float edge_softness;
  float2 pad;
};
// カメラの視錐台と、交わるボリュームだけを、集めて、GPU に渡す。
```

''', before="## よくあるミス")
pg.Refs("atmosphere/volumetric-fog/density.md", [WRONSKI, HILLAIRE15, RTR])

pg.Dedup("atmosphere/volumetric-fog/injection.md")
pg.Add("atmosphere/volumetric-fog/injection.md", '''
## ステップ 2：ライトの、光を、注入する

**密度**（[Step 1: Density](density.md)）が、決まったら、**各セルに**、**ライトの光**を、**散乱光**として、**書き込みます**（**注入**）。**そのセルの、霧が、ライトに照らされて、どれだけ、光るか**を、計算します。

## セルでの、光の、計算

**ライト 1 つ**について、**そのセルで、カメラの方向へ、散乱される光**は、次のとおりです。

```text
散乱光 = 散乱係数 × 位相関数 × ライトの強さ × 影（光が、届くか） × 減衰（距離）
```

| 項 | 内容 |
| --- | --- |
| 散乱係数（`σ_s`） | **セルの、密度**（霧が、濃いほど、よく光る） |
| 位相関数 | **ライトの向き**と、**カメラへの向き**の、角度に、**依存**（[Phase Functions](../scattering/phase-function.md)） |
| ライトの強さ | **太陽、点光源**の、明るさ |
| 影 | **シャドウ マップ**で、**光が、届くか** |
| 減衰 | 点光源の、**距離による、減衰** |

## 太陽（平行光）を、注入する

```hlsl
// 計算シェーダー: 各セルに、太陽の光の、散乱を、足す。
[numthreads(8, 8, 4)]
void InjectSunCS(uint3 id : SV_DispatchThreadID) {
  float4 cell = g_froxel_scatter[id];                                      // 密度のステップで書いた値
  float3 scattering = cell.xyz;                                            // 散乱係数（RGB）
  if (cell.w < 1e-6) return;                                               // 霧が、無いセルは、スキップ

  float3 world = FroxelToWorld(float3(id) + JitterOffset());
  float3 view_dir = normalize(world - g_camera_position);                  // カメラから、セルへ向かう向き
```

**霧が、ない**セル（密度 0）は、**光らない**ので、**スキップ**します。**カメラから、セルへの、向き**が、**位相関数**に、必要です。

```hlsl
  // 太陽の光が、このセルに、届くか。シャドウ マップ（カスケード）を、1 回引く。雲の影も、掛ける。
  float shadow = SampleCascadedShadow(world) * CloudShadow(world);

  // 位相関数: 太陽の光が、カメラの方向へ、散る割合。霧は、前方に、やや強く、散る。
  float phase = HenyeyGreenstein(dot(view_dir, g_sun_dir), g_phase_g);

  float3 sun_scatter = scattering * g_sun_color * shadow * phase;
  g_froxel_scatter[id] = float4(cell.xyz, cell.w);                          // 密度は、そのまま
  g_froxel_lighting[id] += float4(sun_scatter, 0);                          // 散乱光を、別のテクスチャに、足す
}
```

**シャドウ マップ**（[CSM](../../shadows/cascaded.md)）を、**セルごとに、1 回**、引きます。**影の中のセル**は、**光らず**、**光が、届くセル**だけが、**散乱光**を、持ちます。これが、**光の筋**（ゴッド レイ）の、**源**です（[Volume-Based God Rays](../god-rays/volume.md)）。

## 点光源・スポットライトを、注入する

**ライトの、周りの、霧**は、**光の玉**になります。**セルごとに**、**影響する、ライト**を、**探して**、**足し合わせます**。

```hlsl
// 点光源: セルから、ライトへの距離で、減衰させ、位相関数と、影（ライトの、シャドウ マップ）を、掛ける。
float3 InjectPointLight(Light light, float3 world, float3 view_dir, float3 scattering) {
  float3 to_light = light.position - world;
  float dist = length(to_light);
  if (dist > light.range) return 0.0;                                       // 範囲外
  float3 light_dir = to_light / dist;

  float attenuation = saturate(1.0 - pow(dist / light.range, 4.0));        // 距離による、減衰（窓関数）
  attenuation *= attenuation / (dist * dist + 1.0);                         // 逆二乗の、減衰
  float shadow = (light.shadow_slot >= 0) ? SamplePointShadow(light, world) : 1.0;
  float phase = HenyeyGreenstein(dot(view_dir, -light_dir), g_phase_g);

  return scattering * light.color * light.intensity * attenuation * shadow * phase;
}
```

**光源からの距離**の**2 乗に、反比例**して、**暗く**なる、**逆二乗の法則**と、**範囲での、打ち切り**（窓関数）を、組み合わせます。**影つきの、ライト**は、**ライトの、シャドウ マップ**（[Point Lights: Cube Maps](../../shadows/local-lights/point-cubemap.md)）を、**セルごとに**、引きます。

```hlsl
// ライトが、多いとき: クラスターごとの、ライトのリストを、使い、そのセルに影響する、ライトだけを、ループする。
uint cluster = ClusterIndexAt(world);
uint count = g_cluster_light_count[cluster];
float3 total = 0.0;
for (uint i = 0; i < count; ++i) {
  Light light = g_lights[g_cluster_light_indices[cluster * kMaxLightsPerCluster + i]];
  total += InjectPointLight(light, world, view_dir, scattering);
}
```

**ライトが、数百個**ある場合、**全ライト**を、全セルで、ループすると、**非常に、重い**です。**クラスター**（空間を、小さな領域に、分け、**各領域に、影響する、ライトの、リストを、持つ**）を、使います（[Shadows for Many Lights](../../shadows/local-lights/many-lights.md)）。

## 環境光（空の光）を、足す

**ライトが、無い**場所でも、**霧は、空の光**で、**ぼんやり**と、**明るい**ものです。**環境光**を、**一様に**、足します。

```hlsl
float3 ambient_scatter = scattering * g_ambient_color * g_ambient_strength;     // 空の光が、霧を、全方向から、照らす
```

**霧の中の、日陰が、真っ黒に、ならない**ための、**重要な、項**です。**空の色**（**青い**）が、**霧の、日陰の色**です（[Using the Sky for Lighting](../sky-models/sky-lighting.md)）。

## 結果

注入が、終わると、**3D テクスチャの、各セル**に、**そのセルの、散乱光**（RGB）と、**消散係数**（A）が、**入っています**。次の段階（[Steps 3 and 4: Integration and Application](integration.md)）で、**奥行き方向に、積分**します。

''', before="## よくあるミス")
pg.Refs("atmosphere/volumetric-fog/injection.md", [WRONSKI, HILLAIRE15, "Olsson, Billeter, Assarsson, \"Clustered Deferred and Forward Shading\", High-Performance Graphics 2012", RTR])

pg.Dedup("atmosphere/volumetric-fog/integration.md")
pg.Add("atmosphere/volumetric-fog/integration.md", '''
## ステップ 3：奥行き方向の、積分

**注入**（[Step 2: Light Injection](injection.md)）で、**各セルの、散乱光と、消散係数**が、決まりました。**画面の、各画素**に、必要なのは、**「カメラから、そこまでの、すべてのセルの、散乱光の、合計」**です。これを、**奥行き方向の、積分**で、**事前に、求めておきます**。

```text
画素 (x, y) の、列:  カメラ ──→  [z=0] [z=1] [z=2] ... [z=63]
                           ↓ 手前から、奥へ、散乱光を、累積。透過率も、更新。
                      「z = k までの、累積した、散乱光と、透過率」を、各 z に、保存
```

## 積分の、計算シェーダー

**画面の、各 (x, y) の、列**について、**1 スレッド**が、**奥行き方向に、ループ**します。

```hlsl
Texture3D<float4> g_froxel_lighting : register(t0);        // 各セルの、散乱光（xyz）と、消散（w）
RWTexture3D<float4> g_froxel_integrated : register(u0);    // 出力: カメラから、スライス z までの、累積した、散乱光（xyz）と、透過率（w）

[numthreads(8, 8, 1)]
void IntegrateCS(uint3 id : SV_DispatchThreadID) {
  float3 accumulated = 0.0;                                 // これまでに、累積した、散乱光
  float transmittance = 1.0;                                // これまでの、透過率（カメラ → このスライス）
```

**スレッドの、ブロック**は、**(x, y) を**、担当し、**z は、ループ**で、手前から、奥へ、進みます。

```hlsl
  for (uint z = 0; z < 64; ++z) {
    float4 cell = g_froxel_lighting[uint3(id.xy, z)];       // このセルの、散乱光と、消散係数
    float3 scatter = cell.xyz;
    float extinction = cell.w;
    float slice_thickness = SliceThickness(z);              // このスライスの、厚み（メートル。奥ほど、厚い）
```

**セルの、散乱光と、消散係数**を、**読み**、**スライスの、厚み**（**奥行き方向の、長さ**）を、求めます。**奥のスライスほど、厚い**（[Froxels](froxel.md) の、奥行きの割り当て）ので、**厚みを、掛ける**ことが、重要です。

```hlsl
    // このスライスを、通るときの、透過率（Beer の法則）。
    float slice_transmittance = exp(-extinction * slice_thickness);

    // スライスの中の、積分（解析的）: 散乱光 × (1 − 透過率) / 消散。エネルギーを、保つ。
    float3 integral = (scatter - scatter * slice_transmittance) / max(extinction, 1e-5);
    accumulated += transmittance * integral;                // これまでの透過率を、掛けて、足す
    transmittance *= slice_transmittance;                    // 透過率を、更新
```

**区間の中でも、光は、減る**ので、**解析的な、積分**（[Single-Scattering Integral](../scattering/single-scattering.md) と、同じ）を、使います。**単純に、散乱光 × 厚み**を、足す方法は、**ステップが、粗いと、不安定**で、**エネルギーが、保存されません**。

```hlsl
    g_froxel_integrated[uint3(id.xy, z)] = float4(accumulated, transmittance);   // z までの結果を、保存
  }
}
```

**各スライス `z` に、「カメラから、`z` まで」の、累積結果**を、保存します。**画素は、自分の距離に、対応する、スライスを、1 回読む**だけで、**カメラから、その物までの、霧の効果**が、**得られます**。

## ステップ 4：画面に、適用する

**物体を、描く**とき（またはポスト プロセス）に、**物体の、距離**から、**対応するスライス**を、**読んで**、**霧を、かけます**。

```hlsl
// ピクセル シェーダーの、最後（または、ポスト プロセス）で、ボリューム フォグを、かける。
float3 ApplyVolumetricFog(float3 scene_color, float2 screen_uv, float view_depth) {
  float slice = ViewDepthToSlice(view_depth);                              // 距離 → スライス（連続値）
  float4 fog = g_froxel_integrated.SampleLevel(g_linear_clamp, float3(screen_uv, slice), 0);
  return scene_color * fog.a + fog.rgb;                                    // 物の色 × 透過率 + 散乱光
}
```

**3D テクスチャの、トライリニア補間**（`SampleLevel` + `LINEAR`）が、**スライスの間**も、**なめらかに、補間**します。**1 回の、読み込み**で、**霧の、色と、透過率**が、得られます。

### 物体の、深度が、froxel の範囲の外

**物体が、froxel の、最大距離より、遠い**とき、**最後のスライス**の、値を、使います（**クランプ**）。それ以上の、遠景の、霧は、**空気遠近法**など、**別の方法**で、補います（[Froxels](froxel.md)）。

```hlsl
float slice = saturate(ViewDepthToSlice(view_depth));                       // 0〜1 に、クランプ。範囲の外は、最後のスライス
```

### 半透明の物にも

**半透明の物**（パーティクル）も、**自分の、距離**で、**同じ、ボリュームを、引いて**、**霧を、かける**ことができます。**ポスト プロセスでなく**、**物体の、ピクセル シェーダー**で、行うのが、**一般的**です（[Where to Apply Fog](../aerial-fog/where.md)）。

## 描画の、順序

| 順 | 内容 |
| --- | --- |
| 1 | **シャドウ マップ**を、描く |
| 2 | **密度**（[Step 1: Density](density.md)）、**ライト注入**（[Step 2: Light Injection](injection.md)）、**積分**（このページ）を、計算シェーダーで、実行 |
| 3 | 不透明な物を、描く（**ピクセル シェーダーで、ボリュームを、引いて、霧を、かける**） |
| 4 | 半透明の物を、描く（**同様に、霧を、かける**） |

**ボリュームの、計算**は、**画面を、描く前**に、行います。**物体の、描画**が、**ボリュームを、引く**ためです。

''', before="## よくあるミス")
pg.Refs("atmosphere/volumetric-fog/integration.md", [WRONSKI, HILLAIRE15, HILLAIRE16, RTR])

pg.Dedup("atmosphere/volumetric-fog/temporal.md")
pg.Add("atmosphere/volumetric-fog/temporal.md", '''
## 時間方向の、平均で、品質を、上げる

**froxel** は、**低解像度**（160×90×64）なので、**そのまま**使うと、**縞**（バンディング）や、**ちらつき**が、出ます。**フレームごとに、サンプル位置を、わずかに、ずらし**（ジッター）、**前のフレームの結果と、混ぜる**（**時間方向の、平均**）と、**多くの、フレームの情報**が、**集まり**、**なめらかで、高品質**に、なります（Wronski、2014、Hillaire、2015）。

## ジッター：サンプル位置を、ずらす

**各フレームで**、**セルの中の、どの位置で、密度や、影を、サンプルするか**を、**少しずつ、変えます**。

```hlsl
// フレームごとに、違うジッター（0〜1）を、返す。ハルトン数列などの、低食い違い量列を、使う。
float3 JitterOffset() {
  return float3(Halton(g_frame_index, 2), Halton(g_frame_index, 3), Halton(g_frame_index, 5)) - 0.5;
}

// セルの、ワールド位置を求めるとき、ジッターを足す（Step 1、Step 2 の、FroxelToWorld の、引数に、足す）。
float3 world = FroxelToWorld(float3(id) + 0.5 + JitterOffset());
```

**セルの、中心**ではなく、**セルの中の、ランダムな位置**で、サンプルします。**フレームごとに、違う位置**を、サンプルするので、**複数フレームを、平均**すると、**セル全体の、平均**に、近づきます。**ハルトン数列**は、**一様に、かたよりなく**、**点を、並べる**（**低食い違い量列**）ので、**ランダムより、少ないフレームで、収束**します。

## 再投影：前のフレームを、探す

**カメラが、動く**と、**前のフレームの、froxel**の、**同じセル**は、**今のフレームの、別の位置**に、対応します。**前のフレームの、ビュー・射影行列**で、**今のセルの、ワールド位置**を、**前の froxel の、座標**へ、**変換**します。

```hlsl
// 今のセルのワールド位置から、前のフレームの froxel の、uvw を求める。
float3 ReprojectToPrevFroxel(float3 world) {
  float4 prev_clip = mul(float4(world, 1.0), g_prev_view_proj);
  float2 prev_uv = prev_clip.xy / prev_clip.w * float2(0.5, -0.5) + 0.5;
  float prev_depth = prev_clip.w;                                           // 前のフレームでの、ビュー深度
  float prev_slice = ViewDepthToSlice(prev_depth);
  return float3(prev_uv, prev_slice);
}
```

**ワールド位置は、同じ**（**霧の、その場所**）ですが、**前のフレームでは、画面の、別の位置**でした。**前の行列**で、**前の画面座標と、スライス**を、求めます。

## 履歴と、混ぜる

```hlsl
// 注入後の、散乱光（今フレーム）を、前フレームの、履歴と、混ぜる。
float3 uvw = ReprojectToPrevFroxel(world);
bool valid = all(uvw >= 0.0) && all(uvw <= 1.0);                           // 前の froxel の、範囲内か
float4 history = valid ? g_froxel_history.SampleLevel(g_linear_clamp, uvw, 0) : current;

float blend = valid ? 0.05 : 1.0;                                          // 履歴が、有効なら、今フレームは 5%、無効なら 100%
float4 result = lerp(history, current, blend);
g_froxel_lighting_out[id] = result;
```

**履歴を、95%** 残し、**今フレームを、5%** だけ、混ぜます。**約 20 フレーム**の、**指数移動平均**に、相当し、**ノイズ・縞が、大きく、減ります**。**履歴が、範囲の外**（カメラが、動いて、新しく、見える領域）なら、**今フレームの値を、100%** 使います。

| 混ぜる割合（今フレーム） | 効果 |
| --- | --- |
| **0.02〜0.05**（履歴を、強く） | **非常に、なめらか**。**ゴースト**（動いたものの、残像）が、出やすい |
| **0.1〜0.2** | ほどほど。**ゴースト**が、少ない、**ノイズ**が、残る |
| **1.0** | 時間方向の平均なし（**縞が、そのまま**） |

## ゴーストを、抑える

**ライトが、動く**、**霧が、動く**、**物が、動く**と、**前のフレームの、結果が、古く**、**残像**（ゴースト）が、出ます。

| 対策 | 内容 |
| --- | --- |
| **履歴の、クランプ** | 今フレームの、**周囲の、セル**の、**最小・最大**に、**履歴を、押し込む**（[Cloud Temporal Reprojection](../clouds/temporal.md) と、同じ） |
| **動きの、速さで、割合を、変える** | **カメラ・ライトが、速く動く**ほど、**今フレームの、割合を、大きく** |
| **ライトが、動いたら、リセット** | **動く、ライト**の、**周囲の、セル**だけ、**履歴を、捨てる** |
| **ライトの、強さが、急に変わる** | **履歴を、捨てる**（フラッシュなど） |

```hlsl
// 動いているライトの、影響範囲では、履歴を、弱める。
float light_motion = g_moving_light_influence(world);                       // 0（静止）〜 1（動いている）
float blend = lerp(0.05, 0.5, light_motion);
```

## 描画への、影響

**時間方向の、平均**は、**ボリューム フォグの、品質**に、**大きく、貢献**します。**ほぼ、必須**です。

| 設定 | 効果 |
| --- | --- |
| **時間方向の平均なし** | **縞**、**ちらつき**。**高解像度**（重い）が、必要 |
| **ジッター + 履歴（95%）** | **なめらか**。**低解像度**（160×90×64）で、**十分** |

**カメラが、止まっている**と、**履歴が、収束**して、**非常に、なめらか**に、なります。**カメラが、急に動く**と、**一時的に、品質が、落ちます**。

''', before="## よくあるミス")
pg.Refs("atmosphere/volumetric-fog/temporal.md", [WRONSKI, HILLAIRE15, KARIS, "Halton, \"On the Efficiency of Certain Quasi-Random Sequences of Points in Evaluating Multi-Dimensional Integrals\", Numerische Mathematik, Vol. 2, 1960（ハルトン数列）"])

pg.Dedup("atmosphere/volumetric-fog/quality.md")
pg.Add("atmosphere/volumetric-fog/quality.md", '''
## 品質を、決める、要素

ボリューム フォグの、**見た目**と、**コスト**は、**いくつかの、設定**で、決まります。

| 要素 | 内容 | 大きくすると |
| --- | --- | --- |
| **froxel の、解像度**（x、y） | 画面の、**横・縦**の、分割数 | **細かい光の筋**。**重い** |
| **奥行きの、分割数**（z） | **奥行きの、スライス**数 | **縞が、減る**。**重い** |
| **最大の距離** | **froxel が、覆う範囲** | **遠くまで**、ボリュームの霧。**スライスが、粗くなる** |
| **ライトの数** | 注入する、**ライトの、数** | **光の玉が、増える**。**重い** |
| **影の、品質** | 注入での、**シャドウ マップの、読み方** | **光の筋が、きれい** |

## よくある、見た目の、問題と、対策

### ① 縞（バンディング）

**奥行き方向の、スライス**に、沿って、**縞模様**が、見えます。**スライスの境目**で、**値が、急に、変わる**ためです。

| 原因 | 対策 |
| --- | --- |
| **スライスが、粗い** | スライス数を、増やす。**近くを、細かく**（指数的な、割り当て。[Froxels](froxel.md)） |
| **トライリニア補間**でも、**滑らかさが、足りない** | **トリキュービック補間**（高次の補間）で、**読む**。コストが、増える |
| **ジッターなし** | **ジッター + 時間方向の平均**（[Temporal Accumulation](temporal.md)）で、縞を、細かいノイズに、変えて、平均 |

### ② 光の筋が、ぼやける

**低解像度**の、froxel では、**細い、光の筋**（**窓の、格子**）が、**ぼやけ**、**消えます**。

| 対策 | 内容 |
| --- | --- |
| **解像度を、上げる** | 160×90 → 240×135 など。**メモリ・コストが、増える** |
| **重要な、ライトだけ**、**別の、方法**（放射状ブラー、メッシュ）で、補う | [Screen-Space Radial Blur](../god-rays/radial-blur.md)、[Light Shaft Meshes](../god-rays/mesh-shafts.md) |
| **ぼやけを、許容** | 霧は、**ゆるやかな、効果**。**ある程度の、ぼやけ**は、**自然** |

### ③ 光漏れ（ライトが、壁を、越える）

**低解像度の、froxel**では、**壁の、向こう側の、セル**も、**壁の、こちら側と、同じセル**に、**混ざり**、**壁の向こうの、光**が、**漏れて**見えます。

| 対策 | 内容 |
| --- | --- |
| **解像度を、上げる** | セルを、小さくする |
| **セルの、影を、複数サンプル** | セルの、中の、**複数の位置**で、**シャドウ マップを、引き**、**平均** |
| **ジッター + 履歴** | 複数フレームで、平均すると、**漏れが、目立ちにくい** |

### ④ 遠景で、解像度が、粗い

**奥行きが、遠い**スライスは、**厚く**、**1 つの、セルが、非常に、広い**範囲を、**代表**します。**遠くの、霧の、細部**（光の筋、局所的な、霧）が、**失われます**。

| 対策 | 内容 |
| --- | --- |
| **最大距離を、短く**（64 m〜128 m） | **近くだけ**、**細かく** |
| **遠景は、別の方法**（空気遠近法） | [Physically Based Aerial Perspective](../aerial-fog/physical.md)、[Height Fog](../aerial-fog/height-fog.md) |

## コストの、内訳（目安、1080p）

| 処理 | コスト |
| --- | --- |
| **密度**（ノイズ読み込み、ボリューム） | 0.1〜0.2 ms |
| **ライト注入**（太陽 + 数個の、ライト、影の読み込み） | **0.3〜0.8 ms**（ライトの数、影の有無で、変わる） |
| **積分**（奥行き方向の、ループ） | 0.05〜0.1 ms |
| **時間方向の、平均** | 0.05〜0.1 ms |
| **適用**（全画素で、1 回の、3D テクスチャ読み込み） | 0.1〜0.2 ms |
| **合計** | **0.6〜1.4 ms** |

**ライト注入が、最も、重い**ことが、多いです。**影つきライトの数を、絞る**（[Shadows for Many Lights](../../shadows/local-lights/many-lights.md)）、**重要な、ライトだけ**、**ボリューム フォグに、注入**する、といった、**工夫**が、効きます。

## 品質設定の、プリセット

| 設定 | froxel | 最大距離 | ライト | 時間方向 |
| --- | --- | --- | --- | --- |
| **低** | 80×45×32 | 64 m | 太陽のみ | あり |
| **中** | 160×90×64 | 128 m | 太陽 + 影つき 2 | あり |
| **高** | 240×135×96 | 256 m | 太陽 + 影つき 4 + 影なし 多数 | あり |
| **最高** | 320×180×128 | 512 m | すべて | あり |

**ユーザー設定**で、**切り替えられる**ように、しておくと、**幅広い環境**で、動かせます。

''', before="## よくあるミス")
pg.Refs("atmosphere/volumetric-fog/quality.md", [WRONSKI, HILLAIRE15, KARIS, RTR])
pg.Refs("atmosphere/index.md", ["Hillaire, \"A Scalable and Production Ready Sky and Atmosphere Rendering Technique\", Computer Graphics Forum (Eurographics Symposium on Rendering 2020)", "Bruneton, Neyret, \"Precomputed Atmospheric Scattering\", Computer Graphics Forum (EGSR 2008)", SCHNEIDER15, WRONSKI])
print("ok")
