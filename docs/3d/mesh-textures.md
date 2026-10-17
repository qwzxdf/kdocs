---
title: メッシュとテクスチャ
tags:
  - 3Dゲーム
---

# メッシュとテクスチャ

3D モデルは、**頂点の並び**（メッシュ）と、**表面に貼る画像**（テクスチャ）でできています。このページは、DX11 での**頂点バッファ・インデックスバッファ・入力レイアウト**の作り方、**UV 座標**、**テクスチャとサンプラー**、**ミップマップ**をまとめます。

!!! tip "ポイント"
    - メッシュは、<strong>頂点バッファ</strong>（頂点の配列）+ <strong>インデックスバッファ</strong>（頂点の番号の並び）。<strong>インデックスで、頂点を使い回す</strong>。
    - 頂点には、<strong>位置・法線・UV</strong> などを持たせる。<strong>入力レイアウト</strong>で、GPU に並びを教える。
    - <strong>UV</strong>は、テクスチャ上の座標（<strong>DX は、左上が (0, 0)</strong>）。
    - <strong>サンプラー</strong>で、拡大縮小の補間・繰り返しを決める。<strong>ミップマップ</strong>で、遠くのちらつきを抑える。
    - <strong>バッファは、一度作って使い回す</strong>。毎フレーム作らない。
    - <strong>頂点が多いほど、頂点バッファは、大きく</strong>。<strong>インデックス型は、16 ビットで足りるか</strong>を考える。

## 頂点

頂点は、**位置**だけでなく、陰影やテクスチャに必要な値を持ちます。

```cpp
struct Vertex {
  DirectX::SimpleMath::Vector3 position;
  DirectX::SimpleMath::Vector3 normal;
  DirectX::SimpleMath::Vector2 uv;
};
```

| 属性 | 型 | 用途 |
| --- | --- | --- |
| **位置**（position） | `Vector3` | 頂点の座標（ローカル） |
| **法線**（normal） | `Vector3` | 陰影（[法線とライティング](lighting-normals.md)） |
| **UV**（texcoord） | `Vector2` | テクスチャの座標 |
| **接線**（tangent） | `Vector3` / `Vector4` | 法線マップ |
| **色**（color） | `Vector4` / `uint32_t` | 頂点カラー |
| **ボーン番号・重み** | `uint8_t[4]` / `float[4]` | スキニング（[スキニング](skinning-animation.md)） |

## インデックスバッファ

四角形は、**2 つの三角形**です。**頂点を共有**して、インデックスで三角形を組みます。

```text
 v3 ─── v2          頂点：  v0 v1 v2 v3    （4 個）
  │ ╲   │           インデックス：  0 1 2,  0 2 3    （6 個）
  │   ╲ │
 v0 ─── v1          インデックスなし： 6 頂点が必要
```

| 方式 | 頂点数（四角形） | メモリ |
| --- | --- | --- |
| インデックスなし | 6 | 多い |
| **インデックスあり** | **4** + インデックス 6 | **少ない**（共有の多いメッシュで、大きく節約） |

| インデックス型 | 範囲 | 用途 |
| --- | --- | --- |
| **`uint16_t`** | 〜 65535 頂点 | **小さなメッシュ**。メモリが半分 |
| **`uint32_t`** | 約 43 億 | **大きなメッシュ** |

!!! note "巻き順（CCW が表）"
    **三角形の頂点の並びは、反時計回りが表**です（[深度とカリング](depth-culling.md)）。上の例は、`0 1 2`・`0 2 3` とも反時計回りです。

## DX11 でバッファを作る

### 頂点バッファ

```cpp
std::vector<Vertex> vertices = {
    {{-0.5f, 0.0f, 0.5f}, {0, 1, 0}, {0, 0}},
    {{0.5f, 0.0f, 0.5f}, {0, 1, 0}, {1, 0}},
    {{0.5f, 0.0f, -0.5f}, {0, 1, 0}, {1, 1}},
    {{-0.5f, 0.0f, -0.5f}, {0, 1, 0}, {0, 1}},
};

D3D11_BUFFER_DESC vb_desc = {};
vb_desc.ByteWidth = static_cast<UINT>(sizeof(Vertex) * vertices.size());
vb_desc.Usage = D3D11_USAGE_IMMUTABLE;
vb_desc.BindFlags = D3D11_BIND_VERTEX_BUFFER;

D3D11_SUBRESOURCE_DATA vb_data = {};
vb_data.pSysMem = vertices.data();

Microsoft::WRL::ComPtr<ID3D11Buffer> vertex_buffer;
device->CreateBuffer(&vb_desc, &vb_data, &vertex_buffer);
```

### インデックスバッファ

```cpp
std::vector<uint16_t> indices = {0, 1, 2, 0, 2, 3};

D3D11_BUFFER_DESC ib_desc = {};
ib_desc.ByteWidth = static_cast<UINT>(sizeof(uint16_t) * indices.size());
ib_desc.Usage = D3D11_USAGE_IMMUTABLE;
ib_desc.BindFlags = D3D11_BIND_INDEX_BUFFER;

D3D11_SUBRESOURCE_DATA ib_data = {};
ib_data.pSysMem = indices.data();

Microsoft::WRL::ComPtr<ID3D11Buffer> index_buffer;
device->CreateBuffer(&ib_desc, &ib_data, &index_buffer);
```

### Usage の選び方

| `Usage` | 更新 | 用途 |
| --- | --- | --- |
| **`IMMUTABLE`** | **できない**（作成時のみ） | **変わらないメッシュ**。最速 |
| **`DEFAULT`** | `UpdateSubresource` | たまに更新 |
| **`DYNAMIC`** | **`Map`（`WRITE_DISCARD`）で、毎フレーム** | パーティクル、動的なメッシュ。`CPUAccessFlags = WRITE` が必要 |

## 入力レイアウト

**頂点バッファの中身の並び**を、GPU に教えるのが、**入力レイアウト**です。**頂点シェーダーの入力**（セマンティクス）と対応させます。

```cpp
D3D11_INPUT_ELEMENT_DESC layout[] = {
    {"POSITION", 0, DXGI_FORMAT_R32G32B32_FLOAT, 0, offsetof(Vertex, position),
     D3D11_INPUT_PER_VERTEX_DATA, 0},
    {"NORMAL", 0, DXGI_FORMAT_R32G32B32_FLOAT, 0, offsetof(Vertex, normal),
     D3D11_INPUT_PER_VERTEX_DATA, 0},
    {"TEXCOORD", 0, DXGI_FORMAT_R32G32_FLOAT, 0, offsetof(Vertex, uv),
     D3D11_INPUT_PER_VERTEX_DATA, 0},
};

Microsoft::WRL::ComPtr<ID3D11InputLayout> input_layout;
device->CreateInputLayout(layout, _countof(layout), vs_bytecode->GetBufferPointer(),
                          vs_bytecode->GetBufferSize(), &input_layout);
```

| 項目 | 説明 |
| --- | --- |
| セマンティクス名・番号 | HLSL の `POSITION`・`NORMAL`・`TEXCOORD0` と、**同じ名前** |
| フォーマット | `R32G32B32_FLOAT` ＝ `float` 3 つ。`Vector3` に対応 |
| オフセット | 構造体の中の位置。**`offsetof`** が確実 |
| スロット | 頂点バッファの番号（複数の頂点バッファを使うとき） |
| `PER_VERTEX_DATA` / `PER_INSTANCE_DATA` | **頂点ごと**か、**インスタンスごと**か（インスタンシング） |

## 描画する

```cpp
UINT stride = sizeof(Vertex);
UINT offset = 0;
context->IASetInputLayout(input_layout.Get());
context->IASetVertexBuffers(0, 1, vertex_buffer.GetAddressOf(), &stride, &offset);
context->IASetIndexBuffer(index_buffer.Get(), DXGI_FORMAT_R16_UINT, 0);
context->IASetPrimitiveTopology(D3D11_PRIMITIVE_TOPOLOGY_TRIANGLELIST);

context->DrawIndexed(static_cast<UINT>(indices.size()), 0, 0);
```

| 項目 | 説明 |
| --- | --- |
| `stride` | 頂点 1 つのバイト数（`sizeof(Vertex)`） |
| `DXGI_FORMAT_R16_UINT` / `R32_UINT` | インデックスの型と**一致**させる |
| `TRIANGLELIST` | 3 つごとに、1 つの三角形（最も一般的） |
| `DrawIndexed(個数, 開始位置, 頂点のずれ)` | インデックスを使う描画 |

## UV とテクスチャ

**UV**は、テクスチャ上の座標です。頂点ごとに持ち、**三角形の内部は、補間**されます。

```text
(0,0) ────────→ U (1,0)        DirectX：左上が原点、V は下向き
  │
  │   テクスチャ
  ↓
  V
(0,1)             (1,1)
```

| API | UV の原点 |
| --- | --- |
| **DirectX** | **左上** |
| OpenGL | **左下** |

**OpenGL 系のモデル（`.obj`・`.gltf` など）を読むと、上下が逆**になることがあります。読み込み時に **`v = 1 - v`** で直します。

### テクスチャを読み込んで使う（DirectXTK）

```cpp
#include <DDSTextureLoader.h>
#include <WICTextureLoader.h>

Microsoft::WRL::ComPtr<ID3D11ShaderResourceView> srv;
DirectX::CreateWICTextureFromFile(device, context, L"assets/albedo.png", nullptr, &srv);
DirectX::CreateDDSTextureFromFile(device, L"assets/albedo.dds", nullptr, &srv);

context->PSSetShaderResources(0, 1, srv.GetAddressOf());
```

| ローダー | 用途 |
| --- | --- |
| **`CreateWICTextureFromFile`** | PNG・JPG など。**ミップマップを自動生成**する（`context` を渡したとき） |
| **`CreateDDSTextureFromFile`** | **DDS**（圧縮・ミップ済み）。**本番は、これが速い** |
| `DirectXTex` | 変換・圧縮・ミップ生成のツール・ライブラリ |

**sRGB**：色のテクスチャは、`DXGI_FORMAT_*_SRGB` として読むと、**ガンマ補正が自動**です（`WIC_LOADER_FORCE_SRGB`）。**法線マップ・数値のテクスチャ**は、sRGB に**しません**。

## サンプラー

**テクスチャを、どう読むか**を決めます。

```cpp
D3D11_SAMPLER_DESC sampler_desc = {};
sampler_desc.Filter = D3D11_FILTER_MIN_MAG_MIP_LINEAR;
sampler_desc.AddressU = D3D11_TEXTURE_ADDRESS_WRAP;
sampler_desc.AddressV = D3D11_TEXTURE_ADDRESS_WRAP;
sampler_desc.AddressW = D3D11_TEXTURE_ADDRESS_WRAP;
sampler_desc.MaxLOD = D3D11_FLOAT32_MAX;

Microsoft::WRL::ComPtr<ID3D11SamplerState> sampler;
device->CreateSamplerState(&sampler_desc, &sampler);
context->PSSetSamplers(0, 1, sampler.GetAddressOf());
```

### フィルター

| フィルター | 説明 | 用途 |
| --- | --- | --- |
| `MIN_MAG_MIP_POINT` | **最近傍**（補間なし）。**ドット絵**がくっきり | ピクセルアート、データのテクスチャ |
| `MIN_MAG_MIP_LINEAR` | **双線形 + ミップ間も補間**（トライリニア） | **標準** |
| `ANISOTROPIC` | **異方性**。**斜めから見た面**が、くっきり | 床・道路など。`MaxAnisotropy` を設定 |

### アドレスモード

UV が `0..1` の外に出たときの扱いです。

| モード | 動き | 用途 |
| --- | --- | --- |
| **`WRAP`** | **繰り返す** | 床・壁のタイリング |
| **`CLAMP`** | 端の色を伸ばす | スカイボックス、UI |
| `MIRROR` | 折り返す | つなぎ目を目立たせない |
| `BORDER` | 指定色 | 影の範囲外など |

## ミップマップ

**テクスチャを、半分・4 分の 1 ... と縮小した画像を、あらかじめ作っておく**仕組みです。遠くの面では、小さい画像を使うので、**ちらつき（モアレ）が減り**、**キャッシュにも優しく**なります。

```text
512×512 → 256×256 → 128×128 → ... → 1×1      （メモリは、約 1.33 倍）
```

| 項目 | 説明 |
| --- | --- |
| **効果** | 遠くの**ちらつきが消える**。**速くなる**ことが多い |
| **コスト** | メモリが約 **33% 増える** |
| **作り方** | ローダーの自動生成、`GenerateMips`、DDS に最初から入れる |
| **使わない場合** | UI・2D スプライト（等倍で表示するもの） |

## メッシュの読み込み

| 形式 | 特徴 |
| --- | --- |
| **`.obj`** | 単純なテキスト。アニメーションなし。学習・簡単な用途 |
| **`.fbx`** | 業界標準。アニメーション・骨あり。SDK が重い |
| **`.gltf` / `.glb`** | **オープン形式**。軽量。PBR・アニメーション対応。**おすすめ** |
| **独自形式** | 読み込みが速い。**ツールで変換**して、ゲーム用に最適化 |
| **`.sdkmesh`**（DirectXTK） | DX 向けのサンプル形式 |

!!! tip "ゲームの本番は、独自の軽い形式に変換する"
    開発中は `.gltf`・`.fbx`、リリース時は、**ビルド時に独自の形式に変換**して、**そのままメモリに読む**形にします。読み込みが速く、扱いも単純になります。

## 頂点の最適化

| 方法 | 効果 |
| --- | --- |
| **頂点の共有**（インデックス） | メモリ・頂点処理を減らす |
| **頂点のフォーマットを小さく** | 法線を `R10G10B10A2`、UV を `half` に |
| **頂点キャッシュの最適化** | 三角形の並びを、GPU のキャッシュに優しく並べ替え（`DirectXMesh` の `OptimizeFaces`） |
| **インスタンシング** | **同じメッシュを、大量に**描く（木・草・弾）。1 回の描画命令で |
| **LOD** | 遠くは、頂点の少ないモデル |

## よくあるミス

??? failure "メッシュが表示されない"
    巻き順（CCW が表）、`FrontCounterClockwise`、入力レイアウト、`stride`、インデックスの型（`R16_UINT` / `R32_UINT`）を確認します。

??? failure "テクスチャが、上下逆になる"
    UV の原点の違い（DX は左上）です。`v = 1 - v` で直します。

??? failure "入力レイアウトの作成が失敗する"
    頂点シェーダーの入力と、セマンティクス・フォーマットが、一致していません。

??? failure "テクスチャが、ぼやける・ちらつく"
    ミップマップとフィルター（`MIN_MAG_MIP_LINEAR`、異方性）を確認します。

??? failure "色が、暗い・明るすぎる"
    sRGB の扱い（色は sRGB、法線マップなどは、sRGB にしない）を確認します。

??? failure "毎フレーム、バッファを作り直して遅い"
    **一度作って、使い回す**。動くなら `DYNAMIC` + `Map` で更新します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] メッシュは<strong>頂点バッファ + インデックスバッファ</strong>。<strong>入力レイアウト</strong>でシェーダーとつなぐ
    - [x] <strong>巻き順は CCW が表</strong>。<strong>UV は DX が左上原点</strong>（<strong>OpenGL 系は `v = 1 - v`</strong>）
    - [x] <strong>変わらないものは `IMMUTABLE`</strong>、毎フレーム変わるものは<strong>`DYNAMIC`</strong>
    - [x] <strong>サンプラー</strong>は、標準は<strong>トライリニア + WRAP</strong>。斜めの面は<strong>異方性</strong>。<strong>ミップマップ</strong>で、遠くのちらつきを消す
    - [x] 本番は、<strong>独自の軽い形式に変換</strong>。同じ物の大量描画は<strong>インスタンシング</strong>

## 関連ページ

- [3D ゲーム（目次）](index.md)
- [法線とライティング](lighting-normals.md)
- [深度とカリング](depth-culling.md)
- [スキニングとアニメーション](skinning-animation.md)
