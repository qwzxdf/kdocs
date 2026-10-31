---
title: fastgltf の特徴と最小の読み込み
tags:
  - 外部ライブラリ
  - 3Dゲーム
---

# fastgltf の特徴と最小の読み込み

fastgltf で**glTF ファイルを読み込む最小のコード**とtinygltf との違いをまとめます。構造（参照は配列の番号）は tinygltf と同じなので、[glTF の構造](../tinygltf/structure.md)を先に読むと理解しやすくなります。

!!! tip "ポイント"
    - 流れは <strong>`Parser` を作る → `GltfDataBuffer` にファイルを読む → `loadGltf` → `Asset`</strong>。
    - <strong>戻り値は `Expected<T>`</strong>。`.error()` が `Error::None` か確認してから `.get()`。
    - `Asset` の中の配列（`meshes`・`nodes`・`accessors` ...）を番号で引く（tinygltf と同じ）。
    - 省略可能な参照は `std::optional<std::size_t>`（`-1` ではない）。
    - 外部の `.bin` を読むかは、`Options` で指定（`LoadExternalBuffers`）。
    - 必要な拡張だけを `Parser` に教える（`Extensions`）。

!!! info "このページを読む前に"
    - [fastgltf（高速な glTF 読み込み）](index.md)（このセクション全体の地図と、読む順番）
    - [3D モデルの読み込みライブラリの選び方](../model-loading.md)（3D モデルの読み込みの選び方）

## 最小の読み込み

```cpp
#include <print>

#include <fastgltf/core.hpp>
#include <fastgltf/types.hpp>

bool LoadModel(const std::filesystem::path& path, fastgltf::Asset& out) {
  fastgltf::Parser parser(fastgltf::Extensions::KHR_mesh_quantization |
                          fastgltf::Extensions::KHR_texture_transform);

  auto data = fastgltf::GltfDataBuffer::FromPath(path);
  if (data.error() != fastgltf::Error::None) {
    std::println("ファイルを読めません: {}", fastgltf::getErrorMessage(data.error()));
    return false;
  }

  constexpr auto kOptions = fastgltf::Options::LoadExternalBuffers |
                            fastgltf::Options::LoadExternalImages;
  auto asset = parser.loadGltf(data.get(), path.parent_path(), kOptions);
  if (asset.error() != fastgltf::Error::None) {
    std::println("glTF の解析に失敗: {}", fastgltf::getErrorMessage(asset.error()));
    return false;
  }

  out = std::move(asset.get());
  return true;
}
```

| 部分 | 意味 |
| --- | --- |
| **`Parser(Extensions)`** | 使う拡張をビットフラグで指定（指定しないと、その拡張を使うファイルはエラー） |
| `GltfDataBuffer::FromPath` | ファイルをメモリに読む（`Expected`）。古い版は `loadFromFile` など別の書き方 |
| `loadGltf(data, 基準フォルダ, Options)` | 解析して、`Asset` を作る。基準フォルダは外部ファイル（`.bin`・画像）を探す場所 |
| `Options::LoadExternalBuffers` | `.bin` を読み込む（指定しないと場所（URI）だけを持つ） |
| `Error` | エラーの種類（`Error::None` なら成功）。`getErrorMessage` で説明 |

!!! note ".glb と .gltf"
    `.glb` も`.gltf` も`loadGltf` が、自動判別します（ファイルの種類を確認して、それぞれの読み方で処理）。tinygltf のように関数を分ける必要は、ありません。

## Asset の中身

**`fastgltf::Asset`** はglTF の内容をそのまま構造体にしたものです。

| メンバ | 内容 |
| --- | --- |
| `scenes`・`nodes`・`meshes` | シーン・ノード・メッシュ |
| `accessors`・`bufferViews`・`buffers` | 数値データの読み方・範囲・実体 |
| `materials`・`textures`・`images`・`samplers` | 見た目 |
| `skins`・`animations` | ボーン・アニメーション |
| `defaultScene` | 既定のシーン（`std::optional<size_t>`） |

```cpp
const fastgltf::Mesh& mesh = asset.meshes[node.meshIndex.value()];
const fastgltf::Accessor& accessor = asset.accessors[primitive.indicesAccessor.value()];
```

## tinygltf との違い

| | tinygltf | fastgltf |
| --- | --- | --- |
| **速さ** | 普通 | 速い（simdjson。大きなファイルで差が出る） |
| JSON | nlohmann/json（同梱） | simdjson |
| 参照の型 | `int`（`-1` が、なし） | `std::size_t`（なしは `std::optional`） |
| 画像のデコード | する（`stb_image` を使う） | しない（自分で） |
| バッファの扱い | `std::vector<unsigned char>` | `std::variant`（`sources::Array`・`URI`・`BufferView` など。メモリの持ち方を選べる） |
| データの取り出し | 自分で、バイトを読む（[データの取り出し方](../tinygltf/reading.md)） | `iterateAccessor` などヘルパーが型変換・stride を処理 |
| 書き出し | できる | 限定的（バージョンによる） |
| API の安定性 | 安定 | バージョンで変わりやすい |
| 向く用途 | 学習・小さなツール | 大きなアセットを速くロード |

学習用や手軽さなら tinygltf、ロード速度が重要なら fastgltf です（[3D モデルの読み込みライブラリの選び方](../model-loading.md)）。

## バッファの持ち方（variant）

**fastgltf はバッファ（バイナリ）の実体を `std::variant` で、持ちます**。

| 種類 | 意味 |
| --- | --- |
| `sources::Array` | メモリ上のバイト配列（読み込み済み） |
| `sources::URI` | ファイルの場所（まだ読んでいない） |
| `sources::BufferView` | 別のバッファの一部（`.glb` に埋め込まれた画像など） |
| `sources::ByteView` | 外部のメモリを指す（コピーしない。呼び出し側が生存を保証） |

`LoadExternalBuffers` を指定すると`Array` に読み込まれます。指定しない場合は自分で、`URI` を読んで読み込みます（非同期ロード・ストリーミングに便利）。

## 拡張

```cpp
fastgltf::Parser parser(fastgltf::Extensions::KHR_materials_emissive_strength |
                        fastgltf::Extensions::KHR_texture_basisu);
```

| 拡張 | 対応 |
| --- | --- |
| `KHR_mesh_quantization` | **頂点を小さい型で持つ**（fastgltf は、読める） |
| `KHR_texture_transform` | UV の変換 |
| `KHR_materials_*` | マテリアルの拡張（emissive strength・clearcoat など） |
| `KHR_draco_mesh_compression` | デコードはしない（別のライブラリ） |
| `EXT_meshopt_compression` | 対応（meshoptimizer を使って、展開するオプション） |
| `KHR_texture_basisu` | 画像の場所を返す（KTX2 の展開は、自分で） |

使う拡張を `Parser` に教えておく必要があります（教えないとそのファイルを拒否します）。

## よくあるミス

??? failure "`.error()` を確認せず `.get()` する"
    **失敗しているのに、値を取り出して未定義動作**になります。

??? failure "`LoadExternalBuffers` を指定せずデータが空"
    バッファが `URI`（場所）のままです。オプションを指定するか自分で読み込みます。

??? failure "tinygltf の書き方（`-1` との比較）をそのまま使う"
    省略可能な参照は `std::optional`。`.has_value()`・`.value()` を使います。

??? failure "使う拡張を `Parser` に教えずエラーになる"
    `Extensions` に必要な拡張を足します。

??? failure "古いサンプルの API で、コンパイルできない"
    バージョンで変わっています。使っている版の `examples` / ドキュメントを見ます。

## 関連ページ

- [fastgltf（目次）](index.md)
- [データの取り出し方](reading.md)
- [glTF の構造](../tinygltf/structure.md)
- [tinygltf](../tinygltf/index.md)
- [3D モデルの読み込みライブラリの選び方](../model-loading.md)
