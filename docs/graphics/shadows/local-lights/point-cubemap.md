---
title: Point Lights: Cube Maps
tags:
  - 描画
---

# Point Lights: Cube Maps

**点光源は、全方向を照らす**ので、**影を作るには、全方向の深度が必要**です。**キューブ マップ（6 面）に、各方向の深度を描く**のが**標準**で、**サンプルは、ライトから画面の点への方向ベクトルで引く**ので**簡単**です。**ただし、6 回描くので、コストが 6 倍**です。このページでは、**キューブ マップの作り方・方向ベクトルでのサンプル・線形距離の保存・面の境界と PCF**を説明します。

!!! tip "ポイント"
    - **点光源の影 ＝ 6 面のキューブ マップ**（**各面 90° の透視投影**）。
    - **サンプルは、方向ベクトルで引く**（**面を意識しなくてよい**）。
    - **保存は、非線形深度より、ライトからの距離（線形）**が**扱いやすい**。
    - **面の境界で、PCF のサンプルが隣の面に跨ぐ**ので**注意**。

<!-- fig:point-cubemap-faces:begin -->

<svg class="fig illust motion" data-fig="point-cubemap-faces" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-point-cubemap-faces" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">点光源の影:6 方向にシャドウ マップを描く（キューブ マップ）</text>
<polygon points="390,238 473.44,154.56 473.44,321.44" fill="#fecaca" fill-opacity="0.18" stroke="#94a3b8" stroke-width="1.5"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0741;0.0963;0.2000;0.2222;1.0000" values="0.18;0.18;0.55;0.55;0.18;0.18"/></polygon>
<polygon points="390,238 306.56,154.56 473.44,154.56" fill="#bbf7d0" fill-opacity="0.18" stroke="#94a3b8" stroke-width="1.5"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2222;0.2444;0.3481;0.3704;1.0000" values="0.18;0.18;0.55;0.55;0.18;0.18"/></polygon>
<polygon points="390,238 306.56,321.44 306.56,154.56" fill="#bfdbfe" fill-opacity="0.18" stroke="#94a3b8" stroke-width="1.5"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3704;0.3926;0.4963;0.5185;1.0000" values="0.18;0.18;0.55;0.55;0.18;0.18"/></polygon>
<polygon points="390,238 473.44,321.44 306.56,321.44" fill="#fde68a" fill-opacity="0.18" stroke="#94a3b8" stroke-width="1.5"><animate attributeName="fill-opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5185;0.5407;0.6444;0.6667;1.0000" values="0.18;0.18;0.55;0.55;0.18;0.18"/></polygon>
<circle cx="490" cy="218" r="15" fill="#e5484d" stroke="#ffffff" stroke-width="2"/>
<circle cx="370" cy="133" r="15" fill="#2ea043" stroke="#ffffff" stroke-width="2"/>
<circle cx="295" cy="273" r="15" fill="#2563eb" stroke="#ffffff" stroke-width="2"/>
<circle cx="430" cy="333" r="15" fill="#e5aa28" stroke="#ffffff" stroke-width="2"/>
<circle cx="390" cy="238" r="13" fill="#e5aa28" stroke="#ffffff" stroke-width="2"/>
<text x="390" y="274" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#e5aa28">点光源</text>
<text x="532.0" y="243.0" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937">+X（右）</text>
<text x="60" y="70" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937" opacity="0">面 1:+X 向きに、90° の視野でシャドウ マップを描く<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.0738;0.0741;0.2219;0.2222;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390.0" y="101.0" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937">+Z（奥）</text>
<text x="60" y="70" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937" opacity="0">面 2:+Z 向きに、90° の視野でシャドウ マップを描く<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.2219;0.2222;0.3701;0.3704;1.0000" values="0;0;1;1;0;0"/></text>
<text x="248.0" y="243.00000000000003" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937">−X（左）</text>
<text x="60" y="70" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937" opacity="0">面 3:−X 向きに、90° の視野でシャドウ マップを描く<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.3701;0.3704;0.5182;0.5185;1.0000" values="0;0;1;1;0;0"/></text>
<text x="390.0" y="385.0" text-anchor="middle" style="font-size:14px;font-weight:700;fill:#1f2937">−Z（手前）</text>
<text x="60" y="70" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937" opacity="0">面 4:−Z 向きに、90° の視野でシャドウ マップを描く<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.5182;0.5185;0.6664;0.6667;1.0000" values="0;0;1;1;0;0"/></text>
<text x="60" y="390" text-anchor="start" style="font-size:14px;font-weight:700;fill:#1f2937" opacity="0">上（+Y）と下（−Y）も加えて 6 面。描画は 6 回（視錐台カリングで、物が無い面は省ける）<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6664;0.6667;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="60" y="70" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2ea043" opacity="0">まとめ:光を中心に、6 つの方向へ<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6664;0.6667;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="60" y="410" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">上から見た図。影を引く時は、光から見た方向ベクトルで、6 面のうちの 1 枚を選ぶ。</text>
</svg>

<!-- fig:point-cubemap-faces:end -->

## 点光源：キューブ マップ
**点光源**は**あらゆる方向**に光を出します。**6 方向（±X, ±Y, ±Z）に、視野角 90 度の透視投影**で描けば、**全方向を覆えます**（**キューブ シャドウ マップ**）。

<svg class="fig illust" viewBox="0 0 780 260" role="img" aria-label="キューブ シャドウ マップ">
<text x="20" y="24" class="fig-title">点光源から 6 方向へ、視野角 90 度で描く（真上から見た図）</text>
<circle cx="200" cy="140" r="9" fill="rgba(229,170,40,0.9)" stroke="currentColor" stroke-width="2"/><text x="214" y="132" style="font-size:12px">光源</text>
<line x1="200" y1="140" x2="320" y2="40" stroke="currentColor" stroke-dasharray="4 3"/><line x1="200" y1="140" x2="320" y2="240" stroke="currentColor" stroke-dasharray="4 3"/>
<line x1="200" y1="140" x2="80" y2="40" stroke="currentColor" stroke-dasharray="4 3"/><line x1="200" y1="140" x2="80" y2="240" stroke="currentColor" stroke-dasharray="4 3"/>
<text x="326" y="146" style="font-size:12px">+X 面</text><text x="30" y="146" style="font-size:12px">−X 面</text><text x="170" y="40" style="font-size:12px">+Z 面</text><text x="170" y="254" style="font-size:12px">−Z 面</text>
<text x="420" y="90" style="font-size:13px">各面：視野角 90°、アスペクト 1</text>
<text x="420" y="116" style="font-size:13px">±Y 面（上下）も同様に描く（図は省略）</text>
<text x="420" y="152" style="font-size:13px">画素 → ライトからのベクトル v の</text>
<text x="420" y="172" style="font-size:13px">絶対値が最大の成分で、使う面が決まる</text>
</svg>

6 面の描き方は 3 通りです。6 枚のレンダー ターゲットに 6 回描く方法（`Texture2DArray` の 6 スライス、または `TextureCube`）が基本です。ジオメトリ シェーダーで `SV_RenderTargetArrayIndex` を使い、1 回の描画で 6 面に出す方法もありますが、効率は環境によります。ビュー インスタンシングに対応した環境なら、1 回のドローで複数面に出せます。

### サンプル：方向ベクトルで引く

**キューブ マップ**は、**ライトから画素へのベクトル**で、**サンプル**できます。**比較には保存された深度**と<strong>そのベクトルの長さ（または面ごとの深度）</strong>を使います。

```hlsl
float PointShadow(float3 world_pos) {
  float3 v = world_pos - light_position;
  float3 a = abs(v);
  float major = max(a.x, max(a.y, a.z));
  float depth = (light_far * (major - light_near)) / (major * (light_far - light_near));
  return shadow_cube.SampleCmpLevelZero(shadow_sampler, v, depth - bias);
}
```

サンプリングのコードの要点です。`major` は絶対値が最大の成分で、その面のビュー空間の z にあたります。`depth` は、透視投影の深度の式で、射影後の深度（0〜1）に変換します（左手系の `XMMatrixPerspectiveFovLH` と同じです）。`shadow_cube` は比較サンプラー付きの `TextureCube` で、面の境界もハードウェアが補間してくれます。

### 線形な距離を保存する方法

**射影後の深度**でなく、**ライトからの線形距離**（`length(v) / light_far`）を、**ピクセル シェーダーで書く**方式もあります。**比較は単純**ですが**ハードウェアの深度テスト・Early-Z を使えない**（深度を自分で書く）ので**描画が遅く**なります。**射影後の深度**が一般的です。

### 面の境界と PCF

**面の境界をまたぐ PCF**は、**隣の面のテクセル**を参照する必要があります。**キューブ マップのハードウェア サンプラー**は、**面をまたぐ補間**を**正しく**処理します。**自前で面ごとの 2D テクスチャ配列**を使うと、**境界で PCF が途切れる**ので、**注意**が必要です。

## キューブマップで、全方向を、覆う

点光源の、光は、**全方向**に、広がります。全方向の、影を、**1 枚の透視投影**では、作れません。**6 つの面**（+X、−X、+Y、−Y、+Z、−Z）、それぞれを、**視野角 90° の、透視投影**で、描き、**キューブマップ**に、保存します。**画素の、光からの方向**で、**どの面を、読むか**が、決まります。

```text
        +Y
         │
   −X ───┼─── +X       （キューブマップの、6 面）
        ╱│
      +Z  −Y                  光を、中心とした、立方体の 6 面に、深度を、保存
```

## DirectX 11 で、キューブマップを、作る

6 つの面を、**テクスチャ配列**（6 スライス）として、作り、**キューブとして、読む**ように、ビューを、設定します。

```cpp
// 点光源のシャドウ キューブマップ（1024×1024 × 6 面）。
D3D11_TEXTURE2D_DESC desc = {};
desc.Width = 1024;
desc.Height = 1024;
desc.MipLevels = 1;
desc.ArraySize = 6;                                         // 6 面
desc.Format = DXGI_FORMAT_R32_TYPELESS;
desc.SampleDesc.Count = 1;
desc.Usage = D3D11_USAGE_DEFAULT;
desc.BindFlags = D3D11_BIND_DEPTH_STENCIL | D3D11_BIND_SHADER_RESOURCE;
desc.MiscFlags = D3D11_RESOURCE_MISC_TEXTURECUBE;           // キューブとして、使える
device->CreateTexture2D(&desc, nullptr, &shadow_cube_tex);

// 各面に書き込む DSV（6 つ）。
for (UINT face = 0; face < 6; ++face) {
  D3D11_DEPTH_STENCIL_VIEW_DESC dsv = {};
  dsv.Format = DXGI_FORMAT_D32_FLOAT;
  dsv.ViewDimension = D3D11_DSV_DIMENSION_TEXTURE2DARRAY;
  dsv.Texture2DArray.FirstArraySlice = face;
  dsv.Texture2DArray.ArraySize = 1;
  device->CreateDepthStencilView(shadow_cube_tex.Get(), &dsv, &face_dsv[face]);
}

// 読み取り用: キューブとして。
D3D11_SHADER_RESOURCE_VIEW_DESC srv = {};
srv.Format = DXGI_FORMAT_R32_FLOAT;
srv.ViewDimension = D3D11_SRV_DIMENSION_TEXTURECUBE;
srv.TextureCube.MipLevels = 1;
device->CreateShaderResourceView(shadow_cube_tex.Get(), &srv, &shadow_cube_srv);
```

## 6 面の、行列

各面の、**向き**（前、上方向）を、**決まりに従って**、決めます。**視野角は、90°**、**アスペクト比 1**。

```cpp
using namespace DirectX::SimpleMath;

// キューブの 6 面の、向きと、上方向。+X, −X, +Y, −Y, +Z, −Z の順（DirectX の、キューブの面の順）。
const Vector3 kForward[6] = {{1, 0, 0}, {-1, 0, 0}, {0, 1, 0}, {0, -1, 0}, {0, 0, 1}, {0, 0, -1}};
const Vector3 kUp[6] =      {{0, 1, 0}, {0, 1, 0}, {0, 0, -1}, {0, 0, 1}, {0, 1, 0}, {0, 1, 0}};

for (int face = 0; face < 6; ++face) {
  Matrix view = Matrix::CreateLookAt(light.position, light.position + kForward[face], kUp[face]);
  Matrix proj = Matrix::CreatePerspectiveFieldOfView(DirectX::XM_PIDIV2, 1.0f, near_z, light.range);
  face_view_proj[face] = view * proj;
}
```

!!! warning "面の、向きと、上方向は、DirectX の、キューブの規約に、合わせる"
    キューブマップの、各面の、**上方向と、左右**は、**規約**で、決まっています。**間違えると**、**面が、回転、反転**して、**影が、ずれたり、つぎはぎ**になります。**シェーダーの、キューブの読み方**（方向ベクトル）と、**シャドウ パスの、行列**を、**合わせる**。**書き込みと、読み込みで、同じ規約**を、使うことが、肝心です。

## 6 面を、描く

```cpp
// 6 面のそれぞれに、深度を描く。各面ごとに、光の行列を、変える。
for (int face = 0; face < 6; ++face) {
  context->OMSetRenderTargets(0, nullptr, face_dsv[face].Get());
  context->ClearDepthStencilView(face_dsv[face].Get(), D3D11_CLEAR_DEPTH, 1.0f, 0);
  UpdateLightCB(face_view_proj[face]);
  DrawShadowCasters(face);                   // この面の視錐台に入る物だけ（面ごとに、カリング）
}
```

**面ごとの、視錐台カリング**が、重要です。**ある面の、視錐台に入らない物**は、その面で、**描かない**。**全部の物を、6 回描く**と、**重い**です。

## シェーダーで、読む

**画素の、光からの方向ベクトル**で、キューブマップを、読みます。**どの面を、読むか**は、**ハードウェアが、方向の、最大の成分**から、**自動で**、決めます。

```hlsl
TextureCube<float> g_shadow_cube : register(t6);
SamplerComparisonState g_shadow_sampler : register(s5);

float PointShadow(float3 world_pos, float3 world_normal) {
  float3 to_pixel = world_pos - g_light_position;               // 光から、画素へ向かう、方向
  // 法線オフセット（距離に応じて）
  float dist = length(to_pixel);
  float3 offset = world_normal * normal_offset;
  float3 dir = to_pixel + offset;

  // この方向で、どの面か、ハードウェアが、決めて、その面の、深度を読む。
  // 比較に使う深度は、その面の、射影で変換した値。面ごとに、射影を適用する必要がある。
  float3 abs_dir = abs(dir);
  float major = max(abs_dir.x, max(abs_dir.y, abs_dir.z));        // 最大の成分（奥行き方向の距離）
  // 透視投影の、深度（非線形）を、再現する: z' = (f / (f − n)) × (1 − n / major)
  float depth = (g_far / (g_far - g_near)) * (1.0 - g_near / major);
  return g_shadow_cube.SampleCmpLevelZero(g_shadow_sampler, dir, depth);
}
```

**深度の、再現**が、ポイントです。シャドウ パスで、書かれた、深度は、**面の透視投影**で、変換された値で、**その面での、奥行き成分**（`dir` の、最大成分）で、決まります。**メイン パスでも、同じ変換**を、**再現**して、比べる必要があります。

**距離を、直接、保存**する方法（[Point and Spot Light Shadows](index.md)）なら、**この変換**は、**不要**になります。

## 面の、継ぎ目

キューブの、**面の境界**で、PCF などの、フィルタが、**隣の面**の、情報を、**読めない**ことがあります。**境界で、影が、途切れる**、**線が出る**ことがあります。

| 対策 | 内容 |
| --- | --- |
| **視野角を、少し、広げる**（90° → 91°〜92°） | 各面が、**隣の面と、少し、重なる**。境界の、フィルタが、**自分の面の、内側**で、完結する |
| キューブマップの、**ハードウェア フィルタ** | `TextureCube` の、サンプラーは、**面の境界を、またいで**、補間する（シームレス キューブマップ。DirectX 11 では、標準） |

## 解像度と、コスト

| 解像度 | メモリ（`D32_FLOAT`、6 面） | 用途 |
| --- | --- | --- |
| 512×512 | 6 MB | 小さい光、遠くの光 |
| 1024×1024 | 24 MB | 標準 |
| 2048×2048 | 96 MB | 主要な光（高品質） |

**1 つの、点光源**で、**6 面**を、描き、メモリも、大きいので、**影を、落とす点光源の数は、限る**（**画面の、近くの、重要な、光だけ**）。

## よくあるミス

??? failure "キューブ マップの面の継ぎ目に線が出る"
    **PCF のサンプルが面を跨ぐ**ので、**方向ベクトルでサンプル**し、**境界の処理**をする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **点光源の影 ＝ 6 面のキューブ マップ**
    - [x] **方向ベクトルで引く**。**コストは 6 倍**

## 参考

- Brabec, Annen, Seidel, "Shadow Mapping for Hemispherical and Omnidirectional Light Sources", Advances in Modelling, Animation and Rendering (Computer Graphics International 2002)（放物面マッピング）
- Olsson, Billeter, Assarsson, "Clustered Deferred and Forward Shading", High-Performance Graphics 2012
- Microsoft Learn, "Common Techniques to Improve Shadow Depth Maps"
- Microsoft Learn, "D3D11_RESOURCE_MISC_FLAG"（`D3D11_RESOURCE_MISC_TEXTURECUBE`）

## 関連ページ

- [Point and Spot Light Shadows](index.md)
- [Spot Lights](spot-light.md)
- [Dual Paraboloid](dual-paraboloid.md)
