import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import pg  # noqa: E402

KARIS = '''Karis, "Real Shading in Unreal Engine 4", SIGGRAPH 2013, Physically Based Shading in Theory and Practice（split-sum 近似）'''
LAGARDE = '''Lagarde, de Rousiers, "Moving Frostbite to Physically Based Rendering 3.0", SIGGRAPH 2014, Physically Based Shading in Theory and Practice'''
LAGARDE12 = '''Lagarde, Zanuttini, "Local Image-Based Lighting With Parallax-Corrected Cubemap", SIGGRAPH 2012 Talks（箱による、視差補正）'''
BJORKE = '''Bjorke, "Image-Based Lighting", GPU Gems, Chapter 19, 2004（キューブマップの、視差補正のはしり）'''
MCGUIRE = '''McGuire, Mara, "Efficient GPU Screen-Space Ray Tracing", Journal of Computer Graphics Techniques, Vol. 3, No. 4, 2014'''
STACHOWIAK15 = '''Stachowiak, Uludag, "Stochastic Screen-Space Reflections", SIGGRAPH 2015, Advances in Real-Time Rendering in Games（Frostbite の SSR）'''
ULUDAG = '''Uludag, "Hi-Z Screen-Space Cone-Traced Reflections", GPU Pro 5, 2014'''
VALIENT = '''Valient, "Reflections and Volumetrics of Killzone Shadow Fall", SIGGRAPH 2014, Advances in Real-Time Rendering in Games'''
STACHOWIAK18 = '''Stachowiak, "Stochastic All The Things: Raytracing in Hybrid Real-Time Rendering", Digital Dragons 2018'''
BARRE = '''Barré-Brisebois, Halén, Wihlidal, Lauritzen, Bekkers, Stachowiak, Andersson, "Hybrid Rendering for Real-Time Ray Tracing", Ray Tracing Gems, Chapter 25, 2019'''
HEITZ = '''Heitz, "Sampling the GGX Distribution of Visible Normals", Journal of Computer Graphics Techniques, Vol. 7, No. 4, 2018'''
WALTER = '''Walter, Marschner, Li, Torrance, "Microfacet Models for Refraction through Rough Surfaces", Eurographics Symposium on Rendering 2007'''
SCHIED = '''Schied et al., "Spatiotemporal Variance-Guided Filtering: Real-Time Reconstruction for Path-Traced Global Illumination", High-Performance Graphics 2017'''
DXR = '''Microsoft, "DirectX Raytracing (DXR) Functional Spec"'''
MITTRING = '''Mittring, "Finding Next Gen: CryEngine 2", SIGGRAPH 2007, Advances in Real-Time Rendering in 3D Graphics and Games'''
RTR = '''Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（反射、IBL の章）'''
KAUTZ = '''Kautz, McCool, "Approximation of Glossy Reflection with Prefiltered Environment Maps", Graphics Interface 2000'''
D3D11_CUBE = '''Microsoft Learn, "D3D11_RESOURCE_MISC_FLAG"（`D3D11_RESOURCE_MISC_TEXTURECUBE`、`D3D11_RESOURCE_MISC_GENERATE_MIPS`）'''

# ================================================================ probes
pg.Dedup("reflections/probes/index.md")
pg.Add("reflections/probes/index.md", '''
## 反射プローブとは

**反射プローブ**は、**空間の、ある点**から、**周りの景色**を、**キューブマップ**に、**撮影**した、ものです。**つるつるの、面**（金属、水たまり、磨いた床）は、**この、キューブマップを、引いて**、**周りの景色を、映します**。**画面の、外にある物**も、映せて、**安い**ので、**反射の、土台**として、使われます。

```text
 部屋の中央に、プローブを置く → 6 方向（上下左右前後）の景色を、キューブマップに撮影（事前、または、動的）
 床や金属の面は、「反射の向き」で、キューブマップを引く → 周りの景色が、映る
```

## 仕組み

| 段階 | 内容 | ページ |
| --- | --- | --- |
| ① **撮影** | プローブの位置で、**6 面**を、レンダリング（HDR） | このページ |
| ② **事前フィルタ** | **粗さごと**に、**ぼかした、ミップ**を、作る | [Prefiltering (Split-Sum)](prefilter.md) |
| ③ **視差補正** | プローブの位置と、**物の位置が、違う**ことによる、**ずれ**を、補正 | [Parallax Correction](parallax.md) |
| ④ **ブレンド** | **複数の、プローブ**を、**位置に応じて、混ぜる** | [Probe Operation](blending.md) |
| ⑤ **SSR との、併用** | **画面内の、近くの物**は、SSR、**画面外**は、プローブ | [Combining with SSR](combine-ssr.md) |

## ①撮影

**プローブの、位置に、カメラを、置き**、**6 方向を、レンダリング**して、**キューブマップ**に、書きます。

```cpp
// 反射プローブ用の、キューブマップ（HDR、ミップつき）。128×128 × 6 面。
D3D11_TEXTURE2D_DESC desc = {};
desc.Width = 128;
desc.Height = 128;
desc.MipLevels = 0;                                         // 全ミップ（粗さに応じた、ぼかしのため）
desc.ArraySize = 6;
desc.Format = DXGI_FORMAT_R16G16B16A16_FLOAT;               // HDR
desc.SampleDesc.Count = 1;
desc.Usage = D3D11_USAGE_DEFAULT;
desc.BindFlags = D3D11_BIND_SHADER_RESOURCE | D3D11_BIND_RENDER_TARGET;
desc.MiscFlags = D3D11_RESOURCE_MISC_TEXTURECUBE | D3D11_RESOURCE_MISC_GENERATE_MIPS;
device->CreateTexture2D(&desc, nullptr, &probe_cube);
```

**6 面の、行列**は、**点光源の、キューブ シャドウ**と、同じ、**視野角 90°**の、透視投影です（[Point Lights: Cube Maps](../../shadows/local-lights/point-cubemap.md)）。**HDR**（`R16G16B16A16_FLOAT`）で、撮るのは、**明るい光**（太陽の反射）を、**保つ**ためです。

```cpp
// 6 面を、それぞれ、レンダリングする。反射プローブでは、プローブ自身の反射は、描かない（無限再帰を、避ける）。
for (int face = 0; face < 6; ++face) {
  context->OMSetRenderTargets(1, face_rtv[face].GetAddressOf(), probe_depth_dsv.Get());
  UpdateCameraCB(probe_position, kForward[face], kUp[face], DirectX::XM_PIDIV2);
  RenderSceneForProbe();                                    // 簡易なシーン（遠景、主要な物だけ。低品質でよい）
}
context->GenerateMips(probe_cube_srv.Get());                // いったん、ミップを作る（正式な、ぼかしは、次のページ）
```

## 静的と、動的

| 種類 | 内容 | コスト |
| --- | --- | --- |
| **ベイク（静的）** | **制作時**に、撮影して、**保存**。実行時は、**読むだけ** | **最小** |
| **動的**（実行時に、撮り直す） | **昼夜の、変化、動く物**を、**反映** | **重い**（6 面を、描き直す） |
| **昼夜用に、複数ベイク** | 朝・昼・夕・夜の、キューブマップを、**補間** | 小 |

**動的な、更新**は、**重い**ので、**1 フレームに、1 面だけ**、**数フレームで、一巡**、**カメラの近くの、プローブを、優先**、などの、**間引き**を、行います。

## 反射プローブの、限界

| 限界 | 内容 |
| --- | --- |
| **位置の、ずれ** | キューブマップは、**プローブの、位置から、見た景色**。**物の位置**は、**プローブと、違う**ので、**映る景色が、ずれる**（視差。[Parallax Correction](parallax.md)） |
| **解像度が、有限** | 128×128 で、**細かい景色は、ぼやける**。**つるつるの、鏡面**では、**粗さが、目立つ** |
| **動く物が、映らない**（ベイク） | **プレイヤー、車**が、**映らない**。**SSR や、平面反射で、補う** |
| **自分自身が、映らない** | プローブは、**物が、無い、状態**で、撮る |
| **遠景が、中心** | **遠くの景色**（空、山）は、**正確**。**近くの物**は、**ずれる** |

''', before="## よくあるミス")
pg.Refs("reflections/probes/index.md", [LAGARDE, KARIS, LAGARDE12, BJORKE, RTR])

pg.Dedup("reflections/probes/prefilter.md")
pg.Add("reflections/probes/prefilter.md", '''
## 粗さと、ぼかし

**鏡面反射**の、**見た目**は、**粗さ**で、変わります（[Diffuse and Specular](../../gi/theory/diffuse-specular.md)）。**つるつる**なら、**周りの景色が、くっきり**、**ざらざら**なら、**ぼんやり、広い範囲が、混ざります**。反射プローブの、キューブマップを、**そのまま**引くと、**常に、くっきり**映り、**粗い面でも、鏡のよう**に、なって、**不自然**です。**粗さに応じた、ぼかし**が、必要です。

## ミップに、ぼかしを、焼く

**キューブマップの、ミップ**を、**粗さごとの、ぼかし**として、**使います**。**ミップ 0** が、**粗さ 0**（くっきり）、**高いミップ**が、**粗さが、大きい**（ぼやけ）に、**対応**するよう、**各ミップを、事前に、ぼかして、作ります**（Kautz と McCool、2000。**事前フィルタ**環境マップ）。

```text
ミップ 0（128×128）: 粗さ 0.0  ← ほぼ、元の画像
ミップ 1（64×64）  : 粗さ 0.2
ミップ 2（32×32）  : 粗さ 0.4
ミップ 3（16×16）  : 粗さ 0.6
ミップ 4（8×8）    : 粗さ 0.8
ミップ 5（4×4）    : 粗さ 1.0  ← ほぼ、全方向の平均
```

**通常のミップ**（4 画素を、平均）では、**粗さに対応する、正しい、ぼかし**にならないので、**GGX の、反射ローブ**に、**合わせた、ぼかし**で、**各ミップを、作ります**。

## 重点サンプリングで、ぼかす

**各ミップの、各テクセル**（**反射方向 `R`** に、対応）について、**GGX の、分布**に、従って、**周りの方向を、サンプル**し、**環境マップを、引いて**、**平均**します。**重点サンプリング**（[Monte Carlo Integration](../../gi/theory/monte-carlo.md)）で、**少ないサンプル**でも、**正しい、ぼかし**が、得られます。

```hlsl
// GGX の分布に従って、ハーフ ベクトル H をサンプルする（ローカル座標。z が法線）。
float3 ImportanceSampleGGX(float2 u, float roughness) {
  float a = roughness * roughness;                                      // 知覚的な粗さ → GGX の α
  float phi = 2.0 * 3.14159265 * u.x;
  float cos_theta = sqrt((1.0 - u.y) / (1.0 + (a * a - 1.0) * u.y));    // GGX の、逆累積分布
  float sin_theta = sqrt(1.0 - cos_theta * cos_theta);
  return float3(sin_theta * cos(phi), sin_theta * sin(phi), cos_theta);
}
```

**GGX の、法線分布**に、**比例した、確率**で、**ハーフ ベクトル `H`** を、選びます（Walter ら、2007）。**粗さが、小さい**ほど、**`H` は、法線の、近くに、集中**し、**粗さが、大きい**ほど、**広がります**。

```hlsl
// 事前フィルタ: 反射方向 R に対応する、1 テクセルを、GGX の重点サンプリングで、環境マップから、ぼかして作る。
float3 PrefilterEnvMap(float3 R, float roughness) {
  float3 N = R;                                  // 近似: 法線 = 反射方向 = 視線（Karis の、仮定）
  float3 V = R;
  const uint kSamples = 256;
  float3 sum = 0.0;
  float weight = 0.0;
  for (uint i = 0; i < kSamples; ++i) {
    float2 u = Hammersley(i, kSamples);                                  // 低食い違い量列
    float3 H = LocalToWorld(ImportanceSampleGGX(u, roughness), N);       // GGX に従った、ハーフ ベクトル
    float3 L = normalize(2.0 * dot(V, H) * H - V);                       // 反射: 光の方向
    float n_dot_l = saturate(dot(N, L));
    if (n_dot_l > 0.0) {
      sum += g_env.SampleLevel(g_linear_clamp, L, 0).rgb * n_dot_l;      // その方向の、環境の光（余弦で重みづけ）
      weight += n_dot_l;
    }
  }
  return sum / max(weight, 1e-4);
}
```

**ハーフ ベクトル `H`** を、サンプルし、**それで、視線 `V` を、反射**させた、**光の方向 `L`** で、**環境マップを、引き**ます。**余弦で、重みづけ**して、**平均**します。**粗さごとに、各ミップを、この関数で、焼きます**（制作時、または、起動時）。

!!! note "`N = V = R` の、近似"
    実際の、鏡面反射は、**視線と、法線が、別**ですが、**事前フィルタの、キューブマップ**は、**反射方向 `R` だけ**で、引くので、**`N = V = R`** と、**仮定**します（Karis、2013）。**視線が、面に、斜め**のとき、**実際の反射の、伸び**（**斜めから見ると、反射が、縦に、伸びる**）は、**再現できません**。これは、**既知の、近似の、限界**です。

## 反射の、式の、分解：split-sum

**鏡面反射の、間接光**は、**環境の、光 `L_i` と、BRDF の、積**を、**半球で、積分**した、ものです。**この積分を、2 つに、分けて、近似**する、**split-sum**（Karis、2013）が、**標準**です。

```text
∫ L_i(l) × f(l, v) × cosθ dl  ≈  ( 1/N Σ L_i(l_k) × cosθ_k / Σ cosθ_k )  ×  ( 1/N Σ f(l_k, v) × cosθ_k / pdf )
                                    └── ① 事前フィルタした環境マップ ──┘      └── ② BRDF の積分（LUT） ──┘
```

| 項 | 内容 | 事前計算 |
| --- | --- | --- |
| ① **環境光の、積分** | **粗さごとに、ぼかした、環境マップ**（上の、`PrefilterEnvMap`） | **キューブマップの、ミップ**（粗さ × 反射方向） |
| ② **BRDF の、積分** | **視線と法線の角度（`n·v`）**と、**粗さ**の、関数。**2 つの数**（`A`、`B`）に、まとまる | **2D の、LUT**（`n·v` × 粗さ。256×256 の `R16G16`） |

**積を、2 つの、積分の、積に、分ける**（**厳密には、正しくない**が、**十分に、近い**）ことで、**どちらも、事前計算**できます。

### BRDF の LUT

```hlsl
// BRDF の LUT: (n·v, roughness) → (A, B)。鏡面反射の、フレネルと、可視性を含めた、積分。
float2 IntegrateBRDF(float n_dot_v, float roughness) {
  float3 V = float3(sqrt(1.0 - n_dot_v * n_dot_v), 0.0, n_dot_v);        // 視線（ローカル座標。法線は +Z）
  float A = 0.0, B = 0.0;
  const uint kSamples = 1024;
  for (uint i = 0; i < kSamples; ++i) {
    float2 u = Hammersley(i, kSamples);
    float3 H = ImportanceSampleGGX(u, roughness);
    float3 L = 2.0 * dot(V, H) * H - V;
    float n_dot_l = saturate(L.z);
    float n_dot_h = saturate(H.z);
    float v_dot_h = saturate(dot(V, H));
    if (n_dot_l > 0.0) {
      float G = GeometrySmith(n_dot_v, n_dot_l, roughness);               // 幾何減衰（マスキング・シャドウイング）
      float G_vis = G * v_dot_h / (n_dot_h * n_dot_v);                    // 可視性項
      float Fc = pow(1.0 - v_dot_h, 5.0);                                 // フレネル（Schlick）の、可変部分
      A += (1.0 - Fc) * G_vis;                                            // F0 に掛かる係数
      B += Fc * G_vis;                                                    // F0 に関係しない、加算の係数
    }
  }
  return float2(A, B) / kSamples;
}
```

**フレネルの、Schlick 近似**（`F = F0 + (1 − F0) × Fc`）を、**`F0` に、掛かる項と、そうでない項に、分けて**、**`A`、`B`** に、**積分**します。**実行時**、**`F0 × A + B`** で、**BRDF の、積分**が、**得られます**（[Water Fresnel](../../water/shading/fresnel.md) の、Schlick 近似と、同じ）。

## 実行時の、使い方

```hlsl
// 鏡面の間接光: 粗さに応じたミップで、反射方向を読み、split-sum の、BRDF の積分を掛ける。
float3 SpecularIBL(float3 N, float3 V, float3 f0, float roughness) {
  float3 R = reflect(-V, N);
  float n_dot_v = saturate(dot(N, V));
  float mip = roughness * (kEnvMipCount - 1);                              // 粗さ → ミップ
  float3 prefiltered = g_probe_cube.SampleLevel(g_linear_clamp, R, mip).rgb;
  float2 brdf = g_brdf_lut.SampleLevel(g_linear_clamp, float2(n_dot_v, roughness), 0).xy;
  return prefiltered * (f0 * brdf.x + brdf.y);
}
```

**ミップの、選択**は、**粗さに、比例**（`roughness × (ミップ数 − 1)`）が、**標準的**ですが、**ミップ数、ミップごとの、粗さの割り当て**は、**事前フィルタ**を、**作るとき**と、**同じ式**に、そろえます。**`SampleLevel`** の、ミップは、**連続**（小数）なので、**トライリニアで、2 つの、ミップが、補間**され、**粗さが、なめらかに、変わります**。

## 注意点

| 問題 | 内容 | 対策 |
| --- | --- | --- |
| **ミップ間の、継ぎ目**（面の境目） | キューブマップの、面の、境目で、ぼかしが、**途切れる**（ミップで、特に目立つ） | **シームレス キューブマップ**（DirectX 11 は、標準でシームレス）、**事前フィルタを、全方向で、サンプル** |
| **粗さ 0**（完全な鏡）で、ぼやける | ミップ 0 が、**128×128**。つるつるの、面では、**解像度が、足りない** | 解像度を上げる（256×256）、または、**SSR / RT で、補う** |
| **ファイアフライ**（明るい点が、散らばる） | **明るい光源**（太陽）が、**少ないサンプルで、拾われる** | **サンプル数を、増やす**、**元のキューブマップの、ミップを、読んで、サンプルする**（フィルタード重点サンプリング）、**明るさを、クランプ** |

''', before="## よくあるミス")
pg.Refs("reflections/probes/prefilter.md", [KARIS, LAGARDE, KAUTZ, WALTER, RTR])

pg.Dedup("reflections/probes/parallax.md")
pg.Add("reflections/probes/parallax.md", '''
## 視差の問題

**反射プローブ**は、**ある 1 点**（プローブの、位置）から、見た、景色を、保存しています。ところが、**反射を、映したい**のは、**プローブから、離れた、場所の、床や、金属**です。**面の位置**が、**プローブの位置と、違う**と、**同じ、反射方向でも**、**実際に、映るべき景色**は、**違う**ので、**映る景色が、ずれます**。これが、**視差**の、問題です。

```text
        壁
  ━━━━━━━━━━━━━━━━━━━        プローブ ● は、部屋の中央
                                 床の点 P は、壁の近く（プローブから、離れている）
        ●  プローブ                P から、反射方向 R に、進むと、実際は、壁の A 点に当たる
                                 しかし、キューブマップを、R で引くと、プローブから、R に進んだ、壁の B 点が、映る → ずれる
  P ──R──→ A
```

**部屋の中の、鏡面**で、**壁の、模様が、実際の位置と、ずれて**映ります。**窓の、反射が、床の、全面で、同じ**位置に、見える（**どこを、歩いても**、**窓が、同じ向きに、映る**）、**不自然**です。

## 箱による、視差補正

**部屋を、箱**と、**近似**します。**反射レイを、箱と、交差**させて、**当たった位置**を、求め、**その位置から、プローブへの、向き**で、**キューブマップを、引き直します**（Bjorke、2004、Lagarde と Zanuttini、2012）。

```text
  P ──R──→ A（箱の壁との、交点）
  プローブ ● から A への向き R' で、キューブマップを引く → 実際に、A が映るはずの、景色
```

```hlsl
// 箱（軸に平行）による、視差補正。box_min, box_max: 箱の範囲（ワールド座標）、probe_pos: プローブの位置。
float3 ParallaxCorrect(float3 R, float3 world_pos, float3 box_min, float3 box_max, float3 probe_pos) {
  // レイ（world_pos から、R の向き）と、箱の、交点を求める（スラブ法）。
  float3 first_plane = (box_max - world_pos) / R;
  float3 second_plane = (box_min - world_pos) / R;
  float3 furthest = max(first_plane, second_plane);                      // 各軸で、遠い方の、平面までの距離
  float dist = min(min(furthest.x, furthest.y), furthest.z);             // 3 つの軸のうち、最も近い（= 箱から、出る）距離
  float3 hit = world_pos + R * dist;                                      // 箱の壁との交点
  return hit - probe_pos;                                                 // プローブから、交点への向き（これで、キューブマップを引く）
}
```

**スラブ法**で、**レイと、箱の交点**を、求めます。**各軸**について、**レイが、箱の、外へ出る、平面までの距離**を、求め、**その、最小**が、**箱から、出る、距離**です。**交点**から、**プローブへの、向き**が、**補正した、反射方向**です。

```hlsl
float3 corrected = ParallaxCorrect(R, input.world_position, g_probe_box_min, g_probe_box_max, g_probe_position);
float3 prefiltered = g_probe_cube.SampleLevel(g_linear_clamp, corrected, mip).rgb;
```

**補正した、方向**で、**キューブマップを、引く**だけで、**反射が、面の位置に、合い**、**窓が、歩くと、動いて、見えます**。

## 箱の、設定

**箱**は、**部屋の、形に、合わせて**、**アーティストが、設定**します。

| 設定 | 内容 |
| --- | --- |
| **箱の、大きさ** | **部屋の壁に、ぴったり**（壁の内側）。**大きすぎる**と、**補正が、弱く**、**小さすぎる**と、**映像が、歪む** |
| **プローブの位置** | **箱の中央付近**（最も、バランスが、良い） |
| **影響範囲**（ブレンド用） | **プローブが、効く、範囲**（箱より、少し、大きく）。**範囲の端で、フェード**（[Probe Operation](blending.md)） |

## 球による、補正（屋外）

**屋外**（**箱では、ない、広い空間**）では、**球**で、近似する方法も、あります。**半径**を、**環境の、大きさ**に、合わせます。

```hlsl
// 球による、視差補正（プローブを、中心とした、半径 radius の球）。
float3 ParallaxCorrectSphere(float3 R, float3 world_pos, float3 center, float radius) {
  float3 oc = world_pos - center;
  float b = dot(oc, R);
  float c = dot(oc, oc) - radius * radius;
  float dist = -b + sqrt(max(b * b - c, 0.0));                             // レイが、球から出る距離
  return (world_pos + R * dist) - center;                                   // 球の、交点への向き
}
```

**球は、箱より、単純**ですが、**部屋の、形**（直方体）には、**合いにくい**ので、**屋内には、箱**、**屋外・円形の空間には、球**を、使い分けます。

## 補正の、限界

| 限界 | 内容 |
| --- | --- |
| **箱は、近似** | **実際の部屋**が、**直方体でない**（柱、家具、凹み）と、**補正が、ずれる** |
| **物は、補正されない** | キューブマップに、**焼かれた、家具**は、**箱の壁**に、あるものとして、**扱われる**。**家具の、反射位置**は、**ずれる** |
| **視線が、箱の外** | **面が、箱の、外にある**（プローブの、影響範囲の、端）と、**補正が、破綻**する。**ブレンドで、薄める** |
| **近い面の、補正が、強い** | **壁の、すぐ近く**の、面では、**補正の、効果が、極端**で、**歪む**。**箱を、少し、小さく**、**補正を、弱める** |

## 補正の、強さを、調整する

**補正した、方向**と、**補正なしの、方向**を、**補間**して、**補正の、強さを、調整**します。

```hlsl
float3 dir = lerp(R, corrected, g_parallax_strength);                    // 0 = 補正なし、1 = 完全な補正
```

**部屋の、形に、合わない**場合、**弱める**（0.5〜0.8）と、**破綻が、目立ちません**。

''', before="## よくあるミス")
pg.Refs("reflections/probes/parallax.md", [LAGARDE12, BJORKE, LAGARDE, RTR])

pg.Dedup("reflections/probes/blending.md")
pg.Add("reflections/probes/blending.md", '''
## 複数の、プローブを、使う

**シーンには、複数の、反射プローブ**（部屋ごと、エリアごと）が、あります。**物の位置**に、**応じて**、**どのプローブを、使うか**、**複数が、重なるとき**に、**どう、混ぜるか**を、決める必要が、あります。

## 影響範囲

**各プローブ**は、**影響範囲**（**箱、または、球**）を、持ちます。**範囲の中**の、物だけが、**そのプローブを、使います**。

```text
  ┌──────────────┐      ┌──────────────┐
  │  プローブ A   │      │  プローブ B   │
  │      ●       │ ░░░░ │      ●       │       ░░ = A と B の影響範囲が、重なる境目（ブレンド領域）
  └──────────────┘      └──────────────┘
```

**範囲の境目**で、**急に、切り替える**と、**反射が、ぱっと、変わります**（**ポップ**）。**境目で、2 つを、ブレンド**して、**なめらかに、つなぎます**。

## 重みの、計算

**物の位置**が、**各プローブの、範囲の、どこに、あるか**で、**重み**を、決めます。**範囲の、中心に近い**ほど、**重みが、大きく**、**端に、近づく**と、**0** に、近づきます。

```hlsl
// 軸に平行な、箱の影響範囲に対する、重み。中心で 1、端で 0 になる（blend_distance だけ、内側からフェード）。
float ProbeWeight(float3 world_pos, float3 box_min, float3 box_max, float blend_distance) {
  float3 inside = min(world_pos - box_min, box_max - world_pos);          // 各軸で、最も近い面までの距離（内側が正）
  float d = min(min(inside.x, inside.y), inside.z);                        // 3 軸のうち、最も近い面までの距離
  return saturate(d / blend_distance);                                      // 面から、blend_distance 以上内側なら 1。面の上で 0
}
```

**箱の、面からの、距離**が、**`blend_distance`**（フェードの、幅）より、小さければ、**重みが、距離に、比例して、減ります**。**十分、内側**なら、**重み 1**です。**範囲の外**では、**0** です。

## 複数を、混ぜる

**重みが、0 でない、プローブ**（物の位置を、含む、範囲）を、**すべて**、読み、**重みで、混ぜます**。

```hlsl
// 影響する、すべてのプローブを、重みで混ぜる。重みの合計が 1 を超えたら、正規化する。
float3 SampleProbes(float3 world_pos, float3 R, float roughness, uint probe_count, uint probe_indices[8]) {
  float3 sum = 0.0;
  float weight_sum = 0.0;
  for (uint i = 0; i < probe_count; ++i) {
    ProbeData p = g_probes[probe_indices[i]];
    float w = ProbeWeight(world_pos, p.box_min, p.box_max, p.blend_distance);
    if (w <= 0.0) continue;
    float3 dir = ParallaxCorrect(R, world_pos, p.box_min, p.box_max, p.position);       // 各プローブごとに、視差補正
    float mip = roughness * (p.mip_count - 1);
    sum += g_probe_cubes.SampleLevel(g_linear_clamp, float4(dir, p.cube_index), mip).rgb * w;   // キューブマップ配列から引く
    weight_sum += w;
  }
  return sum / max(weight_sum, 1e-4);
}
```

**キューブマップ配列**（`TextureCubeArray`）に、**全プローブの、キューブマップ**を、**まとめて**、**インデックスで、選びます**。**各プローブごとに、視差補正**（[Parallax Correction](parallax.md)）を、行って、**引き**ます。

## 優先度

**プローブの、範囲が、入れ子**（**部屋の、中の、小さな、部屋**）に、なっているとき、**内側の、小さな、プローブを、優先**します。**面積が、小さい、範囲**ほど、**優先度が、高い**（より、局所的な、情報）。

```hlsl
// 優先度の高い（範囲の小さい）プローブから、順に、重みを「使い切る」方式。
float remaining = 1.0;
for (uint i = 0; i < probe_count; ++i) {                                    // probe_indices は、優先度順（範囲が小さい順）に、ソート済み
  float w = min(ProbeWeight(...), remaining);                                // 残りの重みの、範囲で
  ...
  remaining -= w;
  if (remaining <= 0.0) break;
}
// 残りは、グローバルな反射（空のキューブマップ）で、埋める。
float3 result = local_sum + g_sky_cube.SampleLevel(g_linear_clamp, R, mip).rgb * remaining;
```

**内側の、局所プローブが、重みを、取り**、**残りの、重み**は、**外側の**（**空の、グローバル プローブ**）で、**埋めます**。**局所プローブの、範囲の、端**で、**空の反射へ、なめらかに、つながります**。

## プローブの、探索

**物ごとに、全プローブを、調べる**のは、**重い**（数百個）です。**物の位置**に、**影響する、プローブだけ**を、**効率よく、探します**。

| 方法 | 内容 |
| --- | --- |
| **CPU で、物ごとに、決める**（動く物） | **物の、位置**から、**影響する、プローブ**を、**事前に、選び**、**物の、定数バッファ**で、渡す（最大 2〜4 個） |
| **画面を、クラスターに、分ける**（クラスタード シェーディング） | **クラスターごと**に、**影響するプローブの、リスト**を、持つ（[Shadows for Many Lights](../../shadows/local-lights/many-lights.md) と、同じ、仕組み） |
| **プローブの、範囲を、描く**（ディファード デカール方式） | **各プローブの範囲を、箱として、描き**、**その、箱の中の画素**に、**反射を、足し込む** |

## 動く物の、扱い

**動く物**（車、キャラクター）は、**位置が、変わる**ので、**影響する、プローブも、変わります**。**位置から、毎フレーム、プローブを、選び**、**重みを、計算**します。**物が、プローブの、範囲を、またぐ**とき、**なめらかに、切り替わる**よう、**重みを、時間方向に、補間**（**前のフレームの重みと、混ぜる**）します。

''', before="## よくあるミス")
pg.Refs("reflections/probes/blending.md", [LAGARDE, LAGARDE12, RTR, "Microsoft Learn, \"TextureCubeArray (HLSL)\""])

pg.Dedup("reflections/probes/combine-ssr.md")
pg.Add("reflections/probes/combine-ssr.md", '''
## なぜ、組み合わせるのか

**反射プローブ**と、**SSR**（画面空間の、反射）は、**得意・不得意が、正反対**です。**組み合わせる**と、**互いの、弱点を、補えます**。

| | **反射プローブ** | **SSR** |
| --- | --- | --- |
| **画面の外の物** | ○（映る） | ×（画面に、無いので、映らない） |
| **動く物** | ×（ベイクなら、映らない） | ○（今のフレームの、画面から、拾う） |
| **近くの、細かい反射** | ×（解像度が、粗い、視差の、ずれ） | ○（**正確**、画面の、実際の、ジオメトリ） |
| **遠景** | ○ | △（遠いと、レイマーチが、長く、**重い**） |
| **コスト** | **小**（テクスチャを、引くだけ） | **中〜大**（画素ごとに、レイマーチ） |
| **画面の端** | ○ | ×（端で、反射が、欠ける） |

## 基本の、合成

**SSR が、成功した、画素**（**レイが、画面内の、何かに、当たった**）は、**SSR の、結果**を、使い、**失敗した、画素**（**画面の外、見つからない**）は、**反射プローブ**で、**補います**。

```hlsl
// SSR の結果（rgb = 色、a = 信頼度 0〜1）と、反射プローブで、合成する。
float4 ssr = g_ssr_result.Load(int3(pixel, 0));                            // rgb: 反射色、a: SSR が、有効な割合
float3 probe = SampleProbes(world_pos, R, roughness, ...);                  // 反射プローブ（粗さに応じた、ぼかし、視差補正）

float3 reflection = lerp(probe, ssr.rgb, ssr.a);                            // SSR が、有効なら SSR、無効ならプローブ
```

**`ssr.a`**（**信頼度**）が、**1** なら、**SSR だけ**、**0** なら、**プローブだけ**です。**途中の、値**で、**なめらかに、つなぎます**。

### 信頼度の、決め方

**SSR の、信頼度**を、**いくつかの、要素**から、**計算**します（[Color Lookup and Fading](../ssr-basics/color-fade.md)）。

```hlsl
// SSR の、信頼度: 画面の端、レイの長さ、反射方向、粗さ、で、徐々に、下げる。
float confidence = 1.0;
confidence *= 1.0 - saturate(max(abs(hit_uv.x * 2.0 - 1.0), abs(hit_uv.y * 2.0 - 1.0)) * 4.0 - 3.0);   // 画面の端で、フェード
confidence *= 1.0 - saturate(ray_length / g_max_ssr_distance);                                          // 遠いほど、弱く
confidence *= saturate(dot(R, -V) * 4.0 + 1.0);                                                          // カメラに、向かう反射は、弱く（情報が、欠ける）
confidence *= 1.0 - saturate((roughness - 0.6) / 0.4);                                                    // 粗いほど、弱く（プローブに、任せる）
```

**画面の端**、**遠い**、**カメラに向かう**、**粗い**、という、**SSR の、苦手な、条件**で、**信頼度を、下げ**、**プローブに、切り替えます**。

## 順序と、重み付け

**3 段階**の、フォールバックを、考えます。

```text
① SSR（画面内の、近距離。最も、正確）  → 信頼度 a1
② 反射プローブ（画面の外・遠景）          → 残り (1 − a1) の、うち、プローブの、重み a2
③ グローバルな、空のキューブマップ          → 残り
```

```hlsl
float3 result = ssr.rgb * ssr.a                                              // ① SSR
              + local_probe * (1.0 - ssr.a) * probe_weight                   // ② ローカル プローブ
              + sky * (1.0 - ssr.a) * (1.0 - probe_weight);                  // ③ 空
```

**SSR が、有効な部分**は、**SSR**、**それ以外**は、**局所プローブ**、**さらに、プローブの、範囲外**は、**空**（[Probe Operation](blending.md)）、と、**段階的に、フォールバック**します。

## 色の、つながり

**SSR と、プローブ**は、**別の、方法で、作られた**ので、**同じ物を、映しても、色や、明るさが、わずかに、違う**ことが、あります。**境目**（信頼度が、変わる所）で、**反射の色が、ずれて見える**場合が、あります。

| 問題 | 対策 |
| --- | --- |
| **明るさの、ずれ** | **SSR の、露出**（前フレームの、トーン マッピング前の、色）と、**プローブの、HDR**を、**同じ、スケール**で、扱う |
| **色の、ずれ** | プローブの、**撮影時の、ライティング**が、**今のシーン**と、**違う**（昼夜が、変わった）。**プローブを、動的に、更新**、**または、時間帯で、補間** |
| **境目が、見える** | **信頼度の、フェードを、広く**（急に、切り替えない） |

## 描画の、順序

| 順 | 内容 |
| --- | --- |
| 1 | **不透明な物**を、描く（G バッファ） |
| 2 | **SSR**（G バッファと、前フレームの色から） |
| 3 | **反射プローブ**と、SSR を、**合成**（ライティングの、一部として） |
| 4 | **半透明**、ポスト プロセス |

**SSR は、前フレームの、色**を、使うことが、多く（**今フレームの、ライティングは、まだ、終わっていない**ため）、**1 フレームの、遅れ**が、あります（[SSR Fallback and Compositing](../ssr-fallback.md)）。

''', before="## よくあるミス")
pg.Refs("reflections/probes/combine-ssr.md", [STACHOWIAK15, VALIENT, MCGUIRE, LAGARDE, RTR])

# ================================================================ ssr-basics
pg.Dedup("reflections/ssr-basics/index.md")
pg.Add("reflections/ssr-basics/index.md", '''
## SSR とは

**SSR**（Screen-Space Reflections、**画面空間の、反射**）は、**画面に、映っている、情報**（深度、色）だけを、使って、**反射**を、**近似**する方法です。**反射する面**の、各画素から、**反射方向に、レイを、飛ばし**、**画面の中の、何かに、当たったら**、**その画素の、色**を、**反射として、使います**。

```text
反射する面の画素 P:
   視線 V と法線 N から、反射方向 R を求める
   P から R の向きに、画面空間で、レイを進める（深度バッファを、辿る）
   何かに、当たったら、当たった画素の「ライティング済みの色」を、P の反射色にする
```

## 最小の、考え方

**1 つの、画素**について、**5 つの手順**です。

| 手順 | 内容 | ページ |
| --- | --- | --- |
| ① **反射ベクトル**を、求める | 視線と、法線から | このページ |
| ② **レイを、進める** | 画面空間で、1 歩ずつ、深度を、確かめる | [Linear Marching](linear-march.md) |
| ③ **当たりを、判定**する | **レイが、面の、裏に、入った**（厚み以内） | [Thickness](thickness.md) |
| ④ **色を、読む**・フェードする | 当たった画素の、色。**画面の端、遠い**ほど、薄く | [Color Lookup and Fading](color-fade.md) |
| ⑤ **粗さ**に、応じて、ぼかす | **粗い面**は、**ぼかす**（[Cost and Roughness](cost-roughness.md)） | [Cost and Roughness](cost-roughness.md) |

## ① 反射ベクトルと、画面空間への、投影

```hlsl
// G バッファから、ビュー空間の位置と、法線を読み、反射ベクトルを求める。
float3 position_vs = ReconstructViewPosition(uv, depth);                    // ビュー空間の位置（カメラが原点）
float3 normal_vs = DecodeNormal(g_gbuffer_normal.Load(int3(pixel, 0)));
float3 view_dir_vs = normalize(position_vs);                                // カメラから、画素へ向かう向き
float3 reflect_dir_vs = reflect(view_dir_vs, normal_vs);                    // 反射ベクトル
```

**カメラから、画素への、向き**（視線）を、**法線で、反射**させた向きが、**反射ベクトル**です。**ビュー空間**で、扱うと、**カメラが、原点**で、**簡単**です。

```hlsl
// レイの、始点と終点を、画面（uv）に、投影して、画面上の、線分にする。
float3 end_vs = position_vs + reflect_dir_vs * g_max_distance;
float4 start_clip = mul(float4(position_vs, 1.0), g_proj);
float4 end_clip = mul(float4(end_vs, 1.0), g_proj);
float2 start_uv = start_clip.xy / start_clip.w * float2(0.5, -0.5) + 0.5;
float2 end_uv = end_clip.xy / end_clip.w * float2(0.5, -0.5) + 0.5;
```

**レイの始点と終点**を、**画面空間**（uv）に、**投影**します。**画面上の、線分**を、**1 画素ずつ**（または、数画素ずつ）**辿る**と、**画面の、深度**と、**比べられます**（[Linear Marching](linear-march.md)）。

## SSR の、限界

SSR は、**画面の、情報だけ**を、使うので、**根本的な、限界**が、あります。

| 限界 | 内容 | 対策 |
| --- | --- | --- |
| **画面の外**が、映らない | **画面に、映っていない**物は、**反射に、出ない** | **反射プローブ**で、補う（[Combining with SSR](../probes/combine-ssr.md)） |
| **隠れた面**が、映らない | **手前の物の、裏**は、深度バッファに、**無い**。**物の、裏側の、反射**が、**欠ける** | 厚みを、仮定（[Thickness](thickness.md)）、プローブで補う |
| **画面の端**で、**反射が、消える** | レイが、**画面の外**に、出る | **端で、フェード**（[Color Lookup and Fading](color-fade.md)） |
| **カメラに、向かう反射**が、弱い | 反射方向が、**カメラの方向**に、近い（鏡に、真正面から、向き合う）と、**カメラの、背後**の、景色が、必要（画面に、無い） | **信頼度を、下げて**、プローブへ |
| **細い物**を、**すり抜ける** | **ステップが、粗い**と、**細い物を、飛び越える** | ステップを、細かく、**Hi-Z**（[Hi-Z SSR](../ssr-hiz.md)） |

''', before="## よくあるミス")
pg.Refs("reflections/ssr-basics/index.md", [MCGUIRE, STACHOWIAK15, ULUDAG, VALIENT, RTR])

pg.Dedup("reflections/ssr-basics/linear-march.md")
pg.Add("reflections/ssr-basics/linear-march.md", '''
## 線形マーチ：画面空間で、レイを、辿る

**最も、単純な、SSR** は、**反射レイを、画面空間で、一定の歩幅で、辿り**、**各点で、深度バッファと、比べる**方法です（**線形マーチ**）。**当たりを、見つける**まで、**繰り返します**。

```text
画面上の、線分（始点 → 終点）を、N 区間に、分ける。各区間で:
   レイ上の点の、深度 と、その画素の、深度バッファの値 を、比べる
   レイの方が、奥（面の、裏）に、入った → 交差
```

## 実装

```hlsl
// 線形マーチ: 画面空間で、レイを、一定の歩幅で、進める。戻り値: 当たった uv（当たらなければ、-1）。
float2 LinearMarch(float3 origin_vs, float3 dir_vs, float2 pixel) {
  // 始点・終点を、クリップ空間→ uv へ（前のページと同じ）。
  float3 end_vs = origin_vs + dir_vs * g_max_distance;
  float4 s = mul(float4(origin_vs, 1.0), g_proj);
  float4 e = mul(float4(end_vs, 1.0), g_proj);
  float2 start_uv = s.xy / s.w * float2(0.5, -0.5) + 0.5;
  float2 end_uv = e.xy / e.w * float2(0.5, -0.5) + 0.5;
  float start_inv_w = 1.0 / s.w;                                          // 1/w（透視補正のため）
  float end_inv_w = 1.0 / e.w;
```

**始点と終点**を、**uv に、投影**します。**`1/w`** を、**覚えておく**のは、**透視投影の、補間**（**画面空間で、直線的に、補間しても、奥行きは、直線的でない**）を、**正しく、行う**ためです。

```hlsl
  const int kSteps = 32;
  float jitter = InterleavedGradientNoise(pixel) * 0.5;                   // 開始位置を、ずらして、縞を、減らす
  for (int i = 1; i <= kSteps; ++i) {
    float t = (i + jitter) / kSteps;                                        // 線分上の、位置（0〜1）。画面空間で、等間隔
    float2 uv = lerp(start_uv, end_uv, t);                                  // 画面上の位置
    if (any(uv < 0.0) || any(uv > 1.0)) return -1.0;                        // 画面の外に出た → 当たらない
```

**画面空間で、等間隔**に、進みます。**画面の外**に、出たら、**情報が、無い**ので、**打ち切ります**。

```hlsl
    // レイ上の点の、深度（ビュー空間の距離）。1/w を、画面空間で線形補間して、逆数を取る（透視補正）。
    float inv_w = lerp(start_inv_w, end_inv_w, t);
    float ray_depth = 1.0 / inv_w;                                          // レイ上の点の、ビュー空間での、深度（正の距離）

    float scene_depth = LinearizeDepth(g_depth.SampleLevel(g_point_clamp, uv, 0));   // その画素の、実際の深度

    float diff = ray_depth - scene_depth;
    if (diff > 0.0 && diff < g_thickness) return uv;                        // レイが、面の「裏」に入った（厚み以内）→ 当たり
  }
  return -1.0;                                                              // 当たらなかった
}
```

**レイ上の、点の、深度**は、**`1 / w` を、画面空間で、線形補間し**、**その逆数**を、取ると、**正しい**値です（**透視補正**）。**画面の深度**と、**比べ**、**レイが、面より、奥**に、入って、**かつ、厚み以内**なら、**当たり**です。

## 線形マーチの、問題

### ① 細い物を、すり抜ける

**歩幅が、粗い**と、**細い物**（フェンス、手すり）の、**上を、飛び越えて**、**当たりを、見逃します**。

```text
ステップ:  ●     ●     ●     ●     ●          ← 粗い歩幅
                  ┃ 細い物
                 ●が、物の、手前と奥に、またがって、当たりを、検出できない（厚みの範囲を、飛び越える）
```

| 対策 | 内容 |
| --- | --- |
| **歩幅を、細かく** | ステップ数を、増やす。**重い** |
| **厚みを、大きく** | **すり抜けは、減る**が、**偽の当たり**（物の、手前の面に、誤って当たる）が、増える（[Thickness](thickness.md)） |
| **二分探索**で、洗練 | **当たりを、見つけた**後、**直前の、ステップと、の間**で、**二分探索**し、**正確な、交点**を、求める |
| **Hi-Z** | **階層的な深度**で、**空の部分を、大きく、飛ばし**、**細かい所は、細かく**（[Hi-Z SSR](../ssr-hiz.md)） |

### ② 二分探索で、交点を、洗練する

**当たった、ステップ**の、**1 つ前**（まだ、当たっていない）と、**当たったステップ**の、**間**に、**真の、交点**が、あります。**二分探索**で、**絞り込みます**。

```hlsl
// 当たった t_hit と、その 1 つ前 t_prev の間を、二分探索して、正確な交点を求める。
float lo = t_prev, hi = t_hit;
for (int k = 0; k < 6; ++k) {                                               // 6 回で、歩幅の 1/64 の精度
  float mid = 0.5 * (lo + hi);
  float2 uv_mid = lerp(start_uv, end_uv, mid);
  float ray_d = 1.0 / lerp(start_inv_w, end_inv_w, mid);
  float scene_d = LinearizeDepth(g_depth.SampleLevel(g_point_clamp, uv_mid, 0));
  if (ray_d > scene_d) hi = mid; else lo = mid;                              // レイが、面の裏なら、手前へ。そうでなければ、奥へ
}
float2 hit_uv = lerp(start_uv, end_uv, hi);
```

**6 回の、二分探索**で、**歩幅の、1/64**の、**精度**に、なります。**粗い歩幅**でも、**正確な、交点**が、得られ、**反射が、なめらか**になります。

### ③ 画面空間で、等間隔でも、3D では、不均等

**画面空間で、等間隔**に、進むと、**カメラに、近い所**では、**3D の歩幅が、小さく**、**遠い所**では、**大きく**なります。**遠くの物**は、**粗い歩幅**で、**すり抜けやすく**なります。

| 方式 | 内容 |
| --- | --- |
| **画面空間で、等間隔** | **実装が、簡単**。**遠くが、粗い** |
| **3D 空間で、等間隔** | 歩幅が、**3D で、一定**。**画面上の、歩幅が、不均等**（近くは、画素を、飛ばす） |
| **DDA**（デジタル微分解析器）で、1 画素ずつ | **画面上の、**すべての**画素**を、**1 つずつ、辿る**。**取りこぼしが、無い**。**線が、長いと、重い** |

**DDA** は、**線分が、通る、すべての画素**を、**辿る**ので、**取りこぼしが、ありません**（McGuire と Mara、2014）。**画面上の、線分が、長い**と、**ステップが、非常に、多く**なるので、**最大のステップ数**を、**制限**します。

## 速さの、目安

| 設定 | コスト |
| --- | --- |
| 線形マーチ 16 ステップ + 二分探索 | 約 0.5 ms（1080p、半解像度） |
| 線形マーチ 32 ステップ + 二分探索 | 約 1 ms |
| **Hi-Z**（[Hi-Z SSR](../ssr-hiz.md)） | 同品質で、**数倍速い** |

''', before="## よくあるミス")
pg.Refs("reflections/ssr-basics/linear-march.md", [MCGUIRE, STACHOWIAK15, ULUDAG, RTR])

pg.Dedup("reflections/ssr-basics/thickness.md")
pg.Add("reflections/ssr-basics/thickness.md", '''
## 深度バッファは、「面」しか、知らない

**深度バッファ**が、持っているのは、**各画素で、カメラに、最も、近い、面の、距離**だけです。**その面の、裏**（**物の、厚み**）や、**手前の物に、隠れた、奥の物**は、**知りません**。SSR で、**レイが、深度バッファと、交差した**とき、**その面が、どれだけ、厚いか**が、**分からない**ので、**仮定**が、必要になります。これが、**厚み**（thickness）の、問題です。

## 当たりの、判定

**レイ上の、点の、深度**と、**その画素の、深度**を、比べて、**当たり**かを、判定します。

```text
diff = レイの深度 − 画面の深度

diff < 0       : レイが、面より手前（まだ、面に、達していない）→ 当たりなし
0 ≤ diff < T   : レイが、面の「裏」に入ったが、厚み T 以内 → 当たり
diff ≥ T       : レイが、面の裏に入って、かつ、厚み T を超えた → 当たりなし（物の「向こう」を、通り抜けた）
```

```hlsl
float diff = ray_depth - scene_depth;
bool hit = (diff > 0.0) && (diff < g_thickness);
```

**厚み `T`** は、**「物が、これくらいの、厚さ**まで、あると**、仮定する**」値です。

## 厚みの、大小の、トレードオフ

| 厚み T | 結果 |
| --- | --- |
| **小さい**（0.1 m など） | **細い物**（フェンス、手すり）は、**すり抜ける**（レイが、物の、裏に、入る前に、**T を、超えて**、**見逃す**）。**偽の当たりは、少ない** |
| **大きい**（2 m など） | **すり抜けは、減る**が、**偽の当たり**が、**増える**。**レイが、手前の物の、裏**（**実際は、向こうに、物は、無い**）を、**当たりと、誤認** |

```text
 偽の当たり（T が大きすぎる）:
        ┃柱（手前）
 カメラ ●──→ 柱の向こう側を、通る反射レイ
        レイが、柱の、深度の「裏」に入った瞬間、T 以内なので、「柱に当たった」と、誤認（実際は、柱の向こうの、何かが、映るはず）
```

**厚みが、大きすぎる**と、**柱の、すぐ後ろ**で、**反射が、柱の色に、染まったり**、**引き伸ばされた**、**縞状の、アーティファクト**が、出ます。

## 厚みの、決め方

| 方法 | 内容 |
| --- | --- |
| **一定の値**（定数） | 簡単。**場面に、合わせて、調整**（0.2〜1 m） |
| **距離に比例** | **遠くの物ほど**、**画面上の、1 画素が、広い**ので、**厚みも、大きく**（`T = 画素の、ワールド上の、大きさ × k`） |
| **物ごとに**、**G バッファに**、**厚みを、保存** | **メッシュごと**（**薄い板、厚い箱**）に、**適切な、厚み**を、持たせる。**正確**だが、**G バッファの、チャンネルが、必要** |
| **裏面の、深度バッファ**（**デプス ピーリング**の、2 層目） | **物の、裏面**の、深度を、**別に、保存**し、**表と、裏の差**が、**その画素の、厚み**。**最も、正確**。**描画が、増える** |

### 距離に、比例させる

```hlsl
// 距離に比例した、厚み。遠いほど、1 画素が、広いので、厚みを、大きくする。
float pixel_world_size = scene_depth * g_pixel_angle;                       // 1 画素が、その距離で、覆う、ワールドの大きさ
float thickness = max(g_min_thickness, pixel_world_size * g_thickness_scale);
```

**遠くの、物**ほど、**深度バッファの、解像度が、粗く**（**1 画素が、広い範囲**）、**厚みを、大きく、取らないと**、**すり抜け**ます。**近くは、小さく**します。

## 厚みの、調整だけでは、解決できない

**厚みの、仮定は、近似**で、**限界**が、あります。

| 場面 | 問題 |
| --- | --- |
| **細い物**（フェンス）と、**厚い物**（壁）が、混在 | **どちらにも、合う、厚み**が、**無い**。**薄い物は、すり抜け**、**厚い物の、裏で、偽の当たり** |
| **カメラに、近い**（画面上で、大きい）物 | **深度が、急に、変わる**（物の、縁）。**縁で、偽の当たり** |
| **物の、縁**（シルエット）の、近く | **深度が、不連続**で、**縁を、またぐ**レイは、**どちらの面に、当たったか、不定** |

## 偽の当たりを、減らす、工夫

| 工夫 | 内容 |
| --- | --- |
| **当たった点の、法線を、確認** | 当たった画素の、**法線**が、**レイと、同じ向き**（**面の、表を、向いている**）なら、**無効**（**裏から、当たった**）。**物の、表側に、当たる、はず** |
| **当たった点の、位置を、確認**（再投影） | **当たった画素の、ワールド位置**と、**レイの位置**が、**近いか** |
| **深度の、勾配を、確認** | 当たった画素の、**周りの、深度の差が、大きい**（**縁**）なら、**信頼度を、下げる** |

```hlsl
// 当たった画素の、法線が、レイと、同じ向き（面の裏から、当たった）なら、無効にする。
float3 hit_normal = DecodeNormal(g_gbuffer_normal.Load(int3(hit_pixel, 0)));
if (dot(hit_normal, reflect_dir_vs) > 0.0) return false;                    // 面が、レイの方を、向いていない → 裏から当たった
```

''', before="## よくあるミス")
pg.Refs("reflections/ssr-basics/thickness.md", [MCGUIRE, STACHOWIAK15, ULUDAG, RTR])

pg.Dedup("reflections/ssr-basics/cost-roughness.md")
pg.Add("reflections/ssr-basics/cost-roughness.md", '''
## 粗さと、SSR の、関係

**SSR の、レイ**は、**反射方向**に、**1 本**飛ばして、**当たった、色**を、読みます。これは、**粗さ 0**（完全な、鏡）の、反射**です。**粗い面**は、**反射が、ぼやけ**（周りの、広い範囲が、混ざる）ので、**1 本の、レイ**では、**足りません**。

| 粗さ | 反射の見え方 | SSR で、必要なこと |
| --- | --- | --- |
| **0**（鏡） | くっきり | レイ 1 本で、よい |
| **0.2〜0.4** | **少し、ぼやける** | **ぼかし**、または、**複数のレイ** |
| **0.5〜0.7** | **かなり、ぼやける** | **多数の、レイ**、または、**大きな、ぼかし** |
| **0.8 以上** | **ほぼ、拡散**（景色が、判別できない） | **SSR は、やめて**、**反射プローブ**（ミップで、ぼかした）に、任せる |

## 方法 1：反射を、ぼかす

**くっきり、1 本のレイ**で、**反射を、取り**、**粗さに応じて、ぼかします**。**安い**が、**偽物**（**距離による、ぼけの、変化が、出ない**）です。

```hlsl
// SSR の結果（反射色）を、粗さに応じて、ぼかす。画面（色）のミップマップを、使う。
float mip = roughness * g_max_blur_mip;                                      // 粗さ → ミップ（粗いほど、ぼやける）
float3 reflected = g_lit_scene_mips.SampleLevel(g_linear_clamp, hit_uv, mip).rgb;
```

**当たった、画素の位置**で、**画面の色の、ミップマップ**を、**読む**（**粗いほど、高いミップ**）と、**当たった点の、周りが、ぼけて**、**反射が、ぼやけます**。**1 回の、テクスチャ読み込み**で、**安い**です。

### 距離による、ぼけの、変化

**現実の、反射**は、**反射する物が、遠い**ほど、**ぼけが、大きく**なります（**反射の、円錐が、広がる**ため）。**レイの長さ**に、応じて、**ミップを、上げる**と、**これを、近似**できます。

```hlsl
float cone_radius = ray_length * tan(roughness_to_cone_angle(roughness));    // レイの長さに、比例して、円錐が広がる
float mip = log2(cone_radius * g_screen_size_pixels / pixel_world_size);      // 円錐の広がりに合う、ミップ
```

**レイが、長い**（遠くの物が、映る）ほど、**ぼけが、大きく**なります。**コーン トレーシング**の、考え方です（[Hi-Z SSR](../ssr-hiz.md) の、Uludag の、方法）。

## 方法 2：確率的に、複数のレイ

**粗さに応じた、分布**で、**反射方向を、ランダムに**（GGX の、重点サンプリング）、**数本**飛ばし、**平均**します（**確率的 SSR**、Stachowiak と Uludag、2015）。**本物の、ぼけ**が、得られますが、**ノイズ**が、出るので、**時間蓄積**と、**空間フィルタ**が、必要です（[Stochastic SSR](../ssr-stochastic.md)）。

```hlsl
// 粗さに応じて、反射方向を、GGX の分布で、ランダムに、ずらす（重点サンプリング）。
float3 H = LocalToWorld(ImportanceSampleGGX(Random2(pixel, g_frame_index), roughness), normal_vs);
float3 R = reflect(view_dir_vs, H);                                           // 法線を、H に、ずらして、反射
```

**GGX の分布**に従って、**法線**を、**ずらした**もの（ハーフ ベクトル `H`）で、**反射**させます。**粗い面**ほど、**大きく、ずれる**ので、**周りの、広い範囲**を、サンプルします。

## コストの、内訳

| 処理 | コスト（1080p、目安） |
| --- | --- |
| **レイマーチ**（画素ごと、16〜32 ステップ） | **0.5〜2 ms**（**最大の、コスト**） |
| **反射色の、読み込み + ぼかし** | 0.1〜0.3 ms |
| **時間蓄積・空間フィルタ**（確率的 SSR の場合） | 0.3〜1 ms |
| **プローブとの、合成** | 0.1 ms |

**SSR の、コスト**の、**大部分**は、**レイマーチ**です。

## コストを、下げる

| 工夫 | 効果 |
| --- | --- |
| **半分の、解像度**で、トレースして、アップサンプル | 約 **1/4** のコスト。**反射が、少し、ぼける** |
| **粗さが、大きい**（0.7 以上）画素は、**スキップ** | **多くの画素**を、**スキップ**（プローブに、任せる） |
| **反射しない**面（粗さが、高い、**非金属**で、反射が、弱い）を、**スキップ** | **反射が、見えない**画素の、レイマーチを、省く |
| **レイの、最大距離**を、短く | **ステップ数が、減る** |
| **Hi-Z**（[Hi-Z SSR](../ssr-hiz.md)） | **同品質で、数倍、速い** |

```hlsl
// 反射が、ほぼ見えない画素は、レイマーチを、スキップする。
float fresnel_scale = 0.04 + metallic * 0.96;                                 // 非金属は、約 4% しか、反射しない
if (roughness > 0.7 || fresnel_scale * (1.0 - roughness) < 0.01) return float4(0, 0, 0, 0);   // SSR なし → プローブに、任せる
```

**非金属**（**反射率 4%**）で、**粗い**面は、**反射が、ほとんど、見えません**。**レイマーチを、省いて**、**反射プローブ**に、**任せます**。**画素の、多くを、スキップ**できるので、**大きな、節約**に、なります。

''', before="## よくあるミス")
pg.Refs("reflections/ssr-basics/cost-roughness.md", [STACHOWIAK15, ULUDAG, HEITZ, WALTER, RTR])

pg.Dedup("reflections/ssr-basics/color-fade.md")
pg.Add("reflections/ssr-basics/color-fade.md", '''
## 当たった画素の、色を、使う

**レイが、当たった**（交差した）画素の、**色**が、**反射の色**です。**どの色を、読むか**、**どう、フェードするか**で、**反射の見た目**が、決まります。

## どの色を、読むか

**当たった画素の、色**は、**ライティング済みの、画面の色**（**HDR**）を、**使います**。**ただし**、**今フレームの、ライティングは、まだ、完了していない**（SSR は、ライティングの、一部）ので、**2 通り**の、方法が、あります。

| 方法 | 内容 | 長所 | 短所 |
| --- | --- | --- | --- |
| **前フレームの、色**（**履歴**） | **前のフレームの、最終的な色**（反射を、含む）を、読む | **反射の、反射**（**多重反射**）が、**自然に**、出る。**ライティング完了後の色**なので、**正確** | **1 フレームの、遅れ**（物が、動くと、**反射が、遅れる**）。**再投影**が、必要 |
| **今フレームの、色**（反射なし） | **今フレームの、ライティング**（SSR を、含まない、**直接光 + 間接光**）を、読む | **遅れが、ない** | **反射の、反射が、出ない**。**SSR の、前に、ライティングを、完了**させる必要 |

**多くの、ゲーム**は、**前フレームの色**を、使います（**反射の、反射**が、**簡単に、手に入る**ため）。

### 前フレームの色を、読む（再投影）

**前フレームの、画面**は、**カメラが、動いて**いるので、**当たった点**が、**前のフレームの、画面の、どこに**映っていたかを、**再投影**で、求めます。

```hlsl
// 当たった点の、ワールド位置から、前フレームの uv を求めて、前フレームの最終色を読む。
float3 hit_world = ViewToWorld(hit_position_vs);
float4 prev_clip = mul(float4(hit_world, 1.0), g_prev_view_proj);
float2 prev_uv = prev_clip.xy / prev_clip.w * float2(0.5, -0.5) + 0.5;
float3 reflected_color = g_prev_frame_color.SampleLevel(g_linear_clamp, prev_uv, mip).rgb;
```

**当たった点の、ワールド位置**を、**前のフレームの、行列**で、**投影**して、**前フレームの、画面座標**を、得ます。**動く物**は、**前のフレームで、別の位置**にいた（**位置が、ずれる**）ので、**速度バッファ**（[Velocity Buffer](../../postprocess/motion-blur/velocity-buffer.md)）で、**補正**します。

## フェード：信頼できない、反射を、薄める

**SSR の、結果**が、**あまり、信頼できない**状況で、**急に、消える**と、**反射が、ぱっと、変わって**見えます。**状況に、応じて、徐々に、薄めます**（**フェード**）。**薄めた分**は、**反射プローブ**（[Combining with SSR](../probes/combine-ssr.md)）が、補います。

### ① 画面の端

**レイが、画面の端に、近い所**に、**当たる**と、**画面の外の、情報が、欠けて**、**不正確**です。**端に、近いほど、薄めます**。

```hlsl
// 当たった uv が、画面の端に近いほど、フェード アウト（端から 10% の幅で、0 になる）。
float2 edge = saturate((0.5 - abs(hit_uv - 0.5)) * 10.0);                    // 端で 0、端から 0.1 以上内側で 1
float edge_fade = min(edge.x, edge.y);
```

### ② レイの、長さ

**遠くに、当たった**反射は、**精度が、低く**（ステップが、粗い）、**画面の外へ、出やすい**ので、**薄めます**。

```hlsl
float distance_fade = 1.0 - saturate(ray_length / g_max_distance);           // 遠いほど、弱く
```

### ③ 反射の向き

**反射方向が、カメラに、向かう**（鏡に、真正面から、向き合う）と、**カメラの背後**（**画面に、映っていない**）の、景色が、必要です。**情報が、無い**ので、**薄めます**。

```hlsl
float facing = dot(reflect_dir_vs, view_dir_vs);                              // 反射が、視線と、同じ向き（奥へ向かう）なら 1、カメラへ戻るなら −1
float direction_fade = saturate(facing * 3.0 + 1.0);                          // カメラに戻る反射（facing < −1/3）で、0
```

### ④ 粗さ

**粗い面**は、**SSR の、1 本のレイが、あまり、意味を、持たない**（ぼけが、大きい）ので、**粗さが、大きい**ほど、**薄め**、**プローブに、任せます**。

```hlsl
float roughness_fade = 1.0 - saturate((roughness - 0.5) / 0.3);               // 粗さ 0.5 から、0.8 にかけて、0 へ
```

### ⑤ フェードを、まとめる

```hlsl
float confidence = edge_fade * distance_fade * direction_fade * roughness_fade;
float3 reflection = lerp(probe_reflection, ssr_color, confidence);            // 信頼度が低いほど、プローブ
```

**4 つの、フェード**を、**掛け合わせ**、**1 つの、信頼度**にまとめます。**どれか 1 つでも、0 に、近ければ、プローブ**に、**切り替わります**。

## 明るさの、問題：ファイアフライ

**反射色に、非常に、明るい**画素（**太陽、光源**）が、**含まれる**と、**反射が、まぶしい、点**（**ファイアフライ**）に、なります。**ぼかし**で、**周りに、広がって**、**目立つ**ことも、あります。

| 対策 | 内容 |
| --- | --- |
| **明るさを、クランプ** | **反射色の、輝度**に、**上限**（たとえば、10）を、設ける。**太陽の、反射**が、**明るすぎ**ないように |
| **トーン マッピングの、前に、クランプ**しない（太陽の、輝きは、残したい） | **ブルーム**で、光らせる **用途**では、**クランプは、弱め**に |

```hlsl
// 明るすぎる、反射を、抑える（色相を保ったまま、輝度に上限）。
float lum = Luminance(reflected_color);
reflected_color *= min(1.0, g_max_reflection_luminance / max(lum, 1e-4));
```

''', before="## よくあるミス")
pg.Refs("reflections/ssr-basics/color-fade.md", [STACHOWIAK15, VALIENT, MCGUIRE, RTR])

pg.Dedup("reflections/ssr-basics/artifacts.md")
pg.Add("reflections/ssr-basics/artifacts.md", '''
## SSR で、よく出る、見た目の、問題

SSR は、**画面の、情報だけ**で、反射を、作るので、**いくつかの、典型的な、見た目の、問題**が、**出ます**。**原因**と**対策**を、整理します。

| 症状 | 原因 | 対策 |
| --- | --- | --- |
| **反射が、画面の端で、途切れる** | レイが、**画面の外**に出る | **端でフェード**、プローブで、補う |
| **反射が、手前の物の、裏で、欠ける**（**反射の、穴**） | **手前の物に、隠れた**部分は、**画面に、無い** | プローブで補う、**厚みの、調整** |
| **反射が、引き伸ばされる**（縞） | **厚みが、大きすぎ**、**物の、縁を、またぐ** | 厚みを、小さく、当たった面の、法線を、確認（[Thickness](thickness.md)） |
| **細い物が、反射に、映らない** | **ステップが、粗く**、**すり抜ける** | ステップを、細かく、**Hi-Z**（[Hi-Z SSR](../ssr-hiz.md)） |
| **反射が、ちらつく** | **ステップの、位置が、フレームごとに、ずれる**、**ノイズ** | **ジッターを、固定**、**時間蓄積** |
| **反射が、ざらざら（ノイズ）**（粗い面） | **確率的な、レイ** | **時間蓄積 + 空間フィルタ**（[Stochastic SSR](../ssr-stochastic.md)） |
| **反射が、1 フレーム遅れる** | **前フレームの色**を、使っている | **速度バッファで、補正**、許容 |
| **動く物の、反射が、ゴースト** | **前フレームの、色が、古い** | **速度バッファ**、**履歴の、クランプ** |
| **反射が、地面の下に、突き抜ける** | 反射ベクトルが、**面の下**を向く（法線と、視線の、角度が、浅い） | **反射ベクトルを、法線に、押し戻す**、**レイの、始点を、面から、少し、離す** |

## 反射の、穴

**反射する面の、前に、物がある**とき、**その物の、裏側に、映るはず**の、**景色**が、**画面に、無い**ため、**反射に、穴**が、あきます（**黒く**なる、**または、背景が、見える**）。

```text
 カメラ ●
         ╲
          ╲   ┃柱（手前）
           ╲  ┃
        ━━━━╲━┃━━━━━ 床
              ╲┃     床の、柱の裏側にある部分の、反射には、柱の「裏面」が、映るはずだが、画面には、柱の「表面」しか、無い
```

**この問題は、SSR の、根本的な、限界**です。**反射プローブ**（[Combining with SSR](../probes/combine-ssr.md)）で、**穴を、埋めます**。

## 反射の、引き伸ばし

**レイが、物の、縁**（シルエット）で、**当たる**と、**縁の、先**の、**遠くの、背景**を、**物の色で、引き伸ばした**ような、**縞**が、出ます。

**原因**は、**当たった画素の、深度**と、**レイ上の点の、深度の差**が、**厚み以内**であれば、**当たりと、見なす**ため、**物の縁の、すぐ後ろ**の、**遠い背景**まで、**同じ物に、当たったと、誤認**することです。

| 対策 | 内容 |
| --- | --- |
| **厚みを、小さく**（**距離に比例**） | **偽の当たりが、減る**（[Thickness](thickness.md)） |
| **当たった面の、法線を、確認** | **面が、反射レイの方を、向いている**場合だけ、**有効** |
| **深度の、不連続を、検出** | **当たった画素の、周りの、深度が、大きく、違う**（縁）なら、**信頼度を、下げる** |

## 時間方向の、問題

| 問題 | 内容 | 対策 |
| --- | --- | --- |
| **ちらつき** | **ジッター**が、フレームごとに、**変わる**、ノイズが、**揺れる** | **ジッターに、ブルー ノイズ + フレーム番号**（TAA で、平均される）。**時間蓄積** |
| **ゴースト** | **前フレームの、反射**が、**今の状態と、合わない** | **履歴の、クランプ**、**動き（速度バッファ）の、考慮** |
| **反射の、遅れ** | **前フレームの、色を、読む**ため、**動く物の、反射が、遅れる** | **速度で、補正**、または、**今フレームの、色**を、読む |

## デバッグ

SSR の、**問題を、見つける**には、**中間結果を、画面に、表示**します。

| 表示するもの | 見つかる問題 |
| --- | --- |
| **反射ベクトル**（色で、方向を表示） | 法線が、**間違っている**、反射の向きが、**おかしい** |
| **当たったか**（白 = 当たり、黒 = 外れ） | **ステップが、足りない**、**厚みが、合わない** |
| **当たった位置の uv**（色で、表示） | **レイが、思った場所に、当たっているか** |
| **信頼度**（フェードの、結果） | **フェードが、効きすぎ・足りない** |
| **SSR だけ**（プローブなしで、表示） | **SSR の、本来の、品質**を、**確認** |

```hlsl
// デバッグ: 当たったか否かを、色で表示（緑 = 当たり、赤 = 外れ、青 = 画面の外）。
return hit ? float4(0, 1, 0, 1) : (out_of_screen ? float4(0, 0, 1, 1) : float4(1, 0, 0, 1));
```

''', before="## よくあるミス")
pg.Refs("reflections/ssr-basics/artifacts.md", [MCGUIRE, STACHOWIAK15, VALIENT, ULUDAG, RTR])

# ================================================================ RT reflections
pg.Dedup("reflections/rt-reflections/index.md")
pg.Add("reflections/rt-reflections/index.md", '''
## レイトレーシングで、反射を、描く

**ハードウェア レイトレーシング**（DXR）を、使うと、**反射**を、**実際の、三角形に、レイを、飛ばして**、**正確に**、求められます。**SSR の、限界**（画面の外、隠れた面）が、**ありません**。**反射の、反射**（多重反射）、**屈折**、**ガラスの、反射**も、**自然に、扱えます**。

## 基本の、流れ

```text
各画素（反射する面）から、反射方向に、レイを、飛ばす（DXR の TraceRay）
   ↓ 当たった面の、色を、求める（ヒット シェーダー）
当たった面の、ライティング（直接光 + 影レイ）+ 当たった面が、さらに、反射するなら、もう一度、レイ
   ↓
ノイズを、取る（デノイズ）→ 反射を、画面に、合成
```

## 構成要素

| 要素 | 内容 | ページ |
| --- | --- | --- |
| **レイの、生成** | **どの画素**から、**どの方向**に、レイを、飛ばすか（**粗さに、応じた、分布**） | [Ray Generation](ray-generation.md) |
| **ヒット シェーディング** | 当たった面の、**色**を、求める。**BVH**（加速構造）の、管理 | [Hit Shading and BVH](hit-shading.md) |
| **ハイブリッド** | **SSR と、レイトレーシング**の、**組み合わせ**（**画面内は SSR、外れたら RT**） | [Hybrid Pipeline](hybrid.md) |
| **デノイズ** | **ノイズを、取り除く** | [Denoising](denoise.md) |

## SSR との、比較

| | SSR | **レイトレーシング**（RT） |
| --- | --- | --- |
| **画面の外**の物 | ×（映らない） | ○（**映る**） |
| **隠れた面**（物の裏） | ×（穴が、あく） | ○（**正確**） |
| **反射の、反射** | △（前フレームの色で、近似） | ○（**正確**。再帰） |
| **ガラスの、屈折・反射** | ×（簡易） | ○（**レイを、屈折・反射**させられる） |
| **コスト** | **中** | **大**（レイ、BVH、シェーディング） |
| **必要な、ハードウェア** | **不要**（どの GPU でも） | **DXR 対応の GPU**が、必要 |
| **ノイズ** | 中（粗い面） | **大**（粗い面は、レイが、散らばる） |
| **実装の、難しさ** | 中 | **高**（BVH、シェーダー テーブル、デノイズ） |

## RT 反射の、現実的な、使い方

**フルスクリーンの、RT 反射**は、**重い**ので、**工夫**して、使います。

| 工夫 | 内容 |
| --- | --- |
| **ハイブリッド** | **SSR で、取れる画素**は、**SSR**（安い）、**取れなかった画素**だけ、**RT**（[Hybrid Pipeline](hybrid.md)） |
| **反射が、強い**（つるつるの）面**だけ**、**RT** | **粗い面**や、**非金属**は、**反射プローブ**で、十分 |
| **半分の、解像度**で、RT | レイ数が、**1/4**。**アップサンプル**して、デノイズ |
| **レイの、最大距離**を、短く | **遠くは、プローブ**に、任せる |
| **ヒット シェーディングを、簡略化** | 当たった面は、**低品質なシェーディング**（影なし、**簡易ライティング**） |

''', before="## よくあるミス")
pg.Refs("reflections/rt-reflections/index.md", [DXR, STACHOWIAK18, BARRE, SCHIED, HEITZ])

pg.Dedup("reflections/rt-reflections/ray-generation.md")
pg.Add("reflections/rt-reflections/ray-generation.md", '''
## どの画素から、どの方向へ、レイを、飛ばすか

**RT 反射**の、最初の、仕事は、**反射する面の、各画素**から、**反射方向に、レイを、生成**することです。**DXR** では、**レイ生成シェーダー**（ray generation shader）が、これを、行います。

## 基本：鏡面の、反射

**粗さが、0**（完全な、鏡）なら、**反射方向**は、**1 つ**に、決まります。

```hlsl
// DXR のレイ生成シェーダー（鏡面）。G バッファから、位置と法線を読み、反射レイを飛ばす。
[shader("raygeneration")]
void ReflectionRayGen() {
  uint2 pixel = DispatchRaysIndex().xy;
  float3 position = g_gbuffer_position[pixel];
  float3 normal = g_gbuffer_normal[pixel];
  float3 view_dir = normalize(position - g_camera_position);          // カメラから、画素へ向かう向き
  float3 reflect_dir = reflect(view_dir, normal);                     // 反射方向

  RayDesc ray;
  ray.Origin = position + normal * 1e-3;                              // 面に、めり込まないように、少し離す
  ray.TMin = 0.0;
  ray.Direction = reflect_dir;
  ray.TMax = g_max_reflection_distance;                               // 遠くは、プローブに、任せる
  ReflectionPayload payload = (ReflectionPayload)0;
  TraceRay(g_scene, RAY_FLAG_NONE, 0xFF, 0, 1, 0, ray, payload);      // 反射レイを、飛ばす
  g_reflection_raw[pixel] = float4(payload.radiance, payload.hit_distance);
}
```

**始点を、法線方向に、少し離す**（`+ normal * 1e-3`）のは、**面自身に、当たる**（**自己交差**）のを、**避ける**ためです。**`TMax`** で、**レイの、最大距離**を、制限し、**遠くの、物**は、**反射プローブ**に、任せます。

## 粗い面：分布に従って、方向を、選ぶ

**粗さが、0 より、大きい**と、**反射は、1 方向でなく、広がり**ます（**反射ローブ**）。**レイを、ランダムな、方向**に、飛ばし、**反射ローブの、分布**に従って、**サンプル**します（[Monte Carlo Integration](../../gi/theory/monte-carlo.md)）。

| 方法 | 内容 |
| --- | --- |
| **GGX の、法線分布から、サンプル** | **法線の、ずれ**（ハーフ ベクトル `H`）を、GGX に従って選び、**`H` で、反射**。**標準** |
| **可視法線の、サンプリング**（Heitz、2018） | **視線から、見える、法線だけ**を、**サンプル**。**無駄な、サンプル**（**面の裏**）が、**減り**、**ノイズが、少ない** |

```hlsl
// GGX の、可視法線を、サンプルする（Heitz 2018）。Ve: ローカル座標（法線が +Z）での、視線。
float3 SampleGGXVNDF(float3 Ve, float alpha_x, float alpha_y, float u1, float u2) {
  float3 Vh = normalize(float3(alpha_x * Ve.x, alpha_y * Ve.y, Ve.z));      // 視線を、異方性の、スケールで、半球の形に、変換
  float lensq = Vh.x * Vh.x + Vh.y * Vh.y;
  float3 T1 = lensq > 0.0 ? float3(-Vh.y, Vh.x, 0.0) * rsqrt(lensq) : float3(1, 0, 0);
  float3 T2 = cross(Vh, T1);
  float r = sqrt(u1);
  float phi = 2.0 * 3.14159265 * u2;
  float t1 = r * cos(phi);
  float t2 = r * sin(phi);
  float s = 0.5 * (1.0 + Vh.z);
  t2 = (1.0 - s) * sqrt(1.0 - t1 * t1) + s * t2;                            // 視線の側に、偏らせる
  float3 Nh = t1 * T1 + t2 * T2 + sqrt(max(0.0, 1.0 - t1 * t1 - t2 * t2)) * Vh;
  return normalize(float3(alpha_x * Nh.x, alpha_y * Nh.y, max(0.0, Nh.z)));   // 元の空間に、戻す
}
```

**視線から、見える**法線だけを、**サンプル**するので、**反射方向が、面の下を、向く**（**無効な、サンプル**）ことが、**減ります**。**同じ、レイ数**で、**ノイズが、少なく**なります（Heitz、2018）。

```hlsl
// 粗さに応じた、反射レイ: 可視法線 H で、視線を、反射させる。
float3 V_local = WorldToLocal(-view_dir, normal);
float alpha = roughness * roughness;
float3 H_local = SampleGGXVNDF(V_local, alpha, alpha, u.x, u.y);
float3 H = LocalToWorld(H_local, normal);
float3 reflect_dir = reflect(view_dir, H);                                  // 法線を H にして、反射
if (dot(reflect_dir, normal) <= 0.0) { /* 面の下を向いた（まれ）: 無効にする */ }
```

**ガウスの、法線 `N`** の代わりに、**サンプルした、`H`** で、**視線を、反射**させます。**粗い面**ほど、**反射方向が、大きく、ばらつき**、**周りの、広い範囲**を、**サンプル**します。

## レイを、飛ばす、画素を、減らす

**すべての画素**から、レイを、飛ばすと、**重い**です。**反射が、見えない画素**は、**スキップ**します。

| 条件 | 判断 |
| --- | --- |
| **粗さが、高い**（0.7 以上） | **スキップ**（反射プローブに、任せる） |
| **反射率が、低い**（非金属で、フレネルが、小さい）、**視線が、垂直に近い** | **スキップ**（反射が、見えない） |
| **画面外、空**（深度が、最大） | **スキップ** |
| **SSR で、取れた**画素 | **スキップ**（ハイブリッド。[Hybrid Pipeline](hybrid.md)） |

```hlsl
// 反射が、ほぼ、見えない画素は、レイを、飛ばさない。
float reflectivity = lerp(0.04, 1.0, metallic) * (1.0 - roughness);          // 簡易な、反射の強さ
if (roughness > 0.7 || reflectivity < 0.02) { g_reflection_raw[pixel] = 0; return; }
```

## 解像度と、レイ数

| 設定 | 内容 | 品質 | コスト |
| --- | --- | --- | --- |
| **フル解像度、1 画素 1 レイ** | 最高 | 高 | **大** |
| **半分の、解像度、1 画素 1 レイ** | **1/4 の、レイ数**。アップサンプル | 中 | 中 |
| **フル解像度、粗さに応じて、レイ数を、変える**（つるつるは、1 本、粗いは、多め） | **バランス** | 中〜高 | 中 |

**レイの、方向**は、**ブルー ノイズ**で、選ぶ（**ノイズの、粒が、均一**で、デノイズが、効きやすい）。

''', before="## よくあるミス")
pg.Refs("reflections/rt-reflections/ray-generation.md", [HEITZ, WALTER, DXR, BARRE, STACHOWIAK18])

pg.Dedup("reflections/rt-reflections/hit-shading.md")
pg.Add("reflections/rt-reflections/hit-shading.md", '''
## レイが、当たった面の、色を、求める

**反射レイ**が、**三角形に、当たる**と、**その面の、色**（**反射として、返す光**）を、求める必要があります。**DXR** では、**ヒット シェーダー**（closest hit shader）が、これを、行います。

## 加速構造（BVH）

**レイが、どの三角形に、当たるか**を、**高速に、探す**ために、**シーンの、三角形**を、**加速構造**（**BVH**：Bounding Volume Hierarchy、境界ボリューム階層）に、**まとめます**。

| 階層 | 内容 |
| --- | --- |
| **BLAS**（Bottom-Level Acceleration Structure） | **1 つのメッシュ**の、三角形を、**BVH** に、まとめたもの |
| **TLAS**（Top-Level Acceleration Structure） | **BLAS の、インスタンス**（**位置・向き・大きさ**を、持った、メッシュの、配置）を、まとめたもの |

```text
TLAS（シーン全体）
 ├ インスタンス 1: 岩（BLAS A）  位置 (10, 0, 5)
 ├ インスタンス 2: 岩（BLAS A）  位置 (30, 0, 8)     ← 同じ BLAS を、複数回、使い回す
 ├ インスタンス 3: 木（BLAS B）  位置 (15, 0, 2)
 └ インスタンス 4: キャラクター（BLAS C）  位置 (…)  ← 動く物は、TLAS だけを、更新（BLAS は、アニメーションするなら、再構築）
```

| 更新 | コスト |
| --- | --- |
| **静的メッシュ** | **BLAS は、1 回だけ**作る |
| **動く物（剛体）** | **TLAS の、変換行列だけ**を、毎フレーム更新（**軽い**） |
| **スキニング、変形する物** | **BLAS を、更新**（refit）、または、**再構築**（**重い**） |
| **TLAS** | 毎フレーム**再構築**（インスタンスの数に、比例） |

## ヒット シェーダーの、流れ

**ヒット シェーダー**で、**当たった面の、色**を、**計算**します。

```hlsl
// 最も近い交点で、呼ばれる。当たった面の、属性（UV、法線、マテリアル）から、色を求める。
[shader("closesthit")]
void ReflectionClosestHit(inout ReflectionPayload payload, in BuiltInTriangleIntersectionAttributes attr) {
  // ① 当たった三角形の、頂点属性を、補間して、UV と法線を得る（重心座標 attr.barycentrics）。
  Vertex v = InterpolateVertex(InstanceID(), PrimitiveIndex(), attr.barycentrics);
  float3 hit_position = WorldRayOrigin() + WorldRayDirection() * RayTCurrent();
  float3 normal = normalize(mul(v.normal, (float3x3)ObjectToWorld3x4()));
```

**ヒット シェーダー**では、**画面の G バッファが、無い**（**画面外の、面**かもしれない）ので、**頂点バッファ**と、**インデックス バッファ**から、**当たった三角形の、属性**を、**自分で、補間**します（**重心座標**）。

```hlsl
  // ② マテリアルを、読む（アルベド、粗さなど）。テクスチャは、ミップを、手で選ぶ（レイは、画面の微分を、持たない）。
  Material m = g_materials[v.material_id];
  float mip = ComputeRayConeMip(payload.cone_width + RayTCurrent() * payload.cone_spread, v);   // レイ コーンから、ミップを決める
  float3 albedo = g_textures[m.albedo_index].SampleLevel(g_linear_wrap, v.uv, mip).rgb;
```

**ヒット シェーダーでは、画面の微分**（`ddx`、`ddy`）が、**使えません**。**ミップを、自分で、決める**必要が、あり、**レイ コーン**（レイが、進むほど、広がる、円錐の、幅）から、**ミップを、求めます**（**近似**）。

```hlsl
  // ③ ライティング: 直接光（太陽 + 影レイ）+ 間接光（簡易）。
  float3 radiance = 0.0;
  float3 L = -g_sun_dir;
  float n_dot_l = saturate(dot(normal, L));
  if (n_dot_l > 0.0 && !InShadow(hit_position + normal * 1e-3, L)) {                // 影レイ（別のレイ）
    radiance += albedo / 3.14159265 * g_sun_color * n_dot_l;
  }
  radiance += albedo * SampleAmbient(normal);                                       // 簡易な間接光（SH、プローブ）
  payload.radiance = radiance;
  payload.hit_distance = RayTCurrent();
}
```

**直接光**は、**影レイ**（**光の方向に、短いレイ**を、飛ばして、**遮られるか**）で、**影を、判定**します。**間接光**は、**簡易**（SH、ライト プローブ）にします（**反射の、反射**に、**フル GI**を、使うと、**重すぎる**）。

## コストを、減らす、工夫

**ヒット シェーダーが、重い**と、**RT 反射全体が、重く**なります。**当たる、面の、シェーディング**は、**簡略化**します。

| 工夫 | 内容 |
| --- | --- |
| **影を、省く**（または、**遠くだけ**） | **影レイを、飛ばさない**（**反射の中の、影は、見えにくい**）。**シャドウ マップ**で、代用 |
| **間接光を、簡易に** | **SH プローブ**、**環境光**。**フル GI は、使わない** |
| **ライティングを、キャッシュから** | **当たった面の、ライティング**を、**サーフェス キャッシュ**から、読む（[Lumen-Style Approaches](../../gi/rt-gi/lumen-style.md)） |
| **LOD** | **反射の中の、物**は、**低 LOD のメッシュ**で、**BVH を、作る**（三角形が、少ない） |
| **テクスチャの、ミップを、粗く** | **ミップ バイアス**で、**粗いテクスチャ**を、読む（**反射は、細かい模様**が、見えにくい） |
| **透過・アルファ テスト** | **アルファ テストの、メッシュ**は、**any hit シェーダー**が、必要（**重い**）。**反射では、アルファ テストを、省く**、または、**不透明として、扱う** |

## 反射の、反射（再帰）

**反射レイが、当たった面**が、**さらに、反射する**（**つるつる**）なら、**2 回目の、反射レイ**を、飛ばせます（**再帰**）。**反射の中の、反射**です。

| 再帰の、深さ | 内容 |
| --- | --- |
| **1**（反射なし） | 当たった面は、**拡散として、ライティング**。**最安** |
| **2** | **1 回の、反射の、反射**（鏡の部屋、向かい合う、窓）。**重い** |
| **3 以上** | 非常に、重い。**ほぼ、不要**（**2 回目以降は、暗く、見えにくい**） |

**実用**では、**再帰は、1〜2 回**に、**制限**し、**それ以降は、プローブ**や、**空の色**で、**打ち切り**ます。

''', before="## よくあるミス")
pg.Refs("reflections/rt-reflections/hit-shading.md", [DXR, BARRE, STACHOWIAK18, "Akenine-Möller, Nilsson, Andersson, Barré-Brisebois, Toth, Karis, \"Texture Level of Detail Strategies for Real-Time Ray Tracing\", Ray Tracing Gems, Chapter 20, 2019（レイ コーンによる、ミップの選択）"])

pg.Dedup("reflections/rt-reflections/hybrid.md")
pg.Add("reflections/rt-reflections/hybrid.md", '''
## ハイブリッド：SSR と、RT の、いいとこ取り

**フルスクリーンの、RT 反射**は、**重い**です。**SSR**は、**安い**が、**画面の外・隠れた面**は、**映せません**。**組み合わせ**ます。**SSR で、取れる画素**は、**SSR**（安い）、**取れなかった画素**だけ、**RT**（高い）で、**補います**（Stachowiak、2018、Barré-Brisebois ら、2019）。

```text
各画素:
   ① まず、SSR を、試す（画面空間の、レイマーチ）
        ↓ 当たった（信頼できる）→ SSR の結果を使う（RT は、不要）
        ↓ 当たらなかった / 信頼できない → ② RT を、飛ばす
```

## 利点

| 利点 | 内容 |
| --- | --- |
| **コストが、下がる** | **SSR で、取れる画素**（多くの、画面内の反射）は、**RT を、飛ばさない**。**RT の、レイ数が、大幅に、減る** |
| **画質が、高い** | **SSR が、取れない**（画面の外、隠れた面）部分は、**RT で、正確** |
| **近距離の、精度** | **SSR は、画面の、実際の、ジオメトリ**を、使うので、**近距離で、細かく、正確**（RT の、BVH は、**簡略化した、メッシュ**かもしれない） |

## 流れ（概略）

```hlsl
// ① SSR パス: 各画素で、SSR を試す。結果と、成否を、書き出す。
float4 ssr = TraceSSR(pixel);                                          // rgb = 色、a = 信頼度（0 = 失敗）
g_ssr_result[pixel] = ssr;

// ② RT パス: SSR が、失敗（信頼度が低い）した画素だけ、RT を飛ばす。
[shader("raygeneration")]
void HybridRayGen() {
  uint2 pixel = DispatchRaysIndex().xy;
  float4 ssr = g_ssr_result[pixel];
  if (ssr.a > 0.99) { g_final_reflection[pixel] = ssr.rgb; return; }   // SSR が、十分 → RT は、不要
  // ... 反射レイを、飛ばす（[Ray Generation]）...
  float3 rt = payload.radiance;
  g_final_reflection[pixel] = lerp(rt, ssr.rgb, ssr.a);                // 信頼度で、混ぜる（SSR が、一部、成功した画素）
}
```

**SSR の、信頼度が、十分に、高い**画素は、**RT を、飛ばしません**。**信頼度が、低い**（画面の端、物の裏、SSR が、外れた）画素だけ、**RT** を、**飛ばします**。**RT の、画素数**が、**画面の、数 %〜数十 %** に、減ります。

## DXR の、インライン レイトレーシング

**RT を、飛ばす、画素が、少ない**（疎）なら、**計算シェーダー**の、中から、**インライン**で、**レイを、飛ばす**（`RayQuery`）方法が、**効率的**です。**DXR 1.1** の、機能で、**レイ生成シェーダーの、ディスパッチ**（**シェーダー テーブル**）が、**不要**です。

```hlsl
// 計算シェーダーの中から、インラインで、レイを飛ばす（DXR 1.1 の RayQuery）。
[numthreads(8, 8, 1)]
void InlineRTCS(uint3 id : SV_DispatchThreadID) {
  if (g_ssr_result[id.xy].a > 0.99) return;                              // SSR が、十分な画素は、スキップ
  RayDesc ray = MakeReflectionRay(id.xy);
  RayQuery<RAY_FLAG_CULL_NON_OPAQUE | RAY_FLAG_ACCEPT_FIRST_HIT_AND_END_SEARCH> q;
  q.TraceRayInline(g_scene, RAY_FLAG_NONE, 0xFF, ray);
  q.Proceed();                                                           // BVH を辿る
  if (q.CommittedStatus() == COMMITTED_TRIANGLE_HIT) {
    // 当たった: 三角形の情報から、手で、シェーディング
  }
}
```

**`RayQuery`** は、**計算シェーダー・ピクセル シェーダー**から、**呼べます**。**画素を、絞って**、**シェーダー テーブルを、使わず**、**手軽**に、RT を、組み込めます。**ただし**、**当たった面の、マテリアルを、動的に、切り替える**（**シェーダー テーブル**の、利点）ことは、**自分で**、書く必要が、あります。

## SSR と RT の、継ぎ目

**SSR の画素**と、**RT の画素**が、**隣り合う**と、**色が、ずれて**、**境目が、見える**ことが、あります。

| 問題 | 対策 |
| --- | --- |
| **明るさ・色の、ずれ** | **SSR と RT の、ライティングを、そろえる**（同じ、**露出、環境光**） |
| **境目の、ギザギザ** | **信頼度を、なめらかに**変化させる（SSR の、フェード。[Color Lookup and Fading](../ssr-basics/color-fade.md)）、**RT の、重み**を、少しずつ増やす |
| **SSR の、細部と、RT の、粗さ** | RT の、**BVH が、簡略**（LOD、**細部が、無い**）だと、**SSR の、詳細な反射**と、**差**が、出る。**BVH の、LOD を、高めに** |

## 選択の、目安

| 状況 | 方式 |
| --- | --- |
| **コストを、最小**に | **SSR + 反射プローブ**（RT なし） |
| **品質と、コストの、バランス** | **ハイブリッド**（SSR + RT、SSR が、外れた、画素だけ） |
| **最高品質**（ハイエンド） | **フル RT**（全反射面で、RT） |

''', before="## よくあるミス")
pg.Refs("reflections/rt-reflections/hybrid.md", [STACHOWIAK18, BARRE, DXR, STACHOWIAK15, MCGUIRE])

pg.Dedup("reflections/rt-reflections/denoise.md")
pg.Add("reflections/rt-reflections/denoise.md", '''
## 反射の、ノイズ

**粗い面**の、RT 反射は、**1 画素 1 本の、レイ**を、**ランダムな、方向**に、飛ばすので、**ノイズだらけ**です。**GI の、デノイズ**（[Fighting Noise](../../gi/rt-gi/noise.md)）と、**似ています**が、**反射には、反射特有の、問題**が、あります。

| | GI（拡散の、間接光） | 反射（鏡面） |
| --- | --- | --- |
| **ノイズの、性質** | **低周波**（なめらかな、光） | **高周波**（反射する物の、細かい形が、見える） |
| **視点依存** | **無し** | **有り**（見る角度で、反射が、変わる） |
| **時間蓄積** | **画面上の、同じ点**を、再投影で、追える | **反射像は、画面上の、点とは、別の位置**に、動く（**視差**）。**再投影が、難しい** |
| **フィルタの、範囲** | **広く、ぼかしても、よい**（なめらか） | **広く、ぼかすと、反射の、形が、失われる**（鏡面は、くっきり） |

## 反射の、時間蓄積：反射像の、位置を、追う

**反射する面**（床）の、**画素**は、**カメラが、動かなくても**、**反射像**（映っている、物）が、**動けば、変わります**。**普通の再投影**（**面の位置**を、再投影）は、**面の、色**には、**正しい**ですが、**反射像**は、**面より、奥**に、**映っている**ので、**ずれて**、**反射が、ぼやけます**。

```text
カメラが、右に、動く:
   床の点 P は、画面上で、左へ動く（面の動き）
   P に映る、反射像（遠い物）は、画面上で、もっと、少ししか、動かない（遠いので）
   → P の位置で、再投影すると、反射像が、ずれて、ぼやける（ゴースト）
```

### 反射像の、位置を、再投影する

**反射像が、当たった**、**ヒット位置**（**反射の、中の、物の位置**）を、**再投影**します。**ヒット位置の、前フレームでの、画面位置**で、**履歴を、読みます**。

```hlsl
// 反射の、ヒット位置（ワールド）を、前フレームの画面へ投影して、反射像の、履歴を読む。
float3 hit_world = position + reflect_dir * hit_distance;                    // 反射レイが、当たった位置
float4 prev_clip = mul(float4(hit_world, 1.0), g_prev_view_proj);
float2 prev_uv = prev_clip.xy / prev_clip.w * float2(0.5, -0.5) + 0.5;
float4 history = g_reflection_history.SampleLevel(g_linear_clamp, prev_uv, 0);
```

**鏡面の**、**反射像**は、**「ヒット位置」**が、**画面上で、どこに動くか**で、**追えます**（**仮想的な、鏡像の、位置**を、追う、考え方）。**面の位置で、再投影**するより、**反射像が、ずれません**。

**粗い面**（反射が、ぼやけている）では、**面の位置での、再投影**でも、**あまり、目立たない**（**ぼけて、いるので**）。**粗さに応じて**、**2 つの再投影を、混ぜる**方法も、あります。

## 空間フィルタ

**時間蓄積の、後**、**まだ、残る、ノイズ**を、**空間フィルタ**で、**ぼかします**。**GI の、デノイザー**と、同じ、**エッジを、保つ、フィルタ**（À-Trous など）を、使いますが、**反射の、特徴**に、合わせます。

| 工夫 | 内容 |
| --- | --- |
| **粗さに、比例した、フィルタ半径** | **粗い面**は、**広く**ぼかす、**つるつるの面**は、**ほとんど**ぼかさない（**ぼかすと、反射が、失われる**） |
| **ヒット距離を、考慮** | **反射の、ヒット位置が、遠い**ほど、**ぼけが、大きい**（反射の、円錐が、広がる）。**ヒット距離に応じて**、**フィルタ半径を、変える** |
| **法線・深度で、エッジを、保つ** | GI と同じ。**別の面**を、**またいで、混ぜない** |
| **ヒット位置で、エッジを、保つ** | **反射像の、境目**（別の物が、映っている）を、**越えない** |

```hlsl
// フィルタ半径を、粗さとヒット距離から決める。つるつる・近い反射は、ほとんど、ぼかさない。
float radius = g_max_filter_radius * saturate(roughness * 2.0) * saturate(hit_distance / g_blur_distance);
```

## ノイズを、減らす、入力側の、工夫

| 工夫 | 内容 |
| --- | --- |
| **可視法線の、サンプリング**（Heitz、2018） | **無駄な、サンプルを、減らし**、**ノイズが、少ない**（[Ray Generation](ray-generation.md)） |
| **ブルー ノイズ** | **ノイズの、粒が、均一**で、**フィルタが、効きやすい** |
| **明るさの、クランプ** | **ファイアフライ**（太陽を、拾った、白い点）を、**抑える** |
| **粗さに、応じた、ミップ** | **反射先**の、テクスチャを、**粗いミップ**で、読む（**高周波を、減らす**） |
| **複数レイ**（粗い面） | **粗さが、大きい**画素は、**レイを、増やす** |

## 専用の、デノイザーを、使う

**デノイザーを、自作**するのは、**大変**です。**ライブラリ**が、あります。

| ライブラリ | 内容 |
| --- | --- |
| **NVIDIA Real-Time Denoisers**（NRD） | **反射・拡散・影**の、**リアルタイム デノイザー**。**ReBLUR、ReLAX** など |
| **AMD FidelityFX Denoiser** | **反射・影**の、デノイザー |
| **Intel Open Image Denoise** | **オフライン向け**の、**高品質デノイザー**（ニューラル ネット）。リアルタイムには、重い |

**反射と、拡散**を、**別々に**、**デノイズ**するのが、**一般的**です（**性質が、違う**ため。[Diffuse and Specular](../../gi/theory/diffuse-specular.md)）。

## 限界

| 問題 | 内容 |
| --- | --- |
| **ぼやけ** | **強くフィルタ**すると、**鏡面反射の、細部が、失われる** |
| **ゴースト** | **時間蓄積**で、**動く物の、反射**が、**残像**を、引く |
| **ちらつき** | **粗い面**で、**デノイザーの、判断が、揺れる** |
| **つるつるの面** | **ほぼ、ノイズが、ない**ので、**デノイズ不要**（**ぼかさない**） |

''', before="## よくあるミス")
pg.Refs("reflections/rt-reflections/denoise.md", [SCHIED, HEITZ, STACHOWIAK18, BARRE, "NVIDIA, \"Real-Time Denoisers (NRD)\"（公開ライブラリ、GitHub: NVIDIAGameWorks/RayTracingDenoiser）"])

# ================================================================ refs for the large pages
pg.Refs("reflections/planar.md", [MITTRING, RTR, "Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, \"Real-Time Rendering\", 4th Edition, CRC Press, 2018（斜めクリップ面）"])
pg.Refs("reflections/ssr-fallback.md", [STACHOWIAK15, VALIENT, LAGARDE, MCGUIRE])
pg.Refs("reflections/ssr-hiz.md", [ULUDAG, MCGUIRE, STACHOWIAK15, "Tevs, Ihrke, Seidel, \"Maximum Mipmaps for Fast, Accurate, and Scalable Dynamic Height Field Rendering\", Symposium on Interactive 3D Graphics and Games 2008（最大ミップマップによる、高速なレイ交差）"])
pg.Refs("reflections/ssr-stochastic.md", [STACHOWIAK15, HEITZ, WALTER, SCHIED])
pg.Refs("reflections/comparison.md", [MCGUIRE, STACHOWIAK15, LAGARDE, BARRE, RTR])
pg.Refs("reflections/index.md", [KARIS, LAGARDE, MCGUIRE, STACHOWIAK15, BARRE])
print("ok")
