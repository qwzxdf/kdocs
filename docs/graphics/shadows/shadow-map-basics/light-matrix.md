---
title: The Light Matrix
tags:
  - 描画
---

# The Light Matrix

<strong>シャドウ マップを作るには、「光から見た世界」を描く</strong>必要があり、そのためのビュー行列と射影行列（光の行列）を作ります。光の種類で射影が変わります：太陽（平行光）は正射影、スポットライトは透視投影、点光源はキューブ マップの 6 方向です。このページではそれぞれの行列の作り方・範囲の決め方・点光源の 6 方向を説明します。

!!! tip "ポイント"
    - 平行光（太陽）：正射影。光の向きにカメラを置き見える範囲を箱で囲む。
    - スポットライト：透視投影。視野角 ＝ 円錐の角度の 2 倍。
    - 点光源：90° の透視投影を 6 面（キューブ マップ）。
    - 範囲（箱・近い面・遠い面）を、狭く決めると解像度が無駄にならない。

## ① 光の行列
<!-- fig:light-frustum:begin -->

<svg class="fig illust motion" data-fig="light-frustum" viewBox="0 0 780 420" role="img"><rect x="0" y="0" width="780" height="420" rx="14" fill="#ffffff"/>
<defs><marker id="arr-light-frustum" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#1f2937"/>
</marker>
</defs>
<text x="20" y="28" text-anchor="start" style="font-size:17px;font-weight:700;fill:#1f2937">光の行列:平行光は「箱」、スポットは「錐」でシーンを捉える</text>
<rect x="40" y="300" width="700" height="14" fill="#d6c7a1"/>
<rect x="220" y="230" width="34" height="70" fill="#b8794b" stroke="#7a4b2a" stroke-width="1.5"/>
<rect x="360" y="190" width="34" height="110" fill="#b8794b" stroke="#7a4b2a" stroke-width="1.5"/>
<rect x="480" y="240" width="34" height="60" fill="#b8794b" stroke="#7a4b2a" stroke-width="1.5"/>
<rect x="590" y="210" width="34" height="90" fill="#b8794b" stroke="#7a4b2a" stroke-width="1.5"/>
<polygon points="0,0 0,0 0,0 0,0" fill="#2563eb" fill-opacity="0.12" stroke="#2563eb" stroke-width="3"><animate attributeName="points" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.0663;0.0667;0.3333;0.5833;0.9167;1.0000" values="0,0 0,0 0,0 0,0;0,0 0,0 0,0 0,0;160,90 620,90 620,305 160,305;160,90 620,90 620,305 160,305;370,90 410,90 640,305 140,305;370,90 410,90 640,305 140,305;370,90 410,90 640,305 140,305"/></polygon>
<circle cx="390" cy="70" r="12" fill="#e5aa28" stroke="#ffffff" stroke-width="2"/>
<text x="410" y="66" text-anchor="start" style="font-size:13px;font-weight:700;fill:#e5aa28">光</text>
<text x="40" y="56" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">平行光（太陽）:光線は平行 → 正射影（箱）。範囲が一定<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.3330;0.3333;1.0000" values="1;1;0;0"/></text>
<text x="40" y="56" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">光を近くへ（点光源・スポットライト）…<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.3330;0.3333;0.5830;0.5833;1.0000" values="0;0;1;1;0;0"/></text>
<text x="40" y="56" text-anchor="start" style="font-size:15px;font-weight:700;fill:#1f2937" opacity="0">スポットライト:光線は 1 点から広がる → 透視投影（錐）<animate attributeName="opacity" dur="12s" repeatCount="indefinite" keyTimes="0.0000;0.5830;0.5833;1.0000;1.0000" values="0;0;1;1;0"/></text>
<text x="40" y="360" text-anchor="start" style="font-size:13px;font-weight:500;fill:#64748b">この箱 / 錐が、シャドウ マップに映る範囲。範囲を狭くするほど、1 テクセルあたりの解像度が上がる。</text>
</svg>

<!-- fig:light-frustum:end -->

### 平行光（太陽）：正射影

平行光は<strong>光が全て平行</strong>なので正射影（遠近感なし）で撮ります。光の向きを前方向にしてシーンの範囲（影を落とす物・受ける物）を覆う箱を決めます。

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
| 光の位置 | シーンの中心から、光の逆向きに十分に離れた所。平行光では位置は本質的ではないが、ビュー行列を作るために必要 |
| 正射影の大きさ | 影を受ける範囲を覆う。大きいほど 1 テクセルが粗い（エイリアシング） |
| 近・遠クリップ | 影を落とす物体が範囲内に入るように |
| 上方向 `Up` | 光の向きと平行だと破綻する（真上からの光）。別の軸を使う |

### スポットライト：透視投影

スポットライトは 一点から円錐状に光が出るので、透視投影で撮ります。視野角はスポットの円錐の角度に合わせます。

### 点光源：キューブマップ

全方向に光が出るので6 方向（キューブマップ）で撮ります（[Point and Spot Light Shadows](../local-lights/index.md)）。

## 光の行列：ビューと射影

シャドウ マップを描くには <strong>光の視点</strong>から見た、ビュー行列と射影行列が必要です。メインのカメラの行列と同じ考え方で、作ります。このサイトの座標系は右手系・Y 上・行ベクトル（`v * M`）です（[座標系](../../../3d/index.md)）。

```text
ワールド座標 → [ビュー行列] → 光の視点の座標 → [射影行列] → 光のクリップ空間 → シャドウ マップの UV と深度
```

## 平行光源（太陽）：正射影

太陽の光は <strong>平行</strong>なので 正射影（遠近感なし）で、描きます。

### ビュー行列

光の向きだけが重要で 位置は影を、落とす範囲の中心から光の逆向きに、離れた所に置きます。

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

影を落とす範囲をちょうど覆う、箱（正射影のボリューム）を、作ります。

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
| `radius` | 影の範囲の半径。小さいほどシャドウ マップの、解像度が有効に使われる。大きいと広く覆えるがぼやける |
| `near_z`、`far_z` | 光の方向の奥行き範囲。影を落とす物がすべて含まれるように、広めに取る |

影を落とす物が範囲の外（光の、さらに手前、たとえば高い山）にあると 影が、欠けます。ニアを手前に延ばすか光の後ろにある、物の深度をクランプします（深度クランプ、`DepthClipEnable = FALSE`）。

## スポットライト：透視投影

スポットライトは <strong>円錐状</strong>に、光を出すので 透視投影で描きます。円錐の開き角が視野角です。

```cpp
Vector3 position = spot.position;
Vector3 target = spot.position + spot.direction;
Matrix light_view = Matrix::CreateLookAt(position, target, Vector3::UnitY);

float fov = 2.0f * spot.outer_angle;                              // 開き角（ラジアン）
float aspect = 1.0f;                                              // シャドウ マップは、正方形
Matrix light_proj = Matrix::CreatePerspectiveFieldOfView(fov, aspect, spot.near_z, spot.range);
Matrix light_view_proj = light_view * light_proj;
```

視野角は 170° 未満に、します（180° に近づくと、透視投影が破綻する）。

## メイン パスで：ワールドから、シャドウ マップの座標へ

メインの描画で各画素の <strong>ワールド座標</strong>を、光の行列で変換しシャドウ マップの UV と深度を、求めます。

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

v を反転（`-0.5`）するのは、NDC の y は上が正で、テクスチャの v は下が正だからです。この反転を忘れると影が上下に、逆転します。

### 変換を 1 つの行列に、まとめる

NDC から UV への変換（`* 0.5 + 0.5`、y の反転）も 行列にして、光の行列と掛けておくとシェーダーが、簡単になります。

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

## 視錐台にぴったり合わせる

太陽の `radius` を <strong>メインのカメラの視錐台</strong>に、合わせて、毎フレーム、計算すると無駄なく解像度を使えます。ただし、カメラが動くたびに範囲が変わり影が、ちらつきます（[Aliasing and Stabilization](aliasing-stabilize.md)）。カスケードでは視錐台を分割して、それぞれに合わせた行列を作ります（[CSM](../cascaded.md)）。

## よくあるミス

??? failure "太陽の範囲を、シーン全体にして影がぼやける"
    <strong>カメラの視錐台を覆う最小の箱</strong>にする（[カスケード](../cascaded.md)）。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 光の種類で射影が違う（正射影・透視・キューブ）
    - [x] 範囲は狭く、必要な所だけ

## 参考

- Williams, "Casting Curved Shadows on Curved Surfaces", SIGGRAPH 1978（シャドウ マップの原典）
- Microsoft Learn, "Common Techniques to Improve Shadow Depth Maps"（Direct3D 11 のドキュメント。バイアス、平行光源、PCF）
- Dimitrov, "Cascaded Shadow Maps", NVIDIA White Paper, 2007
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（影の章）

## 関連ページ

- [Shadow Map Basics](index.md)
- [Rendering Depth](render-depth.md)
- [Cascaded Shadow Maps (CSM)](../cascaded.md)
