---
title: fastgltf のデータの取り出し方
tags:
  - 外部ライブラリ
  - 3Dゲーム
---

# fastgltf のデータの取り出し方

fastgltf は**アクセサー（accessor）からのデータの取り出し**をヘルパー関数で簡単にしてくれます。型の変換・`byteStride`・正規化をライブラリが処理します。このページは頂点・インデックス・ノード・マテリアル・アニメーションを SimpleMath の型で取り出す方法をまとめます。番号で配列を引く考え方は[glTF の構造](../tinygltf/structure.md)と同じです。

!!! tip "ポイント"
    - <strong>メッシュの描画単位は `Primitive`</strong>。<strong>`findAttribute("POSITION")` で頂点属性の accessor の番号</strong>を得る。
    - `fastgltf::iterateAccessor<T>(asset, accessor, 関数)` で 1 要素ずつ、`copyFromAccessor<T>(asset, accessor, 出力先)` で まとめてコピー。
    - 型は `fastgltf::math::fvec3` など。SimpleMath の `Vector3` には、成分を写す（または要素の特性を定義）。
    - ノードの変換は `getTransformMatrix`（TRS または行列を 4×4 に）。
    - `std::optional` の参照は `.has_value()` を確認してから使う。
    - 画像は自分でデコード（`stb_image`）。

!!! info "このページを読む前に"
    - [fastgltf（高速な glTF 読み込み）](index.md)（このセクション全体の地図と、読む順番）
    - [3D モデルの読み込みライブラリの選び方](../model-loading.md)（3D モデルの読み込みの選び方）

## 頂点を取り出す

```cpp
#include <fastgltf/tools.hpp>
#include <SimpleMath.h>
using namespace DirectX::SimpleMath;

struct Vertex {
  Vector3 position;
  Vector3 normal;
  Vector2 uv;
};

bool ReadPrimitive(const fastgltf::Asset& asset, const fastgltf::Primitive& primitive,
                   std::vector<Vertex>& vertices, std::vector<uint32_t>& indices) {
  auto position_it = primitive.findAttribute("POSITION");
  if (position_it == primitive.attributes.end()) return false;

  const fastgltf::Accessor& position_accessor = asset.accessors[position_it->accessorIndex];
  vertices.resize(position_accessor.count);

  fastgltf::iterateAccessorWithIndex<fastgltf::math::fvec3>(
      asset, position_accessor, [&](fastgltf::math::fvec3 p, size_t i) {
        vertices[i].position = Vector3(p.x(), p.y(), p.z());
      });

  if (auto it = primitive.findAttribute("NORMAL"); it != primitive.attributes.end()) {
    fastgltf::iterateAccessorWithIndex<fastgltf::math::fvec3>(
        asset, asset.accessors[it->accessorIndex], [&](fastgltf::math::fvec3 n, size_t i) {
          vertices[i].normal = Vector3(n.x(), n.y(), n.z());
        });
  }

  if (auto it = primitive.findAttribute("TEXCOORD_0"); it != primitive.attributes.end()) {
    fastgltf::iterateAccessorWithIndex<fastgltf::math::fvec2>(
        asset, asset.accessors[it->accessorIndex], [&](fastgltf::math::fvec2 uv, size_t i) {
          vertices[i].uv = Vector2(uv.x(), uv.y());
        });
  }

  if (primitive.indicesAccessor.has_value()) {
    const fastgltf::Accessor& index_accessor = asset.accessors[primitive.indicesAccessor.value()];
    indices.resize(index_accessor.count);
    fastgltf::copyFromAccessor<uint32_t>(asset, index_accessor, indices.data());
  }
  return true;
}
```

| 関数・型 | 意味 |
| --- | --- |
| **`primitive.findAttribute("POSITION")`** | 属性名 → accessor の番号（`attributes` の中を探す）。見つからなければ `end()` |
| `it->accessorIndex` | accessor の番号（`std::size_t`） |
| `asset.accessors[番号]` | accessor |
| `iterateAccessorWithIndex<T>(asset, accessor, 関数)` | 各要素を `T` 型に変換して、関数に渡す（要素の番号つき） |
| `iterateAccessor<T>` | 番号なし版 |
| `copyFromAccessor<T>(asset, accessor, dst)` | 全要素を `dst` にまとめてコピー（インデックスなど、そのまま使う型） |
| `fastgltf::math::fvec3` など | fastgltf の小さなベクトル型（`.x()`・`.y()`・`.z()`） |
| `primitive.indicesAccessor` | インデックスの accessor の番号（`std::optional`） |

ライブラリが `byteStride`・`componentType`（`unsigned short` → `uint32_t`）・正規化（`normalized`）を自動で処理します（tinygltf では、自分で書いた部分）。

!!! note "バージョン差に注意"
    ベクトル型は古い版では `glm`（`glm::vec3`）、新しい版では独自の `fastgltf::math` です。SimpleMath の型を直接渡すには、`fastgltf::ElementTraits<Vector3>` を特殊化する方法もあります（要素の成分数・型をライブラリに教える）。ドキュメントの「Accessor tools」を確認します。

## インデックスがないとき

**`indicesAccessor` が `std::nullopt`**（インデックスなし）の場合は、頂点を順に 3 つずつ三角形にします。

```cpp
if (!primitive.indicesAccessor.has_value()) {
  indices.resize(vertices.size());
  std::iota(indices.begin(), indices.end(), 0u);
}
```

## ノードの階層

```cpp
void Traverse(const fastgltf::Asset& asset, size_t node_index, const Matrix& parent_world,
              std::vector<DrawItem>& out) {
  const fastgltf::Node& node = asset.nodes[node_index];

  fastgltf::math::fmat4x4 local = fastgltf::getLocalTransformMatrix(node);
  Matrix local_matrix;
  std::memcpy(&local_matrix, local.data(), sizeof(Matrix));

  Matrix world = local_matrix * parent_world;

  if (node.meshIndex.has_value()) {
    out.push_back({node.meshIndex.value(), world});
  }
  for (size_t child : node.children) {
    Traverse(asset, child, world, out);
  }
}

void LoadScene(const fastgltf::Asset& asset, std::vector<DrawItem>& out) {
  size_t scene_index = asset.defaultScene.value_or(0);
  for (size_t root : asset.scenes[scene_index].nodeIndices) {
    Traverse(asset, root, Matrix::Identity, out);
  }
}
```

| 点 | 説明 |
| --- | --- |
| **`node.transform`** | TRS か行列の `std::variant`。`getLocalTransformMatrix(node)`（バージョンで名前が違う：`getTransformMatrix` など）で、4×4 行列に統一 |
| 行列の並び | glTF は列優先。SimpleMath の行優先（行ベクトル規約）にそのまま `memcpy` できる（[tinygltf の取り出し方](../tinygltf/reading.md)と同じ理由）。左手系へはルートに X 反転の行列を掛ける（[glTF の基本と規約](../tinygltf/gltf-basics.md#to-left-handed)） |
| `node.meshIndex` | `std::optional<size_t>`。`has_value()` を確認 |
| `node.children` | 子ノードの番号（`size_t` の配列） |
| **`world = local * parent_world` | 行ベクトル規約での 子 × 親** |
| `asset.defaultScene.value_or(0)` | 既定のシーン、なければ 0 番 |

`Options::DecomposeNodeMatrices` を指定するとノードの行列を TRS に分解して持ちます（アニメーションで、TRS が必要なとき）。

## マテリアル・テクスチャ

```cpp
const fastgltf::Material& material = asset.materials[primitive.materialIndex.value()];

const auto& pbr = material.pbrData;
Vector4 base_color(pbr.baseColorFactor[0], pbr.baseColorFactor[1], pbr.baseColorFactor[2], pbr.baseColorFactor[3]);
float metallic = pbr.metallicFactor;
float roughness = pbr.roughnessFactor;

if (pbr.baseColorTexture.has_value()) {
  size_t texture_index = pbr.baseColorTexture->textureIndex;
  const fastgltf::Texture& texture = asset.textures[texture_index];
  size_t image_index = texture.imageIndex.value();
  const fastgltf::Image& image = asset.images[image_index];
}
```

| 点 | 説明 |
| --- | --- |
| **`primitive.materialIndex`** | `std::optional<size_t>`（マテリアルなしもある） |
| `material.pbrData` | メタリック・ラフネスのデータ |
| `baseColorTexture` | `std::optional`。`->textureIndex`（`textures` の番号） |
| `texture.imageIndex` | `images` の番号（`std::optional`） |
| `texture.samplerIndex` | `samplers` の番号 |
| `material.normalTexture`・`occlusionTexture`・`emissiveTexture` | 同様（`std::optional`） |

### 画像の実体

`image.data` は`std::variant`で場所かメモリを持ちます。

```cpp
std::visit(fastgltf::visitor{
    [&](const fastgltf::sources::URI& uri) {
      std::filesystem::path path = base_directory / uri.uri.fspath();
      LoadImageFile(path);
    },
    [&](const fastgltf::sources::Array& array) {
      DecodeImage(array.bytes.data(), array.bytes.size());
    },
    [&](const fastgltf::sources::BufferView& view) {
      const fastgltf::BufferView& bv = asset.bufferViews[view.bufferViewIndex];
      const fastgltf::Buffer& buffer = asset.buffers[bv.bufferIndex];
      // buffer の中の、bv.byteOffset から bv.byteLength バイトが画像
    },
    [](auto&) {},
}, image.data);
```

| 種類 | 意味 |
| --- | --- |
| `URI` | 外部ファイル（`.png` など）の場所 |
| `Array` | メモリ上のバイト列（`LoadExternalImages` や base64 の埋め込み） |
| `BufferView` | `.glb` の中に埋め込まれた画像 |

デコードは `stb_image`（`stbi_load_from_memory`）などで、自分で行います（[ImGui のテクスチャ](../imgui/textures.md)）。色の空間（sRGB かリニアか）は、tinygltf と同じです（[PBR](../../3d/pbr.md)）。

## アニメーション

```cpp
const fastgltf::Animation& animation = asset.animations[0];

for (const fastgltf::AnimationChannel& channel : animation.channels) {
  const fastgltf::AnimationSampler& sampler = animation.samplers[channel.samplerIndex];

  std::vector<float> times(asset.accessors[sampler.inputAccessor].count);
  fastgltf::copyFromAccessor<float>(asset, asset.accessors[sampler.inputAccessor], times.data());

  if (channel.path == fastgltf::AnimationPath::Rotation) {
    fastgltf::iterateAccessor<fastgltf::math::fvec4>(
        asset, asset.accessors[sampler.outputAccessor], [&](fastgltf::math::fvec4 q) {
          Quaternion rotation(q.x(), q.y(), q.z(), q.w());
        });
  }

  size_t target_node = channel.nodeIndex.value();
}
```

| 項目 | 意味 |
| --- | --- |
| **`channel.samplerIndex`** | そのアニメーションの `samplers` の番号 |
| `channel.nodeIndex` | 動かすノードの番号（`std::optional`） |
| `channel.path` | `Translation` / `Rotation` / `Scale` / `Weights` |
| `sampler.inputAccessor` / `outputAccessor` | 時刻・値の accessor の番号 |
| `sampler.interpolation` | `Linear` / `Step` / `CubicSpline` |

クォータニオンは `(x, y, z, w)` で、SimpleMath と同じ並びです。ノードの値は変換せずルートの X 反転の行列でまとめて反転します（[glTF の基本と規約](../tinygltf/gltf-basics.md#to-left-handed)）。補間は `Slerp`（[回転](../../gamemath/rotation.md)）。

## スキン

```cpp
const fastgltf::Skin& skin = asset.skins[node.skinIndex.value()];
std::vector<size_t> joints(skin.joints.begin(), skin.joints.end());

std::vector<Matrix> inverse_bind(skin.joints.size());
fastgltf::copyFromAccessor<fastgltf::math::fmat4x4>(
    asset, asset.accessors[skin.inverseBindMatrices.value()], inverse_bind.data());
```

**頂点の `JOINTS_0` の値は `skin.joints` の位置**（ノード番号ではない）、という点は tinygltf と同じです（[スキニング](../../3d/skinning-animation.md)）。

## まとめ方

| やること | 説明 |
| --- | --- |
| **プリミティブごとに `MeshData`** | 1 プリミティブ ＝ 1 回の描画 |
| テクスチャは番号の表で重複を避ける | 同じ `textures[i]` を一度だけ作る |
| `Asset` は変換後に捨てる | メモリを節約 |
| 非同期ロード | `Parser` と `Asset` は、別スレッドで読み込める（スレッドごとに `Parser`） |
| ゲーム用の形式にビルド時に変換 | 開発中は glTF、製品は独自のバイナリ（[ベイク](../../optimize/baking.md)） |

## よくあるミス

??? failure "`std::optional` の参照を `.has_value()` を確認せず `.value()` する"
    **値がないと例外**（`bad_optional_access`）です。

??? failure "accessor の型と `iterateAccessor<T>` の `T` が合わずコンパイルエラー"
    要素の型（`VEC3` なら3 成分の型）を指定します。SimpleMath の型はそのままでは使えません（`fastgltf::math` の型で受けて、写す）。

??? failure "インデックスなしのメッシュを `indicesAccessor.value()` で読んで落ちる"
    インデックスは省略可能です。

??? failure "画像が `URI` のままで、デコードを忘れる"
    `LoadExternalImages`、または自分で読み込んでデコードします。

??? failure "`getTransformMatrix` の名前がバージョンで違いコンパイルできない"
    使っている版のヘッダ（`fastgltf/tools.hpp`・`math.hpp`）を確認します。

## 関連ページ

- [fastgltf（目次）](index.md)
- [特徴と最小の読み込み](quickstart.md)
- [glTF の構造](../tinygltf/structure.md)
- [tinygltf のデータの取り出し方](../tinygltf/reading.md)
- [メッシュとテクスチャ](../../3d/mesh-textures.md)
- [スキニングとアニメーション](../../3d/skinning-animation.md)
