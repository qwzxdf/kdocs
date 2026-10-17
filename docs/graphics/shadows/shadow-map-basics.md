---
title: シャドウ マップの基礎
tags:
  - 描画
---

# シャドウ マップの基礎

**シャドウ マップ**（Shadow Mapping）は、1978 年に Williams が提案した方式で、現在も**最も使われている影の方式**です。発想は単純です。<strong>光源から見て、各方向で「一番手前の面までの距離」</strong>を、あらかじめ<strong>画像（深度マップ）</strong>に撮っておきます。<strong>画面の点が光から見て、その一番手前より奥にあれば、遮られている（影）</strong>、**一番手前なら、光が当たっている**。**深度を比べる**だけで**あらゆる形の影**が作れます。

!!! tip "ポイント"
    - <strong>パス 1</strong>：<strong>光源の視点から、シーンの深度だけを描く</strong>（シャドウ マップ）。
    - <strong>パス 2</strong>：<strong>通常の描画</strong>で各点を<strong>光の座標に変換</strong>し、<strong>シャドウ マップの深度と比べる</strong>。
    - 比べるとき、<strong>光から見た、その点の深度 ＞ マップの深度</strong>なら、影。
    - 平行光（太陽）は<strong>正射影</strong>、スポットライトは<strong>透視投影</strong>、点光源は<strong>6 面（キューブ）</strong>。
    - <strong>比較サンプラー（`SampleCmp`）</strong>で、ハードウェアが比較と、2×2 の補間を一度に行う。
    - 課題：<strong>解像度（エイリアシング）・バイアス・縁のぼかし</strong>。

## 原理

<svg class="fig illust" viewBox="0 0 780 290" role="img" aria-label="シャドウ マップの原理">
<text x="20" y="24" class="fig-title">光から見た一番手前の深度（シャドウ マップ）と、点の深度を比べる</text>
<circle cx="90" cy="130" r="11" fill="#e5a828"/><text x="70" y="112" style="font-size:12px">光源</text>
<rect x="320" y="90" width="26" height="80" fill="rgba(150,150,150,0.6)" stroke="currentColor" stroke-width="2"/><text x="300" y="82" style="font-size:12px">遮蔽物</text>
<line x1="40" y1="250" x2="740" y2="250" stroke="currentColor" stroke-width="4"/>
<line x1="90" y1="130" x2="320" y2="95" stroke="currentColor" stroke-width="1.5" stroke-dasharray="4 3"/>
<line x1="90" y1="130" x2="320" y2="165" stroke="currentColor" stroke-width="1.5" stroke-dasharray="4 3"/>
<line x1="90" y1="130" x2="200" y2="250" stroke="#2ea043" stroke-width="2.5"/>
<circle cx="200" cy="250" r="6" fill="#2ea043"/><text x="150" y="272" style="font-size:12px;fill:#2ea043;font-weight:700">日向（光から一番手前）</text>
<line x1="346" y1="125" x2="470" y2="250" stroke="#e5484d" stroke-width="2.5"/>
<circle cx="470" cy="250" r="6" fill="#e5484d"/><text x="400" y="272" style="font-size:12px;fill:#e5484d;font-weight:700">影（手前に遮蔽物がある）</text>
<text x="500" y="110" style="font-weight:700">シャドウ マップ ＝ 各方向の</text>
<text x="500" y="132" style="font-weight:700">「光から一番手前の面」までの深度</text>
<text x="500" y="164" style="font-size:12px">点の深度 ＞ マップの深度 → 遮られている（影）</text>
<text x="500" y="184" style="font-size:12px">点の深度 ≦ マップの深度 → 光が当たっている</text>
</svg>

## 手順

| 手順 | 内容 |
| --- | --- |
| **① 光のビュー・射影行列を作る** | 光の位置・向きから、**ビュー**と**射影**（平行光は正射影） |
| **② シャドウ マップを描く** | 光の視点から、**影を落とす物体**の深度だけを描く（**ピクセルシェーダーなし**） |
| **③ 通常の描画で光の座標に変換** | 各ピクセルの**ワールド位置**を、**光のクリップ空間**へ |
| **④ シャドウ マップを引く** | 変換した <strong>(u, v)</strong> で、保存された深度を読む |
| **⑤ 深度を比べる** | <strong>自分の深度（光から見た）</strong>が、**保存された深度より奥**なら、影 |

## ① 光の行列

### 平行光（太陽）：正射影

平行光は**光が全て平行**なので**正射影**（遠近感なし）で撮ります。**光の向き**を前方向にして、**シーンの範囲（影を落とす物・受ける物）を覆う箱**を決めます。

```cpp
Matrix LightViewProjection(const Vector3& light_dir, const Vector3& center, float radius) {
  Vector3 light_pos = center - light_dir * radius * 2.0f;
  Matrix view = XMMatrixLookAtLH(light_pos, center, Vector3::Up);
  Matrix proj = XMMatrixOrthographicLH(radius * 2.0f, radius * 2.0f, 0.0f, radius * 4.0f);
  return view * proj;
}
```

| 点 | 説明 |
| --- | --- |
| **光の位置** | **シーンの中心から、光の逆向きに十分に離れた所**。平行光では位置は本質的ではないが、**ビュー行列を作るため**に必要 |
| **正射影の大きさ** | 影を受ける範囲を覆う。**大きいほど、1 テクセルが粗い**（エイリアシング） |
| **近・遠クリップ** | 影を落とす物体が範囲内に入るように |
| **上方向 `Up`** | 光の向きと平行だと破綻する（真上からの光）。別の軸を使う |

### スポットライト：透視投影

**スポットライト**は、**一点から円錐状**に光が出るので、**透視投影**で撮ります。**視野角**はスポットの**円錐の角度**に合わせます。

### 点光源：キューブマップ

**全方向**に光が出るので<strong>6 方向（キューブマップ）</strong>で撮ります（[点光源・スポットライトの影](local-lights.md)）。

## ② シャドウ マップを描く

**深度だけ**を描きます。**ピクセルシェーダーは不要**（アルファ テストする物を除く）で、**非常に速い**描画です。

```cpp
D3D11_TEXTURE2D_DESC desc = {};
desc.Width = 2048;
desc.Height = 2048;
desc.MipLevels = 1;
desc.ArraySize = 1;
desc.Format = DXGI_FORMAT_R32_TYPELESS;
desc.SampleDesc.Count = 1;
desc.BindFlags = D3D11_BIND_DEPTH_STENCIL | D3D11_BIND_SHADER_RESOURCE;
device->CreateTexture2D(&desc, nullptr, &shadow_tex);

D3D11_DEPTH_STENCIL_VIEW_DESC dsv_desc = {};
dsv_desc.Format = DXGI_FORMAT_D32_FLOAT;
dsv_desc.ViewDimension = D3D11_DSV_DIMENSION_TEXTURE2D;
device->CreateDepthStencilView(shadow_tex, &dsv_desc, &shadow_dsv);

D3D11_SHADER_RESOURCE_VIEW_DESC srv_desc = {};
srv_desc.Format = DXGI_FORMAT_R32_FLOAT;
srv_desc.ViewDimension = D3D11_SRV_DIMENSION_TEXTURE2D;
srv_desc.Texture2D.MipLevels = 1;
device->CreateShaderResourceView(shadow_tex, &srv_desc, &shadow_srv);
```

| 点 | 説明 |
| --- | --- |
| **`R32_TYPELESS`** | **深度として書き、シェーダーから読む**ため、型なしで作る |
| **DSV は `D32_FLOAT`、SRV は `R32_FLOAT`** | 同じ領域を、2 通りに見る |
| **解像度** | 1024〜4096。**大きいほど細かい影・メモリと帯域を食う**（[メモリ帯域幅](../../rendering/bandwidth.md)） |
| **フォーマット** | 16 ビットで足りることも多い（精度を許容できれば、帯域が半分） |
| **描画する物** | **影を落とす物だけ**。**ライティングなし**のシェーダー（頂点シェーダーのみ） |

## ③〜⑤ 比較

**ワールド位置**を**光のクリップ空間**に変換し、**シャドウ マップの座標と深度**を得ます。

```hlsl
float ShadowFactor(float3 world_pos) {
  float4 light_clip = mul(float4(world_pos, 1.0), light_view_projection);
  float3 ndc = light_clip.xyz / light_clip.w;

  float2 uv = ndc.xy * float2(0.5, -0.5) + 0.5;
  float depth = ndc.z - bias;

  if (any(uv < 0.0) || any(uv > 1.0) || ndc.z > 1.0) return 1.0;

  return shadow_tex.SampleCmpLevelZero(shadow_sampler, uv, depth);
}
```

| 点 | 説明 |
| --- | --- |
| **`ndc.xy * (0.5, −0.5) + 0.5`** | NDC（−1〜1、y は上向き）を、テクスチャ座標（0〜1、v は下向き）に |
| **`depth = ndc.z − bias`** | **バイアス**で自己影を防ぐ（[バイアス](bias.md)） |
| **範囲外** | シャドウ マップの外は、**影なし**（1）として扱う（または別の扱い） |
| **`SampleCmpLevelZero`** | **比較サンプラー**。**比較して、結果（0〜1）を、2×2 でバイリニア補間** |

### 比較サンプラー

**比較サンプラー**は、**ハードウェアが「保存された深度」と「参照値」を比べる**機能です。結果は**比較が真なら 1、偽なら 0**で**バイリニアで補間**されます（4 点の比較結果を混ぜる）。

```cpp
D3D11_SAMPLER_DESC sampler = {};
sampler.Filter = D3D11_FILTER_COMPARISON_MIN_MAG_LINEAR_MIP_POINT;
sampler.AddressU = sampler.AddressV = sampler.AddressW = D3D11_TEXTURE_ADDRESS_BORDER;
sampler.BorderColor[0] = sampler.BorderColor[1] = sampler.BorderColor[2] = sampler.BorderColor[3] = 1.0f;
sampler.ComparisonFunc = D3D11_COMPARISON_LESS_EQUAL;
device->CreateSamplerState(&sampler, &shadow_sampler);
```

| 設定 | 説明 |
| --- | --- |
| **`COMPARISON_..._LINEAR`** | 4 点の比較結果を**線形補間**（これが最も簡単な PCF） |
| **`ComparisonFunc = LESS_EQUAL`** | **参照値 ≦ 保存された深度**なら 1（光が当たる） |
| **アドレス モード：BORDER、色 1.0** | シャドウ マップの外は、<strong>影なし（1）</strong> |

!!! note "標準 Z のとき"
    標準の Z（near → 0、far → 1）では**遠いほど深度が大きい**ので、`LESS_EQUAL` を使います。**reverse-Z** のときは、`GREATER_EQUAL` です（[投影](../../3d/projection.md)）。

## 問題の整理

| 問題 | 症状 | 原因 | 対策 |
| --- | --- | --- | --- |
| **シャドウ アクネ** | 面に縞・斑点 | 深度の離散化で**自分自身を遮蔽物と誤判定** | [バイアス](bias.md) |
| **ピーター パンニング** | 影が物体から**浮く** | バイアスが大きすぎる | バイアスの調整・法線オフセット |
| **エイリアシング** | 影の縁が**ギザギザ** | シャドウ マップの解像度が足りない | [カスケード](cascaded.md)・高解像度・フィルタ |
| **縁がハード** | 影の縁がくっきりしすぎ | 点での比較（0/1）だけ | [PCF](pcf.md)・[PCSS](pcss.md) |
| **範囲外** | 画面の端で影が途切れる | シャドウ マップの範囲不足 | 範囲の設計・カスケード |
| **透明部分** | 葉・フェンスの影が板状 | 深度だけを描いている | [特殊なケース](special-cases.md) |

## エイリアシングの 2 種類

シャドウ マップは、**解像度が有限**なので**縁がギザギザ**になります。その原因は 2 つに分けられます。

| 種類 | 原因 | 対策 |
| --- | --- | --- |
| **投影エイリアシング** | <strong>光の向きと面の向きが近い（斜め）</strong>と、**1 テクセルが面の上で細長く伸びる** | **スロープ バイアス・面の向きに応じた処理** |
| **遠近エイリアシング** | **カメラの近くは、画面上の 1 ピクセルが、シャドウ マップの 1 テクセルより小さい**（粗く見える）。**遠くは逆に過剰** | <strong>カスケード（距離ごとに分割）</strong>、**射影の工夫**（LiSPSM・TSM など） |

**カメラの近くで細かい影が必要**なのに**マップは全体を均等に**覆っているので、**近くが粗く**、**遠くが無駄**になります。**距離に応じて、解像度を配分**する方式（**カスケード**）が、これを解決します。

## 安定させる：テクセルのスナップ

カメラや光が動くと**シャドウ マップの範囲**が動き、**影の縁がちらつきます**（テクセルの境界がずれるため）。**範囲の位置をテクセル単位に揃える**と、ちらつきが止まります（[カスケード](cascaded.md)）。

## 全体のコード（最小）

```hlsl
Texture2D<float> shadow_tex : register(t5);
SamplerComparisonState shadow_sampler : register(s5);

cbuffer ShadowConstant : register(b3) {
  row_major float4x4 light_view_projection;
  float shadow_bias;
}

float3 Shade(float3 world_pos, float3 N, float3 L, float3 albedo, float3 light_color) {
  float shadow = ShadowFactor(world_pos);
  return albedo * light_color * saturate(dot(N, L)) * shadow;
}
```

## よくあるミス

??? failure "バイアスなしで、平らな面に縞（アクネ）が出る"
    バイアスを入れます（[バイアス](bias.md)）。

??? failure "シャドウ マップを描くときに、表面を描かず、裏面だけを描く（または逆）"
    **カリングの設定**で**表・裏**どちらを描くかを選びます（[バイアス](bias.md)）。

??? failure "比較の向き（`LESS_EQUAL`・`GREATER_EQUAL`）が、reverse-Z と合っていない"
    影が全部ついたり、全部消えたりします。

??? failure "テクスチャ座標の y を反転し忘れて、影が上下逆"
    `uv = ndc.xy * float2(0.5, −0.5) + 0.5`。

??? failure "シャドウ マップの範囲の外が、真っ暗（影）になる"
    ボーダー色を **1.0**（影なし）にします。

??? failure "光や物体が動いて、影の縁がちらつく"
    **テクセルのスナップ**・範囲の安定化をします。

## これだけ覚える

!!! abstract "まとめ"
    - [x] シャドウ マップ ＝ <strong>光から見た深度を撮り、各点を光の座標に変換して、深度を比べる</strong>
    - [x] 平行光は<strong>正射影</strong>、スポットは<strong>透視</strong>、点光源は<strong>キューブ</strong>
    - [x] <strong>比較サンプラー（`SampleCmp`）</strong>で、比較と補間をハードウェアに任せる
    - [x] 課題は<strong>バイアス・エイリアシング（遠近・投影）・縁のぼかし</strong>
    - [x] <strong>カスケード</strong>で距離ごとに解像度を配分。<strong>テクセルのスナップ</strong>でちらつきを止める

## 参考

- Williams, "Casting Curved Shadows on Curved Surfaces"（SIGGRAPH 1978）
- Microsoft, "Common Techniques to Improve Shadow Depth Maps"（DirectX ドキュメント）

## 関連ページ

- [影](index.md)
- [バイアス](bias.md)
- [PCF](pcf.md)
- [カスケード シャドウ マップ](cascaded.md)
- [影のコスト（最適化）](../../rendering/shadows.md)
