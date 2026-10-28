---
title: Spot Lights
tags:
  - 描画
---

# Spot Lights

<strong>スポットライトは円錐状に光を照らす</strong>ので、光の位置から円錐の中心方向を向いた、透視投影の 1 枚のシャドウ マップで影を作れます。平行光の正射影より距離で解像度が変わる（近いほど細かい）ことに注意します。このページではスポットライトのシャドウ マップの作り方・視野角・解像度を説明します。

!!! tip "ポイント"
    - スポットライトの影 ＝ 透視投影の 1 枚のシャドウ マップ。
    - 視野角 ＝ 円錐の外側の角度（少し余裕を持つ）。
    - 比較の深度は距離に対して非線形。線形深度で保存すると扱いやすい。
    - 近い面・遠い面をライトの範囲に合わせる。

!!! info "このページを読む前に"
    - [Point and Spot Light Shadows](index.md)（このセクション全体の地図と、読む順番）
    - [MVP 変換（モデル・ビュー・プロジェクション）](../../../3d/transforms-mvp.md)（座標変換（ワールド・ビュー・射影）の流れ）
    - [GPU Pipeline Overview](../../../directx/concepts/gpu-pipeline.md)（GPU のパイプラインの流れ）

## スポットライト
<strong>スポットライト</strong>の光は 位置・向き・円錐の角度で決まります。円錐の外には光が届かないので円錐を覆う透視投影のシャドウ マップ 1 枚で済みます。

スポットライトのシャドウ マップの設定です。ビュー行列はライトの位置と向きから作ります（`XMMatrixLookToLH`）。射影行列は視野角を円錐の全角、アスペクト比を 1 にして近遠はライトの範囲にします。シャドウ マップは正方形の 1 枚です。

スポットライトの影は 1 枚のシャドウ マップで済むので、ローカル ライトの影の中では最も安く、品質も安定しています。そのため、「点光源を向きの違う複数のスポットライトで近似する」「どうしても点光源の影が必要な所だけキューブ マップを使う」といった設計もよく行われます。

```cpp
XMMATRIX view = XMMatrixLookToLH(light_position, light_direction, up);
XMMATRIX proj = XMMatrixPerspectiveFovLH(outer_cone_angle * 2.0f, 1.0f, near_z, light_range);
```

近クリップ面を小さくしすぎないことが大切です。近すぎると深度の精度が遠くで足りなくなります（透視投影の深度は、近くに集中）。

## スポットライトの影は 1 枚

スポットライトは <strong>円錐状</strong>に、光を出すので 透視投影のシャドウ マップ 1 枚で影を作れます。光の位置にカメラを置き円錐の向きを見て円錐の、開き角を視野角にします。

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
| `fov` | `2 × 外側の円錐の半角` | 円錐がちょうど、シャドウ マップに収まる |
| `near_z` | 0.1〜1 m | できるだけ、大きく（深度の精度を守る） |
| `range` | 光の到達距離 | これを超えた所は光が当たらない。ファー面 |

## 深度の精度とバイアス

<strong>透視投影</strong>では深度が 非線形です。近くで精度が高く遠くで粗い。同じバイアスでも距離によって、ワールドでの大きさが違うので調整が難しいです。

| 対策 | 内容 |
| --- | --- |
| `near_z` を大きく | ニア面を可能な限り遠くに。精度の無駄が減る |
| 線形深度で比べる | シャドウ パスで、距離（線形）を書き込み比較する（上の、[Point and Spot Light Shadows](index.md) の、距離の保存） |
| 法線オフセット | 深度をいじらず位置をずらす。距離に応じてずらす量をスケール（[Normal Offset](../bias/normal-offset.md)） |
| ハードウェアの傾き依存バイアス | `SlopeScaledDepthBias`（[Slope-Scale Bias](../bias/slope-scale-bias.md)） |

```hlsl
// 透視投影の、シャドウ マップの、画素の、ワールドでの、大きさ（距離に比例）を法線オフセットに使う。
float texel_world = 2.0 * distance_to_light * tan(0.5 * fov) / shadow_resolution;
float3 offset = world_normal * (sin_theta * texel_world * 2.0);
```

## スポット ライトの影の判定

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

<strong>`w` で割る</strong>ことを 忘れない（太陽の、正射影では `w = 1`）。光の後ろ側（`w ≤ 0`）の画素は円錐の外なので、そもそも光が当たらない。

## 効率

| 工夫 | 内容 |
| --- | --- |
| 円錐に収まる物だけを描く | 光の、視錐台で物をカリング |
| 解像度を光の画面上の大きさに、合わせる | 画面で小さい光は、シャドウ マップも小さく（512×512 など）。大きな光は大きく（2048×2048） |
| 更新を間引く | 静止した光 + 静止した物なら、一度作って保存（キャッシュ）。動く物だけを毎フレーム、足す（[Shadows for Many Lights](many-lights.md)） |
| 光の範囲外では影を省く | 画面に映らない光の影は描かない |

## 複数のスポットライト

<strong>複数のスポットライトのシャドウ マップ</strong>は、1 枚の大きなテクスチャ（アトラス）に並べるまたは、テクスチャ配列にまとめます。

| 方法 | 内容 |
| --- | --- |
| アトラス | 1 枚の大きなテクスチャに各ライトのシャドウ マップをタイルとして配置。1 つのテクスチャをシェーダーに渡せる。ライトごとに UV の変換が必要 |
| テクスチャ配列 | `Texture2DArray`。スライス番号でライトを選ぶ。同じ解像度が必要 |

## よくあるミス

??? failure "円錐の縁で、影が切れる"
    <strong>視野角に少し余裕</strong>を持たせる。

## これだけ覚える

!!! abstract "まとめ"
    - [x] スポットの影 ＝ 透視投影 1 枚
    - [x] 視野角・近い面・遠い面をライトの範囲に合わせる

## 参考

- Williams, "Casting Curved Shadows on Curved Surfaces", SIGGRAPH 1978
- Microsoft Learn, "Common Techniques to Improve Shadow Depth Maps"
- Olsson, Billeter, Assarsson, "Clustered Deferred and Forward Shading", High-Performance Graphics 2012
- Akenine-Möller, Haines, Hoffman, Pesce, Iwanicki, Hillaire, "Real-Time Rendering", 4th Edition, CRC Press, 2018（影の章）

## 関連ページ

- [Point and Spot Light Shadows](index.md)
- [Point Lights: Cube Maps](point-cubemap.md)
- [The Light Matrix](../shadow-map-basics/light-matrix.md)
