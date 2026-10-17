---
title: 深度とカリング
tags:
  - 3Dゲーム
---

# 深度とカリング

3D の描画では、「**手前のものが、奥のものを隠す**」ことと、「**見えないものを、描かない**」ことが、必要です。前者は**深度バッファ**（Z バッファ）、後者は**カリング**です。このページは、DirectX 11 での設定（深度ステンシル、ラスタライザー）、Z ファイティング、リバース Z、視錐台カリングをまとめます。

!!! tip "ポイント"
    - <strong>深度バッファ</strong>は、ピクセルごとに「いちばん手前の深度」を覚え、<strong>奥のものを描かない</strong>ようにする。
    - DX11 では、<strong>深度ステンシルビュー（DSV）を作って、`OMSetRenderTargets` に渡す</strong>。毎フレーム `ClearDepthStencilView` でクリア。
    - <strong>バックフェイスカリング</strong>：<strong>裏を向いた三角形は描かない</strong>。右手系・CCW 表なら <strong>`FrontCounterClockwise = TRUE`</strong>。
    - <strong>Z ファイティング</strong>は、深度の精度不足。<strong>near を大きく</strong>、または<strong>リバース Z</strong> で減らす。
    - <strong>視錐台カリング</strong>：<strong>画面に入らないオブジェクトを、描画前に除外</strong>する（`BoundingFrustum`）。
    - 半透明は、<strong>深度の書き込みを止めて、奥から手前の順</strong>に描く。

## 深度バッファ

各ピクセルについて、**今までに描いた中で、いちばん手前の深度**を、バッファに記録します。新しいピクセルが、**記録より手前なら描いて更新、奥なら捨てます**。

```text
ピクセルの深度     0.8（奥）          0.3（手前）        0.5
バッファの値      1.0(初期) → 0.8     0.8 → 0.3          0.3 のまま
                 描く(更新)          描く(更新)         奥なので、捨てる
```

### 作る（DX11）

```cpp
D3D11_TEXTURE2D_DESC depth_desc = {};
depth_desc.Width = width;
depth_desc.Height = height;
depth_desc.MipLevels = 1;
depth_desc.ArraySize = 1;
depth_desc.Format = DXGI_FORMAT_D32_FLOAT;
depth_desc.SampleDesc.Count = 1;
depth_desc.Usage = D3D11_USAGE_DEFAULT;
depth_desc.BindFlags = D3D11_BIND_DEPTH_STENCIL;

Microsoft::WRL::ComPtr<ID3D11Texture2D> depth_texture;
device->CreateTexture2D(&depth_desc, nullptr, &depth_texture);

Microsoft::WRL::ComPtr<ID3D11DepthStencilView> dsv;
device->CreateDepthStencilView(depth_texture.Get(), nullptr, &dsv);
```

| フォーマット | 説明 |
| --- | --- |
| `DXGI_FORMAT_D32_FLOAT` | 32 ビット浮動小数点の深度。**ステンシルなし**。リバース Z と相性がよい |
| `DXGI_FORMAT_D24_UNORM_S8_UINT` | 24 ビット整数の深度 + 8 ビットのステンシル。**昔ながらの標準** |
| `DXGI_FORMAT_D32_FLOAT_S8X24_UINT` | 32 ビット浮動小数点 + ステンシル |

### 使う

```cpp
context->OMSetRenderTargets(1, rtv.GetAddressOf(), dsv.Get());

float clear_color[4] = {0.1f, 0.1f, 0.15f, 1.0f};
context->ClearRenderTargetView(rtv.Get(), clear_color);
context->ClearDepthStencilView(dsv.Get(), D3D11_CLEAR_DEPTH | D3D11_CLEAR_STENCIL, 1.0f, 0);
```

**毎フレーム、深度をクリア**します。忘れると、前のフレームの深度が残って、描画が欠けます。

### 深度ステンシルステート

```cpp
D3D11_DEPTH_STENCIL_DESC ds_desc = {};
ds_desc.DepthEnable = TRUE;
ds_desc.DepthWriteMask = D3D11_DEPTH_WRITE_MASK_ALL;
ds_desc.DepthFunc = D3D11_COMPARISON_LESS;

Microsoft::WRL::ComPtr<ID3D11DepthStencilState> ds_state;
device->CreateDepthStencilState(&ds_desc, &ds_state);
context->OMSetDepthStencilState(ds_state.Get(), 0);
```

| 設定 | 値 | 用途 |
| --- | --- | --- |
| `DepthEnable` | `TRUE` | 深度テストを行う |
| `DepthWriteMask` | `ALL` / `ZERO` | **`ZERO`**：テストはするが、書き込まない（**半透明**、パーティクル） |
| `DepthFunc` | `LESS`（手前なら描く）/ `LESS_EQUAL` / `GREATER`（リバース Z）/ `ALWAYS` | 通常は `LESS`。スカイボックスは `LESS_EQUAL`、リバース Z は `GREATER` |

## カリング（ラスタライザーステート）

**裏を向いた三角形**は、立体の内側なので、見えません。描かないことで、**描画を、ほぼ半分**にできます。

```cpp
D3D11_RASTERIZER_DESC rs_desc = {};
rs_desc.FillMode = D3D11_FILL_SOLID;
rs_desc.CullMode = D3D11_CULL_BACK;
rs_desc.FrontCounterClockwise = TRUE;
rs_desc.DepthClipEnable = TRUE;

Microsoft::WRL::ComPtr<ID3D11RasterizerState> rs_state;
device->CreateRasterizerState(&rs_desc, &rs_state);
context->RSSetState(rs_state.Get());
```

| 設定 | 値 | 説明 |
| --- | --- | --- |
| `CullMode` | `BACK` / `FRONT` / `NONE` | **`BACK`**：裏を描かない。**`NONE`**：両面（葉っぱ、布、**デバッグ**） |
| `FrontCounterClockwise` | `TRUE` / `FALSE` | **何を表とするか**。**このカテゴリは右手系・CCW が表なので `TRUE`**（[座標系](coordinate-systems.md)） |
| `FillMode` | `SOLID` / `WIREFRAME` | ワイヤーフレームは、デバッグ用 |

!!! warning "DX11 の既定は `FrontCounterClockwise = FALSE`（時計回りが表）"
    **何も設定しないと、DX11 は、時計回りを表とします**。右手系で作ったメッシュ（CCW が表）は、**裏表が逆**になって、**外側が消え、内側が見えます**。症状が出たら、`FrontCounterClockwise` と、メッシュの巻き順を確認します。

### 巻き順（ワインディング）

| 巻き順 | どう見えるか |
| --- | --- |
| <strong>反時計回り（CCW）</strong> | 見る側から、頂点が反時計回り → **表** |
| 時計回り（CW） | 見る側から、頂点が時計回り → **裏** |

モデルが、**裏返って見える**ときは、(1) `FrontCounterClockwise` の設定、(2) モデルの巻き順、(3) 負のスケール（`Scale(-1, 1, 1)` は、巻き順を反転させる）を疑います。

## Z ファイティング

**ほぼ同じ深度の 2 つの面**が、**ちらちら入れ替わる**現象です。深度の**精度が足りない**ために、起こります。

### なぜ起こるか

透視投影の深度は、**手前に精度が集中**し、**遠くでは、粗くなります**（[射影](projection.md)）。`near` が小さく、`far` が大きいほど、遠くの精度が、悪化します。

### 対策

| 対策 | 説明 |
| --- | --- |
| **near を大きくする** | 最も効く。`0.01` → `0.1` で、精度が、10 倍ほど改善する |
| **far を小さくする** | 効果は、near ほど大きくない |
| **リバース Z** | 浮動小数点の精度が、遠くに多く残り、**大きく改善** |
| **面の位置をずらす** | 壁の絵（デカール）は、少し浮かす。または、**深度バイアス** |
| **同じ位置に面を置かない** | モデリングの段階で避ける |
| **深度の精度を上げる** | `D24` → `D32_FLOAT` |

### 深度バイアス

デカールや影で、**わずかに、深度をずらす**設定です。

```cpp
rs_desc.DepthBias = -100;
rs_desc.SlopeScaledDepthBias = -1.0f;
rs_desc.DepthBiasClamp = 0.0f;
```

シャドウマップの<strong>自己影（シャドウアクネ）</strong>にも使います。

## リバース Z

**深度の割り当てを逆**にして、**near を 1、far を 0** にします。浮動小数点は、**0 の近くに、精度が多く**あるので、**遠くの精度**が、大きく改善します。

```cpp
Matrix proj = Matrix::CreatePerspectiveFieldOfView(fov, aspect, far_plane, near_plane);

ds_desc.DepthFunc = D3D11_COMPARISON_GREATER;
context->ClearDepthStencilView(dsv.Get(), D3D11_CLEAR_DEPTH, 0.0f, 0);
```

| 変更点 | 通常 | リバース Z |
| --- | --- | --- |
| 射影行列の near・far | `(near, far)` | **`(far, near)`**（逆に渡す） |
| `DepthFunc` | `LESS` | **`GREATER`** |
| 深度のクリア値 | `1.0` | **`0.0`** |
| 深度フォーマット | どれでもよい | **`D32_FLOAT`**（浮動小数点が必須） |

!!! warning "全部、そろえる"
    **どれか 1 つ忘れる**と、何も描かれない、または、すべて手前に見えます。**射影・比較関数・クリア値・フォーマット**は、セットで切り替えます。

## 視錐台カリング

**視錐台**（カメラの見える範囲）の**外にあるオブジェクトを、描画命令の前に、除外**します。描画命令・頂点処理を、丸ごと省けます。

```cpp
#include <DirectXCollision.h>

DirectX::BoundingFrustum frustum;
DirectX::BoundingFrustum::CreateFromMatrix(frustum, proj);

DirectX::BoundingFrustum world_frustum;
frustum.Transform(world_frustum, view.Invert());

for (const Object& obj : objects) {
  if (world_frustum.Contains(obj.bounds) == DirectX::DISJOINT) continue;
  Draw(obj);
}
```

| 結果 | 意味 |
| --- | --- |
| `DISJOINT` | **完全に外**。描かない |
| `INTERSECTS` | 一部が、交差。描く |
| `CONTAINS` | **完全に中**。描く |

| 注意 | 説明 |
| --- | --- |
| **ワールド空間にする** | 射影行列から作った錐台は、**カメラ空間**。`Transform` で、ワールドに変換する（ビュー行列の逆） |
| **境界は、ワールド空間** | `obj.bounds` も、ワールド座標に（`BoundingSphere`・`BoundingBox`、[3D の衝突判定](collision-3d.md)） |
| **球が速い** | 球は、判定が軽い。精度は、箱より粗い |
| **数が多いなら、空間分割** | 数万個を 1 つずつ調べるより、**BVH・八分木**で、まとめて除外（[空間分割](../optimize/algorithms.md)） |

## そのほかのカリング

| 種類 | 説明 |
| --- | --- |
| **バックフェイスカリング** | 裏向きの三角形を描かない（ラスタライザー） |
| **視錐台カリング** | 画面の外を描かない（CPU） |
| **オクルージョンカリング** | **ほかのものに隠れて見えない**ものを描かない（部屋の向こうなど）。実装が重い |
| **距離カリング / LOD** | 遠いものは、描かない、または簡易モデル |
| **小物カリング** | 画面上で、数ピクセルしかないものを描かない |

## 半透明の描画

半透明は、**ブレンド**（奥の色と混ぜる）のため、**奥から手前の順**に描く必要があります。

1. **不透明なものを先に描く**（深度の書き込みあり）。
2. **半透明を、カメラから遠い順に並べて**、描く。
3. 半透明は、**深度テストあり・書き込みなし**（`DepthWriteMask = ZERO`）。

```cpp
std::sort(transparent.begin(), transparent.end(),
          [&](const Object& a, const Object& b) {
            return Vector3::DistanceSquared(a.position, camera_pos) >
                   Vector3::DistanceSquared(b.position, camera_pos);
          });
```

## よくあるミス

??? failure "深度バッファを作ったのに、何も隠れない"
    `OMSetRenderTargets` に DSV を渡していない、または `DepthEnable = FALSE` です。

??? failure "モデルが、裏返って見える"
    `FrontCounterClockwise` と、メッシュの巻き順を確認します。DX11 の既定は、**時計回りが表**です。

??? failure "リバース Z にしたら、何も描かれない"
    `DepthFunc`（`GREATER`）、クリア値（`0.0`）、射影の near・far の順を、すべて確認します。

??? failure "近くで画面が欠ける"
    `near` が大きすぎて、手前がクリップされています。小さくするなら、**リバース Z** で精度を補います。

??? failure "半透明が、ほかの物体に隠れて、おかしく見える"
    不透明を先、半透明を遠い順に描き、半透明は深度を書き込みません。

??? failure "視錐台カリングで、見えるものが消える"
    錐台が、カメラ空間のままです。ワールドに変換します。境界も、ワールド空間にします。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>DSV を作って `OMSetRenderTargets` に渡す</strong>。<strong>毎フレーム、深度をクリア</strong>
    - [x] <strong>`CullMode = BACK`</strong> + <strong>右手系・CCW 表なら `FrontCounterClockwise = TRUE`</strong>
    - [x] <strong>Z ファイティング</strong>は、<strong>near を大きく</strong>、または<strong>リバース Z</strong>（<strong>射影・比較・クリア・フォーマット</strong>をそろえる）
    - [x] <strong>視錐台カリング</strong>は、<strong>ワールド空間</strong>で、<strong>描画前</strong>に
    - [x] 半透明は、<strong>不透明のあとに、遠い順</strong>。深度は書かない

## 関連ページ

- [3D ゲーム（目次）](index.md)
- [射影](projection.md)
- [3D の衝突判定](collision-3d.md)
- [空間分割](../optimize/algorithms.md)
