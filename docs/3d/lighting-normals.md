---
title: 法線とライティング
tags:
  - 3Dゲーム
---

# 法線とライティング

3D の物体に**陰影**をつけるには、**面が、どちらを向いているか**（**法線**）と、**光が、どちらから来るか**が必要です。このページは、法線の意味、ランバート拡散とブリン・フォンのスペキュラ、**法線を変換するときの落とし穴**（逆転置行列）、DX11 / HLSL のシェーダー例をまとめます。

!!! tip "ポイント"
    - <strong>法線</strong>は、<strong>面に垂直な、長さ 1 のベクトル</strong>。頂点に持たせる。
    - <strong>拡散光（ランバート）</strong>は、<strong>`max(dot(N, L), 0)`</strong>。<strong>L は、面から光への向き</strong>。
    - <strong>スペキュラ（ブリン・フォン）</strong>は、<strong>`pow(max(dot(N, H), 0), 光沢)`</strong>。H は、光と視線の中間。
    - <strong>法線は、ワールド行列では変換しない</strong>。<strong>逆転置行列</strong>で変換する（非一様スケールがあるとき）。
    - シェーダーで、<strong>法線を、毎回 `normalize`</strong> する（補間で、長さがずれる）。
    - ライトの向きは、<strong>光が進む向きではなく、光源へ向かう向き</strong>で持つと、計算が楽。

## 法線

**法線**は、**面に垂直な、長さ 1 のベクトル**です。陰影の計算の、中心です。

```text
          N（法線）
          ↑
   ───────────────  面
```

### 面法線と頂点法線

| 種類 | 説明 | 見た目 |
| --- | --- | --- |
| **面法線** | 三角形ごとに 1 つ（外積で求める） | **カクカク**（フラットシェーディング） |
| **頂点法線** | 頂点ごとに持つ。**隣り合う面の法線の平均** | **滑らか**（スムースシェーディング） |

```cpp
Vector3 FaceNormal(const Vector3& v0, const Vector3& v1, const Vector3& v2) {
  Vector3 n = (v1 - v0).Cross(v2 - v0);
  n.Normalize();
  return n;
}
```

**CCW が表の三角形**なら、<strong>外積の向きが、表（外向き）</strong>になります（右手系）。巻き順が逆だと、法線が内向きになり、**暗く**なります。

## 拡散光（ランバート）

面が、**光に向いているほど明るく**、横を向くと**暗く**なります。**法線と、光への向きの内積**で決まります。

```text
明るさ = max( dot(N, L), 0 )

N と L が同じ向き → 1（最大）　　直角 → 0　　逆向き → 0（負は 0 にする）
```

**L は、面から光源へ向かう向き**です。光が、上から下へ進む（`(0, -1, 0)`）なら、**L は `(0, 1, 0)`** です。逆にすると、陰影が反転します。

## スペキュラ（ブリン・フォン）

**ツヤのある反射**（ハイライト）です。**視線と光の中間のベクトル H** を使います。

```text
H = normalize(L + V)          V は、面から、カメラへの向き
スペキュラ = pow( max(dot(N, H), 0), 光沢 )
```

| 光沢（shininess） | 見た目 |
| --- | --- |
| 小さい（8 など） | ぼんやり広いハイライト（ゴム） |
| 大きい（128 など） | 小さく鋭いハイライト（金属・ガラス） |

## ライトの種類

| 種類 | 向き | 減衰 | 用途 |
| --- | --- | --- | --- |
| **ディレクショナル** | 全体で、同じ向き | なし | 太陽、月 |
| **ポイント** | 光源の位置から、四方へ | 距離で減る | 電球、松明、爆発 |
| **スポット** | 位置 + 向き + 角度の制限 | 距離と角度 | 懐中電灯、ヘッドライト |
| <strong>環境光（アンビエント）</strong> | なし | なし | 影の部分が真っ黒にならないための、一定の明るさ |

## HLSL の例（DX11）

### 頂点シェーダーとピクセルシェーダー

```hlsl
cbuffer Transform : register(b0) {
  row_major float4x4 world;
  row_major float4x4 world_inverse_transpose;
  row_major float4x4 view_proj;
};

cbuffer Light : register(b1) {
  float3 light_direction;   // 面から光源へ向かう向き（正規化済み）
  float pad0;
  float3 light_color;
  float pad1;
  float3 camera_position;
  float shininess;
};

struct VsInput {
  float3 position : POSITION;
  float3 normal : NORMAL;
  float2 uv : TEXCOORD0;
};

struct VsOutput {
  float4 position : SV_POSITION;
  float3 world_position : TEXCOORD1;
  float3 normal : TEXCOORD2;
  float2 uv : TEXCOORD0;
};

VsOutput VSMain(VsInput input) {
  VsOutput output;
  float4 world_pos = mul(float4(input.position, 1.0f), world);
  output.position = mul(world_pos, view_proj);
  output.world_position = world_pos.xyz;
  output.normal = mul(input.normal, (float3x3)world_inverse_transpose);
  output.uv = input.uv;
  return output;
}

Texture2D albedo_texture : register(t0);
SamplerState linear_sampler : register(s0);

float4 PSMain(VsOutput input) : SV_TARGET {
  float3 n = normalize(input.normal);
  float3 l = normalize(light_direction);
  float3 v = normalize(camera_position - input.world_position);
  float3 h = normalize(l + v);

  float diffuse = max(dot(n, l), 0.0f);
  float specular = pow(max(dot(n, h), 0.0f), shininess) * step(0.0f, diffuse);
  float3 ambient = float3(0.1f, 0.1f, 0.12f);

  float3 albedo = albedo_texture.Sample(linear_sampler, input.uv).rgb;
  float3 color = albedo * (ambient + light_color * diffuse) + light_color * specular;
  return float4(color, 1.0f);
}
```

| ポイント | 説明 |
| --- | --- |
| **`row_major`** | SimpleMath の行列を、そのまま渡すため（[MVP](transforms-mvp.md)） |
| **`mul(ベクトル, 行列)`** | 行ベクトル規約 |
| **ピクセルシェーダーで `normalize`** | 頂点から補間された法線は、長さが 1 からずれる |
| **`float pad`** | 定数バッファの **16 バイト境界**（`float3` の後ろに詰め物） |
| **`step(0, diffuse)`** | 光が当たっていない面に、ハイライトが出ないように |

### C++ 側の定数バッファ

```cpp
struct TransformCB {
  Matrix world;
  Matrix world_inverse_transpose;
  Matrix view_proj;
};

struct LightCB {
  Vector3 direction;
  float pad0;
  Vector3 color;
  float pad1;
  Vector3 camera_position;
  float shininess;
};

TransformCB cb;
cb.world = world;
cb.world_inverse_transpose = world.Invert().Transpose();
cb.view_proj = view * proj;
```

**C++ と HLSL の構造体の並びを、そろえます**。`float3` の次に `float` を置くと、ちょうど 16 バイトに収まります。

## 法線の変換（逆転置行列）

!!! warning "法線を、ワールド行列で変換してはいけない"
    **非一様スケール**（`Scale(2, 1, 1)` など）があると、法線が**面に垂直でなくなります**。法線は、**ワールド行列の逆行列の転置**で変換します。

```text
位置：  p' = p × World
法線：  n' = n × transpose( inverse(World) )   → normalize
```

| 場面 | 法線の変換 |
| --- | --- |
| **回転と平行移動だけ**（スケールなし） | ワールド行列の回転部分で、よい |
| **一様スケール**（`Scale(2,2,2)`） | 回転部分でよい。**`normalize`** は必須 |
| **非一様スケール** | **逆転置行列が必要** |
| **迷ったら** | **逆転置行列**（安全） |

逆転置行列は、**物体ごとに、C++ で 1 回**計算して、定数バッファで渡します。**ピクセルごとに、シェーダーで逆行列を計算しません**（重い）。

## 法線マップ

**テクスチャで、細かい凹凸の法線**を与えると、**頂点数を増やさず**、凹凸を表現できます。

| 要素 | 説明 |
| --- | --- |
| **法線マップ** | RGB に、法線の XYZ（`0..1` → `-1..1`）を入れた、テクスチャ |
| <strong>接空間（タンジェント空間）</strong> | 法線マップの座標系。頂点に、<strong>接線（tangent）</strong> が必要 |
| **TBN 行列** | 接線・従接線・法線から作る、接空間 → ワールドの変換 |

法線マップは、**法線の向きが、モデルの表面に沿っている**前提です。**Y 軸の向き（OpenGL 系と DirectX 系）の違い**で、凹凸が反転することがあります。

## ライトの計算の注意

| 注意 | 説明 |
| --- | --- |
| **ポイントライトの L** | `normalize(light_position - world_position)`。**ピクセルごと**に求める |
| **減衰** | `1 / (1 + k1*d + k2*d*d)` など。**範囲外は 0**にする |
| <strong>色空間（ガンマ）</strong> | 計算は**リニア**空間。表示の前に、ガンマ補正（sRGB のレンダーターゲットなら、自動） |
| **HDR・トーンマッピング** | 明るさが 1 を超えるなら、トーンマッピングで画面に収める |
| **コストの目安** | ピクセルごとの計算。ライト数に比例。多数なら、ディファード・タイルベース |

## よくあるミス

??? failure "陰影が、反転して見える"
    **L の向き**が逆です。L は、**面から光源へ**向かう向きです。

??? failure "拡大・縮小した物体の、陰影がおかしい"
    法線を、ワールド行列で変換しています。**逆転置行列**を使います。

??? failure "カクカク・ギザギザに見える"
    頂点法線が、面法線のままです。**隣の面の法線を平均**します。

??? failure "ハイライトが、光の反対側に出る"
    スペキュラの H や V の向きが、逆です。V は、**面から、カメラへ**。

??? failure "モデル全体が、暗い"
    法線が、**内向き**（巻き順の間違い）、または、`normalize` していません。

??? failure "定数バッファの値が、ずれる"
    `float3` の後ろに、詰め物が足りません。**16 バイト境界**を確認します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>法線</strong>は、面に垂直な長さ 1 のベクトル。<strong>頂点法線</strong>で滑らかに
    - [x] <strong>拡散</strong>＝<strong>`max(dot(N, L), 0)`</strong>（<strong>L は、面から光源へ</strong>）。<strong>スペキュラ</strong>＝<strong>`pow(dot(N, H), 光沢)`</strong>
    - [x] <strong>法線は、逆転置行列で変換</strong>。<strong>C++ で 1 回計算</strong>して渡す
    - [x] <strong>シェーダーで `normalize`</strong>。<strong>定数バッファは 16 バイト境界</strong>

## 関連ページ

- [3D ゲーム（目次）](index.md)
- [変換と MVP](transforms-mvp.md)
- [メッシュとテクスチャ](mesh-textures.md)
- [行列](matrices.md)
