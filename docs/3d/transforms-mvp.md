---
title: MVP 変換（モデル・ビュー・プロジェクション）
tags:
  - 3Dゲーム
---

# MVP 変換（モデル・ビュー・プロジェクション）

3D の描画の核心が、**MVP 変換**です。<strong>M（Model：モデル／ワールド）</strong>、<strong>V（View：ビュー）</strong>、<strong>P（Projection：プロジェクション）</strong>の 3 つの行列で、モデルの中の頂点を、画面に映る位置まで、順番に変換します。この 3 つを、**CPU で 1 つの行列（`mvp`）に掛け合わせて、GPU に渡し、頂点シェーダーで頂点に掛ける**のが、基本の流れです。このページは、**3 つの行列がそれぞれ何をするか**、**DirectX 11 で、どう GPU に渡して使うか**を、コードで説明します。

!!! tip "ポイント"
    - <strong>M（ワールド）＝ 物体を世界に置く</strong>。<strong>V（ビュー）＝ カメラから見た座標にする</strong>。<strong>P（プロジェクション）＝ 遠近感をつけて、画面に映る範囲にする</strong>。
    - 掛け順（行ベクトル規約）は <strong>`world * view * proj`</strong>（左から右）。頂点は<strong>左から</strong>掛ける。
    - <strong>CPU で 1 回掛けて</strong>（`mvp`）、<strong>定数バッファ</strong>に入れて、GPU に渡す。<strong>頂点ごとに 3 回掛けない</strong>。
    - HLSL では <strong>`row_major float4x4`</strong> と <strong>`mul(float4(pos, 1), mvp)`</strong>（SimpleMath の行列を、そのまま渡せる）。
    - <strong>`view * proj` は、カメラが同じなら全オブジェクトで共通</strong>。1 回だけ作る。

## 3 つの行列

### M：モデル行列（ワールド行列） {#model}

**モデルの座標（ローカル空間）を、ゲームの世界の座標（ワールド空間）に変換**します。物体の**位置・向き・大きさ**を表します。

```cpp
Matrix world = Matrix::CreateScale(scale)
             * Matrix::CreateFromQuaternion(rotation)
             * Matrix::CreateTranslation(position);
```

物体ごとに、1 つずつ持ちます。動くたびに更新します。

### V：ビュー行列 {#view}

**ワールド空間の座標を、カメラを原点とした座標（ビュー空間）に変換**します。「カメラを世界に置く」変換の**逆**です。

```cpp
// カメラの位置、見ている点、上方向から作る（右手系）
Matrix view = Matrix::CreateLookAt(camera_position, camera_target, Vector3::Up);
```

ビュー空間では、**カメラが原点**にいて、**−Z の方向を見て**（右手系）、**+Y が上、+X が右**です。カメラが動くと、全部の物体の見え方が変わるので、**カメラの更新ごとに作り直す**（1 フレームに 1 回）。詳しくは [カメラ](camera.md) を見てください。

### P：プロジェクション行列

**ビュー空間の座標を、クリップ空間に変換**します。**遠近感**（遠いものが小さく見える）をつけ、<strong>見える範囲（視錐台）</strong>を、標準の箱に変換します。

```cpp
float fov_y = DirectX::XMConvertToRadians(60.0f);          // 縦の視野角
float aspect = width / static_cast<float>(height);          // 画面の縦横比
Matrix proj = Matrix::CreatePerspectiveFieldOfView(fov_y, aspect, 0.1f, 1000.0f);   // near=0.1、far=1000
```

画面のサイズ（ウィンドウの大きさ）が変わったときだけ、作り直します。詳しくは [投影](projection.md) を見てください。

## 掛け合わせる

```cpp
// 行ベクトル規約：頂点に、左から ワールド → ビュー → プロジェクション の順に掛ける
Matrix mvp = world * view * proj;

// 同じカメラの間は、view * proj を共通にして、物体ごとに world だけ掛ける
Matrix view_proj = view * proj;                    // 1 フレームに 1 回
for (Object& obj : objects) {
  Matrix mvp = obj.world * view_proj;              // 物体ごとに 1 回
  Draw(obj, mvp);
}
```

| 計算 | 回数 | 頻度 |
| --- | --- | --- |
| `proj` を作る | 1 | 画面のサイズが変わったとき |
| `view` を作る | 1 | 毎フレーム（カメラが動けば） |
| `view * proj` | 1 | 毎フレーム 1 回 |
| `world`（物体ごと） | 物体の数 | 物体が動いたとき |
| `world * view_proj` | 物体の数 | 毎フレーム、物体ごと |
| 頂点の変換 | **頂点の数** | **GPU が、並列に** |

**頂点ごとの計算は GPU が行う**ので、CPU は、物体ごとの `mvp` を用意するだけです。

## DirectX 11 で、GPU に渡す

行列は、**定数バッファ**（constant buffer）に入れて、頂点シェーダーに渡します。

### 1. 定数バッファの構造体

```cpp
// HLSL の cbuffer と、同じ並びにする（16 バイト単位）
struct PerObjectConstants {
  Matrix world;      // 64 バイト
  Matrix mvp;        // 64 バイト
};
static_assert(sizeof(PerObjectConstants) % 16 == 0, "定数バッファは 16 バイトの倍数");
```

### 2. 定数バッファの作成（最初に 1 回）

```cpp
D3D11_BUFFER_DESC desc = {};
desc.ByteWidth = sizeof(PerObjectConstants);
desc.Usage = D3D11_USAGE_DYNAMIC;                  // 毎フレーム書き換える
desc.BindFlags = D3D11_BIND_CONSTANT_BUFFER;
desc.CPUAccessFlags = D3D11_CPU_ACCESS_WRITE;

Microsoft::WRL::ComPtr<ID3D11Buffer> constant_buffer;
device->CreateBuffer(&desc, nullptr, &constant_buffer);
```

### 3. 毎フレーム、値を書き込んで、頂点シェーダーにセット

```cpp
void DrawObject(ID3D11DeviceContext* context, ID3D11Buffer* cb,
                const Matrix& world, const Matrix& view_proj) {
  D3D11_MAPPED_SUBRESOURCE mapped;
  context->Map(cb, 0, D3D11_MAP_WRITE_DISCARD, 0, &mapped);   // 書き込み用に開く
  auto* data = static_cast<PerObjectConstants*>(mapped.pData);
  data->world = world;
  data->mvp = world * view_proj;                               // CPU で 1 回掛ける
  context->Unmap(cb, 0);

  context->VSSetConstantBuffers(0, 1, &cb);                    // スロット 0（b0）に、頂点シェーダーへ
  // ... 頂点バッファ、インデックス バッファをセットして DrawIndexed
}
```

### 4. HLSL 側（頂点シェーダー）

```hlsl
// SimpleMath の Matrix（行優先）をそのまま受けるために、row_major を指定する
cbuffer PerObject : register(b0) {
  row_major float4x4 world;
  row_major float4x4 mvp;
};

struct VSInput {
  float3 position : POSITION;
  float3 normal   : NORMAL;
  float2 uv       : TEXCOORD0;
};

struct VSOutput {
  float4 position : SV_POSITION;   // クリップ空間の座標（GPU が、w で割って、画面に出す）
  float3 world_normal : NORMAL;
  float2 uv : TEXCOORD0;
};

VSOutput main(VSInput input) {
  VSOutput output;
  output.position = mul(float4(input.position, 1.0f), mvp);   // 行ベクトル × 行列（v * M）
  output.world_normal = mul(input.normal, (float3x3)world);   // 法線を、ワールド空間へ（簡易版）
  output.uv = input.uv;
  return output;
}
```

| 部分 | 意味 |
| --- | --- |
| `row_major float4x4` | メモリの並びが行優先であることを、HLSL に教える。**SimpleMath の `Matrix` を、転置せずに渡せる** |
| `mul(v, M)` | **行ベクトル × 行列**。C++ の `v * M` と同じ意味 |
| `float4(input.position, 1.0f)` | 位置なので、**w = 1** |
| `SV_POSITION` | クリップ空間の座標。<strong>GPU が、w で割る（透視除算）</strong>ところまで、やってくれる |

!!! note "列優先（既定）で受けたいとき"
    `row_major` を付けずに、C++ 側で **`.Transpose()`**（転置）して送る方法もあります。DirectX の古い資料では、「`XMMatrixTranspose` で転置して送り、HLSL で `mul(M, v)`」と書かれていることが多いです。**どちらかに統一**します（このカテゴリは `row_major` + `mul(v, M)`）。

### ピクセル シェーダーとの組み合わせ

頂点シェーダーが、クリップ空間の座標を返すと、GPU が、<strong>透視除算（w で割る）</strong>と**ビューポート変換**を行い、三角形を**ピクセルに分解**（ラスタライズ）して、ピクセル シェーダーを呼びます。<strong>この 2 つは、固定機能（自動）</strong>で、自分では書きません。

```text
頂点シェーダー  → クリップ空間の座標（float4）を返す
   ↓ （GPU が自動）：w で割る → ビューポート変換 → ラスタライズ
ピクセル シェーダー → ピクセルの色を返す
```

## ビューポート（画面への変換）

**ビューポート**は、NDC（−1〜1）の座標を、**画面のピクセル**に変換する設定です。DirectX 11 では、`RSSetViewports` で設定します。

```cpp
D3D11_VIEWPORT viewport = {};
viewport.TopLeftX = 0.0f;
viewport.TopLeftY = 0.0f;
viewport.Width = static_cast<float>(width);
viewport.Height = static_cast<float>(height);
viewport.MinDepth = 0.0f;       // 深度の範囲（0〜1）
viewport.MaxDepth = 1.0f;
context->RSSetViewports(1, &viewport);
```

NDC の `(x, y)` が、画面のピクセル `(sx, sy)` に変換されます（Direct3D の画面は、**左上が原点、Y が下向き**）。

```text
sx = (x_ndc * 0.5 + 0.5) * width
sy = (1 - (y_ndc * 0.5 + 0.5)) * height     ← Y は上下が反転する
```

## 手で変換して、確かめる

GPU が行っている計算を、**CPU で再現**できます（デバッグ、ピッキング、UI の位置合わせに使います）。

```cpp
// ワールド座標の点が、画面のどこに映るか
Vector3 WorldToScreen(const Vector3& world_pos, const Matrix& view, const Matrix& proj,
                      float width, float height) {
  Vector4 clip = Vector4::Transform(Vector4(world_pos.x, world_pos.y, world_pos.z, 1.0f), view * proj);
  if (clip.w <= 0.0f) {
    return Vector3(-1.0f, -1.0f, -1.0f);                 // カメラの後ろ
  }
  float inv_w = 1.0f / clip.w;
  Vector3 ndc(clip.x * inv_w, clip.y * inv_w, clip.z * inv_w);   // 透視除算
  return Vector3((ndc.x * 0.5f + 0.5f) * width,
                 (1.0f - (ndc.y * 0.5f + 0.5f)) * height,        // Y を反転
                 ndc.z);                                          // 深度（0〜1）
}
```

SimpleMath の `Viewport::Project` でも、同じことができます（[SimpleMath](simplemath.md)）。**敵の頭上に HP バー**を出す、**3D の位置に、UI を重ねる**ときに使います。

## 規約の確認

3D の画面が、**何も映らない・反転する・歪む**ときは、規約のずれを疑います。

| 確認すること | 内容 |
| --- | --- |
| **掛け順** | `world * view * proj`（行ベクトル）。`proj * view * world` と書いていないか |
| **座標系** | ビュー・プロジェクションが、**両方とも右手系**（`CreateLookAt` と `CreatePerspectiveFieldOfView`）か |
| **HLSL の行列の並び** | `row_major` を付けたか。付けないなら、転置して送ったか |
| **`mul` の順番** | `mul(float4(pos, 1), mvp)`（ベクトルが左） |
| **三角形の表** | CCW が表なら、`FrontCounterClockwise = TRUE`（[深度とカリング](depth-culling.md)） |
| **w の値** | 位置は `w = 1`、方向は `w = 0` |
| **near / far** | near が 0 や負でないか（[投影](projection.md)） |

## ゲームでの使いどころ

| 場面 | 使い方 |
| --- | --- |
| 物体を描く | 物体ごとに `world` を作り、`world * view_proj` を定数バッファへ |
| 多数の同じ物体 | インスタンシング。`world` の配列を、頂点バッファか構造化バッファで渡す（[描画の最適化](../optimize/rendering.md)） |
| カメラが動く | `view` を作り直して、`view_proj` を更新 |
| ウィンドウをリサイズ | `proj`（アスペクト比）とビューポートを更新 |
| 3D の位置に、UI（HP バー）を出す | `WorldToScreen` で、画面の座標に |
| デバッグ表示（線・球） | `view_proj` を使って、ワールド座標の線を描く |

## よくあるミス

??? failure "掛け順を逆にして、何も映らない"
    行ベクトル規約では `world * view * proj` です。`proj * view * world` にすると、変換が逆順になって、物体が画面の外へ行きます。

??? failure "HLSL で行列が転置されて、画面がめちゃくちゃになる"
    SimpleMath（行優先）と HLSL（既定は列優先）の食い違いです。`row_major` を付けるか、C++ で `.Transpose()` して送ります。

??? failure "頂点ごとに、3 つの行列を掛ける"
    頂点シェーダーで `mul(mul(mul(v, world), view), proj)` と書くと、頂点ごとに 3 回の掛け算が走ります。CPU で `mvp` を 1 回だけ作って、渡します。

??? failure "位置を `w = 0` で変換して、平行移動が効かない"
    `float4(position, 0)` にすると、位置が平行移動されません。位置は `w = 1` です。

??? failure "定数バッファの大きさが、16 バイトの倍数でない"
    `CreateBuffer` が失敗します。`float3` を使うと、16 バイト境界に合わせるための**パディング**が必要です。`float3 + float` の組にするか、パディングを足します。

??? failure "カメラの後ろの点を、画面に出す"
    `clip.w <= 0` の点は、カメラの後ろです。`w` で割ると、反転した位置に出ます。`w` を確認します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>M（ワールド）＝ 世界に置く、V（ビュー）＝ カメラから見る、P（プロジェクション）＝ 遠近感</strong>
    - [x] 行ベクトル規約：<strong>`world * view * proj`</strong>。<strong>CPU で 1 回掛けて</strong>、定数バッファで GPU へ
    - [x] HLSL は <strong>`row_major float4x4`</strong> + <strong>`mul(float4(pos, 1), mvp)`</strong>
    - [x] <strong>`view * proj` は共通</strong>。物体ごとに `world` だけ掛ける
    - [x] 画面に何も出ないときは、<strong>掛け順・手系・行列の並び・w</strong> を確認する

## 関連ページ

- [3D ゲーム（目次）](index.md)
- [行列](matrices.md)
- [投影（プロジェクション）](projection.md)
- [カメラ](camera.md)
- [深度バッファとカリング](depth-culling.md)
- [SimpleMath](simplemath.md)
