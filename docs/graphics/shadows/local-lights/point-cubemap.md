---
title: Point Lights: Cube Maps
tags:
  - 描画
---

# Point Lights: Cube Maps

<strong>点光源は全方向を照らす</strong>ので、影を作るには全方向の深度が必要です。キューブ マップ（6 面）に各方向の深度を描くのが標準で、サンプルはライトから画面の点への方向ベクトルで引くので簡単です。ただし、6 回描くのでコストが 6 倍です。このページではキューブ マップの作り方・方向ベクトルでのサンプル・線形距離の保存・面の境界と PCFを説明します。

!!! tip "ポイント"
    - 点光源の影 ＝ 6 面のキューブ マップ（各面 90° の透視投影）。
    - サンプルは方向ベクトルで引く（面を意識しなくてよい）。
    - 保存は非線形深度より、ライトからの距離（線形）が扱いやすい。
    - 面の境界で PCF のサンプルが隣の面に跨ぐので注意。

!!! info "このページを読む前に"
    - [Point and Spot Light Shadows](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

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
<text x="60" y="70" text-anchor="start" style="font-size:17px;font-weight:700;fill:#2ea043" opacity="0">まとめ:光を中心に 6 つの方向へ<animate attributeName="opacity" dur="13.5s" repeatCount="indefinite" keyTimes="0.0000;0.6664;0.6667;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="60" y="410" text-anchor="start" style="font-size:12px;font-weight:500;fill:#64748b">上から見た図。影を引く時は、光から見た方向ベクトルで、6 面のうちの 1 枚を選ぶ。</text>
</svg>

<!-- fig:point-cubemap-faces:end -->

## 点光源：キューブ マップ
<strong>点光源</strong>はあらゆる方向に光を出します。6 方向（±X, ±Y, ±Z）に視野角 90 度の透視投影で描けば、全方向を覆えます（キューブ シャドウ マップ）。

<svg class="fig illust" viewBox="0 0 780 260" role="img" aria-label="キューブ シャドウ マップ">
<text x="20" y="24" class="fig-title">点光源から 6 方向へ視野角 90 度で描く（真上から見た図）</text>
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

キューブ マップは ライトから画素へのベクトルで、サンプルできます。比較には保存された深度とそのベクトルの長さ（または面ごとの深度）を使います。

```hlsl
float PointShadow(float3 world_pos) {
  float3 v = world_pos - light_position;
  float3 a = abs(v);
  float major = max(a.x, max(a.y, a.z));
  float depth = (light_far * (major - light_near)) / (major * (light_far - light_near));
  return shadow_cube.SampleCmpLevelZero(shadow_sampler, v, depth - bias);
}
```

サンプリングのコードの要点です。`major` は絶対値が最大の成分でその面のビュー空間の z にあたります。`depth` は透視投影の深度の式で射影後の深度（0〜1）に変換します（左手系の `XMMatrixPerspectiveFovLH` と同じです）。`shadow_cube` は比較サンプラー付きの `TextureCube` で、面の境界もハードウェアが補間してくれます。

### 線形な距離を保存する方法

射影後の深度でなく ライトからの線形距離（`length(v) / light_far`）をピクセル シェーダーで書く方式もあります。比較は単純ですがハードウェアの深度テスト・Early-Z を使えない（深度を自分で書く）ので描画が遅くなります。射影後の深度が一般的です。

### 面の境界と PCF

面の境界をまたぐ PCFは、隣の面のテクセルを参照する必要があります。キューブ マップのハードウェア サンプラーは、面をまたぐ補間を正しく処理します。自前で面ごとの 2D テクスチャ配列を使うと、境界で PCF が途切れるので、注意が必要です。

## キューブマップで全方向を覆う

点光源の光は <strong>全方向</strong>に広がります。全方向の影を 1 枚の透視投影では、作れません。6 つの面（+X、−X、+Y、−Y、+Z、−Z）、それぞれを視野角 90° の、透視投影で描きキューブマップに保存します。画素の光からの方向でどの面を読むかが決まります。

```text
        +Y
         │
   −X ───┼─── +X       （キューブマップの、6 面）
        ╱│
      +Z  −Y                  光を、中心とした、立方体の 6 面に、深度を、保存
```

## DirectX 11 で、キューブマップを作る

6 つの面を <strong>テクスチャ配列</strong>（6 スライス）として作り、キューブとして読むように、ビューを設定します。

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

## 6 面の行列

各面の <strong>向き</strong>（前、上方向）を 決まりに従って、決めます。視野角は 90°、アスペクト比 1。

```cpp
using namespace DirectX::SimpleMath;

// キューブの 6 面の、向きと、上方向。+X, −X, +Y, −Y, +Z, −Z の順（DirectX の、キューブの面の順）。
const Vector3 kForward[6] = {{1, 0, 0}, {-1, 0, 0}, {0, 1, 0}, {0, -1, 0}, {0, 0, 1}, {0, 0, -1}};
const Vector3 kUp[6] =      {{0, 1, 0}, {0, 1, 0}, {0, 0, -1}, {0, 0, 1}, {0, 1, 0}, {0, 1, 0}};

for (int face = 0; face < 6; ++face) {
  Matrix view = DirectX::XMMatrixLookAtLH(light.position, light.position + kForward[face], kUp[face]);
  Matrix proj = DirectX::XMMatrixPerspectiveFovLH(DirectX::XM_PIDIV2, 1.0f, near_z, light.range);
  face_view_proj[face] = view * proj;
}
```

!!! warning "面の向きと、上方向は DirectX のキューブの規約に合わせる"
    キューブマップの各面の、上方向と左右は 規約で、決まっています。間違えると面が回転、反転して影がずれたりつぎはぎになります。シェーダーのキューブの読み方（方向ベクトル）と、シャドウ パスの行列を合わせる。書き込みと読み込みで同じ規約を使うことが肝心です。

## 6 面を描く

```cpp
// 6 面のそれぞれに、深度を描く。各面ごとに、光の行列を変える。
for (int face = 0; face < 6; ++face) {
  context->OMSetRenderTargets(0, nullptr, face_dsv[face].Get());
  context->ClearDepthStencilView(face_dsv[face].Get(), D3D11_CLEAR_DEPTH, 1.0f, 0);
  UpdateLightCB(face_view_proj[face]);
  DrawShadowCasters(face);                   // この面の視錐台に入る物だけ（面ごとに、カリング）
}
```

<strong>面ごとの視錐台カリング</strong>が、重要です。ある面の視錐台に入らない物は、その面で描かない。全部の物を 6 回描くと重いです。

## シェーダーで読む

<strong>画素の光からの方向ベクトル</strong>で、キューブマップを読みます。どの面を読むかはハードウェアが方向の、最大の成分から自動で決めます。

```hlsl
TextureCube<float> g_shadow_cube : register(t6);
SamplerComparisonState g_shadow_sampler : register(s5);

float PointShadow(float3 world_pos, float3 world_normal) {
  float3 to_pixel = world_pos - g_light_position;               // 光から、画素へ向かう、方向
  // 法線オフセット（距離に応じて）
  float dist = length(to_pixel);
  float3 offset = world_normal * normal_offset;
  float3 dir = to_pixel + offset;

  // この方向で、どの面か、ハードウェアが決めて、その面の、深度を読む。
  // 比較に使う深度は、その面の、射影で変換した値。面ごとに、射影を適用する必要がある。
  float3 abs_dir = abs(dir);
  float major = max(abs_dir.x, max(abs_dir.y, abs_dir.z));        // 最大の成分（奥行き方向の距離）
  // 透視投影の、深度（非線形）を再現する: z' = (f / (f − n)) × (1 − n / major)
  float depth = (g_far / (g_far - g_near)) * (1.0 - g_near / major);
  return g_shadow_cube.SampleCmpLevelZero(g_shadow_sampler, dir, depth);
}
```

深度の再現がポイントです。シャドウ パスで書かれた深度は、面の透視投影で変換された値で、その面での奥行き成分（`dir` の、最大成分）で決まります。メイン パスでも同じ変換を再現して、比べる必要があります。

距離を直接、保存する方法（[Point and Spot Light Shadows](index.md)）なら、この変換は不要になります。

## 面の継ぎ目

キューブの <strong>面の境界</strong>で PCF などの、フィルタが 隣の面の情報を読めないことがあります。境界で影が途切れる線が出ることがあります。

| 対策 | 内容 |
| --- | --- |
| 視野角を少し広げる（90° → 91°〜92°） | 各面が隣の面と少し重なる。境界のフィルタが自分の面の内側で、完結する |
| キューブマップのハードウェア フィルタ | `TextureCube` の、サンプラーは面の境界をまたいで、補間する（シームレス キューブマップ。DirectX 11 では標準） |

## 解像度とコスト

| 解像度 | メモリ（`D32_FLOAT`、6 面） | 用途 |
| --- | --- | --- |
| 512×512 | 6 MB | 小さい光、遠くの光 |
| 1024×1024 | 24 MB | 標準 |
| 2048×2048 | 96 MB | 主要な光（高品質） |

<strong>1 つの点光源</strong>で 6 面を描き、メモリも大きいので影を落とす点光源の数は、限る（画面の近くの重要な光だけ）。

## よくあるミス

??? failure "キューブ マップの面の継ぎ目に線が出る"
    <strong>PCF のサンプルが面を跨ぐ</strong>ので、方向ベクトルでサンプルし、境界の処理をする。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 点光源の影 ＝ 6 面のキューブ マップ
    - [x] 方向ベクトルで引く。コストは 6 倍

## 参考

- Brabec, Annen, Seidel, "Shadow Mapping for Hemispherical and Omnidirectional Light Sources", Advances in Modelling, Animation and Rendering (Computer Graphics International 2002)（放物面マッピング）
- Olsson, Billeter, Assarsson, "Clustered Deferred and Forward Shading", High-Performance Graphics 2012
- Microsoft Learn, "Common Techniques to Improve Shadow Depth Maps"
- Microsoft Learn, "D3D11_RESOURCE_MISC_FLAG"（`D3D11_RESOURCE_MISC_TEXTURECUBE`）

## 関連ページ

- [Point and Spot Light Shadows](index.md)
- [Spot Lights](spot-light.md)
- [Dual Paraboloid](dual-paraboloid.md)
