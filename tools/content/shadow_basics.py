import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import pg  # noqa: E402

WILLIAMS = '''Williams, "Casting Curved Shadows on Curved Surfaces", SIGGRAPH 1978（シャドウ マップの原典）'''
REEVES = '''Reeves, Salesin, Cook, "Rendering Antialiased Shadows with Depth Maps", SIGGRAPH 1987（PCF の原典）'''
BRABEC = '''Brabec, Annen, Seidel, "Practical Shadow Mapping", Journal of Graphics Tools, Vol. 7, No. 4, 2002'''
ISIDORO = '''Isidoro, "Shadow Mapping: GPU-based Tips and Techniques", Game Developers Conference 2006（レシーバー平面の深度バイアスなど）'''
DIMITROV = '''Dimitrov, "Cascaded Shadow Maps", NVIDIA White Paper, 2007'''
VALIENT = '''Valient, "Stable Rendering of Cascaded Shadow Maps", ShaderX6, 2008（テクセル スナップによる安定化）'''
MS_SHADOW = '''Microsoft Learn, "Common Techniques to Improve Shadow Depth Maps"（Direct3D 11 のドキュメント。バイアス、平行光源、PCF）'''
D3D11_RS = '''Microsoft Learn, "D3D11_RASTERIZER_DESC"（`DepthBias`、`SlopeScaledDepthBias`、`DepthBiasClamp`）'''
D3D11_SAMPLER = '''Microsoft Learn, "D3D11_SAMPLER_DESC"（`D3D11_FILTER_COMPARISON_*`、`ComparisonFunc`）'''
RTR = '''Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（影の章）'''
FERNANDO = '''Fernando, "Percentage-Closer Soft Shadows", SIGGRAPH 2005 Sketches'''
BLINN = '''Blinn, "Me and My (Fake) Shadow", IEEE Computer Graphics and Applications, Vol. 8, No. 1, 1988（平面への、投影影）'''

# ================================================================ shadow-map-basics
pg.Dedup("shadows/shadow-map-basics/index.md")
pg.Add("shadows/shadow-map-basics/index.md", '''
## シャドウ マップの、考え方

**「光から見えない所が、影」** という、単純な、考え方から、シャドウ マップは、できています（Williams、1978）。

1. **光の位置**に、カメラを置いて、シーンを描き、**光から、一番近い物までの、距離（深度）**を、テクスチャに、保存する（**シャドウ マップ**）
2. 普通に、カメラから、シーンを描くとき、**画素ごとに**、「この点を、**光から見たら**、どこに映り、**光からの距離**は、いくつか」を、求める
3. その距離が、シャドウ マップに、保存された**深度より、遠い**なら、**光との間に、別の物がある**（影の中）。**ほぼ同じ**なら、**光が、当たる**

```text
光 ●────────●────────●
        遮蔽物      地面
        深度 5      深度 10   ← シャドウ マップには、深度 5（遮蔽物）が保存されている
地面の点を、光から見ると、深度 10。保存された 5 より、遠い → 影の中
```

## 全体の、流れ

| 段階 | 内容 | 描くもの |
| --- | --- | --- |
| ① シャドウ パス | 光の視点で、**深度だけ**を、描く | シャドウ マップ（深度テクスチャ） |
| ② メイン パス | カメラの視点で、描く。**各画素で**、光の座標系に、変換して、シャドウ マップを、比べる | 最終の色 |

①は、**色を、計算しない**ので、**非常に軽く**（深度だけ）、②では、**1 画素あたり、テクスチャ読み込み 1 回（比較つき）**が、増えます。

## 光の種類ごとの、カメラ

| 光 | 光の視点の、射影 | シャドウ マップの数 |
| --- | --- | --- |
| 平行光源（太陽） | **正射影**（平行投影） | 1 枚（広い場所では、複数。[CSM](../cascaded.md)） |
| スポットライト | **透視投影**（円錐の、開き角が、視野角） | 1 枚 |
| 点光源 | 全方向。**6 面のキューブマップ**（各面が、90° の透視投影） | 6 枚 |

## シャドウ マップの、課題

シャドウ マップは、**解像度に、限りのある、深度の画像**です。そのため、次の、問題が、避けられません。

| 問題 | 原因 | 対策 |
| --- | --- | --- |
| **影の、ジャギー**（階段状の、縁） | 解像度が、足りない（シャドウ マップの 1 画素が、画面の複数画素に、拡大） | フィルタリング（[PCF](../pcf.md)）、解像度を、上げる、カスケード |
| **シャドウ アクネ**（縞模様の、自己影） | 深度の、精度の誤差と、斜めの面で、自分自身を、遮蔽 | **バイアス**（[Shadow Bias](../bias/index.md)） |
| **ピーター パンニング**（影が、物から、浮く） | バイアスが、大きすぎる | バイアスを、適切に、小さく、法線オフセット |
| **影が、ちらつく**（カメラの動きで） | シャドウ マップの、画素の位置が、フレームごとに、ずれる | **テクセル スナップ**（[Aliasing and Stabilization](aliasing-stabilize.md)） |
| 遠くで、解像度が、足りない | 太陽の、シャドウ マップが、広い範囲を、覆う | **カスケード**（[CSM](../cascaded.md)） |
| 影の縁が、硬い | 点光源の、仮定 | [PCSS](../pcss.md)、[VSM](../vsm/index.md) |

## 実装の、順序

シャドウ マップは、次の、順で、作ります。

1. [Rendering Depth](render-depth.md)：光の視点で、深度を、描く
2. [The Light Matrix](light-matrix.md)：光の、ビュー・射影行列を、作る
3. [Comparison Samplers](comparison-sampler.md)：シャドウ マップを、読み、比較する
4. [Shadow Bias](../bias/index.md)：自己影を、防ぐ
5. [Aliasing and Stabilization](aliasing-stabilize.md)：ちらつきを、抑える
6. [PCF](../pcf.md)：縁を、なめらかにする

[Minimal Code](minimal-code.md) に、全体を、通した、最小の、コードが、あります。

''', before="## よくあるミス")
pg.Refs("shadows/shadow-map-basics/index.md", [WILLIAMS, BRABEC, MS_SHADOW, RTR])

pg.Dedup("shadows/shadow-map-basics/render-depth.md")
pg.Add("shadows/shadow-map-basics/render-depth.md", '''
## 深度テクスチャを、作る

シャドウ マップは、**深度だけ**を、保存する、テクスチャです。DirectX 11 では、**同じテクスチャ**を、**深度ステンシル ビュー（DSV）**として、**書き込み**、**シェーダー リソース ビュー（SRV）**として、**読み取り**ます。そのため、テクスチャの形式を、**TYPELESS（型なし）**で作り、**ビューごとに、形式を、指定**します。

```cpp
// シャドウ マップ: 2048×2048、32 ビット浮動小数点の深度。
D3D11_TEXTURE2D_DESC desc = {};
desc.Width = 2048;
desc.Height = 2048;
desc.MipLevels = 1;
desc.ArraySize = 1;
desc.Format = DXGI_FORMAT_R32_TYPELESS;                         // 型なし（ビューで、型を決める）
desc.SampleDesc.Count = 1;
desc.Usage = D3D11_USAGE_DEFAULT;
desc.BindFlags = D3D11_BIND_DEPTH_STENCIL | D3D11_BIND_SHADER_RESOURCE;
device->CreateTexture2D(&desc, nullptr, &shadow_map_tex);

// 書き込み用（シャドウ パスで使う）
D3D11_DEPTH_STENCIL_VIEW_DESC dsv = {};
dsv.Format = DXGI_FORMAT_D32_FLOAT;
dsv.ViewDimension = D3D11_DSV_DIMENSION_TEXTURE2D;
device->CreateDepthStencilView(shadow_map_tex.Get(), &dsv, &shadow_dsv);

// 読み取り用（メイン パスで使う）
D3D11_SHADER_RESOURCE_VIEW_DESC srv = {};
srv.Format = DXGI_FORMAT_R32_FLOAT;
srv.ViewDimension = D3D11_SRV_DIMENSION_TEXTURE2D;
srv.Texture2D.MipLevels = 1;
device->CreateShaderResourceView(shadow_map_tex.Get(), &srv, &shadow_srv);
```

| 形式 | 精度 | メモリ（2048²） | 使いどころ |
| --- | --- | --- | --- |
| `D32_FLOAT` | 32 ビット浮動小数点 | 16 MB | 標準。精度が、高い |
| `D24_UNORM_S8_UINT` | 24 ビット固定小数点 + ステンシル | 16 MB | ステンシルが、必要なとき |
| `D16_UNORM` | 16 ビット | 8 MB | メモリを、節約したい。**精度が、低く、バイアスが、大きくなる** |

## シャドウ パスの、描画

光の視点で、**カメラの代わりに、光の、ビュー・射影行列**を、使って、**影を、落とす物**を、描きます。色は、**書き込まない**ので、**ピクセル シェーダーも、不要**（アルファ テストする物を、除く）です。

```cpp
// ① 書き込み先を、シャドウ マップだけにする（レンダー ターゲットは、なし）。
context->OMSetRenderTargets(0, nullptr, shadow_dsv.Get());
context->ClearDepthStencilView(shadow_dsv.Get(), D3D11_CLEAR_DEPTH, 1.0f, 0);

// ② ビューポートを、シャドウ マップの大きさに。
D3D11_VIEWPORT vp = {0, 0, 2048, 2048, 0.0f, 1.0f};
context->RSSetViewports(1, &vp);

// ③ 頂点シェーダーだけ（ピクセル シェーダーは、なし）。
context->VSSetShader(shadow_vs.Get(), nullptr, 0);
context->PSSetShader(nullptr, nullptr, 0);                    // 深度だけなので、ピクセル シェーダーは、無し

// ④ 光の行列を、定数バッファに入れて、影を落とす物を、描く。
UpdateLightCB(light_view_proj);
DrawShadowCasters();
```

```hlsl
// シャドウ パスの、頂点シェーダー: 光の行列で、頂点を、変換するだけ。
cbuffer LightCB : register(b0) { float4x4 g_light_view_proj; };
cbuffer ObjectCB : register(b1) { float4x4 g_world; };

float4 main(float3 position : POSITION) : SV_Position {
  return mul(mul(float4(position, 1.0), g_world), g_light_view_proj);
}
```

**ピクセル シェーダーを、無し**にすると、GPU は、**深度書き込みだけ**を、高速に、行います（多くの GPU が、通常の、2 倍以上の、速さ）。

## 描く物を、絞る

シャドウ パスは、**物を、もう一度、描く**ので、**描画コストが、増えます**。減らす工夫です。

| 工夫 | 内容 |
| --- | --- |
| **影を落とさない物を、除く** | 小さな物、遠くの物、影が、目立たない物を、シャドウ パスから、外す |
| **光の視錐台で、カリング** | 光の、視錐台の外にある物は、描かない（カメラの視錐台とは、別） |
| **LOD** | シャドウ パスでは、**粗い LOD** を、使う（影は、細部が、見えない） |
| **静的な物の、キャッシュ** | 動かない物の、シャドウ マップを、保存し、**動く物だけ**を、毎フレーム、描き足す（[Shadows for Many Lights](../local-lights/many-lights.md)） |
| **更新の、間引き** | 遠くのカスケードは、**数フレームに、1 回**だけ、更新する（[CSM](../cascaded.md)） |

## 表裏の、カリング

シャドウ パスで、**どの面を、描くか**（表面か、裏面か）が、**バイアスの問題**に、関わります。

| 描く面 | 内容 |
| --- | --- |
| **表面**（通常） | 光に、向いた面の、深度が、保存される。**自己影が、出やすい**（地面の、表面と、同じ面を、比べるため） |
| **裏面**（表面を、カリング） | 光から、**遠い側の面**の、深度が、保存される。表面との間に、**厚み（物の、厚さ）**が、できて、**バイアスが、不要**に近い。ただし、**薄い物**（板）では、影が、欠ける（[Front-Face Culling](../bias/front-face-culling.md)） |

```cpp
// 裏面を描く: 表面をカリング。
D3D11_RASTERIZER_DESC rs = {};
rs.FillMode = D3D11_FILL_SOLID;
rs.CullMode = D3D11_CULL_FRONT;                  // 光に向いた面を、描かない（このサイトでは、反時計回りが表）
rs.FrontCounterClockwise = TRUE;
rs.DepthClipEnable = TRUE;
```

## 射影の、種類と、深度の、精度

| 光 | 射影 | 深度の分布 |
| --- | --- | --- |
| 平行光源（正射影） | 正射影 | **深度は、線形**（近くから、遠くまで、一定の精度）。バイアスが、扱いやすい |
| スポット、点光源（透視） | 透視投影 | **深度は、非線形**（近くで、精度が高く、遠くで、粗い）。バイアスを、距離で、変える必要 |

透視投影の、シャドウ マップでは、**ニア面を、できるだけ、遠く**に置いて、深度の、精度を、保ちます（ニア面が、近すぎると、遠くの、精度が、落ちる）。

''', before="## よくあるミス")
pg.Refs("shadows/shadow-map-basics/render-depth.md", [WILLIAMS, MS_SHADOW, D3D11_RS, RTR])

pg.Dedup("shadows/shadow-map-basics/light-matrix.md")
pg.Add("shadows/shadow-map-basics/light-matrix.md", '''
## 光の行列：ビューと射影

シャドウ マップを、描くには、**光の視点**から、見た、**ビュー行列**と、**射影行列**が、必要です。**メインの、カメラ**の行列と、**同じ**考え方で、作ります。このサイトの、座標系は、**右手系・Y 上・行ベクトル（`v * M`）**です（[座標系](../../../3d/index.md)）。

```text
ワールド座標 → [ビュー行列] → 光の視点の座標 → [射影行列] → 光のクリップ空間 → シャドウ マップの UV と深度
```

## 平行光源（太陽）：正射影

太陽の光は、**平行**なので、**正射影**（遠近感なし）で、描きます。

### ビュー行列

光の**向き**だけが、重要で、**位置**は、**影を、落とす範囲の、中心**から、光の逆向きに、離れた所に、置きます。

```cpp
using namespace DirectX::SimpleMath;

// 太陽の方向（光が進む向き）。例: 斜め下へ。
Vector3 light_dir = Vector3(-0.4f, -1.0f, -0.3f);
light_dir.Normalize();

// 影を落とす範囲の、中心（たとえば、カメラの視錐台の、中心）と、半径。
Vector3 center = frustum_center;
float radius = frustum_radius;

// 光の位置: 中心から、光の来る側（光の進む向きの、逆）へ、radius だけ、下がる。
Vector3 eye = center - light_dir * radius;

// 上向きは、光の方向と、平行にならないものを選ぶ。
Vector3 up = (std::abs(light_dir.y) > 0.99f) ? Vector3::UnitZ : Vector3::UnitY;
Matrix light_view = Matrix::CreateLookAt(eye, center, up);       // 右手系
```

### 射影行列

**影を落とす範囲を、ちょうど、覆う**、**箱（正射影の、ボリューム）**を、作ります。

```cpp
// 正射影: 左、右、下、上、ニア、ファー（光のビュー空間で）。右手系の、オフ センター版。
float near_z = 0.0f;
float far_z = 2.0f * radius;
Matrix light_proj = Matrix::CreateOrthographicOffCenter(
    -radius, radius, -radius, radius, near_z, far_z);              // SimpleMath（右手系）

Matrix light_view_proj = light_view * light_proj;                  // 行ベクトルなので、左から右（ビュー → 射影）
```

| パラメーター | 内容 |
| --- | --- |
| `radius` | 影の範囲の、半径。**小さい**ほど、シャドウ マップの、解像度が、**有効**に使われる。**大きい**と、広く覆えるが、ぼやける |
| `near_z`、`far_z` | **光の方向の、奥行き範囲**。**影を落とす物が、すべて含まれる**ように、広めに取る |

**影を落とす物が、範囲の外**（光の、さらに手前、たとえば、高い山）に、あると、**影が、欠けます**。ニアを、手前に、延ばすか、**光の、後ろにある、物の深度を、クランプ**します（**深度クランプ**、`DepthClipEnable = FALSE`）。

## スポットライト：透視投影

スポットライトは、**円錐状**に、光を出すので、**透視投影**で、描きます。**円錐の、開き角**が、**視野角**です。

```cpp
Vector3 position = spot.position;
Vector3 target = spot.position + spot.direction;
Matrix light_view = Matrix::CreateLookAt(position, target, Vector3::UnitY);

float fov = 2.0f * spot.outer_angle;                              // 開き角（ラジアン）
float aspect = 1.0f;                                              // シャドウ マップは、正方形
Matrix light_proj = Matrix::CreatePerspectiveFieldOfView(fov, aspect, spot.near_z, spot.range);
Matrix light_view_proj = light_view * light_proj;
```

視野角は、**170° 未満**に、します（180° に、近づくと、透視投影が、破綻する）。

## メイン パスで：ワールドから、シャドウ マップの座標へ

メインの、描画で、各画素の、**ワールド座標**を、**光の行列**で、変換し、**シャドウ マップの UV と、深度**を、求めます。

```hlsl
cbuffer ShadowCB : register(b2) { float4x4 g_light_view_proj; };
Texture2D<float> g_shadow_map : register(t5);
SamplerComparisonState g_shadow_sampler : register(s5);

float ShadowFactor(float3 world_pos) {
  // ① 光のクリップ空間へ
  float4 light_clip = mul(float4(world_pos, 1.0), g_light_view_proj);
  float3 ndc = light_clip.xyz / light_clip.w;                    // 正射影では w = 1

  // ② NDC（-1〜1、y は上が +）を、テクスチャ UV（0〜1、v は下が +）へ
  float2 uv = ndc.xy * float2(0.5, -0.5) + 0.5;

  // ③ 範囲外は、影なし
  if (any(uv < 0.0) || any(uv > 1.0) || ndc.z > 1.0) return 1.0;

  // ④ 深度を比較して、影の中なら 0、光が当たるなら 1
  return g_shadow_map.SampleCmpLevelZero(g_shadow_sampler, uv, ndc.z);
}
```

**v を反転**（`-0.5`）するのは、**NDC の y は、上が正**で、**テクスチャの v は、下が正**だからです。この反転を、忘れると、**影が、上下に、逆転**します。

### 変換を、1 つの行列に、まとめる

**NDC から UV への、変換**（`* 0.5 + 0.5`、y の反転）も、**行列**にして、光の行列と、**掛けておく**と、シェーダーが、簡単になります。

```cpp
// NDC (-1..1) → UV (0..1)、y 反転。行ベクトル用。
Matrix ndc_to_uv(0.5f, 0.0f, 0.0f, 0.0f,
                 0.0f, -0.5f, 0.0f, 0.0f,
                 0.0f, 0.0f, 1.0f, 0.0f,
                 0.5f, 0.5f, 0.0f, 1.0f);
Matrix shadow_matrix = light_view * light_proj * ndc_to_uv;        // ワールド → シャドウ マップの UV + 深度
```

```hlsl
float4 shadow_pos = mul(float4(world_pos, 1.0), g_shadow_matrix);
float3 shadow_coord = shadow_pos.xyz / shadow_pos.w;                // xy = UV、z = 深度
float lit = g_shadow_map.SampleCmpLevelZero(g_shadow_sampler, shadow_coord.xy, shadow_coord.z);
```

## 視錐台に、ぴったり合わせる

太陽の、`radius` を、**メインの、カメラの視錐台**に、**合わせて**、**毎フレーム、計算**すると、**無駄なく**、解像度を、使えます。ただし、**カメラが、動くたびに、範囲が、変わり**、**影が、ちらつきます**（[Aliasing and Stabilization](aliasing-stabilize.md)）。**カスケード**では、**視錐台を、分割**して、それぞれに、合わせた、行列を、作ります（[CSM](../cascaded.md)）。

''', before="## よくあるミス")
pg.Refs("shadows/shadow-map-basics/light-matrix.md", [WILLIAMS, MS_SHADOW, DIMITROV, RTR])

pg.Dedup("shadows/shadow-map-basics/comparison-sampler.md")
pg.Add("shadows/shadow-map-basics/comparison-sampler.md", '''
## 比較サンプラーとは

影の判定は、**「シャドウ マップの深度」と、「画素の、光からの深度」を、比較**する作業です。この比較を、**ハードウェアが、やってくれる**のが、**比較サンプラー**です。**さらに**、**4 つの隣の画素**で、比較して、**結果を、バイリニア補間**してくれる（**2×2 の PCF が、ただで、できる**）ため、**シャドウ マップの、読み取りは、比較サンプラー**を使うのが、定番です。

## 比較サンプラーの、作り方

```cpp
D3D11_SAMPLER_DESC desc = {};
desc.Filter = D3D11_FILTER_COMPARISON_MIN_MAG_LINEAR_MIP_POINT;   // 比較 + 線形補間（2×2 PCF）
desc.AddressU = D3D11_TEXTURE_ADDRESS_BORDER;                     // 範囲外は、境界色
desc.AddressV = D3D11_TEXTURE_ADDRESS_BORDER;
desc.AddressW = D3D11_TEXTURE_ADDRESS_BORDER;
desc.BorderColor[0] = 1.0f;                                       // 範囲外の深度 = 1.0（最も遠い）→ 影なし
desc.BorderColor[1] = 1.0f;
desc.BorderColor[2] = 1.0f;
desc.BorderColor[3] = 1.0f;
desc.ComparisonFunc = D3D11_COMPARISON_LESS_EQUAL;                // 画素の深度 <= 保存された深度 → 光が当たる
desc.MaxLOD = D3D11_FLOAT32_MAX;
device->CreateSamplerState(&desc, &shadow_sampler);
```

| 設定 | 内容 |
| --- | --- |
| `Filter` | `COMPARISON_` で始まるものを、選ぶ。`MIN_MAG_LINEAR_MIP_POINT` なら、**比較した結果を、バイリニアで、補間**（影の縁が、なめらか）。`MIN_MAG_MIP_POINT` なら、補間なし（硬い縁） |
| `ComparisonFunc` | `LESS_EQUAL`：**参照値（画素の深度）が、テクスチャの値**以下なら、**1**（光が当たる）。**通常の、深度**（小さいほど、近い）で、使う |
| `AddressU/V` | `BORDER`：範囲外は、`BorderColor`。**1.0**にすると、範囲外は、**影にならない** |

## シェーダーでの、使い方

比較サンプラーは、HLSL では、**`SamplerComparisonState`** 型で、受け、**`SampleCmp`** または、**`SampleCmpLevelZero`** で、読みます。

```hlsl
Texture2D<float> g_shadow_map : register(t5);
SamplerComparisonState g_shadow_sampler : register(s5);

// 戻り値: 0（影の中）〜 1（光が当たる）。2×2 の結果が、補間されて、0〜1 の中間値になる。
float lit = g_shadow_map.SampleCmpLevelZero(g_shadow_sampler, shadow_uv, shadow_depth);
```

| 関数 | 内容 |
| --- | --- |
| `SampleCmp` | **ミップ レベルを、自動で選ぶ**（画面の微分を使う）。分岐の中では、使えない（微分が、不定になる） |
| `SampleCmpLevelZero` | **ミップ 0 を、使う**。**分岐の中でも、使える**。**シャドウ マップは、ミップを持たない**ので、**これが標準** |

## 比較の、意味

```text
SampleCmpLevelZero(map, uv, ref):
   mapの、(uv の周りの 4 画素)  それぞれについて
      ref <= map値  なら 1、そうでなければ 0
   その 4 つの結果を、uv の小数部で、バイリニア補間
```

**重要**：**深度を、補間してから、比較**するのではなく、**比較してから、補間**します。**深度を、先に補間**すると、**遮蔽物の、縁**で、**存在しない、中間の深度**が、できて、**間違った影**になります。**比較してから、補間**するのが、**PCF の、正しい手順**で、ハードウェアが、**それを行います**（[PCF](../pcf.md)）。

### 手動で、比較する場合（比較サンプラーが、使えない）

```hlsl
// 通常のサンプラーで、深度を、読んで、手で比較する（補間なし。ハードの PCF は、無い）。
float stored = g_shadow_map.SampleLevel(g_point_clamp, shadow_uv, 0);
float lit = (shadow_depth <= stored) ? 1.0 : 0.0;
```

比較サンプラーが、**使えない場面**（VSM や、ESM のように、**深度そのものを、使う**場合、**深度の、別の形式**）では、この方法に、なります（[VSM, ESM and MSM](../vsm/index.md)）。

## 使うべき理由

| | 手動の比較 | 比較サンプラー |
| --- | --- | --- |
| 速さ | 4 回読む場合は、**4 回の、テクスチャ読み込み** | **ハードウェアが、1 回**で、2×2 を、処理 |
| 縁のなめらかさ | 自分で、実装 | **標準で、2×2 の、バイリニア PCF** |
| コード | 長い | **1 行** |

## 注意点

| 項目 | 内容 |
| --- | --- |
| 深度の向き | **reversed-Z**（遠いほど、小さい）を、使っているなら、`ComparisonFunc` を、`GREATER_EQUAL` にする |
| 形式 | シャドウ マップの、SRV は、`R32_FLOAT`（または `R24_UNORM_X8_TYPELESS`）。比較サンプラーで、読める |
| ミップ | シャドウ マップは、**ミップを、作らない**（深度の、平均は、意味がない） |
| テクスチャ配列 | カスケードを、**配列**にするなら、`Texture2DArray` と、`float3(uv, slice)` で読む |

''', before="## よくあるミス")
pg.Refs("shadows/shadow-map-basics/comparison-sampler.md", [REEVES, D3D11_SAMPLER, MS_SHADOW, RTR])

pg.Dedup("shadows/shadow-map-basics/aliasing-stabilize.md")
pg.Add("shadows/shadow-map-basics/aliasing-stabilize.md", '''
## エイリアシングの、2 つの種類

シャドウ マップの、エイリアシング（ギザギザ、ちらつき）には、**性質の違う、2 つ**が、あります。

| 種類 | 原因 | 見た目 |
| --- | --- | --- |
| **透視エイリアシング** | シャドウ マップの 1 画素が、**画面上で、大きく**拡大される（カメラの、近くで、画素が、粗い） | 影の縁が、**カクカクした、階段** |
| **射影エイリアシング** | 光に対して、**面が、斜め**（光と、ほぼ平行な、面）で、シャドウ マップの 1 画素が、面の上で、**細長く、引き伸ばされる** | 斜面の影が、**縞模様** |

**透視エイリアシング**は、**解像度を、上げる**、**カスケードを、使う**、**フィルタリング**（[PCF](../pcf.md)）で、軽減します。**射影エイリアシング**は、**バイアスで**、**隠す**（[Shadow Bias](../bias/index.md)）か、**法線オフセット**で、軽減します。

## シャドウの、ちらつき（スイミング）

カメラが、動くと、**影の縁が、ちらちら**動く（泳ぐ）ことがあります。原因は、**シャドウ マップの、画素の位置が、カメラの動きに、つれて、フレームごとに、ずれる**ことです。

```text
フレーム N:    シャドウ マップの画素:  | | | | | |     ← 影の縁は、この画素の、どれかに、落ちる
フレーム N+1:  カメラが、少し動くと、画素が、ずれる: |  |  |  |  ← 縁が、別の画素に落ちて、影が、ぴくぴく動く
```

太陽の、**シャドウ マップの範囲**を、**カメラの視錐台に、合わせて**、毎フレーム、作り直すと、**範囲の位置と、大きさが、連続的に、変わり**、**画素の、境界が、ワールド上で、動きます**。**影が、そのたびに、わずかに、ずれて**見えます。

## 対策 1：範囲の、大きさを、固定する（回転に、強くする）

視錐台に、**ぴったり**合う箱は、カメラが、**回転**すると、**大きさが、変わり**ます。**視錐台を、囲む球**（**バウンディング スフィア**）に、合わせて、箱を作ると、**カメラが回転しても、大きさが、変わりません**。

```cpp
// 視錐台の 8 つの頂点から、バウンディング スフィアを求める（簡易）。
Vector3 center = Vector3::Zero;
for (const Vector3& corner : frustum_corners) center += corner;
center /= 8.0f;

float radius = 0.0f;
for (const Vector3& corner : frustum_corners) radius = std::max(radius, (corner - center).Length());

// 半径を、切り上げて、わずかな変化で、サイズが、揺れないようにする。
radius = std::ceil(radius * 16.0f) / 16.0f;
```

球なので、**どの向きでも、同じ大きさ**です。**無駄**（箱が、視錐台より、大きい）は、増えますが、**安定**します（Valient、2008）。

## 対策 2：テクセル スナップ

箱の**位置**を、**シャドウ マップの、画素の、整数倍**に、**そろえます**。カメラが、少し動いても、**箱は、画素の、整数倍ずつ**しか、動かないので、**画素の境界が、ワールド上で、動かず**、**影の縁が、ちらつきません**。

```cpp
// 光のビュー空間で、箱の中心を、シャドウ マップの 1 画素の大きさの、整数倍に、丸める。
const float texel_size = (2.0f * radius) / shadow_map_resolution;       // 1 画素が、ワールドで、何メートルか

// 球の中心を、光のビュー空間へ
Vector3 center_ls = Vector3::Transform(center, light_view);

// 画素の、整数倍に丸める（x, y のみ。奥行き z は、動かしてよい）。
center_ls.x = std::floor(center_ls.x / texel_size) * texel_size;
center_ls.y = std::floor(center_ls.y / texel_size) * texel_size;

// 丸めた中心から、箱（正射影）を作る。
float left = center_ls.x - radius, right = center_ls.x + radius;
float bottom = center_ls.y - radius, top = center_ls.y + radius;
Matrix light_proj = Matrix::CreateOrthographicOffCenter(left, right, bottom, top, near_z, far_z);
```

**テクセル スナップ**は、**半径を固定**（対策 1）した上で、**初めて**、意味を持ちます。**半径が、揺れる**と、画素の大きさが、変わり、スナップしても、**ずれる**ためです。

| 手法 | 効果 | 代償 |
| --- | --- | --- |
| バウンディング スフィア | カメラの回転で、影が、**拡大縮小しない** | 箱が、大きく、**解像度が、やや、無駄になる** |
| テクセル スナップ | カメラの移動で、影が、**ちらつかない** | 箱の位置が、**画素単位で、飛ぶ**（影の、範囲が、少しずつ、不連続に、動く） |

## 光の方向が、動くとき

**太陽が、動く**（時間の、経過）と、光の**向き**が、変わり、**シャドウ マップの、座標軸が、回転**します。**ゆっくり、動かす**なら、問題ありませんが、**毎フレーム、少しずつ**、動くと、**影が、ちらつく**ことがあります。

| 対策 | 内容 |
| --- | --- |
| 光の向きの、更新を、**間引く** | 数フレームに、1 回だけ、光の向きを、更新（影が、少し、段階的に動く） |
| **フィルタを、強く** | PCF の、範囲を、広げて、ちらつきを、**ぼかして、隠す** |

## 影の、縁の、フィルタ

ちらつきを、**完全に、なくす**のは、難しいので、**フィルタ**で、縁を、**ぼかして**、目立たなくします。

| フィルタ | 効果 |
| --- | --- |
| 2×2（比較サンプラー） | わずかな、なめらかさ。ちらつきは、残る |
| 3×3〜5×5 PCF | ちらつきが、**かなり**減る |
| 回転する、ポアソン円盤 | ノイズに、変えて、ちらつきを、減らす（[PCF](../pcf.md)） |
| TAA | **時間方向**に、平均して、ちらつきを、**消す**（フレームごとに、サンプルを、ずらす） |

## 深度の、精度

シャドウ マップの、**深度の精度**も、重要です。**近い面と、遠い面の、範囲**（ニアとファー）が、**広い**と、**精度が、落ち**、**シャドウ アクネ**（縞模様の、自己影）が、出ます。

| 対策 | 内容 |
| --- | --- |
| 範囲を、**狭く** | ニア、ファーを、**影を落とす物の、範囲**に、ぴったり合わせる（光の視点の、奥行き） |
| 32 ビット浮動小数点 | `D32_FLOAT` を使う（16 ビットを、避ける） |
| 正射影 | 深度が、**線形**なので、精度が、均一 |

''', before="## よくあるミス")
pg.Refs("shadows/shadow-map-basics/aliasing-stabilize.md", [VALIENT, DIMITROV, BRABEC, RTR])

pg.Dedup("shadows/shadow-map-basics/minimal-code.md")
pg.Add("shadows/shadow-map-basics/minimal-code.md", '''
## 最小の、シャドウ マップ（全体の流れ）

ここまでの、ページの、内容を、**1 つの、流れ**に、まとめます。**太陽（平行光源）**の、**1 枚の、シャドウ マップ**です。座標系は、右手系・Y 上、反時計回りが表です。

### ① リソースを、作る（起動時）

```cpp
// シャドウ マップ（2048×2048）、DSV、SRV、比較サンプラー、ラスタライザー ステート。
CreateShadowMap(device, 2048, &shadow_tex, &shadow_dsv, &shadow_srv);   // Rendering Depth のコード

D3D11_SAMPLER_DESC sd = {};
sd.Filter = D3D11_FILTER_COMPARISON_MIN_MAG_LINEAR_MIP_POINT;
sd.AddressU = sd.AddressV = sd.AddressW = D3D11_TEXTURE_ADDRESS_BORDER;
sd.BorderColor[0] = sd.BorderColor[1] = sd.BorderColor[2] = sd.BorderColor[3] = 1.0f;
sd.ComparisonFunc = D3D11_COMPARISON_LESS_EQUAL;
sd.MaxLOD = D3D11_FLOAT32_MAX;
device->CreateSamplerState(&sd, &shadow_sampler);

// シャドウ パス用: ハードウェアのバイアス（Constant Bias / Slope-Scale Bias）。
D3D11_RASTERIZER_DESC rs = {};
rs.FillMode = D3D11_FILL_SOLID;
rs.CullMode = D3D11_CULL_BACK;
rs.FrontCounterClockwise = TRUE;
rs.DepthBias = 1000;                          // 24 ビット深度なら、この値 × 最小の深度の刻み
rs.SlopeScaledDepthBias = 1.5f;
rs.DepthBiasClamp = 0.01f;
rs.DepthClipEnable = TRUE;
device->CreateRasterizerState(&rs, &shadow_rs);
```

### ② 毎フレーム：シャドウ パス

```cpp
// 光の行列を作る（Light Matrix）。
Matrix light_view = Matrix::CreateLookAt(eye, center, up);
Matrix light_proj = Matrix::CreateOrthographicOffCenter(-r, r, -r, r, 0.0f, 2.0f * r);
Matrix shadow_matrix = light_view * light_proj * ndc_to_uv;

// 深度だけを描く。
context->OMSetRenderTargets(0, nullptr, shadow_dsv.Get());
context->ClearDepthStencilView(shadow_dsv.Get(), D3D11_CLEAR_DEPTH, 1.0f, 0);
context->RSSetViewports(1, &shadow_viewport);
context->RSSetState(shadow_rs.Get());
context->VSSetShader(shadow_vs.Get(), nullptr, 0);
context->PSSetShader(nullptr, nullptr, 0);
UpdateLightCB(light_view * light_proj);
DrawShadowCasters();
```

### ③ 毎フレーム：メイン パス

```cpp
// メインの描画: シャドウ マップを SRV として読む（DSV としては、外す）。
context->OMSetRenderTargets(1, scene_rtv.GetAddressOf(), scene_dsv.Get());   // シャドウ DSV は、外れる
context->RSSetViewports(1, &main_viewport);
context->RSSetState(main_rs.Get());
context->PSSetShaderResources(5, 1, shadow_srv.GetAddressOf());
context->PSSetSamplers(5, 1, shadow_sampler.GetAddressOf());
UpdateShadowCB(shadow_matrix);
DrawScene();
```

**同じテクスチャを、DSV と SRV に、同時にバインドしない**ことに、注意します。メインの、`OMSetRenderTargets` で、シャドウ DSV が、**外れる**ので、**SRV として、読めます**。

### ④ シェーダー

```hlsl
// メイン パスの、ピクセル シェーダー（抜粋）。
cbuffer ShadowCB : register(b2) { float4x4 g_shadow_matrix; };
Texture2D<float> g_shadow_map : register(t5);
SamplerComparisonState g_shadow_sampler : register(s5);

float ShadowFactor(float3 world_pos) {
  float4 p = mul(float4(world_pos, 1.0), g_shadow_matrix);
  float3 coord = p.xyz / p.w;                                         // xy = UV、z = 深度
  if (any(coord.xy < 0.0) || any(coord.xy > 1.0) || coord.z > 1.0) return 1.0;
  return g_shadow_map.SampleCmpLevelZero(g_shadow_sampler, coord.xy, coord.z);
}

float4 main(PSInput input) : SV_Target {
  float3 N = normalize(input.world_normal);
  float n_dot_l = saturate(dot(N, -g_light_dir));
  float shadow = ShadowFactor(input.world_position);
  float3 diffuse = g_albedo * g_light_color * n_dot_l * shadow;      // 影の中は、直接光が、0
  float3 ambient = g_albedo * g_ambient;                              // 環境光は、影に関係なく残る
  return float4(diffuse + ambient, 1.0);
}
```

## 動かない、ときの、点検

| 症状 | 見るところ |
| --- | --- |
| 影が、**全く出ない** | シャドウ パスで、物が、描かれているか（PIX / RenderDoc で、シャドウ マップの内容を見る）。光の行列が、正しいか |
| 影が、**上下逆** | NDC → UV の変換で、`y` を反転したか（`ndc.y * -0.5 + 0.5`） |
| 全体が、**縞模様**（シャドウ アクネ） | バイアスが、足りない（[Shadow Bias](../bias/index.md)） |
| 影が、物から、**浮いている** | バイアスが、大きすぎる（ピーター パンニング） |
| 影が、**ずれている** | 光の行列が、シャドウ パスと、メイン パスで、**同じ**か。**カメラの位置を、使っていないか** |
| 影が、**常に、真っ暗** | 比較関数の向き（reversed-Z）。範囲外の、境界色 |
| 影の端が、**ギザギザ** | 解像度を上げる、PCF（[PCF](../pcf.md)） |
| 地形の、**遠くで**、影が、無い | シャドウ マップの、範囲（`radius`）が、足りない。カスケード（[CSM](../cascaded.md)） |

デバッグには、**シャドウ マップを、画面に、表示**するのが、最も、効果的です。深度を、白黒で、画面の隅に、描きます。

```hlsl
// デバッグ表示: シャドウ マップの深度を、グレースケールで、画面に表示する。
float d = g_shadow_map.Load(int3(pos.xy, 0));
return float4(d.xxx, 1.0);
```

''', before="## よくあるミス")
pg.Refs("shadows/shadow-map-basics/minimal-code.md", [WILLIAMS, MS_SHADOW, D3D11_RS, D3D11_SAMPLER])

# ================================================================ bias
pg.Dedup("shadows/bias/index.md")
pg.Add("shadows/bias/index.md", '''
## なぜ、バイアスが、必要か

シャドウ マップでは、**画素の、光からの深度**と、**シャドウ マップに、保存された深度**を、比べます。**自分自身の面**（光に向いた、地面）を、描いているとき、**この 2 つは、理論上、同じ値**のはずです。ところが、実際には、**微小な誤差**で、**画素の深度が、わずかに、大きく**（遠く）なり、**「自分自身が、自分の影の中」**と、判定されます。これが、**シャドウ アクネ**（縞状の、自己影）です。

```text
              光
              ↓
 ─────────────────────────  地面
   保存された深度（4 画素に 1 つ）：階段状
   画素の深度：斜面に沿って、連続的に変わる

 階段より、上の画素 → 光が当たる、階段より下の画素 → 影（自分の影）  → 縞模様
```

**シャドウ マップの、1 画素**は、**面の、ある範囲**を、代表する、**1 つの深度**です。**斜めの面**では、その範囲の中で、**深度が、変わっている**ので、**画素ごとの深度と、保存された、1 つの深度**は、**必ず、ずれます**。そのずれを、**あらかじめ、許容する**のが、バイアスです。

## バイアスの、基本の考え方

**画素の深度から、少し引く**（**光に、近づける**）と、**自分自身の面が、影にならなく**なります。

```text
比較:  画素の深度 − バイアス <= 保存された深度  なら、光が当たる
```

## 問題：バイアスの、大小の、トレードオフ

| バイアス | 結果 |
| --- | --- |
| **小さすぎる** | シャドウ アクネ（縞模様の、自己影） |
| **大きすぎる** | **ピーター パンニング**（影が、物から、離れて、**浮く**）。薄い物の、影が、消える |
| **ちょうどよい** | 自己影なし、影が、物に、しっかり、接地する |

**ちょうど**の値は、**光の、角度**、**面の傾き**、**シャドウ マップの、解像度**、**カメラの、距離**で、**変わります**。**1 つの、固定値**では、すべての場面で、うまくいきません。

## 4 つの、バイアス

| 方式 | 内容 | ページ |
| --- | --- | --- |
| 定数バイアス | **深度に、一定の、値**を、引く | [Constant Bias](constant-bias.md) |
| 傾き依存バイアス | **面が、光に対して、斜めなほど、大きく** | [Slope-Scale Bias](slope-scale-bias.md) |
| 法線オフセット | **面の法線の向きに、ずらして**から、シャドウ マップを、引く | [Normal Offset](normal-offset.md) |
| レシーバー平面バイアス | **画素の周りの、平面**を、**推定**して、**平面に、沿った**深度で、比べる | [Receiver Plane Bias](receiver-plane-bias.md) |
| 表面のカリング | シャドウ パスで、**裏面を描く**（物の、厚みが、バイアス） | [Front-Face Culling](front-face-culling.md) |

**組み合わせて**使うのが、普通です。**定数 + 傾き依存**（ハードウェアの、バイアス）と、**法線オフセット**が、最も、一般的な、組み合わせです。

## どれを、選ぶか

| 状況 | おすすめ |
| --- | --- |
| まず、動かしたい | **定数 + 傾き依存**（ラスタライザー ステート）。簡単 |
| 斜めの面で、シャドウ アクネが、残る | **法線オフセット**を、足す |
| 広い範囲（カスケード）で、バイアスが、変わる | **カスケードごとに、バイアスを、スケール** |
| 高品質（PCF を、広くとる） | **レシーバー平面バイアス**（PCF の、範囲に、合わせた、補正） |
| 薄い物、**接地**が、重要 | 表面の描画（バイアス小）+ 法線オフセット |

**1 つの方式だけでは、足りない**ことが、多く、**併用しながら、場面に合わせて、調整**するのが、現実です。

## 調べ方

バイアスの調整は、**目で見て**行います。**調整用の、場面**（急な斜面、薄い板、光が、地面に、ほぼ平行）を、用意して、**変えながら**見ます。

| 場面 | 見るもの |
| --- | --- |
| 光が、**地面に、ほぼ平行**（朝夕） | シャドウ アクネが、出やすい。**最も、厳しい**条件 |
| **薄い板**（壁、床） | ピーター パンニングで、影が、消えないか |
| **球、円筒** | 曲面での、影の、なめらかさ |
| 影が、**接する場所**（足元） | 影が、物から、離れていないか |

''', before="## よくあるミス")
pg.Refs("shadows/bias/index.md", [WILLIAMS, BRABEC, ISIDORO, MS_SHADOW, D3D11_RS])

pg.Dedup("shadows/bias/constant-bias.md")
pg.Add("shadows/bias/constant-bias.md", '''
## 定数バイアスとは

**深度に、一定の値を、足し引きする**、最も、単純な、バイアスです。**画素の深度から、一定量を、引いて**から、シャドウ マップと、比べます。

```hlsl
// 画素の深度から、定数を引いてから、比較する。
float lit = g_shadow_map.SampleCmpLevelZero(g_shadow_sampler, coord.xy, coord.z - kConstantBias);
```

## 2 つの、掛け方

### ① シェーダーで、引く

比較する深度から、**直接**、定数を引きます。上のコードです。値の**単位**は、**正規化された深度**（0〜1）です。

| 射影 | 深度の分布 | バイアスの、効き方 |
| --- | --- | --- |
| 正射影（太陽） | **線形** | 一定の、**距離**に、相当する、バイアス。扱いやすい |
| 透視投影（スポット、点光源） | **非線形**（遠くで、粗い） | **同じ値でも**、近くと、遠くで、**ワールドの距離**が、**違う**。遠くで、**大きすぎる**（ピーター パンニング） |

### ② ハードウェアの、深度バイアス

**シャドウ パス**（深度を、書くとき）に、**書き込む深度に、バイアスを、足す**ことも、できます。**ラスタライザー ステート**の、`DepthBias` です。

```cpp
D3D11_RASTERIZER_DESC rs = {};
rs.DepthBias = 1000;                  // 整数。最小の、深度の刻み × この値
rs.DepthBiasClamp = 0.0f;
rs.SlopeScaledDepthBias = 0.0f;       // 傾き依存は、別のページ
```

| 深度形式 | `DepthBias` の、意味 |
| --- | --- |
| 24 ビット固定小数点（`D24_UNORM`） | `bias × r`（`r` は、最小の、表現できる、正の値 = 1 / 2²⁴） |
| 32 ビット浮動小数点（`D32_FLOAT`） | `bias × 2^(e − 23)`（`e` は、プリミティブの、最大の、深度の指数）。**浮動小数点なので、深度によって、刻みが違う** |

!!! warning "浮動小数点の、深度では、DepthBias の、効きが、深度で変わる"
    `D32_FLOAT` では、`DepthBias` の、効果が、**深度の大きさ**（指数）に、依存します。近くでは、ごく小さく、遠くでは、大きく、効きます。**固定小数点**（`D24_UNORM`）のほうが、**一定**で、扱いやすいですが、**精度は、浮動小数点が、高い**。通常は、**シェーダーで、引く方式**（①）のほうが、**値の意味が、はっきり**しています。

## 値の、決め方

| 項目 | 目安 |
| --- | --- |
| 正射影（太陽） | 深度の範囲の、**0.0005〜0.005**（ワールドで、数 cm〜数十 cm） |
| `DepthBias`（24 ビット） | 数百〜数千 |
| カスケード | **カスケードごとに**、スケールする（遠いカスケードは、シャドウ マップの 1 画素が、大きいので、バイアスも、大きく） |

```cpp
// カスケードごとに、バイアスを、スケールする（遠いカスケードほど、大きく）。
float bias_cascade = base_bias * (cascade_far - cascade_near) / (cascade0_far - cascade0_near);
```

**ワールドの距離**で、バイアスを、指定する（「5 cm」）と、直感的です。深度の範囲に、換算します。

```hlsl
// ワールド空間の距離（メートル）から、正規化深度のバイアスに、換算する（正射影）。
float bias_depth = bias_world_meters / (light_far - light_near);
```

## 定数バイアスの、限界

定数バイアスだけでは、**面が、光に対して、斜め**になるほど、**足りなく**なります。

| 面の向き | 必要な、バイアス |
| --- | --- |
| 光に、**正面**（垂直） | 小さい |
| **斜め**（45°） | 中くらい |
| ほぼ、**平行**（80°〜） | **非常に大きい** |

**定数**では、**どれかに、合わせる**と、**他で、破綻**します。

| 破綻 | 内容 |
| --- | --- |
| 正面の面に、合わせる（小さい） | 斜めの面で、シャドウ アクネ |
| 斜めの面に、合わせる（大きい） | 正面の面で、ピーター パンニング |

そこで、**面の傾きに、応じて、変える**、**傾き依存バイアス**が、必要です（[Slope-Scale Bias](slope-scale-bias.md)）。

''', before="## よくあるミス")
pg.Refs("shadows/bias/constant-bias.md", [WILLIAMS, MS_SHADOW, D3D11_RS, ISIDORO])

pg.Dedup("shadows/bias/slope-scale-bias.md")
pg.Add("shadows/bias/slope-scale-bias.md", '''
## 傾き依存バイアスとは

面が、**光に対して、斜めになるほど**、シャドウ マップの 1 画素の中で、**深度が、大きく、変わります**。**その変化の大きさ（深度の傾き）に、比例して**、バイアスを、**大きくする**のが、**傾き依存（slope-scale）バイアス**です。

```text
バイアス = 定数 + 傾き係数 × 深度の傾き
```

| 面の向き | 深度の傾き | バイアス |
| --- | --- | --- |
| 光に、正面 | 小さい | 小さい |
| 斜め | 中くらい | 中くらい |
| 光と、ほぼ平行 | **非常に大きい** | **大きい** |

## ハードウェアで、行う

`D3D11_RASTERIZER_DESC` の、**`SlopeScaledDepthBias`** が、これです。**ハードウェアが、三角形ごとに、深度の傾きを、計算**して、**自動で**、バイアスに、反映します。

```cpp
D3D11_RASTERIZER_DESC rs = {};
rs.DepthBias = 1000;                  // 定数分
rs.SlopeScaledDepthBias = 1.5f;       // 傾き係数。深度の最大の傾きに、この値を掛ける
rs.DepthBiasClamp = 0.01f;            // バイアスの、上限（ピーター パンニングの、暴走を、防ぐ）
device->CreateRasterizerState(&rs, &shadow_rs);
```

バイアスの、全体の式は、次のとおりです（Direct3D の、仕様）。

```text
Bias = DepthBias × r  +  SlopeScaledDepthBias × MaxDepthSlope
Bias は、DepthBiasClamp を、超えない
```

| 値 | 意味 |
| --- | --- |
| `DepthBias × r` | 定数バイアス（`r` は、最小の、深度の刻み） |
| `MaxDepthSlope` | **三角形の、深度の傾き**（`max(|∂z/∂x|, |∂z/∂y|)`、画面空間での、変化） |
| `SlopeScaledDepthBias` | 傾きに、掛ける係数。**1〜3** が、一般的 |
| `DepthBiasClamp` | **上限**。非常に、斜めの面で、バイアスが、暴走して、影が、消えるのを防ぐ |

### 傾きの、直感

**光に、ほぼ平行な面**（朝夕の光が、地面に、すれすれ）では、シャドウ マップの 1 画素が、**地面の、非常に長い範囲**を、覆い、**その範囲での、深度の変化が、大きい**。ハードウェアが、**その大きな、傾きに、比例**して、バイアスを、自動で、足します。

## シェーダーで、行う

ハードウェアの、バイアスは、**シャドウ パスで、書く深度**に、効きます。**メイン パスで、比較する側**を、シェーダーで、補正する方法もあります。**面の法線と、光の方向**から、傾きを、計算します。

```hlsl
// 法線と光の方向から、深度の傾きに、比例した、バイアスを求める。
float SlopeScaledBias(float3 normal, float3 light_dir, float base_bias, float slope_bias) {
  float cos_theta = saturate(dot(normal, -light_dir));
  float sin_theta = sqrt(1.0 - cos_theta * cos_theta);
  float tan_theta = sin_theta / max(cos_theta, 0.05);          // tan(光と法線の角度)。斜めほど大きい
  return base_bias + slope_bias * min(tan_theta, 10.0);         // 暴走を、防ぐ上限
}

float bias = SlopeScaledBias(N, g_light_dir, 0.0005, 0.0005);
float lit = g_shadow_map.SampleCmpLevelZero(g_shadow_sampler, coord.xy, coord.z - bias);
```

`tan θ` は、**光に、正面で 0**、**平行に近づくと、無限大**に近づきます。**上限**（`min(…, 10)`）を、入れて、暴走を、防ぎます。

| 方式 | 長所 | 短所 |
| --- | --- | --- |
| ハードウェア（`SlopeScaledDepthBias`） | 設定が、簡単。**三角形ごと**に、正確な傾きを、使える | シャドウ パスの、深度に、効く。**値の意味が、直感的でない**（プリミティブごとに、傾きが、決まる） |
| シェーダー（法線と光から） | **メイン パス側**で、調整できる。値の意味が、明確 | **法線**が、必要。カスケードごとの、調整が、必要 |

## 限界

傾き依存バイアスは、**ほとんどの、場面で、有効**ですが、次の問題が、残ります。

| 問題 | 内容 |
| --- | --- |
| **非常に斜めの面** | バイアスが、非常に、大きくなり、ピーター パンニング |
| **PCF を、広く取る** | PCF の、範囲の中で、面の深度は、**さらに変化**する。傾き依存だけでは、**足りない**（[Receiver Plane Bias](receiver-plane-bias.md)） |
| **曲面** | 1 つの、三角形内で、傾きが、一定とは、限らない |

**法線オフセット**（[Normal Offset](normal-offset.md)）と、**併用**すると、バイアスを、小さく、保ったまま、**自己影を、抑えられます**。

''', before="## よくあるミス")
pg.Refs("shadows/bias/slope-scale-bias.md", [D3D11_RS, MS_SHADOW, ISIDORO, BRABEC])

pg.Dedup("shadows/bias/normal-offset.md")
pg.Add("shadows/bias/normal-offset.md", '''
## 法線オフセットとは

**深度を、引く**代わりに、**画素の位置そのもの**を、**面の法線の向きに、少し、ずらして**から、シャドウ マップを、引きます。**面の、少し上**（**表面の、外側**）の点を、調べることになるので、**自分自身の面と、交差しません**。

```text
              光
              ↓
 ──────────●─────────  地面（P）
            ↑ 法線の向きに、少し持ち上げる
           ●             P' = P + N × offset  ← この点で、シャドウ マップを引く
```

**深度の値は、いじらず**、**位置を動かす**ので、**バイアスの、副作用**（影が、浮く）が、**小さくなります**。

## 実装

```hlsl
float ShadowFactorNormalOffset(float3 world_pos, float3 world_normal, float3 light_dir, float offset_scale) {
  // 面が、光に対して、斜めなほど、大きくずらす（斜めの面ほど、自己影が、出やすいため）。
  float cos_theta = saturate(dot(world_normal, -light_dir));
  float sin_theta = sqrt(1.0 - cos_theta * cos_theta);
  float3 offset = world_normal * (sin_theta * offset_scale);

  // 位置を、法線方向に、ずらしてから、光の座標に変換する。
  float4 p = mul(float4(world_pos + offset, 1.0), g_shadow_matrix);
  float3 coord = p.xyz / p.w;
  return g_shadow_map.SampleCmpLevelZero(g_shadow_sampler, coord.xy, coord.z);
}
```

| 要素 | 内容 |
| --- | --- |
| `offset_scale` | ずらす距離。**シャドウ マップの、1 画素の、ワールドでの、大きさ**の、1〜3 倍が、目安 |
| `sin_theta` | 光に**正面**（`sin = 0`）なら、ずらさない。**斜め**（`sin` が大きい）ほど、大きくずらす |

### ずらす距離の、決め方

シャドウ マップの 1 画素が、ワールドで、**どのくらいの、大きさか**を、基準にします。

```cpp
// 太陽（正射影）のとき、1 画素の、ワールドでの大きさ（メートル）。
float texel_world_size = (2.0f * radius) / shadow_map_resolution;
// 法線オフセットの距離は、その 1〜3 倍。
float normal_offset = texel_world_size * 2.0f;
```

**解像度が、粗い**（遠いカスケード）ほど、1 画素が、大きいので、**オフセットも、大きく**します。**カスケードごとに、`texel_world_size` を、計算**します。

## 長所と短所

| | 内容 |
| --- | --- |
| 長所 | **ピーター パンニングが、少ない**（深度を、動かさないので、影が、物から、離れにくい） |
| 長所 | **斜めの面**でも、自己影を、抑えられる（傾きに、応じて、ずらすため） |
| 長所 | **ワールドの距離**で、指定できる（**直感的**。カスケードごとに、スケールしやすい） |
| 短所 | **法線**が、必要（シャドウを引く、メイン パスで、法線を、持っている必要がある） |
| 短所 | **影が、わずかに、ずれる**（位置を、動かすので）。**物の、縁・角**で、**影が、欠ける**ことがある |
| 短所 | 法線が、**滑らか**（頂点法線の、補間）でないと、**面の境目で、影が、段差**になる。**ノーマル マップ**は、**使わず**、**ジオメトリの、法線**を、使う |

### 角（エッジ）での、問題

**物の角**で、法線方向に、ずらすと、**隣の面の、影の内部**に、入ってしまう**ことがあります。**ずらす距離が、大きすぎる**と、**角の影が、欠けます**。

| 対策 | 内容 |
| --- | --- |
| ずらす距離を、**控えめ**に | 1 画素の、1〜2 倍に、とどめる |
| **補間した法線**（頂点法線）を使う | 面法線ではなく、頂点法線を、補間して、使う（角で、法線が、滑らかに、変わる） |
| **定数バイアス**と、併用 | 法線オフセットで、大部分を、抑え、残りを、**小さな、定数バイアス**で、補う |

## 他のバイアスとの、組み合わせ

**実用的な、組み合わせ**は、次のとおりです。

```text
① 法線オフセット（斜めの面の、自己影を、抑える。ワールド距離で、指定）
② + 小さな定数バイアス（深度の精度の誤差を、補う）
③ + ハードウェアの、傾き依存バイアス（シャドウ パスで、ごく小さく）
```

| 役割 | 方式 |
| --- | --- |
| 斜めの面（射影エイリアシング） | **法線オフセット** |
| 深度の、量子化誤差 | **小さな、定数バイアス** |
| 三角形ごとの、微調整 | **傾き依存**（ごく小さく） |

どれも、**大きく**すると、副作用が、出るので、**小さな値を、組み合わせる**のが、**コツ**です。

''', before="## よくあるミス")
pg.Refs("shadows/bias/normal-offset.md", [ISIDORO, MS_SHADOW, DIMITROV, RTR])

pg.Dedup("shadows/bias/peter-panning.md")
pg.Add("shadows/bias/peter-panning.md", '''
## ピーター パンニングとは

**バイアスを、大きくしすぎた**ときに、**影が、物から、離れて、浮いて見える**現象です。ピーター パンが、**影が、体から、離れた**（影を、縫いつけた）という話に、ちなんで、こう呼ばれます。

```text
 本来の影:                      ピーター パンニング:
   ┌──┐                           ┌──┐
   │物│                           │物│
 ━━┷━━┷━━━━━                    ━━┷━━┷━━━━━
   ▓▓▓▓      ← 足元に、接する       ░░░░▓▓▓   ← 影が、足元から、離れている（浮いている）
```

## 原因

バイアスは、**画素の深度から、一定量を、引く**ことで、**自己影を、防ぎます**。**引く量が、大きすぎる**と、**物の、すぐ近くの、影**まで、**「光が当たる」**と、判定されます（**物の接地部分の、影が、消える**）。

| バイアス | 影の見え方 |
| --- | --- |
| 小さい | 物の、足元から、影が、始まる。ただし、**自己影**（シャドウ アクネ） |
| ちょうどよい | 足元から、影が、始まる。自己影なし |
| **大きすぎる** | 足元の、影が、**欠ける**。**影が、物から、離れる** |

**特に、薄い物**（壁、屋根、板）で、**目立ちます**。**バイアスより、薄い物は、影を、落とせません**（影が、完全に、消える）。

## 見分け方

| 症状 | 原因 |
| --- | --- |
| 物の、**足元**に、**隙間**（光の筋）が、見える | バイアスが、大きすぎる |
| 薄い壁の、**影が、無い**、または、**途切れる** | バイアスが、壁の厚みより、大きい |
| 物が、**浮いて**見える | 影が、接地して、いないので、物が、地面から、浮いて、見える |
| 光が、**斜めの**とき、特に目立つ | 傾き依存の、バイアスが、**暴走**している |

## 対策

### ① バイアスを、小さくする

**根本的**な対策は、**バイアスを、必要最小限に、抑える**ことです。ただし、**シャドウ アクネ**（バイアスが、足りない症状）と、**トレード オフ**です。**他の方法**で、アクネを、防ぎ、**バイアスを、小さく**保ちます。

### ② 法線オフセットを、使う

**深度を、引く**（バイアス）代わりに、**位置を、法線方向に、ずらす**（[Normal Offset](normal-offset.md)）ことで、**アクネを、防ぎ**ます。**深度の値**は、**いじらない**ので、**ピーター パンニングが、起きにくく**なります。

### ③ 表面のカリング（裏面を描く）

シャドウ パスで、**光に向いた面**ではなく、**裏面**（光から、遠い側の面）を、描きます（[Front-Face Culling](front-face-culling.md)）。**表と裏の間**の、**物の厚み**が、**そのまま、バイアスの代わり**になり、**バイアスを、ほぼ、不要**にできます。

| 方法 | ピーター パンニング |
| --- | --- |
| 表面を描く + 大きなバイアス | **起きる** |
| 裏面を描く（バイアス小） | **起きにくい**（物の厚みが、接地を、保つ）。**薄い物は、別の問題**（影が、欠ける） |

### ④ 傾き依存バイアスの、上限

**傾き依存**バイアスは、**光に、ほぼ平行な面**で、**暴走**します。**上限（`DepthBiasClamp`）**を、設けます（[Slope-Scale Bias](slope-scale-bias.md)）。

```cpp
rs.DepthBiasClamp = 0.005f;        // バイアスの、上限。暴走を、防ぐ
```

### ⑤ 薄い物は、厚みを持たせる

薄い壁や、板が、影を、落とせないのは、**ジオメトリが、薄すぎる**ためです。**影用に、少し厚みを、持たせた、メッシュ**（**影用のメッシュ**）を、使うか、**壁そのものに、厚み**を、つけます。

### ⑥ 接地部分を、**偽の影**で、補う

足元の、**接地**が、重要（キャラクター）なら、**足元に、ブロブ状の、影**（[Blob and Planar Projected Shadows](../special-cases/blob-planar.md)）や、**コンタクト シャドウ**（[Contact Shadows](../contact-shadows.md)）を、**足して**、補います。

## 判断の、目安

| 優先 | 内容 |
| --- | --- |
| 1 | **まず、バイアスを、**最小**から**、始める（アクネが、出ない、最小値） |
| 2 | 斜めの面の、アクネは、**法線オフセット**で、抑える |
| 3 | 薄い物は、**影用の、メッシュ**、または、**裏面を、描く** |
| 4 | **接地**が、重要なら、**コンタクト シャドウ**で、補う |

''', before="## よくあるミス")
pg.Refs("shadows/bias/peter-panning.md", [ISIDORO, MS_SHADOW, WILLIAMS, RTR])

pg.Dedup("shadows/bias/front-face-culling.md")
pg.Add("shadows/bias/front-face-culling.md", '''
## 考え方：裏面を、描く

通常、シャドウ パスでは、**光に向いた面（表面）**の、深度が、シャドウ マップに、保存されます。メイン パスで、**同じ表面**を、描くとき、**保存された深度と、画素の深度が、ほぼ同じ**になり、**自己影**（シャドウ アクネ）が、出やすくなります。

**表面を、カリング**し、**裏面**（光から、遠い側の面）だけを、**描く**と、シャドウ マップには、**物の、奥側の面の深度**が、保存されます。メイン パスで、**表面を、描くとき**、**保存された深度（奥側）**は、**画素の深度（表側）より、物の厚みぶん、遠い**ので、**自己影に、なりません**。**物の厚みが、そのまま、バイアスの役割**を、果たします。

```text
              光
              ↓
           ┌────┐   ← 表面（光に、向いた面）  カリングして、描かない
           │ 物 │
           └────┘   ← 裏面（光から、遠い面）  これを、描く → シャドウ マップに、保存される
 ━━━━━━━━━━━━━━━━━━  地面

 メイン パスで、物の表面を描くとき:  画素の深度（表面） < 保存された深度（裏面）  → 光が当たる（自己影なし）
```

## 実装

シャドウ パスの、ラスタライザー ステートで、**表面を、カリング**します（`CULL_FRONT`）。**このサイトの、座標系は、反時計回りが表**なので、`FrontCounterClockwise = TRUE` と、組み合わせます。

```cpp
D3D11_RASTERIZER_DESC rs = {};
rs.FillMode = D3D11_FILL_SOLID;
rs.CullMode = D3D11_CULL_FRONT;                 // 光に向いた面（表面）を、描かない = 裏面を、描く
rs.FrontCounterClockwise = TRUE;                // 反時計回りが表
rs.DepthClipEnable = TRUE;
device->CreateRasterizerState(&rs, &shadow_rs_front_cull);
```

| 設定 | 内容 |
| --- | --- |
| `CullMode = FRONT` | **表面を、描かない**（裏面だけが、深度に、書かれる） |
| `FrontCounterClockwise` | **表裏の判定**の、向き。メインの描画と、**同じ**にする |

## 長所と短所

| | 内容 |
| --- | --- |
| 長所 | **バイアスが、ほぼ、不要**（物の厚みが、バイアスの代わり） |
| 長所 | **ピーター パンニングが、起きにくい**（接地部分で、影が、地面に、つながる） |
| 長所 | 設定が、**ラスタライザー ステートの、1 つだけ** |
| 短所 | **薄い物**（壁、板、葉）では、**表裏の、間隔が、無く**、影が、**欠ける**、または、**自己影が、残る** |
| 短所 | **閉じていない、メッシュ**（地面、1 枚の板）には、裏面が、無い。**地面は、表面を描く**必要 |
| 短所 | **地面（受け手）の、影**は、地面の、表面が、**自己影を、起こす**。地面は、**裏面を描いて**も、**意味がない**（地面の、下には、何もない） |

## 使い分け

**影を落とす物**（キャラクター、建物、木）と、**影を受ける物**（地面）で、**扱いを、分けます**。

| 物 | シャドウ パスで、描く面 | 理由 |
| --- | --- | --- |
| **閉じた、厚みのある物**（キャラクター、岩、建物の、塊） | **裏面**（表面を、カリング） | 厚みが、バイアスになる |
| **地面**（地形）| **表面**（通常）+ バイアス | 地面は、閉じていない。裏面を描くと、地面全体が、影を、**落とさなく**なる |
| **薄い物**（壁、フェンス、葉） | **両面** | 厚みが、無いので、どちらの面も、必要 |

実装では、**物（マテリアル）ごと**に、シャドウ パスの、**ラスタライザー ステートを、切り替えます**。

```cpp
// マテリアルごとに、シャドウ パスの、カリングを、選ぶ。
for (const Mesh& m : shadow_casters) {
  switch (m.shadow_cull) {
    case ShadowCull::Back:  context->RSSetState(rs_cull_back.Get());  break;   // 地面（表面を描く）
    case ShadowCull::Front: context->RSSetState(rs_cull_front.Get()); break;   // 厚みのある物（裏面を描く）
    case ShadowCull::None:  context->RSSetState(rs_cull_none.Get());  break;   // 薄い物（両面）
  }
  Draw(m);
}
```

## 裏面を描く方法の、落とし穴

| 落とし穴 | 内容 |
| --- | --- |
| **影の、始まり**が、**少し、ずれる** | 物の、**奥側**の深度を、使うので、**影が、物の厚み分、奥から、始まる**。**接地**は、きれいだが、**影の始まりが、物の、足元より、後ろ**になることがある |
| **光が、物の、側面に、当たる**とき | 側面（光と、ほぼ平行）では、**表裏の、区別が、あいまい**。**側面の、影の、境目**が、ちらつくことがある |
| **カメラが、物の中**に入る | 描画では、メッシュの内側を、見る。影には、影響しない |

**単独で、使う**というより、**他のバイアス**（法線オフセット、小さな、定数バイアス）と、**組み合わせて**、**バイアスの、量を、小さく**する目的で、使うのが、現実的です。

''', before="## よくあるミス")
pg.Refs("shadows/bias/front-face-culling.md", [WANG := '''Wang, Molnar, "Second-Depth Shadow Mapping", UNC Technical Report TR94-019, 1994（第 2 深度シャドウ マップ。裏面を使う考え方）''', MS_SHADOW, D3D11_RS, ISIDORO])

pg.Dedup("shadows/bias/receiver-plane-bias.md")
pg.Add("shadows/bias/receiver-plane-bias.md", '''
## PCF と、バイアスの、問題

**PCF**（[PCF](../pcf.md)）は、**1 つの画素**を、シャドウ マップの、**複数の画素**（3×3、5×5 など）で、**比較**して、**縁を、なめらか**にします。ところが、**面が、斜め**のとき、**PCF で読む、周囲の画素**は、**画素の位置と、深度が、異なる点**を、指しています。

```text
 光
 ↓       ↓       ↓        ← PCF が、読む、隣の画素（x−1, x, x+1）
 ─────────╲───────────╲──   斜めの面
          ↘ 深度が、画素ごとに、違う
```

**中心の画素の、深度**で、**隣の画素の、シャドウ マップ値**を、比べると、**面が、斜めなので、隣の画素の、実際の深度は、中心と、異なります**。比較が、**常に、「中心の深度」**だと、**隣の、本来、光が当たる点**が、**影**と判定され、**自己影**（縞）が、出ます。

## レシーバー平面バイアス

**レシーバー平面深度バイアス**（Receiver Plane Depth Bias、Isidoro、2006）は、**画素の周りの、面を、平面とみなし**、**PCF で読む、各サンプル位置での、平面の深度**を、**計算**して、**その深度**で、比べます。**1 つの深度**ではなく、**位置ごとの、深度**を、使うので、**面が、斜めでも、各サンプルで、正しい比較**になります。

### 平面の、深度の、求め方

画素の、シャドウ座標 `(u, v, z)` の、**画面空間の、微分**（`ddx`、`ddy`）から、**`z` が、`u`、`v` に対して、どう変わるか**（**深度の勾配**）を、求めます。

```text
dz/du、dz/dv を求める:
  [ ∂u/∂x  ∂v/∂x ] [dz/du]   [ ∂z/∂x ]
  [ ∂u/∂y  ∂v/∂y ] [dz/dv] = [ ∂z/∂y ]
```

2×2 の、連立方程式を、**逆行列**で、解きます。

```hlsl
// シャドウ座標 (u, v, z) の、画面の微分から、深度の勾配 (dz/du, dz/dv) を求める。
float2 ReceiverPlaneDepthBias(float3 shadow_coord_ddx, float3 shadow_coord_ddy) {
  float2 bias_uv;
  // 2×2 の逆行列（行列式で割る）
  bias_uv.x = shadow_coord_ddy.y * shadow_coord_ddx.z - shadow_coord_ddx.y * shadow_coord_ddy.z;
  bias_uv.y = shadow_coord_ddx.x * shadow_coord_ddy.z - shadow_coord_ddy.x * shadow_coord_ddx.z;
  float det = shadow_coord_ddx.x * shadow_coord_ddy.y - shadow_coord_ddx.y * shadow_coord_ddy.x;
  bias_uv /= max(abs(det), 1e-6) * sign(det);
  return bias_uv;                       // x = dz/du、y = dz/dv
}
```

### PCF の、各サンプルで、平面の深度を、使う

```hlsl
float ShadowPCFReceiverPlane(float3 coord) {
  // ① 深度の勾配を、求める（画面の微分から）
  float2 dz_duv = ReceiverPlaneDepthBias(ddx(coord), ddy(coord));

  // ② PCF の、各サンプル位置で、平面の深度を使って、比べる
  float sum = 0.0;
  const int kRadius = 2;                                         // 5×5
  [unroll] for (int y = -kRadius; y <= kRadius; ++y) {
    [unroll] for (int x = -kRadius; x <= kRadius; ++x) {
      float2 offset = float2(x, y) * g_shadow_texel_size;         // シャドウ マップ上の、ずれ（UV）
      float z_at_sample = coord.z + dot(dz_duv, offset);          // 平面に沿った、そのサンプルでの深度
      sum += g_shadow_map.SampleCmpLevelZero(g_shadow_sampler, coord.xy + offset, z_at_sample - kSmallBias);
    }
  }
  return sum / float((2 * kRadius + 1) * (2 * kRadius + 1));
}
```

| 要素 | 内容 |
| --- | --- |
| `dz_duv` | **面の傾きに、沿った**、深度の変化（UV 方向に、1 だけ動いたとき） |
| `z_at_sample` | **サンプル位置での**、平面の深度 = 中心の深度 + 勾配 × ずれ |
| `kSmallBias` | **ごく小さな**定数バイアス（量子化誤差の、補正用） |

## 長所と短所

| | 内容 |
| --- | --- |
| 長所 | **PCF を、広く取っても**、斜めの面で、**自己影が、出ない**。**バイアスを、小さく**保てる |
| 長所 | **ピーター パンニングが、少ない**（バイアスを、大きく取らなくて、よい） |
| 長所 | **カスケードごとの、調整が、少ない**（平面に、沿うので、解像度に、依存しにくい） |
| 短所 | **画面の微分**（`ddx`、`ddy`）に、依存する。**分岐の中**や、**画素の、端**で、**不安定**になる |
| 短所 | **平面**を、仮定する。**曲面、角**では、**平面の仮定が、崩れ**、ずれる |
| 短所 | **微分が、極端な値**（光と、ほぼ平行な面）になり、**数値が、暴走**する。**クランプ**が、必要 |
| 短所 | 計算が、**やや多い**（微分と、逆行列） |

### 暴走を、防ぐ

```hlsl
// 勾配が、極端に大きくならないよう、上限をかける。
dz_duv = clamp(dz_duv, -kMaxSlope, kMaxSlope);
```

また、**画面の微分**は、**2×2 のクアッド**（隣り合う 4 画素）で、**計算**されるので、**クアッドの、画素が、別の面に、またがる**（物の、縁）と、**微分が、乱れます**。**縁では、**この方式の、効果が、弱まります**。

## 他の方式との、使い分け

| 状況 | 方式 |
| --- | --- |
| **2×2 PCF**（比較サンプラー、ハードウェア） | 傾き依存バイアス（[Slope-Scale Bias](slope-scale-bias.md)）で、十分 |
| **3×3〜5×5 PCF**（ソフトな縁） | **レシーバー平面バイアス**が、効く |
| **PCSS**（広い範囲で、読む） | **レシーバー平面バイアス**が、ほぼ、必須（[PCSS](../pcss.md)） |
| **VSM / ESM**（フィルタ可能な、シャドウ マップ） | 別の、問題（光漏れ）。この方式は、使わない |

''', before="## よくあるミス")
pg.Refs("shadows/bias/receiver-plane-bias.md", [ISIDORO, MS_SHADOW, FERNANDO])
print("ok")
