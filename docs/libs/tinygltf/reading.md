---
title: tinygltf のデータの取り出し方
tags:
  - 外部ライブラリ
  - 3Dゲーム
---

# tinygltf のデータの取り出し方

[glTF の構造](structure.md)で見たように、glTF の要素は、<strong>配列の番号（インデックス）</strong>でつながっています。このページは、その番号をたどって、**頂点・インデックス・マテリアル・テクスチャ・ノード・アニメーション**を、**C++（SimpleMath、DX11）で取り出す方法**をまとめます。**番号 → 配列を引く**、という操作を、順に重ねていく形です。

!!! tip "ポイント"
    - <strong>番号は、そのまま配列の添字</strong>：<strong>`model.meshes[node.mesh]`</strong> のように引く。<strong>使う前に、`-1`（参照なし）を確認</strong>。
    - 頂点データは<strong>accessor → bufferView → buffer</strong> をたどって、<strong>先頭アドレス・間隔（stride）・個数</strong>を求める。
    - 先頭は <strong>`buffer.data` ＋ `bufferView.byteOffset` ＋ `accessor.byteOffset`</strong>。間隔は<strong>`accessor.ByteStride(bufferView)`</strong>。
    - インデックスの型は<strong>`unsigned byte / short / int` の 3 種類</strong>。<strong>`uint32_t` にそろえる</strong>と楽。
    - <strong>ノードの行列は `S × R × T`</strong>（行ベクトル規約）。<strong>ワールド ＝ ローカル × 親のワールド</strong>。
    - <strong>glTF の `matrix`（列優先 16 個）は、SimpleMath の `Matrix` に、そのまま入る</strong>。<strong>左手系へは、ルートに X 反転の行列を掛ける</strong>（[glTF の基本と規約](gltf-basics.md#to-left-handed)）。

## 全体の流れ

<svg class="fig flow" viewBox="0 0 797 112" role="img" aria-label="読み込みの流れ：ファイル → Model → 自分のデータ構造 → GPU のバッファ"><defs><marker id="fl45181" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">読み込みの流れ：ファイル → Model → 自分のデータ構造 → GPU のバッファ</text><line x1="151.0" y1="64.0" x2="209.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl45181)"/><text x="180.0" y="58.0" text-anchor="middle" style="font-size:12px">LoadASCIIFromFile</text><line x1="357.0" y1="64.0" x2="415.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl45181)"/><text x="386.0" y="58.0" text-anchor="middle" style="font-size:12px">番号をたどって取り出す</text><line x1="595.0" y1="64.0" x2="653.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl45181)"/><text x="624.0" y="58.0" text-anchor="middle" style="font-size:12px">CreateBuffer</text><rect x="28.0" y="44.0" width="120" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="88.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">glTF ファイル</text><circle cx="30.0" cy="46.0" r="10" fill="#4c8bf5"/><text x="30.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">1</text><rect x="212.0" y="44.0" width="142" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="283.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">tinygltf::Model</text><circle cx="214.0" cy="46.0" r="10" fill="#2ea043"/><text x="214.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="418.0" y="44.0" width="174" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2"/><text x="505.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">自分のメッシュ データ</text><circle cx="420.0" cy="46.0" r="10" fill="#e5a828"/><text x="420.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text><rect x="656.0" y="44.0" width="113" height="40" rx="9" fill="rgba(229,72,77,0.20)" stroke="#e5484d" stroke-width="2"/><text x="712.5" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">GPU バッファ</text><circle cx="658.0" cy="46.0" r="10" fill="#e5484d"/><text x="658.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">4</text></svg>

**`tinygltf::Model` は、ファイルの内容を、そのまま持っているだけ**です。**ゲームで使う形**（頂点バッファ・マテリアルの定数バッファなど）には、**自分で、変換**します。

## accessor からデータを取り出す

**頂点・インデックス・アニメーションの値**は、どれも、**accessor から取り出します**。まず、**先頭アドレス・間隔・個数**を求める関数を、作ります。

```cpp
struct AccessorData {
  const unsigned char* data = nullptr;
  size_t count = 0;
  size_t stride = 0;
  int component_type = 0;
  int type = 0;
};

AccessorData GetAccessorData(const tinygltf::Model& model, int accessor_index) {
  const tinygltf::Accessor& accessor = model.accessors[accessor_index];
  const tinygltf::BufferView& view = model.bufferViews[accessor.bufferView];
  const tinygltf::Buffer& buffer = model.buffers[view.buffer];

  AccessorData result;
  result.data = buffer.data.data() + view.byteOffset + accessor.byteOffset;
  result.count = accessor.count;
  result.stride = accessor.ByteStride(view);
  result.component_type = accessor.componentType;
  result.type = accessor.type;
  return result;
}
```

| 行 | 意味 |
| --- | --- |
| `model.accessors[accessor_index]` | **accessor の番号**で、配列を引く |
| `model.bufferViews[accessor.bufferView]` | accessor が持つ **bufferView の番号**で、引く |
| `model.buffers[view.buffer]` | bufferView が持つ **buffer の番号**で、引く |
| **`buffer.data`** | **バイナリ本体**（`std::vector<unsigned char>`） |
| **先頭** | **`buffer.data` ＋ `view.byteOffset` ＋ `accessor.byteOffset`** |
| **`ByteStride(view)`** | **要素と要素の間隔**（インターリーブなら、`byteStride`。隙間なしなら、要素のサイズ） |

!!! warning "accessor.bufferView が -1 のとき"
    `bufferView` が **`-1`**（無い）の accessor は、**すべてゼロの配列**を意味します（**スパース accessor** の土台など）。**頂点の位置では、まず起きません**が、**念のため確認**します。

### 型と大きさ

| 関数・定数 | 意味 |
| --- | --- |
| `tinygltf::GetComponentSizeInBytes(componentType)` | 1 つの数の**バイト数**（float は 4、unsigned short は 2） |
| `tinygltf::GetNumComponentsInType(type)` | **まとまりの数**（`VEC3` は 3、`MAT4` は 16、`SCALAR` は 1） |
| `TINYGLTF_COMPONENT_TYPE_FLOAT` | `5126` |
| `TINYGLTF_COMPONENT_TYPE_UNSIGNED_SHORT` | `5123` |
| `TINYGLTF_COMPONENT_TYPE_UNSIGNED_INT` | `5125` |
| `TINYGLTF_COMPONENT_TYPE_UNSIGNED_BYTE` | `5121` |
| `TINYGLTF_TYPE_VEC3` | 3 つ組（`SCALAR`・`VEC2`・`VEC4`・`MAT4` もある） |

## メッシュを取り出す

### 頂点

```cpp
#include <SimpleMath.h>
using namespace DirectX::SimpleMath;

struct Vertex {
  Vector3 position;
  Vector3 normal;
  Vector2 uv;
};

struct MeshData {
  std::vector<Vertex> vertices;
  std::vector<uint32_t> indices;
  int material = -1;
};

std::vector<Vector3> ReadVec3(const tinygltf::Model& model, int accessor_index) {
  AccessorData a = GetAccessorData(model, accessor_index);
  std::vector<Vector3> out(a.count);
  for (size_t i = 0; i < a.count; ++i) {
    float v[3];
    std::memcpy(v, a.data + i * a.stride, sizeof(v));
    out[i] = Vector3(v[0], v[1], v[2]);
  }
  return out;
}
```

**`std::memcpy` で、1 要素ずつ読む**のは、**アドレスが、`float` の境界に揃っていない**かもしれないからです（**アライメント**）。直接 `reinterpret_cast<const float*>` すると、未定義動作になることがあります。

### プリミティブごとに、取り出す

```cpp
MeshData ReadPrimitive(const tinygltf::Model& model, const tinygltf::Primitive& prim) {
  MeshData mesh;
  mesh.material = prim.material;

  auto position_it = prim.attributes.find("POSITION");
  if (position_it == prim.attributes.end()) return mesh;

  std::vector<Vector3> positions = ReadVec3(model, position_it->second);
  std::vector<Vector3> normals;
  std::vector<Vector2> uvs;

  if (auto it = prim.attributes.find("NORMAL"); it != prim.attributes.end()) {
    normals = ReadVec3(model, it->second);
  }
  if (auto it = prim.attributes.find("TEXCOORD_0"); it != prim.attributes.end()) {
    uvs = ReadVec2(model, it->second);
  }

  mesh.vertices.resize(positions.size());
  for (size_t i = 0; i < positions.size(); ++i) {
    mesh.vertices[i].position = positions[i];
    mesh.vertices[i].normal = i < normals.size() ? normals[i] : Vector3::Up;
    mesh.vertices[i].uv = i < uvs.size() ? uvs[i] : Vector2::Zero;
  }

  if (prim.indices >= 0) {
    mesh.indices = ReadIndices(model, prim.indices);
  }
  return mesh;
}
```

| 点 | 説明 |
| --- | --- |
| **`prim.attributes`** | `std::map<std::string, int>`。**キー（`"POSITION"`）→ accessor の番号** |
| **`find` で調べる** | **無い属性**（法線がない、UV がない）は、**既定値で埋める** |
| **`prim.indices`** | **インデックスの accessor の番号**。**`-1` なら無い**（頂点を順に並べて三角形にする） |
| **`prim.material`** | **マテリアルの番号**（`-1` なら既定） |
| 描画の単位 | **プリミティブごとに 1 回**の `DrawIndexed`（[メッシュとテクスチャ](../../3d/mesh-textures.md)） |

### インデックス（3 種類の型）

```cpp
std::vector<uint32_t> ReadIndices(const tinygltf::Model& model, int accessor_index) {
  AccessorData a = GetAccessorData(model, accessor_index);
  std::vector<uint32_t> out(a.count);
  for (size_t i = 0; i < a.count; ++i) {
    const unsigned char* p = a.data + i * a.stride;
    switch (a.component_type) {
      case TINYGLTF_COMPONENT_TYPE_UNSIGNED_BYTE:
        out[i] = *p;
        break;
      case TINYGLTF_COMPONENT_TYPE_UNSIGNED_SHORT: {
        uint16_t v;
        std::memcpy(&v, p, sizeof(v));
        out[i] = v;
        break;
      }
      case TINYGLTF_COMPONENT_TYPE_UNSIGNED_INT: {
        uint32_t v;
        std::memcpy(&v, p, sizeof(v));
        out[i] = v;
        break;
      }
    }
  }
  return out;
}
```

**インデックスの型は、メッシュごとに違います**（頂点が少なければ `unsigned short`、多ければ `unsigned int`）。**読むときに `uint32_t` にそろえて**おくと、**DX11 で、`DXGI_FORMAT_R32_UINT`** に統一できます（メモリを節約したいなら、頂点数に応じて、`R16_UINT` を使う）。

### DX11 のバッファにする

```cpp
D3D11_BUFFER_DESC vb_desc = {};
vb_desc.ByteWidth = static_cast<UINT>(sizeof(Vertex) * mesh.vertices.size());
vb_desc.Usage = D3D11_USAGE_IMMUTABLE;
vb_desc.BindFlags = D3D11_BIND_VERTEX_BUFFER;

D3D11_SUBRESOURCE_DATA vb_data = {};
vb_data.pSysMem = mesh.vertices.data();
device->CreateBuffer(&vb_desc, &vb_data, &vertex_buffer);
```

（インデックスバッファも同様。詳しくは、[メッシュとテクスチャ](../../3d/mesh-textures.md)）

## ノードの階層

### ローカル行列

```cpp
Matrix LocalMatrix(const tinygltf::Node& node) {
  if (node.matrix.size() == 16) {
    Matrix m;
    float* dst = &m._11;
    for (int i = 0; i < 16; ++i) dst[i] = static_cast<float>(node.matrix[i]);
    return m;
  }

  Vector3 scale = node.scale.size() == 3
                      ? Vector3(node.scale[0], node.scale[1], node.scale[2])
                      : Vector3::One;
  Quaternion rotation = node.rotation.size() == 4
                            ? Quaternion(node.rotation[0], node.rotation[1], node.rotation[2], node.rotation[3])
                            : Quaternion::Identity;
  Vector3 translation = node.translation.size() == 3
                            ? Vector3(node.translation[0], node.translation[1], node.translation[2])
                            : Vector3::Zero;

  return Matrix::CreateScale(scale) * Matrix::CreateFromQuaternion(rotation) * Matrix::CreateTranslation(translation);
}
```

| 点 | 説明 |
| --- | --- |
| **`node.matrix`** | **`std::vector<double>`**。**16 個あれば、行列で指定**されている。**空なら TRS** |
| **TRS が無い項目** | **既定値**（拡大 1、回転なし、移動 0） |
| **`rotation` の順** | **`[x, y, z, w]`**。SimpleMath の `Quaternion(x, y, z, w)` と**同じ並び**。ノードの回転は**変換せず**、ルートの行列でまとめて反転する |
| **`S × R × T`** | SimpleMath の**行ベクトル規約**で、**この順に掛ける**（[行列](../../gamemath/matrices.md)） |
| **`matrix` の並び** | glTF は**列優先**。**行ベクトル規約の行優先に、同じ並びで読める**（転置と同じ並びのため） |

### 親から子へ、たどる

```cpp
void Traverse(const tinygltf::Model& model, int node_index, const Matrix& parent_world,
              std::vector<DrawItem>& out) {
  const tinygltf::Node& node = model.nodes[node_index];
  Matrix world = LocalMatrix(node) * parent_world;

  if (node.mesh >= 0) {
    out.push_back({node.mesh, world});
  }
  for (int child : node.children) {
    Traverse(model, child, world, out);
  }
}

void LoadScene(const tinygltf::Model& model, std::vector<DrawItem>& out) {
  int scene_index = model.defaultScene >= 0 ? model.defaultScene : 0;
  const tinygltf::Scene& scene = model.scenes[scene_index];
  for (int root : scene.nodes) {
    Traverse(model, root, Matrix::Identity, out);
  }
}
```

<svg class="fig flow" viewBox="0 0 609 112" role="img" aria-label="ノードの木をたどって、ワールド行列を求める（子 ＝ ローカル × 親のワールド）"><defs><marker id="fl7970" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">ノードの木をたどって、ワールド行列を求める（子 ＝ ローカル × 親のワールド）</text><line x1="168.0" y1="64.0" x2="226.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl7970)"/><text x="197.0" y="58.0" text-anchor="middle" style="font-size:12px">children</text><line x1="364.0" y1="64.0" x2="422.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl7970)"/><text x="393.0" y="58.0" text-anchor="middle" style="font-size:12px">children</text><rect x="28.0" y="44.0" width="137" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="96.5" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">ルート world=L0</text><circle cx="30.0" cy="46.0" r="10" fill="#4c8bf5"/><text x="30.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">1</text><rect x="229.0" y="44.0" width="132" height="40" rx="9" fill="rgba(46,160,67,0.22)" stroke="#2ea043" stroke-width="2"/><text x="295.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">子 world=L1×L0</text><circle cx="231.0" cy="46.0" r="10" fill="#2ea043"/><text x="231.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">2</text><rect x="425.0" y="44.0" width="156" height="40" rx="9" fill="rgba(229,170,40,0.25)" stroke="#e5a828" stroke-width="2"/><text x="503.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">孫 world=L2×L1×L0</text><circle cx="427.0" cy="46.0" r="10" fill="#e5a828"/><text x="427.0" y="46.0" text-anchor="middle" dominant-baseline="central" style="fill:#fff;font-size:12px;font-weight:700">3</text></svg>

| 点 | 説明 |
| --- | --- |
| **`model.defaultScene`** | 既定のシーンの番号（**`-1` なら、0 番**を使う） |
| **`scene.nodes`** | **ルートのノード**の番号の一覧 |
| **`node.children`** | **子ノードの番号**（`std::vector<int>`） |
| **`world = local * parent_world`** | **子の行列を先に<strong>。</strong>行ベクトル規約**（[行列](../../gamemath/matrices.md)） |
| **`node.mesh >= 0`** | メッシュを持つノードだけ、**描画の対象**にする |
| **再帰** | 木が深いと、深くなる。**数千ノード**の巨大なモデルは、**スタックを使った繰り返し**にする |

**ノードの数と、メッシュの数は、別**です。**同じメッシュを、複数のノードが参照**できます（**インスタンス**）。**メッシュのバッファは 1 つ作り、ノードごとに、ワールド行列だけを変えて描画**します。

## マテリアルとテクスチャ

### マテリアル

```cpp
struct MaterialData {
  Vector4 base_color = Vector4(1, 1, 1, 1);
  float metallic = 1.0f;
  float roughness = 1.0f;
  Vector3 emissive = Vector3::Zero;
  int base_color_texture = -1;
  int metal_rough_texture = -1;
  int normal_texture = -1;
  int occlusion_texture = -1;
  int emissive_texture = -1;
};

MaterialData ReadMaterial(const tinygltf::Material& m) {
  MaterialData out;
  const auto& pbr = m.pbrMetallicRoughness;

  if (pbr.baseColorFactor.size() == 4) {
    out.base_color = Vector4(pbr.baseColorFactor[0], pbr.baseColorFactor[1],
                             pbr.baseColorFactor[2], pbr.baseColorFactor[3]);
  }
  out.metallic = static_cast<float>(pbr.metallicFactor);
  out.roughness = static_cast<float>(pbr.roughnessFactor);
  out.base_color_texture = pbr.baseColorTexture.index;
  out.metal_rough_texture = pbr.metallicRoughnessTexture.index;
  out.normal_texture = m.normalTexture.index;
  out.occlusion_texture = m.occlusionTexture.index;
  out.emissive_texture = m.emissiveTexture.index;
  return out;
}
```

| 項目 | 説明 |
| --- | --- |
| **`.index`** | **`textures` の番号**。**`-1` ならテクスチャなし**（**`Factor` の値だけ**を使う） |
| **`baseColorFactor`** | ベースカラーの**倍率**（テクスチャの色に**掛ける**） |
| **`metallicFactor` / `roughnessFactor`** | **テクスチャの値に掛ける**倍率。テクスチャがなければ、**この値そのもの** |
| **既定値** | **metallic = 1、roughness = 1**（仕様の既定値）。**tinygltf も、これで初期化**される |
| **`alphaMode`** | `"OPAQUE"`（不透明）、`"MASK"`（抜き）、`"BLEND"`（半透明） |
| **`doubleSided`** | **両面描画**（カリングを切る） |

### テクスチャ → 画像

```cpp
const tinygltf::Texture& texture = model.textures[texture_index];
const tinygltf::Image& image = model.images[texture.source];

int width = image.width;
int height = image.height;
const unsigned char* pixels = image.image.data();
```

| 項目 | 説明 |
| --- | --- |
| **`texture.source`** | **`images` の番号** |
| **`texture.sampler`** | **`samplers` の番号**（`-1` なら、既定のサンプラー） |
| **`image.image`** | **読み込み済みのピクセル**（`std::vector<unsigned char>`）。**tinygltf が `stb_image` でデコード**している |
| **`image.width` / `height`** | 画像の大きさ |
| **`image.component`** | チャンネル数（**通常は RGBA の 4**。**確認する**） |
| **`image.bits`** | 1 チャンネルのビット数（**通常 8**） |

### DX11 のテクスチャにする

```cpp
D3D11_TEXTURE2D_DESC desc = {};
desc.Width = image.width;
desc.Height = image.height;
desc.MipLevels = 1;
desc.ArraySize = 1;
desc.Format = is_srgb ? DXGI_FORMAT_R8G8B8A8_UNORM_SRGB : DXGI_FORMAT_R8G8B8A8_UNORM;
desc.SampleDesc.Count = 1;
desc.Usage = D3D11_USAGE_IMMUTABLE;
desc.BindFlags = D3D11_BIND_SHADER_RESOURCE;

D3D11_SUBRESOURCE_DATA data = {};
data.pSysMem = image.image.data();
data.SysMemPitch = image.width * 4;
device->CreateTexture2D(&desc, &data, &texture2d);
```

| 注意 | 説明 |
| --- | --- |
| **sRGB か、リニアか** | **ベースカラー・エミッシブ**は **sRGB**（`_SRGB`）。**法線・metallicRoughness・AO は、リニア**（[PBR](../../3d/pbr.md#色空間とトーンマッピング)） |
| **同じ画像を、両方で使う** | まれに、**同じ画像を sRGB とリニアの両方**で使う。**用途ごとに、ビューを作る** |
| **ミップマップ** | 作る場合は、`GenerateMips`（[メッシュとテクスチャ](../../3d/mesh-textures.md)） |
| **`SysMemPitch`** | **1 行のバイト数**（`幅 × 4`） |
| **画像がファイルに残る** | `image.image` は、**GPU に転送したら、解放**してよい（`image.image.clear(); shrink_to_fit();`） |

### サンプラー

```cpp
if (texture.sampler >= 0) {
  const tinygltf::Sampler& sampler = model.samplers[texture.sampler];
}
```

| キー | 値の例 |
| --- | --- |
| `magFilter` | `9728`＝NEAREST、`9729`＝LINEAR |
| `minFilter` | `9984〜9987`（ミップマップの組み合わせ。`9987`＝LINEAR_MIPMAP_LINEAR） |
| `wrapS` / `wrapT` | `10497`＝REPEAT、`33071`＝CLAMP_TO_EDGE、`33648`＝MIRRORED_REPEAT |

数字は **OpenGL の定数**です。**DX11 の `D3D11_SAMPLER_DESC`**（`D3D11_TEXTURE_ADDRESS_WRAP` など）に、**変換**します（[メッシュとテクスチャ](../../3d/mesh-textures.md)）。

## スキンとアニメーション

### スキン

```cpp
const tinygltf::Skin& skin = model.skins[node.skin];

std::vector<int> joint_nodes = skin.joints;

AccessorData ibm = GetAccessorData(model, skin.inverseBindMatrices);
std::vector<Matrix> inverse_bind(ibm.count);
for (size_t i = 0; i < ibm.count; ++i) {
  std::memcpy(&inverse_bind[i], ibm.data + i * ibm.stride, sizeof(Matrix));
}
```

| 点 | 説明 |
| --- | --- |
| **`skin.joints`** | **ボーンになるノードの番号**の一覧 |
| **`skin.inverseBindMatrices`** | **逆バインド行列**の accessor の番号（**ボーンごとに 1 つ**） |
| **頂点の `JOINTS_0`** | **`skin.joints` の位置**（**ノード番号ではない**） |
| **スキニング行列** | **`inverse_bind[i] × (ボーンのノードのワールド行列)`**（[スキニング](../../3d/skinning-animation.md)） |

### アニメーション

```cpp
const tinygltf::Animation& anim = model.animations[0];

for (const tinygltf::AnimationChannel& channel : anim.channels) {
  const tinygltf::AnimationSampler& sampler = anim.samplers[channel.sampler];
  AccessorData times = GetAccessorData(model, sampler.input);
  AccessorData values = GetAccessorData(model, sampler.output);

  int target_node = channel.target_node;
  const std::string& path = channel.target_path;
}
```

| 項目 | 説明 |
| --- | --- |
| **`channel.sampler`** | **`anim.samplers` の番号**（**`model.animations` ではなく、アニメーションの中の配列**） |
| **`channel.target_node`** | **動かすノードの番号**（`model.nodes`） |
| **`channel.target_path`** | `"translation"`、`"rotation"`、`"scale"`、`"weights"` |
| **`sampler.input`** | **時刻**の accessor の番号（`float`、秒） |
| **`sampler.output`** | **値**の accessor の番号（`VEC3` / `VEC4`） |
| **補間** | `LINEAR` は、位置・拡大は `Lerp`、回転は `Slerp`（[回転](../../gamemath/rotation.md)） |

**ここでも、番号の参照先の配列が、場所によって違います**（`channel.sampler` は、そのアニメーションの `samplers`）。

## 読み込み後の、まとめ方

| やること | 説明 |
| --- | --- |
| **メッシュを、プリミティブごとの `MeshData` にする** | **1 プリミティブ ＝ 1 回の描画** |
| **マテリアルの番号を、そのまま使う** | `MeshData::material` から、**自分のマテリアル配列**を引く |
| **テクスチャは、番号で重複を避ける** | **同じ `textures[i]` を、複数のマテリアルが参照**するので、**一度だけ作る**（番号 → GPU テクスチャの表） |
| **ノードの木は、自分の構造に変換** | ゲームの**シーンのノード**・エンティティにする |
| **読み込んだら、`Model` を解放** | `tinygltf::Model` は、**大きい**（画像・バイナリを持つ）。**変換が終わったら捨てる** |
| **ゲームで使う形式に変換** | 開発中は glTF、**製品は独自の軽い形式**に、**ビルド時に変換**（[ロード時間](../../optimize/loading.md)） |

### 番号の表（重複を避ける）

```cpp
std::vector<ComPtr<ID3D11ShaderResourceView>> texture_srvs(model.textures.size());

ID3D11ShaderResourceView* GetTexture(int texture_index, bool srgb) {
  if (texture_index < 0) return default_white_.Get();
  if (!texture_srvs[texture_index]) {
    texture_srvs[texture_index] = CreateTexture(model, texture_index, srgb);
  }
  return texture_srvs[texture_index].Get();
}
```

<strong>「番号 → 作ったもの」の配列</strong>を用意して、**初めて参照されたときに作る**ことで、**同じテクスチャを、何度も作らない**ようにします。

## よくあるミス

??? failure "`-1` を調べず、配列を引いてクラッシュする"
    `node.mesh`、`prim.indices`、`prim.material`、`texture.sampler`、`.index` は、<strong>`-1` が「なし」</strong>です。

??? failure "`reinterpret_cast<const float*>` で、直接読む"
    **アライメントが合わない**ことがあります。**`std::memcpy`** で読みます。

??? failure "`byteStride` を使わず、`sizeof(float) * 3` ずつ進める"
    **インターリーブ**のデータで、**ずれます**。`accessor.ByteStride(view)` を使います。

??? failure "インデックスを、すべて `unsigned short` として読む"
    **型は accessor ごとに違います**。`componentType` で、分岐します。

??? failure "プリミティブが、複数あるのに、先頭だけを読む"
    **マテリアルごとに、プリミティブが分かれます**。**全部**読みます。

??? failure "`JOINTS_0` の値で、直接 `model.nodes` を引く"
    **`skin.joints[値]`** を引いた先が、ノード番号です。

??? failure "ワールド行列を、`parent_world * local`（逆順）で掛ける"
    **行ベクトル規約**では、**`local * parent_world`** です。

??? failure "ベースカラーを、リニアの形式で読む"
    **色が薄く・白っぽく**なります。**ベースカラーは sRGB**（`_SRGB`）です。

??? failure "法線マップを sRGB で読む"
    **法線がゆがみます**。**リニア**で読みます。

??? failure "読み込み後も、`tinygltf::Model` を持ち続けて、メモリを使い続ける"
    **GPU に転送したら、`Model` を解放**します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] <strong>番号 ＝ 配列の添字</strong>。<strong>`-1` は「なし」</strong>。<strong>使う前に、必ず確認</strong>
    - [x] データは<strong>accessor → bufferView → buffer</strong>。<strong>先頭 ＝ `buffer.data ＋ view.byteOffset ＋ accessor.byteOffset`</strong>、<strong>間隔 ＝ `ByteStride(view)`</strong>
    - [x] 読むときは<strong>`std::memcpy`</strong>。<strong>インデックスは型で分岐</strong>して、`uint32_t` にそろえる
    - [x] ノードは<strong>`S × R × T`</strong>、<strong>`world ＝ local × parent_world`</strong>。<strong>`matrix` は、そのまま `Matrix` に入る</strong>
    - [x] <strong>ベースカラーは sRGB、ほかのテクスチャはリニア</strong>
    - [x] <strong>プリミティブごとに 1 回の描画</strong>。<strong>同じテクスチャは、番号の表で重複を避ける</strong>

## 関連ページ

- [tinygltf（glTF の読み込み）](index.md)
- [glTF の構造](structure.md)
- [メッシュとテクスチャ](../../3d/mesh-textures.md)
- [スキニングとアニメーション](../../3d/skinning-animation.md)
- [PBR（物理ベースレンダリング）](../../3d/pbr.md)
- [ハンドル](../../engine/handle.md)
