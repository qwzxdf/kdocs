import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import pg  # noqa: E402

SCHLICK = '''Schlick, "An Inexpensive BRDF Model for Physically-based Rendering", Computer Graphics Forum, Vol. 13, No. 3, 1994（Schlick 近似）'''
POPE = '''Pope, Fry, "Absorption Spectrum (380–700 nm) of Pure Water. II. Integrating Cavity Measurements", Applied Optics, Vol. 36, No. 33, 1997（純水の吸収係数の測定値）'''
GORDON = '''Gordon, Brown, Jacobs, "Computed Relationships between the Inherent and Apparent Optical Properties of a Flat Homogeneous Ocean", Applied Optics, Vol. 14, No. 2, 1975（水中の散乱と吸収から、水の色を求める式）'''
JERLOV = '''Jerlov, "Marine Optics", Elsevier, 1976（海水の水質の分類 Jerlov water types）'''
COXMUNK = '''Cox, Munk, "Measurement of the Roughness of the Sea Surface from Photographs of the Sun's Glitter", Journal of the Optical Society of America, Vol. 44, No. 11, 1954（風速と波の傾きの関係）'''
WALTER = '''Walter, Marschner, Li, Torrance, "Microfacet Models for Refraction through Rough Surfaces", Eurographics Symposium on Rendering 2007（GGX 分布の原典）'''
OLANO = '''Olano, Baker, "LEAN Mapping", Symposium on Interactive 3D Graphics and Games 2010'''
SOUSA = '''Sousa, "Generic Refraction Simulation", GPU Gems 2, Chapter 19, 2005（画面のコピーを、ずらして使う屈折）'''
MITTRING = '''Mittring, "Finding Next Gen: CryEngine 2", SIGGRAPH 2007, Advances in Real-Time Rendering in 3D Graphics and Games（水の描画、平面反射と、屈折のコピー）'''
TESSENDORF = '''Tessendorf, "Simulating Ocean Water", SIGGRAPH 2001 Course Notes'''
RTR = '''Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（フレネル、屈折、スネルの法則）'''
D3D11_DEPTH = '''Microsoft Learn, "Reading depth-stencil as shader resource"（深度バッファを、`R32_TYPELESS` で作って、SRV として読む方法）'''
LAGARDE = '''Lagarde, de Rousiers, "Moving Frostbite to Physically Based Rendering 3.0", SIGGRAPH 2014（反射と、フレネルの扱い）'''

# ---------------------------------------------------------------- fresnel
pg.Dedup("water/shading/fresnel.md")
pg.Add("water/shading/fresnel.md", '''
## 反射率は、角度で決まる

水面に、光が当たると、一部は、**反射**し、残りは、水の中へ**屈折**して入ります。**反射する割合**が、フレネル反射率 `F` です。`F` は、**入射の角度**と、**2 つの物質の屈折率**で、決まります。

| 見る角度 | 水面の反射率 F | 見え方 |
| --- | --- | --- |
| 真上から（0°） | 約 2% | ほぼ、透明。底が見える |
| 45° | 約 2.5% | まだ、透けている |
| 60° | 約 6% | 少し、空が映る |
| 80° | 約 35% | 空と、水面が、混ざって見える |
| 89°（地平線のあたり） | 約 90% | **ほぼ、鏡** |

遠くの水面が、**空の色に、光って見える**のは、視線が、水面に浅い角度で、当たっているためです。

## 正確な式（フレネルの式）

屈折率 `n₁`（空気 1.0）から、`n₂`（水 1.33）へ、入射角 `θᵢ`、屈折角 `θₜ` のとき、**偏光の 2 成分**（s 偏光と p 偏光）の反射率は、次のとおりです。

```text
Rs = ( (n₁ cosθᵢ − n₂ cosθₜ) / (n₁ cosθᵢ + n₂ cosθₜ) )²
Rp = ( (n₁ cosθₜ − n₂ cosθᵢ) / (n₁ cosθₜ + n₂ cosθᵢ) )²
F  = (Rs + Rp) / 2                      ← 偏光していない光（太陽光、空の光）の平均
```

`θₜ` は、**スネルの法則** `n₁ sinθᵢ = n₂ sinθₜ` から、求めます。

```hlsl
// 正確なフレネル反射率（偏光していない光）。eta = n2 / n1（空気 → 水なら 1.33）。
float FresnelExact(float cos_i, float eta) {
  float sin_t2 = (1.0 - cos_i * cos_i) / (eta * eta);     // sin²θt（スネルの法則から）
  if (sin_t2 >= 1.0) return 1.0;                           // 全反射（水中から、空を見るとき）
  float cos_t = sqrt(1.0 - sin_t2);
  float rs = (cos_i - eta * cos_t) / (cos_i + eta * cos_t);
  float rp = (eta * cos_i - cos_t) / (eta * cos_i + cos_t);
  return 0.5 * (rs * rs + rp * rp);
}
```

水中から、水面を見上げるとき（`n₁ = 1.33`、`n₂ = 1.0`）、`sin θₜ` が 1 を超える角度では、**光が、外へ出られず、すべて反射**します（全反射）。この現象は、[The Underside of the Surface and Crossing It](../underwater/surface-back.md) で扱います。

## F₀ を、屈折率から求める

真上から（`θ = 0`）のときの反射率 `F₀` は、式を簡単にできます。

```text
F₀ = ( (n₂ − n₁) / (n₂ + n₁) )²  =  ( (1.33 − 1.0) / (1.33 + 1.0) )²  ≈ 0.0201
```

水の `F₀` は、**約 2%** です。ガラス（`n = 1.5`）が 4%、ダイヤモンド（`n = 2.4`）が 17% なので、水は、反射率が、低い部類です。

## Schlick 近似

正確な式は、`sqrt` や、割り算を含んでいて、重いです。**Schlick の近似**（1994）は、ほぼ同じ形を、**5 乗の式**で、表します。

```text
F(θ) ≈ F₀ + (1 − F₀) × (1 − cosθ)⁵
```

```hlsl
float FresnelSchlick(float cos_theta, float f0) {
  return f0 + (1.0 - f0) * pow(1.0 - saturate(cos_theta), 5.0);
}
```

### 近似は、どのくらい合うか

| 入射角 | 正確な式 | Schlick | 差 |
| --- | --- | --- | --- |
| 0° | 0.020 | 0.020 | 0 |
| 60° | 0.021 | 0.021 | 小さい |
| 70° | 0.034 | 0.031 | 小さい |
| 80° | 0.138 | 0.113 | やや差がある |
| 88° | 0.62 | 0.60 | 小さい |

水の場合、Schlick 近似は、**全体として、十分に、近い**です。**低い角度（80° 付近）で、やや、小さく出る**程度で、見た目では、ほとんど、気づきません。**特別な理由がなければ、Schlick を使います**。

## 水面で気をつけること

### ① 法線で、`cos θ` を求める

`cos θ` は、**波で傾いた法線**と、視線の内積です。**波の法線**を、使います。

```hlsl
float cos_theta = saturate(dot(wave_normal, view_dir));
float F = FresnelSchlick(cos_theta, 0.02);
```

幾何学的な（平らな水面の）法線 `(0, 1, 0)` を、使うと、**波による、反射の変化**が出ません。

### ② 遠くで、波の法線を弱める

遠くの水面は、**波の法線が、ちらつく**ので、弱めます（[Computing Normals](../waves/normals.md)）。弱めると、法線が、真上に近づき、`cos θ` が、**実際の、見る角度より、大きく**なって、**反射が、弱く**なります。これを避けるには、**フレネルの計算に、使う法線は、遠くで、弱めすぎず、粗さで補う**か、**平らな水面の `cos θ`** を、遠くで、混ぜます。

```hlsl
// 遠くでは、波の法線の影響を弱めすぎず、地平線に近づくと、反射が強くなる効果を保つ。
float3 N_fresnel = normalize(lerp(wave_normal, float3(0, 1, 0), saturate(dist / 500.0)));
float F = FresnelSchlick(saturate(dot(N_fresnel, view_dir)), 0.02);
```

### ③ 粗さと、フレネル

表面が、粗いと、**浅い角度での、反射率が、少し下がり**ます（微小な凹凸が、反射を、遮るため）。水面でも、波が荒れると、効きます。PBR では、フレネル反射率を、**粗さで、少し、下げる**補正が、使われます（IBL の、フレネルの扱いは、Lagarde と de Rousiers、2014 を参照）。

```hlsl
// 粗さで、浅い角度の反射の上限を、下げる（Lagarde）。
float3 FresnelSchlickRoughness(float cos_theta, float3 f0, float roughness) {
  return f0 + (max(float3(1.0 - roughness, 1.0 - roughness, 1.0 - roughness), f0) - f0)
              * pow(1.0 - saturate(cos_theta), 5.0);
}
```

## 反射と、屈折の混ぜ方

`F` は、**反射する割合**です。残りの `1 − F` が、**水の中へ入る**割合です。

```hlsl
float3 reflection = SampleReflection(...);          // 空、周囲の景色
float3 refraction = SampleRefraction(...);          // 水の中の景色（底、水の色）
float3 color = lerp(refraction, reflection, F);     // F が大きいほど、反射が、見える
```

| 状況 | F | 見え方 |
| --- | --- | --- |
| 足元の水（真上から見る） | 0.02 | 屈折（底が見える）が、ほぼ全て |
| 少し先の水 | 0.05〜0.1 | 底が、見えながら、空が、うっすら映る |
| 遠くの水 | 0.5〜0.9 | 空が、ほぼ全て。水の中は、見えない |

**1 つの式（`F`）で、水面の見た目の大半が、決まります**。フレネルを、**入れ忘れる**（反射を、一定の割合で混ぜる）と、**水が、プラスチックのように、不自然**に見えます。

''', before="## よくあるミス")
pg.Refs("water/shading/fresnel.md", [SCHLICK, RTR, LAGARDE, WALTER])

# ---------------------------------------------------------------- depth color
pg.Dedup("water/shading/depth-color.md")
pg.Add("water/shading/depth-color.md", '''
## 水は、色を吸収する

純水は、**赤い光を、よく吸収し、青い光を、あまり吸収しません**。厚い水の層を、通った光は、**赤が先に消え、青が最後まで残り**ます。これが、**海や、プールが、青い**理由です。

| 波長 | 吸収係数 a（1/m、純水） | 1 m で、残る割合 | 10 m で、残る割合 |
| --- | --- | --- | --- |
| 赤（650 nm） | 約 0.34 | 71% | 3% |
| 緑（550 nm） | 約 0.06 | 94% | 55% |
| 青（450 nm） | 約 0.01 | 99% | 90% |

数値は、純水の測定値（Pope と Fry、1997）の目安です。実際の海水や湖水は、**植物プランクトンや、濁り**で、**緑や、茶色に、寄る**ので、もっと、大きな値になります（Jerlov、1976 の水質分類）。

## Beer–Lambert の法則

光が、吸収だけで減る媒質を、距離 `d` だけ進んだとき、**残る光の割合（透過率）**は、指数関数で、減ります。

```text
T = exp( −a × d )
```

`a` は、色（RGB）ごとに、違う値を持ちます。

| 吸収係数（RGB） | 水の種類 |
| --- | --- |
| (0.34, 0.06, 0.01) | 純水（理論値。南の海のように、非常に澄んだ水） |
| (0.45, 0.07, 0.03) | きれいな、海水 |
| (0.8, 0.2, 0.15) | 少し、濁った水 |
| (1.5, 0.6, 0.5) | 湖、川（緑〜茶色） |

```hlsl
float3 absorption = float3(0.45, 0.07, 0.03);       // 1/m（RGB）
float3 transmittance = exp(-absorption * water_depth);
```

## 水の色は、2 つの項でできている

水を通して、底を見るときの色は、**底から来る光が、減ったもの**と、**水自体が、散乱して返す光**の、足し算です。

```text
見える色 = 底の色 × T  +  水の色 × (1 − T)
```

| 項 | 内容 |
| --- | --- |
| `底の色 × T` | 底（砂、岩）で反射した光が、水を通ってくる間に、吸収されて、減った分 |
| `水の色 × (1 − T)` | 水の中で、**散乱**されて、目に届く光。深くなるほど、増える |

```hlsl
float3 refracted = scene_color * transmittance + deep_color * (1.0 - transmittance);
```

**浅いと**、`T ≈ 1` なので、底の色が、そのまま見えます。**深いと**、`T ≈ 0` なので、底は見えず、**水自体の色（`deep_color`）**になります。

### `deep_color` は、どう決めるか

`deep_color` は、**水が、空の光を、散乱して返す色**です。散乱が、強く、吸収が、弱いほど、明るく、青くなります。**吸収と散乱から、計算**できます（[Scattering Color (SSS-Like)](scattering.md)）。

```text
deep_color ≈ 空と太陽の光 × f × b_b / (a + b_b)        f ≈ 0.33、b_b: 後方散乱係数
```

簡単には、**吸収係数と同じ傾向を持つ、青緑の色**を、アーティストが、直接決めます。

## 水深の、求め方

水深 `d` は、**水面の位置**と、**水の向こうにある、不透明な物（底）の位置**の、距離です。**深度バッファ**から、求めます。

```text
水深 = 底までの距離（視線方向）− 水面までの距離
```

### 視線方向の距離か、鉛直方向の水深か

| 距離 | 内容 | 使う場面 |
| --- | --- | --- |
| 視線方向の距離 | 目から、水面、底までの、**視線に沿った**距離の差 | **光が、水の中を、進む距離**。吸収に使う（斜めから見ると、長く進むので、色が、濃い） |
| 鉛直方向の水深 | 水面から、底までの、**真下への**深さ | 泡、岸辺の、境界（岸に近い所で、水が浅い） |

吸収（Beer の法則）には、**視線方向の距離**を、使います。**斜めから見るほど、光が、水の中を長く通る**ので、色が、濃くなります。

```hlsl
// 水面のピクセルで、水深（視線方向）を求める。
float scene_ndc_depth = g_scene_depth.Sample(g_point_clamp, screen_uv).r;
float scene_linear = LinearizeDepth(scene_ndc_depth);       // 底（不透明な物）までの、視点深度
float surface_linear = input.view_depth;                      // 水面までの、視点深度
float water_depth = max(scene_linear - surface_linear, 0.0);  // 視線方向の距離ではなく、視点深度（z）の差

// 視点深度の差は、「カメラの前方向」に沿った距離。視線方向の距離にするには、cos で割る。
float3 view_dir = normalize(input.world_position - camera_position);
float cos_view = max(dot(view_dir, camera_forward), 0.1);
float path_length = water_depth / cos_view;
```

`LinearizeDepth` は、深度バッファの値を、カメラからの距離（ビュー空間の `z`）に直す関数です。

```hlsl
// 通常の（非 reversed）射影行列の場合。near, far はカメラのクリップ面。
float LinearizeDepth(float d) {
  return near_plane * far_plane / (far_plane - d * (far_plane - near_plane));
}
```

## DirectX 11 で、深度バッファを、シェーダーで読む

水面を描くとき、**水より手前に、描かれた、不透明な物の深度**を、読む必要があります。深度バッファを、**深度ステンシル ビュー（書き込み用）**と、**シェーダー リソース ビュー（読み取り用）**の、両方で使えるように、作ります。

```cpp
// 深度テクスチャ: TYPELESS で作って、DSV と SRV で、別々の形式のビューを作る。
D3D11_TEXTURE2D_DESC desc = {};
desc.Width = width;
desc.Height = height;
desc.MipLevels = 1;
desc.ArraySize = 1;
desc.Format = DXGI_FORMAT_R32_TYPELESS;                       // 型なし
desc.SampleDesc.Count = 1;
desc.Usage = D3D11_USAGE_DEFAULT;
desc.BindFlags = D3D11_BIND_DEPTH_STENCIL | D3D11_BIND_SHADER_RESOURCE;
device->CreateTexture2D(&desc, nullptr, &depth_tex);

D3D11_DEPTH_STENCIL_VIEW_DESC dsv = {};
dsv.Format = DXGI_FORMAT_D32_FLOAT;                           // 書き込み用
dsv.ViewDimension = D3D11_DSV_DIMENSION_TEXTURE2D;
device->CreateDepthStencilView(depth_tex.Get(), &dsv, &depth_dsv);

D3D11_SHADER_RESOURCE_VIEW_DESC srv = {};
srv.Format = DXGI_FORMAT_R32_FLOAT;                           // 読み取り用
srv.ViewDimension = D3D11_SRV_DIMENSION_TEXTURE2D;
srv.Texture2D.MipLevels = 1;
device->CreateShaderResourceView(depth_tex.Get(), &srv, &depth_srv);
```

**同じ深度テクスチャを、DSV として、設定したまま、SRV としても、読むことは、できません**（読み書きの衝突）。水の描画では、**深度の書き込みを、無効**にして、DSV を **読み取り専用**（`D3D11_DSV_READ_ONLY_DEPTH` を指定した DSV）にするか、**深度を、コピー**してから、読みます。

```cpp
// 読み取り専用の DSV: 深度テストはできるが、書き込みはしない。同時に SRV としても読める。
D3D11_DEPTH_STENCIL_VIEW_DESC dsv_ro = dsv;
dsv_ro.Flags = D3D11_DSV_READ_ONLY_DEPTH;
device->CreateDepthStencilView(depth_tex.Get(), &dsv_ro, &depth_dsv_readonly);
```

## 水の色の、仕上げ

### 光が、水深とともに、減る（環境光）

深い所では、**太陽の光そのもの**が、届かなくなります。水中の物（底の岩）を、ライティングするとき、光の、減衰も、考える必要があります。

```hlsl
// 水面から深さ d の所へ届く、太陽光の減衰（赤が、先に消える）。
float3 sun_at_depth = sun_color * exp(-absorption * depth_below_surface);
```

### 水自体の色（`deep_color`）も、時間帯で変わる

`deep_color` を、固定の色にすると、**夜も、昼と同じ色**になります。`deep_color` は、**空の光を、散乱して返す**ので、空の明るさ（太陽の高さ、天気）に、**比例させます**。

```hlsl
float3 deep_color = base_deep_color * (sky_irradiance + sun_color * saturate(sun_dir.y) * 0.5);
```

### 浅瀬：底の色を、見せる

浅い水で、**底の色が、見える**ためには、**屈折（歪み）を、適用した位置で、底の色を、読む**必要があります（[Water Refraction Distortion](refraction.md)）。**水深を、読む位置も、歪ませた位置**にして、深さの、整合性を、保ちます。

''', before="## よくあるミス")
pg.Refs("water/shading/depth-color.md", [POPE, JERLOV, GORDON, D3D11_DEPTH, MITTRING])

# ---------------------------------------------------------------- specular
pg.Dedup("water/shading/specular.md")
pg.Add("water/shading/specular.md", '''
## 太陽の反射は、細かい波の集まり

水面に、太陽が映ると、**1 つの、丸い光ではなく、波ごとに散らばった、細かい光の帯**になります（**グリッター、sun glitter**）。**波の表面は、細かい、無数の、小さな傾き**を持っています。**太陽の方向を、反射する向きに傾いた波の面**だけが、光ります。

```text
太陽 ↘      ↙ 目
      ╱╲╱╲╱╲        ← 波。目に向かって光を反射する向きの面だけが光る
```

## 風速と、傾きの分布（Cox と Munk）

波の面の、傾きの分布は、**風速**で決まります。Cox と Munk（1954）は、**海面の、写真から、太陽の光の分布を調べ**、傾きの、2 乗平均が、風速に、ほぼ比例することを示しました。

```text
波の傾きの 2 乗平均 m² ≈ 0.003 + 0.00512 × U         U: 風速（m/s）
```

| 風速 U（m/s） | m² | 傾きの目安（√m²） | 見た目 |
| --- | --- | --- | --- |
| 0 | 0.003 | 0.055（約 3°） | 鏡のような水面。光が、1 つに、集まる |
| 5 | 0.029 | 0.17（約 10°） | 光が、広がり始める |
| 10 | 0.054 | 0.23（約 13°） | 光の帯が、太く、散らばる |
| 15 | 0.080 | 0.28（約 16°） | 広い範囲が、ぎらつく |

**風が強いほど、波が、荒れて、光る範囲は、広くなり、1 点の明るさは、下がります**。

## 粗さへの、対応

GGX や Beckmann などの、**微小面分布**（法線の分布）の、粗さを、波の傾きの分布に、合わせます。Beckmann 分布のパラメーター `m` は、**傾きの 2 乗平均の、平方根**そのものです。

```text
m² = 傾きの 2 乗平均 = 0.003 + 0.00512 × U         ← Beckmann の m
GGX の roughness（α）≈ m                            ← 近似（GGX は、裾が長い。最終は、見た目で調整）
```

```hlsl
// 風速から、粗さを決める。
float WaterRoughness(float wind_speed) {
  float m2 = 0.003 + 0.00512 * wind_speed;
  return sqrt(m2);                                // GGX の α の目安
}
```

## 太陽の反射を、計算する

PBR の、スペキュラー（GGX）で、計算します。太陽は、**平行光**として、扱います（[PBR](../../../3d/pbr.md)）。

```hlsl
float D_GGX(float n_dot_h, float a) {
  float a2 = a * a;
  float d = n_dot_h * n_dot_h * (a2 - 1.0) + 1.0;
  return a2 / (3.14159265 * d * d);
}

float V_SmithGGX(float n_dot_l, float n_dot_v, float a) {
  // 高さ相関 Smith（可視性項）
  float a2 = a * a;
  float gv = n_dot_l * sqrt(n_dot_v * n_dot_v * (1.0 - a2) + a2);
  float gl = n_dot_v * sqrt(n_dot_l * n_dot_l * (1.0 - a2) + a2);
  return 0.5 / max(gv + gl, 1e-5);
}

float3 WaterSunSpecular(float3 N, float3 V, float3 L, float3 sun_radiance, float roughness) {
  float3 H = normalize(V + L);
  float n_dot_h = saturate(dot(N, H));
  float n_dot_l = saturate(dot(N, L));
  float n_dot_v = saturate(dot(N, V)) + 1e-4;
  float a = max(roughness, 0.02);                 // 0 にすると、点光源が 1 画素に落ちて、ちらつく
  float F = FresnelSchlick(saturate(dot(H, V)), 0.02);
  return sun_radiance * F * D_GGX(n_dot_h, a) * V_SmithGGX(n_dot_l, n_dot_v, a) * n_dot_l;
}
```

**フレネル項**は、`H` と `V` の内積で、計算します（反射を起こす、微小面の向きで、角度を測る）。水の場合、`F₀ = 0.02` です。

## 見た目を、決める 3 つの要素

### ① 強さ（HDR）

太陽の反射は、**空よりはるかに、明るい**です（太陽は、空の数万倍）。**HDR で出力**して、**ブルーム**を、かけると、**まぶしく光る**様子が出ます。LDR のまま、クランプすると、**白く、ただ飽和**するだけです（[Post-Processing](../../postprocess/index.md)）。

| 太陽の、輝度（放射輝度）の目安 | 値 |
| --- | --- |
| 青空 | 数千 cd/m² |
| 太陽（直視） | 10⁹ cd/m²（約 10 億） |

実際の値を、そのまま使うのではなく、**露出と、ブルームを、見た目で調整**します（[Exposure](../../postprocess/tonemapping/exposure.md)）。

### ② 法線の、細かさ

**細かい法線**（さざ波）を、使うほど、光が、**細かく、散らばって**、きらきら光ります。**大きな波の法線だけ**だと、**1 つの、大きな光**になります（[Computing Normals](../waves/normals.md)）。

### ③ 遠くの、ちらつき

**遠くの水面**では、1 画素に、**多数の波が、入り**、法線が、画素ごとに、ばらついて、**光が、ちらつきます**。対策は、2 つです。

| 対策 | 内容 |
| --- | --- |
| 距離で、粗さを、上げる | 遠くほど、`roughness` を大きくして、光を、広げて、ならす |
| 法線の分散を、粗さに足す | 法線マップの、ミップで、失われる、ばらつきを、粗さに足す（LEAN マッピング、Olano と Baker、2010） |

```hlsl
// 距離で、粗さを上げる。
float roughness = lerp(base_roughness, base_roughness + 0.25, saturate(dist / 300.0));
```

## 太陽以外の、光源

| 光源 | 扱い |
| --- | --- |
| 太陽 | 上の式（方向光） |
| 月 | 同じ式で、強さだけ、下げる |
| 点光源（街灯、船のランプ） | 同じ式で、点光源の方向・減衰を使う。**水面に、**縦に、伸びた光の帯**が出る（波で、光源の反射が、縦に散る） |
| 空（環境光） | 反射は、別（[Water Reflection](reflection.md)） |

''', before="## よくあるミス")
pg.Refs("water/shading/specular.md", [COXMUNK, WALTER, OLANO, LAGARDE, TESSENDORF])

# ---------------------------------------------------------------- scattering
pg.Dedup("water/shading/scattering.md")
pg.Add("water/shading/scattering.md", '''
## 水の色は、どこから来るのか

水を通して見える色は、**底から来る光が、減ったもの**と、**水自体から返ってくる光**の、足し算でした（[Color by Water Depth](depth-color.md)）。後者は、**水の中で、光が、散乱**して、目に届く光です。この光が、**水の色**を作っています。

| 現象 | 内容 |
| --- | --- |
| 吸収 | 光が、水に、吸い取られる。赤が先に消える。係数 `a`（1/m） |
| 散乱 | 光が、水の中で、向きを変える。係数 `b`（1/m） |
| 後方散乱 | 散乱のうち、**来た方向へ、戻る**成分。係数 `b_b`。目に届く光の、源 |

海が、**青く見える**のは、赤が吸収され、**青い光が、後方散乱で、返ってくる**ためです。

## 水の色を、計算する

Gordon ら（1975）は、**深い水の、水面から出てくる光の割合**を、吸収と、後方散乱から、次の式で、近似しました。

```text
R ≈ f × b_b / (a + b_b)         f ≈ 0.33
```

`R` は、**入ってきた光の、何割が、水面から、戻ってくるか**を表します（**体積反射率**）。

| 水 | `a`（RGB） | `b_b` | `R`（RGB） |
| --- | --- | --- | --- |
| 澄んだ海 | (0.45, 0.07, 0.03) | 0.005 | (0.004, 0.023, 0.048) |
| 濁った、緑の湖 | (0.8, 0.3, 0.3) | 0.02 | (0.008, 0.021, 0.021) |
| プール（白いタイル） | 底の色が、見える。ここでは、深い水の色の話 | — | — |

`b_b` が、`a` に比べて、小さいので、**R は、小さい値**です。**海は、暗い**のが、普通です。値が、青の成分が、最も大きい（`a` が、青で最小）ことが、**海が、青く見える**理由です。

```hlsl
// 深い水の色（体積反射率）。吸収 a（RGB）と、後方散乱 bb（スカラー）から計算する。
float3 DeepWaterColor(float3 absorption, float backscatter, float3 incident_light) {
  float3 R = 0.33 * backscatter / (absorption + backscatter);
  return incident_light * R;
}
```

`incident_light` は、**水面に降り注ぐ光**（空の光と、太陽光）です。昼と夜、晴れと曇りで、**水の色**も、変わります。

```hlsl
// 水面に降り注ぐ光 = 空の光 + 太陽光。
float3 irradiance = sky_irradiance + sun_color * saturate(sun_dir.y);
float3 water_color = DeepWaterColor(absorption, 0.005, irradiance / 3.14159265);
```

## 波頭が、透けて光る

太陽を背にして、波を見ると、**波頭が、明るい青緑に、光って見える**ことがあります。波頭では、**水の層が薄く**、**背後から、来た太陽光が、水を通り抜けて**、目に届くためです。

**簡単な近似**は、次のとおりです。

```hlsl
// 波頭の透過光（SSS 風）。
float height_factor = saturate((wave_height - sss_height_start) / sss_height_range);   // 高い波頭ほど 1
float sun_behind = pow(saturate(dot(view_dir, -sun_dir)), 4.0);                         // 太陽が、波の向こう側のときだけ
float3 sss = scatter_color * height_factor * sun_behind * sun_intensity;
```

| 要素 | 内容 |
| --- | --- |
| `height_factor` | 波の、**高さ**（または、波の傾きが大きい場所）。**波頭に、近いほど、強い** |
| `sun_behind` | 視線と、太陽の向きが、**逆向き（太陽が、水面の向こう側）**のときだけ、光る |
| `scatter_color` | 青緑の、明るい色（水が、薄い所を、通る光の色） |

波の**頂点の高さ**を、使うので、**波が大きい（荒れた）日ほど、強く**出ます。

!!! warning "入れすぎると、水が、発光する"
    この項は、**足し算**です。強くしすぎると、**水面全体が、ぼんやり光って**見えます。**波頭の、一部だけが、ほんのり光る**くらいに、抑えます。

## 浅瀬の、散乱

浅い場所の、水の色は、**水の散乱の色**と、**底の色**の、混ざったものです。底の色が、白い砂だと、**散乱した光が、明るく、水が、鮮やかな水色**になります。

| 底の色 | 浅い水の見え方 |
| --- | --- |
| 白い砂 | 明るい、水色（南国の海） |
| 暗い岩・泥 | 暗い、濃い色（北の海、沼） |
| 緑の藻 | 緑がかった色 |

**底のテクスチャの色**を、**屈折で、読み**、**水の色と混ぜる**ことで、この違いが、自然に出ます（[Color by Water Depth](depth-color.md)）。

''', before="## よくあるミス")
pg.Refs("water/shading/scattering.md", [GORDON, JERLOV, POPE, TESSENDORF])

# ---------------------------------------------------------------- reflection
pg.Dedup("water/shading/reflection.md")
pg.Add("water/shading/reflection.md", '''
## 反射の、取り方

水面には、**空、雲、遠くの山、近くの建物**が、映ります。映す方法を、状況に合わせて、選び、重ねます。

| 方法 | 映るもの | コスト | 弱点 |
| --- | --- | --- | --- |
| 環境マップ（キューブマップ） | 空、遠景 | 小 | 近くの物（船、岸の建物）が映らない |
| 平面反射 | 水面の上にある、**すべて** | 大（シーンを、もう一度描く） | 波で乱れた反射が、作れない（ごまかす） |
| SSR | 画面に映っているもの | 中 | **画面の外が、映らない**。水平に近い視線で、画面の端から、反射が消える |
| レイトレーシング | すべて | 大 | 対応する GPU が必要 |

## 重ね方：フォールバック

実際のゲームでは、**1 つだけでは足りない**ので、重ねます。

```text
   平面反射 or SSR   （近くの物。画面内の物）
        ↓ 失敗した（映っていない）ピクセルは
   環境マップ         （空、遠景。必ず映る）
```

| 順 | 方法 | 決め方 |
| --- | --- | --- |
| 1 | SSR（または平面反射） | 反射レイが、画面の中の物に、当たったら使う。当たらなければ、次へ |
| 2 | 環境マップ（空） | SSR が、当たらなかったとき |

```hlsl
float3 reflect_dir = reflect(-view_dir, normal);

// ① SSR（当たった場合のみ、色と、信頼度（0〜1）を返す）
float4 ssr = TraceScreenSpaceReflection(world_pos, reflect_dir);   // rgb = 色、a = 信頼度

// ② 環境マップ（空）
float3 sky = g_sky_cube.SampleLevel(g_linear_clamp, reflect_dir, roughness_mip).rgb;

// ③ 重ねる
float3 reflection = lerp(sky, ssr.rgb, ssr.a);
```

SSR の詳細は、[Reflections](../../reflections/index.md) の、SSR のページを参照してください。

## 反射方向の、作り方

反射の方向は、**波の法線**から、計算します（`reflect(−V, N)`）。波で、法線が、傾くので、**反射が、揺れて、歪みます**。

```hlsl
float3 reflect_dir = reflect(-view_dir, wave_normal);
```

### 地平線の下を、向く、反射

波の法線が、**視線の方向に、傾きすぎる**と、反射の向きが、**水面の下を向く**ことがあります。空が映る、環境マップの、**下半分（地面）**を読むことになり、**黒や、不自然な色**が、出ます。

```hlsl
// 反射の向きが、地平線の下に向いたときは、水平に近い向きへ、押し戻す。
reflect_dir.y = max(reflect_dir.y, 0.02);
reflect_dir = normalize(reflect_dir);
```

**遠くの水面ほど、起きやすい**です（視線が、水平に近く、法線の、少しの傾きで、反射が、下を向く）。**遠くでは、波の法線を、弱めて**、反射の向きを、安定させます（[Computing Normals](../waves/normals.md)）。

## 平面反射

水面は、**ほぼ平ら**です。**水面を、鏡として、カメラを、水面の反対側に、置いた、仮想のカメラで、シーンを、もう一度描く**と、**正確な反射**が、得られます。

```text
 実際のカメラ ●
                 ╲
 ━━━━━━━━━━━━━━━━ 水面（y = h）
                 ╱
 鏡像のカメラ  ●   ← 水面について、反対側
```

```cpp
// 水面 (y = h) に対する、鏡像のカメラ。
float3 MirroredPosition(float3 p, float water_height) {
  return {p.x, 2.0f * water_height - p.y, p.z};
}
// 鏡像カメラの視線方向の y 成分も、反転する。
// 水面より下にある物を、描かないよう、斜めクリップ面（水面）を、設定する。
```

| 項目 | 内容 |
| --- | --- |
| 描く範囲 | 水面より、**上**にある物だけ。水面で、**斜めに、クリップ**する（水面より下を、映さない） |
| 解像度 | **画面の半分**程度に、下げる（反射は、ぼやけてよい） |
| 描くもの | 遠景（空、山）と、**重要な、近景だけ**に、絞る。全シーンを、描くと、描画が、2 倍に近くなる |
| 波での、歪み | 反射の、テクスチャを読むときに、**波の法線の `xz` で、UV をずらす** |

```hlsl
// 平面反射のテクスチャを、波の法線で歪ませて読む。
float2 reflect_uv = screen_uv + wave_normal.xz * distortion_strength;
reflect_uv.x = 1.0 - reflect_uv.x;                         // 鏡像なので、左右を反転する（実装による）
float3 reflection = g_planar_reflection.Sample(g_linear_clamp, reflect_uv).rgb;
```

平面反射は、**水面が平ら**（波が小さい）ときに、**最も正確**です。波が大きい海では、歪みが大きく、**ごまかし**になります。小さな池、プール、湖に、向きます。

## 空の反射

空は、**環境マップ**（キューブマップ）で、映すのが、基本です。昼と夜、天候の変化に合わせて、**環境マップを、更新**します。

| 方法 | 内容 |
| --- | --- |
| 事前の、キューブマップ | 昼・夜・夕方の、キューブマップを、用意して、時間帯で、混ぜる |
| 大気から、リアルタイムに、生成 | [Atmosphere Model](../../atmosphere/scattering/atmosphere-model.md) の、結果を、キューブマップに描いて、使う |
| 大気の LUT を、直接引く | 反射ベクトルから、**空の色を、LUT から読む**。キューブマップが要らない |

粗さがあるとき（細かい波の、ばらつき）は、**キューブマップの、ミップ**（ぼかした版）を、読みます。`SampleLevel` で、粗さに応じたミップを選びます（[Prefiltering (Split-Sum)](../../reflections/probes/prefilter.md)）。

## 合成

反射の強さは、**フレネル**で、決まります（[Water Fresnel](fresnel.md)）。

```hlsl
float F = FresnelSchlick(saturate(dot(wave_normal, view_dir)), 0.02);
float3 color = lerp(refraction, reflection, F);
```

真上から見ると、`F ≈ 0.02` で、**反射は、ほぼ見えません**。遠くを見るほど、`F` が大きく、**反射が、支配的**になります。

''', before="## よくあるミス")
pg.Refs("water/shading/reflection.md", [MITTRING, LAGARDE, RTR, TESSENDORF])

# ---------------------------------------------------------------- refraction
pg.Dedup("water/shading/refraction.md")
pg.Add("water/shading/refraction.md", '''
## なぜ、水の中の物は、ずれて見えるのか

光が、空気から水へ入るとき、**境界で、曲がります**（屈折）。**スネルの法則**で、曲がる角度が決まります。

```text
n₁ sinθ₁ = n₂ sinθ₂            n₁ = 1.0（空気）、n₂ = 1.33（水）
```

水の中の、物体から来た光は、水面で、曲がって、目に届きます。**目は、光が、曲がらず、まっすぐ来た、と思い込む**ので、**水の中の物は、実際より、浅い所に、見えます**。ストローが、水面で、折れて見えるのも、同じ理由です。

## 正確な屈折ベクトル

水面の、法線 `N` と、視線 `V` から、**屈折した、光の向き**を計算するのが、HLSL の組み込み関数 `refract` です。

```hlsl
// refract(入射方向（目から、水面へ向かう向き）, 法線, 屈折率の比 = n1 / n2)
float3 refracted_dir = refract(-view_dir, wave_normal, 1.0 / 1.33);
```

この向きに、光が、水の中を進みます。**屈折した向きに、水の中を、一定の距離だけ進んだ点**が、目に、見えている点です。

```hlsl
// 水面の点 P から、屈折した向きに、水の深さぶん進んだ点（水中の、見える位置）。
float3 refracted_pos = world_pos + refracted_dir * (water_depth / max(-refracted_dir.y, 0.05));
// この点を、画面に投影して、そこの、シーンの色を、読む。
float4 clip = mul(float4(refracted_pos, 1), view_proj);
float2 refract_uv = clip.xy / clip.w * float2(0.5, -0.5) + 0.5;
```

これが、**屈折の、幾何学的に、正しい**方法です。**水深**（底までの距離）が、必要なので、深度バッファを読みます（[Color by Water Depth](depth-color.md)）。

## 画面のコピーを、歪ませる（簡易な方法）

幾何学的な方法は、**水深と、屈折ベクトル**が必要で、計算が、増えます。**多くのゲームでは、もっと、簡単な方法**を、使います（Sousa、2005）。

1. 水面を描く前に、**画面（シーンの色）を、テクスチャにコピー**する
2. 水面の、ピクセルで、**波の法線に応じて、UV を、ずらして**、そのコピーを読む

```cpp
// 水面を描く前に、シーンの色を、コピーする。
context->CopyResource(scene_copy_tex.Get(), scene_color_tex.Get());
// 水の描画では、scene_copy を SRV として、読む（書き込み先の scene_color とは、別のテクスチャ）。
```

```hlsl
// 法線の xz 成分で、UV をずらす。
float2 distortion = wave_normal.xz * distortion_strength;
float2 refract_uv = screen_uv + distortion;
float3 scene_color = g_scene_copy.Sample(g_linear_clamp, refract_uv).rgb;
```

波の法線が、**傾いている方向に、ずれて**見えるので、**水面が、ゆらゆらして、水中の物が、揺らいで見えます**。

### パラメーター

| パラメーター | 目安 | 内容 |
| --- | --- | --- |
| `distortion_strength` | 0.02〜0.05 | ずれの大きさ。大きいと、不自然に、歪む |
| 水深での、強さ | 浅いほど、弱める | 浅い所は、光が、水中を、通る距離が短く、ほとんど、ずれない |
| 距離での、強さ | 遠いほど、弱める | 遠くは、ちらつきを、防ぐ |

## 手前の物を、ずらさない

歪ませた UV で、シーンの色を、読むとき、**水より手前にある物**（水面から、突き出た杭、船、プレイヤーの足）を、**読んでしまう**ことがあります。杭の色が、**水面に、にじみ出して**見えます。

```hlsl
// ずらした先の深度が、水面より手前なら（水の外にある物）、ずらさない。
float2 refract_uv = screen_uv + distortion;
float scene_depth_at_uv = LinearizeDepth(g_scene_depth.Sample(g_point_clamp, refract_uv).r);
if (scene_depth_at_uv < surface_depth) {
  refract_uv = screen_uv;                    // ずらさず、元の位置を読む
}
float3 scene_color = g_scene_copy.Sample(g_linear_clamp, refract_uv).rgb;
```

| 状況 | 結果 |
| --- | --- |
| ずらした先が、水の中（底） | そのまま、歪ませた色を使う |
| ずらした先が、水より手前の物 | 歪ませず、元の位置の色を使う |

これでも、**水面の境界で、わずかに、にじみ**ます。さらに、**水の外にある物の、マスク**を、別のテクスチャで、持つ方法もありますが、簡易な方法では、**この深度の、チェックだけで、十分**なことが、多いです。

## 水深から、歪みを決める

**浅い場所**では、光が、水の中を、通る距離が、短く、**屈折の影響が、小さい**です。水深に比例して、歪みを強めます。

```hlsl
float depth_factor = saturate(water_depth / 2.0);       // 2 m で、最大
float2 distortion = wave_normal.xz * distortion_strength * depth_factor;
```

岸に、近づくほど、歪みが、小さくなり、**水際で、屈折が、自然に、消えます**。

## 色収差（分散）

水の屈折率は、**波長で、少し違います**（赤で 1.331、青で 1.337）。これを、再現すると、**RGB を、わずかに、別々にずらして**、読みます。

```hlsl
float3 scene_color;
scene_color.r = g_scene_copy.Sample(g_linear_clamp, screen_uv + distortion * 0.95).r;
scene_color.g = g_scene_copy.Sample(g_linear_clamp, screen_uv + distortion * 1.00).g;
scene_color.b = g_scene_copy.Sample(g_linear_clamp, screen_uv + distortion * 1.05).b;
```

水は、屈折率の差が、小さく、効果は、ごくわずかです。入れると、**水面の縁が、わずかに、虹色**に見えます。ガラス（[Dispersion](../../translucency/refraction/dispersion.md)）では、効果が、目立ちます。

## 画面の端

歪ませた UV が、**画面の外**を指すことがあります。画面の外の色は、無いので、**サンプラーの、クランプ**（`CLAMP`）で、端の色を、繰り返し、読みます。画面の端で、**色が、伸びて**見えることがあります。

| 対策 | 内容 |
| --- | --- |
| 歪みを、画面の端で、弱める | 端に近いほど、歪みを小さくする |
| 画面を、少し大きく描く | シーンを、画面より、少し広い範囲で、描く（コストが、増える） |
| 気にしない | 水面の歪みは、小さいので、多くの場合、目立たない |

''', before="## よくあるミス")
pg.Refs("water/shading/refraction.md", [SOUSA, RTR, MITTRING, TESSENDORF])

# ---------------------------------------------------------------- parameters
pg.Dedup("water/shading/parameters.md")
pg.Add("water/shading/parameters.md", '''
## 物理的な、パラメーターと、アーティスト向けの、パラメーター

水のマテリアルには、2 つの流儀があります。

| 流儀 | パラメーター | 長所 | 短所 |
| --- | --- | --- | --- |
| 物理ベース | 吸収係数 `a`（RGB）、後方散乱 `b_b`、屈折率 | **現実の水を、再現できる**。値の意味が、明確 | アーティストが、直感で扱いにくい |
| アーティスト向け | 浅い所の色、深い所の色、「透明度の距離」 | 直感的。色を、直接、指定できる | 現実から、ずれても、気づきにくい。照明の変化に、追従しにくい |

おすすめは、**内部を物理ベースにして、入力は、アーティスト向けにする**組み合わせです。アーティストが、「**この深さで、底が、見えなくなる**（透明度の距離）」「**深い所の色**」を指定し、そこから、吸収係数を、**自動で計算**します。

## 透明度の距離から、吸収係数を決める

「**ここまでの深さなら、底が、見える**」という、**透明度の距離**（セッキ ディスクの深さに近い）を、指定すると、吸収係数に、換算できます。

```text
透過率が、ほぼ見えなくなる値（たとえば 5%）になる距離を、D とすると:
exp(−a × D) = 0.05   →   a = −ln(0.05) / D = 3.0 / D
```

```cpp
// 透明度の距離（メートル）から、吸収係数を作る。RGB で、赤が強く、青が弱くなるよう、比を掛ける。
float3 AbsorptionFromVisibility(float visibility_m, float3 color_ratio) {
  const float a = 3.0f / visibility_m;            // 赤、緑、青の平均が、この値になる
  return {a * color_ratio.x, a * color_ratio.y, a * color_ratio.z};
}

// 例: 澄んだ海（透明度 20 m）。赤は、青の 15 倍吸収される。
const float3 absorption = AbsorptionFromVisibility(20.0f, {2.1f, 0.5f, 0.14f});
```

比 `color_ratio` は、水の種類で決めます。**赤を、よく吸収**するほど、**青く澄んだ水**です。

## パラメーターの一覧と、目安

| パラメーター | 内容 | 目安 |
| --- | --- | --- |
| 吸収係数 `a`（RGB、1/m） | 色ごとの、吸収の強さ | 澄んだ水 (0.3, 0.05, 0.01)、濁った水 (1.0, 0.4, 0.3) |
| 後方散乱 `b_b`（1/m） | 水自体が、返す光の量 | 澄んだ水 0.003、濁った水 0.02 |
| 屈折率 | スネルの法則と、フレネル | 1.33（水）。ほぼ変えない |
| 屈折の歪み | 画面のコピーの、ずらし量 | 0.02〜0.05 |
| 反射の強さ | フレネルに、掛ける倍率 | 1.0（物理どおり）。0.8〜1.2 で、調整 |
| 粗さ（`roughness`） | スペキュラーと、反射のぼけ | 風速から決める（[Specular](specular.md)）。0.02〜0.3 |
| 波の法線の強さ | 細かい法線の、傾きの倍率 | 1.0 |
| 泡の色・量 | 波頭と、岸の泡 | 白、密度は、風と地形で、変える |
| 水面の高さ | 海面のレベル | ワールドの基準 |

## 水の種類の、プリセット

場所ごとに、パラメーターのセット（プリセット）を持つと、**海、湖、池、プール、沼**を、1 つの水シェーダーで、作り分けられます。

| 種類 | 吸収 a（RGB） | 後方散乱 b_b | 透明度 | 粗さ | 特徴 |
| --- | --- | --- | --- | --- | --- |
| 南国の海 | (0.35, 0.06, 0.02) | 0.004 | 30 m | 0.1〜 | 鮮やかな青緑。浅瀬は、白い砂が、透ける |
| 外洋 | (0.45, 0.07, 0.03) | 0.005 | 20 m | 0.15〜 | 深い青。波が大きい |
| 湖 | (0.7, 0.25, 0.2) | 0.015 | 8 m | 0.05〜 | 緑がかった、静かな水面 |
| 川 | (1.0, 0.45, 0.4) | 0.03 | 3 m | 0.05〜 | 茶〜緑。流れがある |
| 沼 | (2.0, 1.0, 0.9) | 0.05 | 1 m | 0.03 | 暗い緑茶色。透けない |
| プール | (0.25, 0.04, 0.02) | 0.002 | 全部見える | 0.02 | 底のタイルが、見える。塩素の青 |

数値は、**見た目の出発点**です。ゲームの、明るさ・露出に合わせて、**調整**してください。

```cpp
// プリセットを、構造体で持つ。
struct WaterMaterial {
  float3 absorption;          // 1/m
  float backscatter;          // 1/m
  float visibility_m;         // 透明度（参考値。absorption を、自動で決めるときに使う）
  float roughness;
  float refraction_strength;
  float reflection_scale;
  float normal_strength;
  float foam_amount;
};

constexpr WaterMaterial kOcean = {{0.45f, 0.07f, 0.03f}, 0.005f, 20.0f, 0.15f, 0.03f, 1.0f, 1.0f, 0.6f};
constexpr WaterMaterial kLake  = {{0.70f, 0.25f, 0.20f}, 0.015f, 8.0f, 0.05f, 0.02f, 1.0f, 0.6f, 0.1f};
```

```hlsl
cbuffer WaterMaterialCB : register(b3) {
  float3 g_absorption;
  float g_backscatter;
  float g_roughness;
  float g_refraction_strength;
  float g_reflection_scale;
  float g_normal_strength;
  float g_foam_amount;
  float3 pad;
};
```

## 場所ごとに、水を変える

湖から、川へ、**水の種類が、つながっている**ところは、**境目で、パラメーターを、補間**します。

| 方法 | 内容 |
| --- | --- |
| 水域ごとに、別のメッシュ | メッシュごとに、マテリアルを設定。境目が、はっきり分かれる |
| 頂点カラーで、補間 | 頂点に、プリセットの、重みを持たせて、補間する |
| テクスチャで、パラメーターを、描く | 水の、濁り、深さを、**マップ**に描いて、読む（岸の近くだけ、緑にする、など） |

## 天候と、時間帯

水の見た目は、**空の光**で、変わります。

| 要因 | 変わるもの |
| --- | --- |
| 晴れ → 曇り | `deep_color` が暗く、グレーに。太陽の反射が、消える |
| 昼 → 夕方 | 反射が、オレンジに。深い水の色が、暗くなる |
| 夜 | 空の光が、ほぼ、無い。水は、ほぼ、黒（月や街灯の反射だけ） |
| 雨 | 粗さが、増える（水面に、雨粒の波）。反射が、にじむ |

吸収係数は、**水そのもの**の性質なので、**時間帯では、変えません**。変えるのは、**入ってくる光**（`incident_light`）です（[Scattering Color (SSS-Like)](scattering.md)）。

''', before="## よくあるミス")
pg.Refs("water/shading/parameters.md", [POPE, JERLOV, GORDON, TESSENDORF])

pg.Refs("water/shading/index.md", [GORDON, POPE, SCHLICK, SOUSA, COXMUNK, LAGARDE])
print("ok")
