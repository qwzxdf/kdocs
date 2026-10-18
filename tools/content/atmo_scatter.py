import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import pg  # noqa: E402

HILLAIRE = '''Hillaire, "A Scalable and Production Ready Sky and Atmosphere Rendering Technique", Computer Graphics Forum (Eurographics Symposium on Rendering 2020)（4 つの LUT を使う方式。公開デモの実装がある）'''
BRUNETON = '''Bruneton, Neyret, "Precomputed Atmospheric Scattering", Computer Graphics Forum (Eurographics Symposium on Rendering 2008)'''
BRUNETON17 = '''Bruneton, "A Qualitative and Quantitative Evaluation of 8 Clear Sky Models", IEEE Transactions on Visualization and Computer Graphics, Vol. 23, No. 12, 2017（参照実装 `ebruneton/precomputed_atmospheric_scattering` が公開されている）'''
NISHITA = '''Nishita, Sirai, Tadamura, Nakamae, "Display of the Earth Taking into Account Atmospheric Scattering", SIGGRAPH 1993（大気散乱の、CG への導入）'''
ONEIL = '''O'Neil, "Accurate Atmospheric Scattering", GPU Gems 2, Chapter 16, 2005'''
PREETHAM = '''Preetham, Shirley, Smits, "A Practical Analytic Model for Daylight", SIGGRAPH 1999'''
HENYEY = '''Henyey, Greenstein, "Diffuse Radiation in the Galaxy", Astrophysical Journal, Vol. 93, 1941（Henyey-Greenstein 位相関数）'''
CORNETTE = '''Cornette, Shanks, "Physically Reasonable Analytic Expression for the Single-Scattering Phase Function", Applied Optics, Vol. 31, No. 16, 1992'''
JENDERSIE = '''Jendersie, d'Eon, "An Approximate Mie Scattering Function for Fog and Cloud Rendering", SIGGRAPH 2023 Talks'''
RAYLEIGH = '''Strutt (Lord Rayleigh), "On the Light from the Sky, its Polarization and Colour", Philosophical Magazine, Vol. 41, 1871（レイリー散乱）'''
WRENNINGE = '''Wrenninge, "Art-Directable Multiple Volumetric Scattering", SIGGRAPH 2015 Talks（多重散乱の、オクターブによる近似）'''
RTR = '''Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（大気散乱、参加媒質の章）'''

# ================================================================ transmittance
pg.Dedup("atmosphere/scattering/transmittance.md")
pg.Add("atmosphere/scattering/transmittance.md", '''
## 透過率とは、何か

光が、霧や大気の中を、距離 `d` だけ進むと、**一部が、吸収・散乱で、進行方向から、失われます**。**そのまま、進行方向に、残る光の割合**が、**透過率 `T`** です。

```text
T = exp( −σ × d )                       一様な媒質（霧）の場合

T = exp( −∫ σ(s) ds )                   密度が、場所で変わる媒質（大気）の場合。積分は、光の通り道に沿って
```

`σ`（消散係数、1/m）は、**単位長さあたり、どれだけ、光が失われるか**を表します。指数関数の形（Beer–Lambert の法則）なのは、**進んだ分の、一定の割合**が、失われ続けるためです。

## 一様な、媒質：1 行で、済む

霧の、密度が、一定なら、積分は、不要です。

```hlsl
float3 transmittance = exp(-g_sigma_t * distance);
```

`g_sigma_t` は、**RGB の、3 成分**の、消散係数です。空気中の、レイリー散乱は、**青の方が、大きく**、**赤の方が、小さい**ので、**遠くの景色は、青みを帯びます**（[Rayleigh Scattering](../scattering/index.md)）。

## 密度が、変わる媒質：数値積分

大気の、密度は、**高度とともに、指数関数的に、薄く**なります。

```text
ρ(h) = exp( −h / H )         h: 地表からの高さ、H: スケール ハイト（レイリー 8 km、ミー 1.2 km）
```

光の通り道に沿った、積分は、**分割して、足し合わせる**ことで、近似します。

```hlsl
// 地表の中心を原点とした、座標で、位置 p の、高さ（地表からの高さ）を求める。
float HeightAt(float3 p) { return length(p) - g_planet_radius; }
```

大気は、**惑星の中心を、原点**にした、**球**として、扱います。`length(p)` が、中心からの距離で、**惑星の半径を引くと、高度**です。

```hlsl
// 密度（高度 h での、基準の密度に対する、割合）。レイリーと、ミーで、スケール ハイトが違う。
float DensityRayleigh(float h) { return exp(-h / 8000.0); }       // 8 km
float DensityMie(float h) { return exp(-h / 1200.0); }            // 1.2 km
```

レイリー散乱（空気の分子）の、層は、**厚く**（8 km）、ミー散乱（エアロゾル、細かい塵や、水滴）の層は、**薄い**（1.2 km、地表の近く）です。**ミー散乱が、地表の近くに、集まっている**ので、**地平線の、すぐ上だけ、白っぽく濁ります**。

```hlsl
// 光の通り道（点 a から、方向 dir へ、長さ length）の、光学的な厚さ（密度の積分）を、数値で求める。
float2 OpticalDepth(float3 a, float3 dir, float length_m, int steps) {
  float step_len = length_m / steps;
  float2 sum = 0.0;                                               // x = レイリー、y = ミー
  for (int i = 0; i < steps; ++i) {
    float3 p = a + dir * ((i + 0.5) * step_len);                  // 区間の中央で、評価（中点法）
    float h = HeightAt(p);
    sum += float2(DensityRayleigh(h), DensityMie(h)) * step_len;
  }
  return sum;
}
```

ループの中で、**各区間の中央**の、密度を、読み、**区間の長さを掛けて**、足し合わせます。これが、**積分の、近似**です（中点法）。`steps` は、**精度と、速さの、バランス**で、**16〜64** が、よく使われます。

```hlsl
// 透過率 = exp( −(σ_レイリー × 光学的厚さ_レイリー + σ_ミー × 光学的厚さ_ミー) )
float3 Transmittance(float3 a, float3 dir, float length_m) {
  float2 od = OpticalDepth(a, dir, length_m, 32);
  float3 tau = g_rayleigh_extinction * od.x + g_mie_extinction * od.y;       // RGB ごとの、光学的な深さ
  return exp(-tau);
}
```

**消散係数**（`σ`）は、**基準の密度での、値**で、**光学的厚さ**（密度の積分）と、**掛け合わせ**ます。**RGB ごとに、別の `σ`** を持つので、**透過率も、RGB ごと**に、違う値になります。

## 計算量の、問題

太陽の光は、**大気の外から、各点まで**、**透過率**を掛けて、届きます。**空の、各方向**について、**視線に沿った、各サンプル点**で、**太陽方向の透過率**を、求めると、**二重ループ**になります。

```text
空の画素 × 視線のサンプル（32） × 太陽方向のサンプル（32）  =  画素あたり 約 1,000 回の、密度計算
```

画面の、全画素で、これを行うのは、**重すぎます**。そこで、**太陽方向の透過率**は、**事前に、テクスチャ**（LUT）に、計算しておきます。

## 透過率 LUT

**透過率**は、**「点の高度」と「方向の、天頂角」**の、2 つだけで、決まります（大気は、**球対称**なので）。この 2 変数の、関数を、**2 次元のテクスチャ**に、焼いておきます（Bruneton と Neyret、2008）。Hillaire（2020）の、実装では、**256×64** 画素です。

```hlsl
// LUT の uv から、（高度、天頂角の cos）を、求める。
// uv.y は、高度、uv.x は、「大気の上端までの距離」を、正規化した値で、地平線の近くを、細かく取る。
void UvToTransmittanceParams(float2 uv, out float view_height, out float cos_zenith) {
  float H = sqrt(g_top_radius * g_top_radius - g_bottom_radius * g_bottom_radius);   // 地表の接線の、大気の上端までの距離
  float rho = H * uv.y;                                                              // 地平線までの距離
  view_height = sqrt(rho * rho + g_bottom_radius * g_bottom_radius);
  float d_min = g_top_radius - view_height;                                          // 真上に向かう場合の、距離
  float d_max = rho + H;                                                             // 地平線の方向に向かう場合の、距離
  float d = d_min + uv.x * (d_max - d_min);                                          // 大気の上端までの距離
  cos_zenith = (d == 0.0) ? 1.0 : (H * H - rho * rho - d * d) / (2.0 * view_height * d);
  cos_zenith = clamp(cos_zenith, -1.0, 1.0);
}
```

**uv を、角度や、高度に、そのまま、割り当てる**と、**地平線の近く**（変化が、急）の、**解像度が、足りません**。**大気の上端までの距離**で、横軸を、決めると、**地平線の近くを、細かく**、取れます（Hillaire の実装）。この関数は、**LUT を、作るとき**（各画素が、どの高度・角度を、表すか）に、使います。

```hlsl
// 逆変換: （高度、天頂角の cos）から、LUT の uv を求める。LUT を読むときに使う。
float2 TransmittanceParamsToUv(float view_height, float cos_zenith) {
  float H = sqrt(max(0.0, g_top_radius * g_top_radius - g_bottom_radius * g_bottom_radius));
  float rho = sqrt(max(0.0, view_height * view_height - g_bottom_radius * g_bottom_radius));
  float discriminant = view_height * view_height * (cos_zenith * cos_zenith - 1.0) + g_top_radius * g_top_radius;
  float d = max(0.0, -view_height * cos_zenith + sqrt(discriminant));                // 大気の上端までの距離
  float d_min = g_top_radius - view_height;
  float d_max = rho + H;
  return float2((d - d_min) / (d_max - d_min), rho / H);
}
```

読むときは、**この逆変換で、uv を求め**、**テクスチャを 1 回引く**だけです。**透過率の、積分が、1 回の、テクスチャ読み込みに、化けます**。

```hlsl
// 太陽方向の、透過率を、LUT から引く（一瞬で済む）。
float3 SunTransmittance(float3 position, float3 sun_dir) {
  float h = length(position);
  float cos_zenith = dot(position / h, sun_dir);
  return g_transmittance_lut.SampleLevel(g_linear_clamp, TransmittanceParamsToUv(h, cos_zenith), 0).rgb;
}
```

`position / h` は、**位置での、真上の向き**（地表の、法線）で、`sun_dir` との内積が、**太陽の天頂角の cos** です。

## 地面に、遮られる光

光の、通り道が、**地面**に当たる場合（太陽が、地平線の、下にある）、**その方向の、透過率は、0** と、みなします。

```hlsl
// 惑星（地面）に、遮られるか。
float2 RaySphere(float3 origin, float3 dir, float radius);      // 交点までの、距離（2 つ。当たらなければ、負）

bool HitsGround(float3 position, float3 dir) {
  float2 t = RaySphere(position, dir, g_bottom_radius);
  return t.x > 0.0 || t.y > 0.0;                                   // 前方で、地面と交わる
}
```

太陽が、地平線の、**少し下**に、沈んだ後も、**空が、しばらく、明るい**のは、**散乱した光が、回り込んでくる**ためです（[Day-Night Cycle](../sky-models/day-night.md)）。**透過率だけ**では、**直接の光が、消える**瞬間は、出せますが、**残照**は、出ません。

''', before="## よくあるミス")
pg.Refs("atmosphere/scattering/transmittance.md", [HILLAIRE, BRUNETON, BRUNETON17, NISHITA, RTR])

# ================================================================ phase function
pg.Dedup("atmosphere/scattering/phase-function.md")
pg.Add("atmosphere/scattering/phase-function.md", '''
## 位相関数とは

光が、粒子に、当たって、**散乱**するとき、**どの方向に、どれだけ、散らばるか**を、表す関数が、**位相関数**です。**入射した光の向き**と、**散乱した光の向き**の、**間の角度 `θ`** だけで、決まります（粒子が、球に近い、と仮定する）。

```text
θ = 0°    前方散乱（光が、そのまま、直進する向き）
θ = 90°   横方向への、散乱
θ = 180°  後方散乱（光が、来た方向へ、戻る）
```

位相関数は、**全方向に、積分して、1** になるように、決めます（**エネルギーが、保存**される）。

## レイリー散乱の位相関数

空気の分子（光の波長より、はるかに小さい粒子）による、散乱です（Rayleigh、1871）。**前方と後方に、同じだけ、散り**、**横には、少なめ**です。

```text
P_Rayleigh(θ) = 3 / (16π) × (1 + cos²θ)
```

```hlsl
float RayleighPhase(float cos_theta) {
  return 3.0 / (16.0 * 3.14159265) * (1.0 + cos_theta * cos_theta);
}
```

`cos_theta` は、**入射の向きと、散乱の向きの、内積**です。式は、`cos²θ` を、含むので、**前後対称**で、**ゆるやかな、変化**です。

レイリー散乱は、**波長の 4 乗に、反比例**する、**散乱の強さ**（[Atmosphere Model](atmosphere-model.md)）を、持ちます。**位相関数は、向き**の、**分布**だけを、決め、**強さ**（青が、強い）は、**散乱係数**が、決めます。

## ミー散乱：エアロゾルと、水滴

**光の波長と、同じ程度の、大きさの粒子**（塵、水滴、霧）による、散乱です。**前方に、強く、散ります**。**霧の中の、太陽**が、**白く、まぶしく**見えるのは、**前方散乱**が、強いためです。

厳密な、**Mie 理論**の、式は、**複雑**で、**重い**ので、**近似式**を使います。

### Henyey–Greenstein（HG）

Henyey と Greenstein（1941）の、**単純な、近似**です。**非対称パラメーター `g`**（−1〜1）が、**前方か、後方か、どれだけ偏るか**を、決めます。

```text
P_HG(θ, g) = (1 − g²) / ( 4π × (1 + g² − 2 g cosθ)^(3/2) )
```

```hlsl
float HenyeyGreenstein(float cos_theta, float g) {
  float g2 = g * g;
  float denom = 1.0 + g2 - 2.0 * g * cos_theta;
  return (1.0 - g2) / (4.0 * 3.14159265 * pow(max(denom, 1e-4), 1.5));
}
```

`denom`（分母の中の、1 + g² − 2g cosθ）は、**`cosθ = 1`（前方）のとき、最小**（`(1 − g)²`）になり、**値が、最大**になります。`g` を、大きくするほど、**前方への、偏りが、強く**なります。

| `g` | 散り方 | 例 |
| --- | --- | --- |
| 0 | **等方**（全方向に、均等） | — |
| 0.3〜0.5 | **やや、前方** | 薄い霧 |
| 0.7〜0.9 | **強く、前方** | 雲、濃い霧、**太陽の周りの、明るい輪（ハロー）** |
| 負 | **後方**に、偏る | — |

`max(denom, 1e-4)` は、**`g` が、1 に近く、`cosθ` も 1 に近い**ときの、**ゼロ割**（無限大）を、防ぎます。

### Cornette–Shanks

HG は、**後方散乱の、再現が、不十分**です。**Cornette と Shanks（1992）**は、**レイリーに、近い形**の、項（`1 + cos²θ`）を、足して、**より、実際の、ミー散乱に近い**形に、直しました。

```text
P_CS(θ, g) = 3 / (8π) × (1 − g²) / (2 + g²) × (1 + cos²θ) / (1 + g² − 2 g cosθ)^(3/2)
```

```hlsl
float CornetteShanks(float cos_theta, float g) {
  float g2 = g * g;
  float k = 3.0 / (8.0 * 3.14159265) * (1.0 - g2) / (2.0 + g2);
  return k * (1.0 + cos_theta * cos_theta) / pow(max(1.0 + g2 - 2.0 * g * cos_theta, 1e-4), 1.5);
}
```

**HG との違い**は、**分子の `(1 + cos²θ)`** です。**横や、後ろ**への、散り方が、**少し、多く**なります。**大気のミー散乱**（Hillaire の、実装の、標準）では、`g ≈ 0.8` の、**Cornette–Shanks**が、使われます。

## 2 つの、HG を、混ぜる

**雲**や、**霧**の、**実際の、散乱**は、**前方への、強い山**と、**後方への、小さな山**を、**両方、持ちます**。**HG を、2 つ**（前方 `g > 0` と、後方 `g < 0`）、**混ぜる**と、近似できます。

```hlsl
// 2 つの HG の、混合。前方の強い山と、後方の弱い山。
float DualLobePhase(float cos_theta, float g_forward, float g_back, float blend) {
  return lerp(HenyeyGreenstein(cos_theta, g_back), HenyeyGreenstein(cos_theta, g_forward), blend);
}
// 雲の例: g_forward = 0.8、g_back = −0.5、blend = 0.7
```

`blend` が、**前方の山の、割合**です。**雲の、太陽側の縁が、明るく光る**（前方散乱）効果と、**雲の、太陽と反対側が、うっすら明るい**（後方散乱）効果を、**両方**、出せます（[Cloud Lighting](../clouds/lighting.md)）。

Jendersie と d'Eon（2023）は、**雲や霧の、Mie 散乱に、より、近い**、**1 つの、近似式**（HG と、他の関数の、混合）を、提案しています。

## どれを、使うか

| 位相関数 | 向く対象 | コスト |
| --- | --- | --- |
| レイリー | **空気の分子**（空の青さ） | 最小 |
| **HG** | 霧、雲、**簡単に**、前方散乱を出したいとき | 小（`pow` 1 回） |
| **Cornette–Shanks** | 大気の**ミー散乱** | 小 |
| **2 つの HG の、混合** | **雲**（前方と後方の、両方） | 中 |
| 等方（`1 / 4π`） | **多重散乱の、近似**（光が、何度も、散って、向きが、均される） | 最小 |

## シェーダーでの、使い方

視線に沿った、各点で、**太陽の光が、視線の方向へ、どれだけ、散るか**を、求めます。

```hlsl
// view_dir: カメラから、点へ向かう、視線の向き。sun_dir: 点から、太陽へ向かう向き。
// 散乱角（太陽の光の、進む向きと、散乱後の向き = 視線の逆向き）の cos。
float cos_theta = dot(-view_dir, sun_dir);
float phase_r = RayleighPhase(cos_theta);
float phase_m = CornetteShanks(cos_theta, 0.8);
```

**光の進む向き**（太陽 → 点）と、**散乱後の向き**（点 → カメラ）の、間の角度が、`θ` です。**`cos θ` を、取る向き**（符号）を、間違えると、**前方と、後方が、逆**になり、**太陽の反対側が、明るい**、おかしな空になります。向きの規約を、**1 か所に決めて**、**位相関数に渡す**ことが、重要です。

''', before="## よくあるミス")
pg.Refs("atmosphere/scattering/phase-function.md", [HENYEY, CORNETTE, JENDERSIE, RAYLEIGH, RTR])

# ================================================================ single scattering
pg.Dedup("atmosphere/scattering/single-scattering.md")
pg.Add("atmosphere/scattering/single-scattering.md", '''
## 1 回散乱の、積分

**カメラに、届く光**を、考えます。太陽の光は、**大気の外から**来て、**視線の途中の、ある点で、1 回だけ、散乱**し、**カメラの方向へ**、向きを変えます。この、**1 回散乱の光**を、**視線に沿って、すべての点について、足し合わせる**のが、**1 回散乱の、積分**です（Nishita ら、1993）。

```text
L(x, v) = ∫₀^D  T(x → p(s))  ×  σ_s(p(s))  ×  Σ [ P(θ) × E_sun × T(p(s) → 大気の外) ]  ds
```

| 項 | 意味 |
| --- | --- |
| `T(x → p(s))` | 点 `p(s)` から、カメラ `x` までの、透過率（散乱した光が、**カメラまで、届く**割合） |
| `σ_s(p)` | 点 `p` での、**散乱係数**（密度に、比例） |
| `P(θ)` | **位相関数**（太陽の光が、視線の方向へ、散る割合） |
| `E_sun` | 太陽の光の、強さ |
| `T(p → 外)` | 点 `p` から、太陽方向への、透過率（**太陽の光が、点 `p` まで、届く**割合） |

**3 つの透過率の、掛け算**です。**太陽 → 点 `p`**（太陽の光が、点まで来る）、**点 `p` で散乱**、**点 `p` → カメラ**（散乱した光が、カメラまで来る）。

## 実装：視線に沿った、ループ

```hlsl
// 視線（カメラ位置 origin、方向 dir、長さ ray_length）に沿って、1 回散乱を積分する。
float3 SingleScattering(float3 origin, float3 dir, float ray_length, float3 sun_dir, float3 sun_illuminance) {
  const int kSteps = 32;
  float step_len = ray_length / kSteps;
```

視線を、**32 区間に分けて**、各区間の、**中央**で、評価します。`step_len` は、**1 区間の長さ**です。

```hlsl
  float cos_theta = dot(dir, sun_dir);                    // 視線と太陽の間の角度（太陽が、視線の向こうにあるとき 1）
  float phase_r = RayleighPhase(cos_theta);
  float phase_m = CornetteShanks(cos_theta, 0.8);
```

位相関数は、**視線と太陽の、間の角度**だけで決まり、**視線に沿って、一定**なので、**ループの外**で、1 回だけ、計算します。

```hlsl
  float3 sum = 0.0;                                       // 散乱光の、積算
  float3 throughput = 1.0;                                // 視線に沿った、ここまでの、透過率（カメラ → 点）
  for (int i = 0; i < kSteps; ++i) {
    float3 p = origin + dir * ((i + 0.5) * step_len);
    float h = length(p) - g_planet_radius;
    float density_r = exp(-h / 8000.0);
    float density_m = exp(-h / 1200.0);
```

ループの中で、**点 `p` の高度**から、**レイリーと、ミーの、密度**を、求めます。

```hlsl
    // この区間での、消散（吸収 + 散乱）で、視線の光が、どれだけ減るか。
    float3 sigma_t = g_rayleigh_scatter * density_r + g_mie_extinction * density_m;
    float3 step_transmittance = exp(-sigma_t * step_len);
```

**区間を、通るときの、透過率**です。これを、**`throughput` に、掛けていく**ことで、**カメラから、各点までの、透過率**が、**順に、求まります**（区間ごとの、透過率の、積）。

```hlsl
    // 太陽方向の透過率（LUT から）。大気の外から、この点まで、太陽の光が届く割合。
    float3 sun_t = SunTransmittance(p, sun_dir);
```

**太陽の光が、点 `p` まで、届く割合**を、**透過率 LUT**（[Transmittance](transmittance.md)）から、**1 回の読み込み**で、得ます。

```hlsl
    // この点で、視線の方向に、散乱される光。
    float3 scatter = (g_rayleigh_scatter * density_r * phase_r + g_mie_scatter * density_m * phase_m) * sun_t * sun_illuminance;
```

**散乱係数 × 位相関数 × 太陽の光**が、**この点で、視線の方向へ散る光**です。**レイリーと、ミー**を、**別々の、位相関数**で、足します。

```hlsl
    // 区間内の、積分（解析的に、減衰を考慮した形）を、足し込む。throughput は、カメラまでの、透過率。
    float3 scatter_integral = (scatter - scatter * step_transmittance) / max(sigma_t, 1e-6);
    sum += throughput * scatter_integral;
    throughput *= step_transmittance;
  }
  return sum;
}
```

**区間の中でも**、**光は、進むほど、減る**ので、**区間の中の、積分**を、**解析的に**、計算します（`(1 − exp(−σ_t Δs)) / σ_t`）。Hillaire（2020）が、**区間が、粗くても、エネルギーを、保つ**ために、使っている、**改良**です。**単純に、`scatter × step_len` を足す**方法より、**ステップ数が、少なくても、安定**します。

## 地面に、当たる場合

視線が、**地面に、当たる**場合は、**地面までで、積分を止め**、**地面の色**を、足します（**地平線の、下**を向いている、**空ではなく、地面**を見ている場合）。

```hlsl
float2 t_ground = RaySphere(origin, dir, g_bottom_radius);
float2 t_top = RaySphere(origin, dir, g_top_radius);
float ray_length = (t_ground.x > 0.0) ? t_ground.x : t_top.y;       // 地面に当たるなら、そこまで。そうでなければ、大気の上端まで
```

| 視線の向き | 積分する範囲 |
| --- | --- |
| 空へ向かう | カメラ → **大気の上端** |
| 地面へ向かう | カメラ → **地面** |
| カメラが、宇宙にある | 大気の**入口**から、上端、または、地面まで |

## 1 回散乱の、限界

**1 回だけ**散乱した光を、足し合わせた空は、**見た目が、暗く**、**不自然**です（特に、太陽が、**低い**とき、**日陰、夜明け、日没後**）。現実の、大気では、**光が、何度も、散乱**して、**空全体が、明るく**なります（[Multiple Scattering](multiple-scattering.md)）。

| 状況 | 1 回散乱のみ | 実際 |
| --- | --- | --- |
| 昼の空 | **やや暗い**（青が、足りない） | 明るい青 |
| 夕焼けの、反対側の空 | **暗い** | 青紫に、うっすら、明るい |
| 太陽が、地平線の、下 | **ほぼ、真っ暗** | しばらく、空が、明るい（薄明） |

''', before="## よくあるミス")
pg.Refs("atmosphere/scattering/single-scattering.md", [NISHITA, ONEIL, HILLAIRE, BRUNETON, PREETHAM])

# ================================================================ multiple scattering
pg.Dedup("atmosphere/scattering/multiple-scattering.md")
pg.Add("atmosphere/scattering/multiple-scattering.md", '''
## 多重散乱：なぜ、必要か

[Single-Scattering Integral](single-scattering.md) では、**光が、1 回だけ散乱**する場合を、扱いました。しかし、実際の、光は、**何度も、散乱**を、繰り返します。**2 回目以降の、散乱**を、足さないと、**空が、暗く、色が、不足**します。

| 散乱の回数 | 内容 |
| --- | --- |
| 1 回 | 太陽の光が、**1 回だけ**曲がって、カメラへ |
| 2 回 | 1 回目に、曲がった光が、**もう 1 回**、別の点で、曲がって、カメラへ |
| 3 回以上 | さらに、続く。**光は、回数が増えるほど、弱く、全方向に、均される** |

地球の大気では、**2 回目以降の、散乱**が、**空の明るさの、2 割〜3 割**を、占めます。**夕方・夜明け**（太陽が、低い）では、**割合が、さらに大きく**なります。

## 光が、何度も、散乱すると

**散乱を、繰り返す**たびに、光の向きは、**ばらばら**になります。**3 回目以降**は、**向きが、ほぼ、均一**（**等方**）と、みなせます。これを、**利用**した、**近似**があります。

## Hillaire の、近似

Hillaire（2020）は、多重散乱を、**次の、2 つの、仮定**で、近似しました。

1. **2 回目以降の、散乱は、位相関数が、等方**（`1 / 4π`）
2. **ある点での、多重散乱の、光は、その点の、周りの、情報で、決まる**（**空間的に、ゆるやかに、変化**する）

この仮定の下では、**多重散乱の、総和**は、**等比級数**で、**解析的に、表せます**。

```text
全散乱 = L₂ × (1 + f + f² + f³ + …) = L₂ / (1 − f)        （f < 1）
```

`L₂` は、**2 回散乱の光**、`f` は、**「1 回散乱するたびに、光が、散乱して、再び、その点の周りへ戻ってくる、割合」**です。

## 多重散乱 LUT

**高度**と、**太陽の天頂角**の、2 変数に、依存する、`L₂` と `f` を、**小さな、LUT**（Hillaire は **32×32**）に、事前計算します。

### 計算の考え方

各点（高度 `h`、太陽の、天頂角 `θ_s`）で、**球面上の、全方向**に、視線を、**飛ばし**、各方向の、**1 回散乱の光**（`L₂` の、材料）と、**その方向の、透過率**（`f` の材料）を、**積分**します。

```hlsl
// 多重散乱 LUT の、1 つの画素（= 1 つの、高度と、太陽の角度）を、計算する。
// 全方向（64 方向）に、視線を飛ばし、2 つの量を、平均する:
//   L2: 等方な位相関数で、1 回散乱した光（= 2 回目の散乱の、光源）
//   f:  各方向の、散乱で、再び、その点へ戻る、割合
[numthreads(1, 1, 64)]
void MultiScatteringCS(uint3 id : SV_DispatchThreadID, uint group_index : SV_GroupIndex) {
  // 画素から、高度と、太陽の天頂角の cos を求める。
  float2 uv = (id.xy + 0.5) / float2(32, 32);
  float cos_sun_zenith = uv.x * 2.0 - 1.0;
  float view_height = g_bottom_radius + uv.y * (g_top_radius - g_bottom_radius);
```

LUT の、**横軸が、太陽の天頂角**、**縦軸が、高度**です。**64 本の方向**を、**グループ内の、スレッド**（`id.z`）に、割り当てます。

```hlsl
  float3 sun_dir = float3(0.0, cos_sun_zenith, sqrt(saturate(1.0 - cos_sun_zenith * cos_sun_zenith)));
  float3 world_pos = float3(0.0, view_height, 0.0);

  // 球面上の 64 方向（フィボナッチ螺旋などで、均等に）。各スレッドが、1 方向を担当。
  float3 ray_dir = SphereDirection(group_index, 64);
  float3 L2 = 0.0;                                    // この方向の、「等方な 1 回散乱」
  float3 f_ms = 0.0;                                  // この方向の、「戻ってくる割合」
```

**方向の、選び方**は、**球面を、均等に**、覆う、パターンです。**64 方向**で、**滑らかな、LUT** が、得られます。

```hlsl
  // この方向に、視線を進めて、1 回散乱（位相関数は、等方 = 1/4π）を、積分する。
  IntegrateMultiScatter(world_pos, ray_dir, sun_dir, /*out*/ L2, /*out*/ f_ms);

  // 64 方向を、グループ内で、合計して、平均する（共有メモリで、リダクション）。
  // ... 合計の処理 ...

  // 最終結果: 等比級数の、和。f が 1 に近いほど、多重散乱が、強い。
  float3 multi_scattering = L2 / (1.0 - f_ms);
  g_multi_scattering_lut[id.xy] = multi_scattering;
}
```

`IntegrateMultiScatter` の、中身は、**1 回散乱の、積分**（[Single-Scattering Integral](single-scattering.md)）と、**ほぼ同じ**ですが、**位相関数が、等方**（`1 / 4π`）で、**同時に、`f_ms`** も、足します。

## 空の、計算で、使う

**多重散乱 LUT** は、**1 回散乱の、ループ**の中で、**各点**に、**足す**だけです。

```hlsl
    // 各サンプル点で、多重散乱の光を、足す（LUT を、1 回、読むだけ）。
    float2 ms_uv = float2(saturate(cos_sun_zenith_at_p * 0.5 + 0.5), saturate((h - g_bottom_radius) / (g_top_radius - g_bottom_radius)));
    float3 multi = g_multi_scattering_lut.SampleLevel(g_linear_clamp, ms_uv, 0).rgb;
    float3 scatter = (g_rayleigh_scatter * density_r + g_mie_scatter * density_m) * (sun_t * phase_term * sun_illuminance + multi * sun_illuminance);
```

**多重散乱の光は、位相関数なし**（等方）で、**散乱係数だけ**を、掛けて、足します。**1 回散乱**（太陽の透過率 × 位相関数）と、**多重散乱**（LUT）を、**足し合わせる**形です。

## 効果

| 状況 | 1 回散乱のみ | 多重散乱あり |
| --- | --- | --- |
| 昼の空の、明るさ | 暗め | **実際の明るさ** |
| 太陽が、低い、空 | 暗く、色が、不足 | **全体が、明るく、紫〜青の、グラデーション** |
| **雲の、中**や、**霧の、中** | 暗い（光が、奥まで、届かない） | **明るい**（光が、散乱を、繰り返して、奥まで、届く） |

## 雲・霧の、多重散乱

雲は、**ミー散乱が、強く**、**アルベド**（散乱の割合）が、**非常に、高い**（ほぼ 1）ため、**光が、何十回も、散乱**します。**多重散乱**を、無視すると、**雲の、内部が、暗く、墨のように**なります。

| 方法 | 内容 |
| --- | --- |
| **オクターブによる近似**（Wrenninge、2015） | 散乱を、**数段階（オクターブ）**に、分け、**各段階で、減衰を、弱め、位相関数を、等方に、近づける**。各オクターブを、**足し合わせる** |
| **事前計算** | 雲の、密度から、**多重散乱の、ライトマップ**を、作る |

```hlsl
// Wrenninge の、オクターブによる、多重散乱の、近似（雲のライティングで、使われる）。
float3 MultiScatterOctaves(float density_along_light, float cos_theta) {
  float3 sum = 0.0;
  float a = 1.0, b = 1.0, c = 1.0;           // 各オクターブの、散乱量、減衰、位相関数の、偏りの、倍率
  for (int octave = 0; octave < 4; ++octave) {
    float phase = DualLobePhase(cos_theta, 0.8 * c, -0.5 * c, 0.7);
    sum += a * phase * exp(-density_along_light * g_sigma_t * b);
    a *= 0.5;                                // 散乱量は、半分ずつ
    b *= 0.25;                               // 減衰は、弱く（光が、深くまで、届く）
    c *= 0.5;                                // 位相関数の、偏りは、弱く（等方に近づく）
  }
  return sum;
}
```

**オクターブが、進むほど**、**散乱量が、減り**（`a`）、**減衰が、弱まり**（`b`、光が、深く届く）、**位相関数が、等方に、近づく**（`c`）。この、**3 つの、調整**が、**多重散乱の、性質**（**弱く、深く、均一**）を、模倣します（[Cloud Lighting](../clouds/lighting.md)）。

''', before="## よくあるミス")
pg.Refs("atmosphere/scattering/multiple-scattering.md", [HILLAIRE, WRENNINGE, BRUNETON, RTR])

pg.Refs("atmosphere/scattering/index.md", [HILLAIRE, BRUNETON, NISHITA, ONEIL, WRENNINGE])
print("ok")
