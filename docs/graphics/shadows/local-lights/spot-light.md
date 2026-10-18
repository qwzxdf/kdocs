---
title: Spot Lights
tags:
  - 描画
---

# Spot Lights

**スポットライトは、円錐状に光を照らす**ので、**光の位置から円錐の中心方向を向いた、透視投影の 1 枚のシャドウ マップ**で**影を作れます**。**平行光の正射影より、距離で解像度が変わる（近いほど細かい）**ことに**注意**します。このページでは、**スポットライトのシャドウ マップの作り方・視野角・解像度**を説明します。

!!! tip "ポイント"
    - **スポットライトの影 ＝ 透視投影の 1 枚のシャドウ マップ**。
    - **視野角 ＝ 円錐の外側の角度**（**少し余裕**を持つ）。
    - **比較の深度は、距離に対して非線形**。**線形深度で保存**すると**扱いやすい**。
    - **近い面・遠い面**を**ライトの範囲**に**合わせる**。

## スポットライト
**スポットライト**の光は、**位置・向き・円錐の角度**で決まります。**円錐の外には光が届かない**ので**円錐を覆う透視投影**の**シャドウ マップ 1 枚**で済みます。

スポットライトのシャドウ マップの設定です。ビュー行列は、ライトの位置と向きから作ります（`XMMatrixLookToLH`）。射影行列は、視野角を円錐の全角、アスペクト比を 1 にして、近遠はライトの範囲にします。シャドウ マップは正方形の 1 枚です。

スポットライトの影は、1 枚のシャドウ マップで済むので、ローカル ライトの影の中では最も安く、品質も安定しています。そのため、「点光源を、向きの違う複数のスポットライトで近似する」「どうしても点光源の影が必要な所だけキューブ マップを使う」といった設計もよく行われます。

```cpp
XMMATRIX view = XMMatrixLookToLH(light_position, light_direction, up);
XMMATRIX proj = XMMatrixPerspectiveFovLH(outer_cone_angle * 2.0f, 1.0f, near_z, light_range);
```

**近クリップ面**を**小さくしすぎない**ことが大切です。**近すぎる**と**深度の精度**が**遠くで足りなく**なります（透視投影の深度は、近くに集中）。

## スポットライトの、影は、1 枚

スポットライトは、**円錐状**に、光を出すので、**透視投影の、シャドウ マップ 1 枚**で、**影を、作れます**。**光の位置**に、カメラを置き、**円錐の、向き**を、見て、**円錐の、開き角**を、**視野角**にします。

```cpp
using namespace DirectX::SimpleMath;

// スポットライトの、光の行列（右手系、行ベクトル）。
Matrix SpotLightMatrix(const SpotLight& spot) {
  Vector3 position = spot.position;
  Vector3 target = spot.position + spot.direction;
  // 上方向は、光の向きと、平行にならない軸を選ぶ。
  Vector3 up = (std::abs(spot.direction.y) > 0.99f) ? Vector3::UnitZ : Vector3::UnitY;
  Matrix view = Matrix::CreateLookAt(position, target, up);

  // 視野角 = 外側の円錐の全角。170° を超えない（透視投影が破綻する）。
  float fov = std::min(2.0f * spot.outer_angle, DirectX::XMConvertToRadians(170.0f));
  Matrix proj = Matrix::CreatePerspectiveFieldOfView(fov, 1.0f, spot.near_z, spot.range);
  return view * proj;
}
```

| パラメーター | 目安 | 内容 |
| --- | --- | --- |
| `fov` | `2 × 外側の円錐の半角` | 円錐が、ちょうど、シャドウ マップに、収まる |
| `near_z` | 0.1〜1 m | **できるだけ、大きく**（深度の精度を、守る） |
| `range` | 光の、到達距離 | これを超えた所は、光が、当たらない。**ファー面** |

## 深度の、精度とバイアス

**透視投影**では、深度が、**非線形**です。**近くで、精度が、高く**、**遠くで、粗い**。**同じバイアスでも、距離によって、ワールドでの、大きさが違う**ので、**調整が、難しい**です。

| 対策 | 内容 |
| --- | --- |
| `near_z` を、大きく | ニア面を、**可能な限り、遠く**に。精度の、無駄が、減る |
| **線形深度**で、比べる | シャドウ パスで、**距離（線形）**を、書き込み、比較する（上の、[Point and Spot Light Shadows](index.md) の、距離の保存） |
| **法線オフセット** | 深度を、いじらず、**位置を**ずらす。**距離に応じて、ずらす量を、スケール**（[Normal Offset](../bias/normal-offset.md)） |
| **ハードウェアの、傾き依存バイアス** | `SlopeScaledDepthBias`（[Slope-Scale Bias](../bias/slope-scale-bias.md)） |

```hlsl
// 透視投影の、シャドウ マップの、画素の、ワールドでの、大きさ（距離に比例）を、法線オフセットに使う。
float texel_world = 2.0 * distance_to_light * tan(0.5 * fov) / shadow_resolution;
float3 offset = world_normal * (sin_theta * texel_world * 2.0);
```

## スポット ライトの、影の、判定

```hlsl
float SpotShadow(float3 world_pos, float3 world_normal) {
  // 法線オフセット（上記）
  float3 p = world_pos + world_normal * normal_offset;
  float4 light_clip = mul(float4(p, 1.0), g_spot_view_proj);
  // 透視投影なので、w で割る（正射影と違う）
  float3 ndc = light_clip.xyz / light_clip.w;
  float2 uv = ndc.xy * float2(0.5, -0.5) + 0.5;

  // 光の後ろ側（w が負）は、影の判定をしない（光が当たらない）
  if (light_clip.w <= 0.0) return 1.0;
  if (any(uv < 0.0) || any(uv > 1.0)) return 1.0;                // 円錐の外
  return g_spot_shadow.SampleCmpLevelZero(g_shadow_sampler, uv, ndc.z);
}
```

**`w` で割る**ことを、**忘れない**（太陽の、正射影では、`w = 1`）。**光の後ろ側**（`w ≤ 0`）の画素は、**円錐の外**なので、**そもそも、光が、当たらない**。

## 効率

| 工夫 | 内容 |
| --- | --- |
| **円錐に、収まる物だけを、描く** | 光の、**視錐台**で、物を、**カリング** |
| **解像度を、光の、画面上の大きさに、合わせる** | **画面で、小さい光**は、**シャドウ マップも、小さく**（512×512 など）。大きな光は、大きく（2048×2048） |
| **更新を、間引く** | **静止した光 + 静止した物**なら、**一度作って、保存**（キャッシュ）。**動く物だけ**を、毎フレーム、足す（[Shadows for Many Lights](many-lights.md)） |
| **光の、範囲外**では、**影を、省く** | 画面に、映らない、光の影は、**描かない** |

## 複数の、スポットライト

**複数の、スポットライトの、シャドウ マップ**は、**1 枚の、大きなテクスチャ（アトラス）**に、**並べる**、または、**テクスチャ配列**に、まとめます。

| 方法 | 内容 |
| --- | --- |
| **アトラス** | 1 枚の、大きなテクスチャに、各ライトの、シャドウ マップを、**タイルとして**配置。**1 つのテクスチャ**を、シェーダーに、渡せる。**ライトごとに、UV の、変換**が、必要 |
| **テクスチャ配列** | `Texture2DArray`。**スライス番号**で、ライトを、選ぶ。**同じ解像度**が、必要 |

## よくあるミス

??? failure "円錐の縁で、影が切れる"
    **視野角に少し余裕**を持たせる。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **スポットの影 ＝ 透視投影 1 枚**
    - [x] **視野角・近い面・遠い面を、ライトの範囲に合わせる**

## 参考

- Williams, "Casting Curved Shadows on Curved Surfaces", SIGGRAPH 1978
- Microsoft Learn, "Common Techniques to Improve Shadow Depth Maps"
- Olsson, Billeter, Assarsson, "Clustered Deferred and Forward Shading", High-Performance Graphics 2012
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（影の章）

## 関連ページ

- [Point and Spot Light Shadows](index.md)
- [Point Lights: Cube Maps](point-cubemap.md)
- [The Light Matrix](../shadow-map-basics/light-matrix.md)
