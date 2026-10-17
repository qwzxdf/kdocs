---
title: yalantinglibs（struct_pack・バイナリ・速さ重視）
tags:
  - 外部ライブラリ
  - シリアライズ
---

# yalantinglibs（struct_pack・バイナリ・速さ重視）

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="perf perf-4">◎ 速い</span>
<span class="ver ver-20">C++20 推奨（C++17〜）</span>
`#include <ylt/struct_pack.hpp>`
</div>

**yalantinglibs**（ヤランティンリブス）は、Alibaba が公開している C++ のライブラリ集で、その中の **struct_pack** が**とても速いバイナリシリアライザ**です。[zpp_bits](zpp-bits.md) と同じく、**構造体なら何も書かなくても** `struct_pack::serialize(obj)` の 1 行で保存でき、速さも同じくらいのトップクラスです。zpp_bits との一番の違いは、データの先頭に**型の形から計算したハッシュ値**を入れることです。これにより、「違う形の構造体で読もうとした」ことを**読み込みのときに検出**できます。また、**`compatible` という互換フィールド**を使うと、構造体の最後にメンバを足しても古いデータを読めるようになります。速さと安全性のバランスがよく、セーブデータにも通信にも使いやすいライブラリです。

!!! tip "ポイント"
    - <strong>保存は `struct_pack::serialize(obj)`、読み込みは `struct_pack::deserialize<T>(buffer)`。</strong> 構造体なら何も書かなくてよい。
    - 読み込みの結果は **`expected`**（値かエラー）で返る。例外は投げない。
    - データに**型のハッシュ**が入るので、形が違う構造体で読むとエラーで分かる。
    - 後からメンバを足すなら、**最後に `struct_pack::compatible<T, バージョン>`** で足す。
    - private メンバがあるクラスは **`YLT_REFL(型, メンバ...)`** で対応させる。
    - `std::string_view` / `std::span` のメンバは、読み込むと**バッファを指す**（コピーしない）ので、バッファの寿命に注意。

!!! info "このページを読む前に"
    [シリアライズの概要](../../engine/serialization/index.md) と [zpp_bits](zpp-bits.md) を先に読むと、違いが分かりやすいです。読み込みの結果は [std::expected](../../stl/utilities/expected.md) とほぼ同じ使い方です。

## 導入

### Visual Studio で導入する（最初に読む）

Visual Studio を使っているなら、ここから読みます。ライブラリを入れる基本の手順は [Visual Studio：外部ライブラリの入れ方](../../vs/libraries.md) にまとめています。ここでは yalantinglibs（struct_pack） だけの部分を書きます。

=== "ファイルを置く"

    1. [GitHub](https://github.com/alibaba/yalantinglibs) の **`include` フォルダー**（`ylt/struct_pack.hpp` など）を `third_party/yalantinglibs/include/` に置く
    2. プロジェクトのプロパティを開き、構成を **すべての構成**、プラットフォームを **x64** にする
    3. **C/C++ → 全般 → 追加のインクルード ディレクトリ** に、`$(SolutionDir)third_party\yalantinglibs\include` を追加する
    4. `#include <ylt/struct_pack.hpp>` と書いてビルドする

=== "vcpkg"

    1. 初回だけ、Developer PowerShell で `vcpkg integrate install` を実行する（[準備](../../vs/libraries.md#vcpkg)）
    2. ライブラリを入れる

        ```powershell
        vcpkg install yalantinglibs:x64-windows
        ```

        （マニフェスト モードなら、`vcpkg.json` の `dependencies` に `"yalantinglibs"` を足す）
    3. プロジェクトには何も設定せずに、`#include <ylt/struct_pack.hpp>` と書けば使える

!!! note "C++ の設定"
    **C++20 を推奨**します（C++17 でも動く機能がありますが、一部は C++20 が必要です）。C++ 言語標準を `/std:c++latest` にします（[設定](../../vs/settings.md)）。

### そのほかの方法（CMake など）

struct_pack は**ヘッダオンリー**です。yalantinglibs の他の部分（RPC、HTTP など）は使わなくてもかまいません。

=== "vcpkg"

    ```text
    vcpkg install yalantinglibs
    ```

    ```cmake
    find_package(yalantinglibs CONFIG REQUIRED)
    target_link_libraries(my_game PRIVATE yalantinglibs::yalantinglibs)
    target_compile_features(my_game PRIVATE cxx_std_20)
    ```

=== "CMake FetchContent"

    ```cmake
    include(FetchContent)
    FetchContent_Declare(
      yalantinglibs
      GIT_REPOSITORY https://github.com/alibaba/yalantinglibs.git
      GIT_TAG main  # 本番ではタグを固定する
      GIT_SHALLOW TRUE)
    set(BUILD_EXAMPLES OFF)
    set(BUILD_BENCHMARK OFF)
    set(BUILD_UNIT_TESTS OFF)
    FetchContent_MakeAvailable(yalantinglibs)
    target_link_libraries(my_game PRIVATE yalantinglibs::yalantinglibs)
    ```

=== "フォルダを直接置く"

    リポジトリの `include` フォルダの中身（`ylt/` など）をプロジェクトにコピーして、インクルードディレクトリに追加します。

!!! note "yalantinglibs に入っているもの"
    | ライブラリ | 何をする |
    | --- | --- |
    | **struct_pack** | バイナリのシリアライズ（このページ） |
    | struct_json / struct_yaml / struct_xml | 構造体を JSON / YAML / XML と自動で変換 |
    | struct_pb | Protocol Buffers 形式 |
    | coro_rpc / coro_http | C++20 コルーチンを使った通信 |

    同じ「リフレクション」（`YLT_REFL`）の仕組みを使うので、struct_pack と struct_json を同じ構造体で使い分けることもできます。

## 関数一覧

| 関数・型 | 重要度 | 何をする |
| --- | --- | --- |
| [`serialize`](#serialize) | <span class="rank rank-must">必須</span> | オブジェクトをバイト列にする |
| [`deserialize`](#deserialize) | <span class="rank rank-must">必須</span> | バイト列からオブジェクトを作る（expected で返す） |
| [`deserialize_to`](#deserialize_to) | <span class="rank rank-often">よく使う</span> | 既存のオブジェクトに読み込む |
| [`serialize_to`](#serialize_to) | <span class="rank rank-often">よく使う</span> | 既存のバッファ・ファイルに書き足す |
| [`compatible`](#compatible) | <span class="rank rank-often">よく使う</span> | 後から足しても古いデータを読めるメンバ |
| [`YLT_REFL`](#ylt_refl) | <span class="rank rank-often">よく使う</span> | クラスのメンバを教える（private メンバ用） |
| [`get_needed_size`](#get_needed_size) | <span class="rank rank-sometimes">たまに</span> | 保存に必要なバイト数を計算する |
| [`get_field`](#get_field) | <span class="rank rank-rare">知ってるだけ</span> | 全部読まずに、1 つのメンバだけ読む |
| [`var_int32_t`](#var_int32_t) | <span class="rank rank-sometimes">たまに</span> | 小さい数を少ないバイトで書く整数型 |
| [`trivial_view`](#trivial_view) | <span class="rank rank-rare">知ってるだけ</span> | 読み込みでコピーせずにバッファを指す |
| [`sp_config`](#sp_config) | <span class="rank rank-rare">知ってるだけ</span> | 型の情報を入れるかなどの設定 |

## よくある使い方

```cpp
#include <print>
#include <string>
#include <vector>

#include <ylt/struct_pack.hpp>

struct Player {
  std::string name;
  int level = 1;
  std::vector<int> items;
};  // 何も書かなくてよい

int main() {
  Player player{"Alice", 12, {101, 205, 330}};

  // 保存：std::vector<char> が返る
  std::vector<char> buffer = struct_pack::serialize(player);

  // 読み込み：値かエラーのどちらかが返る
  auto result = struct_pack::deserialize<Player>(buffer);
  if (!result.has_value()) {
    std::println("読み込みに失敗しました");
    return 1;
  }
  const Player& loaded = result.value();
  std::println("{} Lv.{} {}", loaded.name, loaded.level, loaded.items);
}
```

```text title="実行結果"
Alice Lv.12 [101, 205, 330]
```

### ファイルに保存する

`serialize_to` と `deserialize` は、`std::ofstream` / `std::ifstream` にも直接使えます。

```cpp
#include <fstream>

#include <ylt/struct_pack.hpp>

bool SaveGame(const SaveData& save, const char* path) {
  std::ofstream file(path, std::ios::binary);
  if (!file) {
    return false;
  }
  struct_pack::serialize_to(file, save);
  return static_cast<bool>(file);
}

bool LoadGame(SaveData& save, const char* path) {
  std::ifstream file(path, std::ios::binary);
  if (!file) {
    return false;
  }
  auto error = struct_pack::deserialize_to(save, file);
  return !error;  // エラーが無ければ成功
}
```

## 型のハッシュ：形が違うデータを見分ける

struct_pack は、保存するときに<strong>データの先頭に 4 バイトの「型のハッシュ値」</strong> を書きます。ハッシュ値は、構造体の**メンバの型と順番**からコンパイル時に計算されます。

| 型のハッシュ（4 バイト） | （必要なら）追加の情報 | name | level | items | … |
| --- | --- | --- | --- | --- | --- |
| Player の形（`string`, `int`, `vector<int>`）から計算した値 | 型の情報 | データ | データ | データ | |

読み込むときに、**読もうとしている型のハッシュ値**と比べて、違っていればエラーにします。

```cpp
#include <print>
#include <string>
#include <vector>

#include <ylt/struct_pack.hpp>

struct Player {
  std::string name;
  int level = 1;
  std::vector<int> items;
};

struct Enemy {
  std::string name;
  float hp = 0.0f;  // int ではなく float
};

int main() {
  auto buffer = struct_pack::serialize(Player{"Alice", 12, {101}});

  auto as_player = struct_pack::deserialize<Player>(buffer);
  auto as_enemy = struct_pack::deserialize<Enemy>(buffer);  // 形が違う

  std::println("Player として: {}", as_player.has_value());
  std::println("Enemy として: {}", as_enemy.has_value());
}
```

```text title="実行結果"
Player として: true
Enemy として: false
```

- ハッシュは**メンバの名前ではなく型と順番**から作られます。メンバの名前を変えても、同じデータを読めます。
- 逆に、`int` を `float` に変える、メンバを並べ替える、間にメンバを足す、といった変更をすると、古いデータは**エラーとして**読めなくなります（でたらめな値にならないのが [zpp_bits](zpp-bits.md) との違いです）。
- 4 バイトのハッシュなので、ごくまれに違う型でも同じ値になることはあり得ます。完全な検証ではなく、「間違いに気づくための仕組み」と考えます。

## バージョン管理：compatible

ハッシュのおかげで間違いには気づけますが、「メンバを足したら古いセーブが全部読めない」のでは困ります。そこで、**後から足すメンバは `struct_pack::compatible<T, バージョン番号>`<strong> という型にして、</strong>構造体の最後に**足します。

```cpp
#include <print>
#include <string>

#include <ylt/struct_pack.hpp>

// リリースしたときの形
struct SaveV1 {
  std::string name;
  int level = 1;
};

// 後から gold を足した形
struct SaveV2 {
  std::string name;
  int level = 1;
  struct_pack::compatible<int, 20260401> gold;  // 最後に足す。番号は日付など増えていく値
};

int main() {
  // 古い形で保存したデータを、新しい形で読む
  auto old_data = struct_pack::serialize(SaveV1{"Alice", 12});
  auto loaded = struct_pack::deserialize<SaveV2>(old_data);
  if (loaded.has_value()) {
    const SaveV2& save = loaded.value();
    std::println("{} Lv.{} gold あり: {}", save.name, save.level, save.gold.has_value());
    std::println("gold = {}", save.gold.value_or(0));
  }
}
```

```text title="実行結果"
Alice Lv.12 gold あり: false
gold = 0
```

- `compatible` は `std::optional` と同じように使えます（`has_value()`、`value()`、`value_or()`、`*` など）。古いデータには値が無いので、空になります。
- <strong>`compatible` のメンバはハッシュの計算に入りません。</strong> そのため、足しても古いデータとハッシュが一致します。
- バージョン番号は、足すたびに**大きくなる数**にします（`20260401` のような日付がおすすめ）。同じ番号のものはまとめて扱われます。
- 新しいデータを古いプログラムで読むこともできます（知らない `compatible` の部分は読み飛ばされます）。

!!! warning "compatible でできないこと"
    - 最後以外の場所に足すことはできません（必ず最後に足していきます）。
    - 普通のメンバの**削除・型の変更・並べ替え**はできません。その場合は、古い形の構造体を残しておいて、[zpp_bits のページ](zpp-bits.md#バージョン管理) と同じように変換します。

## 自作のクラスを対応させる

| 方法 | 使う場面 |
| --- | --- |
| 何も書かない | 集成体（`struct` で全部 public、コンストラクタなし） |
| `YLT_REFL(型, メンバ...)` | コンストラクタがある、private メンバがある、保存するメンバを選びたい |

```cpp
class Enemy {
 public:
  Enemy() = default;
  Enemy(std::string name, int hp) : name_(std::move(name)), hp_(hp) {}

 private:
  std::string name_;
  int hp_ = 10;
  float cache_ = 0.0f;  // 保存しない

  // 保存するメンバを並べる（クラスの中に書くと private も使える）
  YLT_REFL(Enemy, name_, hp_);
};
```

!!! note "古い名前のマクロ"
    古いバージョンでは `STRUCT_PACK_REFL` という名前のマクロでした。インターネットの古い記事ではこちらが使われていることがあります。

## 対応している型

| 型 | 備考 |
| --- | --- |
| 数値、`bool`、enum | そのまま |
| `std::string`、`std::vector`、`std::list`、`std::deque` | 要素数 + 中身 |
| `std::map`、`std::set`、`std::unordered_map` など | 要素数 + 中身 |
| `std::array`、C 配列 | 中身だけ |
| `std::optional`、`std::variant`、`std::expected` | 有無・種類の番号 + 値 |
| `std::unique_ptr` | 有無 + 中身 |
| `std::pair`、`std::tuple` | 中身を順番に |
| `std::string_view`、`std::span` | 読み込むと**バッファを指す**（コピーしない） |
| 構造体（ネストしたものも） | メンバを順番に |

普通のポインタ（`T*`）と `std::shared_ptr` は保存できません。

## エラー処理

struct_pack は**例外を投げません**。エラーは戻り値で返ります。

| 関数 | 戻り値 |
| --- | --- |
| `deserialize<T>(...)` | `expected<T, エラーコード>`。`has_value()` で成功か分かる |
| `deserialize_to(obj, ...)` | エラーコード。`if (error)` で失敗が分かる |

| よくあるエラー | 原因 |
| --- | --- |
| `struct_pack::errc::no_buffer_space` | データが途中で切れている |
| `struct_pack::errc::invalid_buffer` | データが壊れている（ありえない値、要素数など） |
| `struct_pack::errc::hash_conflict` | 型のハッシュが一致しない（違う形の型で読んだ） |

エラーコードの型や細かい名前はバージョンによって少し違うので、まずは「成功か失敗か」で分岐するのが簡単です。

## 速さとサイズの特徴

| 項目 | 特徴 |
| --- | --- |
| 速さ | 非常に速い。数値だけの配列は memcpy でまとめてコピー |
| サイズ | 型のハッシュ（4 バイト）が増えるが、要素数は中身に合わせて小さく書かれる |
| 安全性 | 型のハッシュで、形の違うデータを読み込み時に検出できる |
| ゼロコピー | `std::string_view` / `std::span` / `trivial_view` のメンバは、読み込みでコピーしない |
| コンパイル時間 | テンプレートを多く使うので長め |

## 関数の詳しい説明

### serialize {#serialize}

```cpp
template <typename Buffer = std::vector<char>, typename... Args>
Buffer serialize(const Args&... args);

template <uint64_t conf, typename Buffer = std::vector<char>, typename... Args>
Buffer serialize(const Args&... args);
```

| 引数 | 意味 |
| --- | --- |
| `Buffer` | 結果を入れるコンテナの型。`std::vector<char>`（デフォルト）、`std::string`、`std::vector<std::byte>` など |
| `conf` | 設定（[sp_config](#sp_config)） |
| `args` | 保存するオブジェクト。複数渡すと `std::tuple` として保存される |

- **戻り値:** 保存したバイト列
- 複数渡したときは、読み込みも `deserialize<A, B>(buffer)` のように同じ型の並びで読みます。

### deserialize {#deserialize}

```cpp
template <typename T, typename... Args, typename View>
expected<T, err_code> deserialize(const View& view);

template <typename T, typename... Args>
expected<T, err_code> deserialize(const char* data, size_t size);

template <typename T, typename... Args, typename Reader>
expected<T, err_code> deserialize(Reader& reader);  // std::ifstream など
```

| 引数 | 意味 |
| --- | --- |
| `T` | 読み込む型 |
| `view` | バイト列（`std::vector<char>`、`std::string`、`std::span` など） |
| `data`, `size` | バイト列の先頭と大きさ |
| `reader` | 読み込み元のストリーム |

- **戻り値:** 成功なら `T` の値、失敗ならエラーコードを持つ `expected`
- `T` を作ってから中身を埋めるので、`T` はデフォルトコンストラクタが必要です。
- `std::string_view` のメンバは**バッファを指す**ので、`view` を消すと壊れます。

### deserialize_to {#deserialize_to}

```cpp
template <typename T, typename View>
err_code deserialize_to(T& t, const View& view);

template <typename T, typename Reader>
err_code deserialize_to(T& t, Reader& reader);
```

| 引数 | 意味 |
| --- | --- |
| `t` | 読み込み先のオブジェクト |
| `view` / `reader` | 読み込み元 |

- **戻り値:** エラーコード。成功なら `false` として評価される（`if (error)` で失敗）
- 毎フレーム同じオブジェクトに読み込む（通信の受信など）ときに、オブジェクトを作り直さずに済みます。vector などの容量も再利用されます。
- 失敗したとき、`t` は**途中まで書き換わっている**ことがあります。失敗したら `t` を使わないようにします。

### serialize_to {#serialize_to}

```cpp
template <typename Buffer, typename... Args>
void serialize_to(Buffer& buffer, const Args&... args);

template <typename Writer, typename... Args>
void serialize_to(Writer& writer, const Args&... args);  // std::ofstream など
```

| 引数 | 意味 |
| --- | --- |
| `buffer` | 書き込み先のコンテナ。**後ろに書き足される** |
| `writer` | 書き込み先のストリーム |
| `args` | 保存するオブジェクト |

- 既存のバッファの後ろに書き足すので、「ヘッダを書いてから本体を書く」ような使い方ができます。
- 同じバッファを使い回すと、メモリの再確保が減ります（`buffer.clear()` してから書く）。

### compatible {#compatible}

```cpp
template <typename T, uint64_t version = 0>
struct compatible : public std::optional<T> { /* ... */ };
```

| 引数 | 意味 |
| --- | --- |
| `T` | 中身の型 |
| `version` | 足したときのバージョン番号。足すたびに大きくする |

- 後から足したメンバ用の型です。`std::optional` を継承しているので、同じように使えます。
- 構造体の**最後**に置きます。複数足すときは、バージョン番号が小さい順に並べます。
- ハッシュの計算に入らないので、足しても古いデータを読めます。

### YLT_REFL {#ylt_refl}

```cpp
YLT_REFL(Type, member1, member2, ...);
```

| 引数 | 意味 |
| --- | --- |
| `Type` | クラスの名前 |
| `member...` | 保存するメンバ（並べた順番に保存される） |

- クラスの中に書くと private メンバも使えます。クラスの外（同じ名前空間）に書くこともできます（その場合は public メンバだけ）。
- 並べたメンバだけが保存されるので、キャッシュなどを保存から外せます。

### get_needed_size {#get_needed_size}

```cpp
template <typename... Args>
serialize_buffer_size get_needed_size(const Args&... args);
```

| 引数 | 意味 |
| --- | --- |
| `args` | 保存するオブジェクト |

- **戻り値:** 保存に必要なバイト数（`.size()` で取る）
- 固定の大きさのバッファに収まるか、事前に確かめるときに使います。

### get_field {#get_field}

```cpp
template <typename T, size_t I, typename View>
expected<field_type, err_code> get_field(const View& view);
```

| 引数 | 意味 |
| --- | --- |
| `T` | 保存されている型 |
| `I` | 取り出したいメンバの番号（0 から） |
| `view` | バイト列 |

- **戻り値:** その番号のメンバだけを読んだ値
- 大きなデータの中から 1 つのメンバだけ欲しいとき（セーブ一覧の画面で、プレイヤー名だけ表示する、など）に使います。

```cpp
// Player の 0 番目のメンバ（name）だけ読む
auto name = struct_pack::get_field<Player, 0>(buffer);
```

### var_int32_t {#var_int32_t}

```cpp
using var_int32_t = /* 可変長の int32_t */;
using var_uint32_t = /* 可変長の uint32_t */;
using var_int64_t = /* 可変長の int64_t */;
using var_uint64_t = /* 可変長の uint64_t */;
```

- 値が小さいほど少ないバイトで保存される整数型です（Protocol Buffers の varint と同じ）。
- メンバの型をこれにすると、そのメンバだけ可変長になります。ID や個数など、小さい数が多いときにサイズを減らせます。
- 符号付きの型は、負の数も小さくなる ZigZag という方式で保存されます。

### trivial_view {#trivial_view}

```cpp
template <typename T>
struct trivial_view;
```

| 引数 | 意味 |
| --- | --- |
| `T` | 数値だけでできた型（memcpy でコピーできる型） |

- 読み込むとき、`T` をコピーせずに**バッファの中を直接指す**ようにします。巨大な配列をコピーせずに読みたいときに使います。
- バッファが消えると使えなくなります。

### sp_config {#sp_config}

```cpp
enum sp_config : uint64_t {
  DEFAULT = 0,
  DISABLE_TYPE_INFO = 0b1,
  ENABLE_TYPE_INFO = 0b10,
  DISABLE_ALL_META_INFO = 0b11,
};
```

| 値 | 意味 |
| --- | --- |
| `DEFAULT` | デバッグビルドでは詳しい型情報も入れ、リリースビルドではハッシュだけ |
| `DISABLE_TYPE_INFO` | 詳しい型情報を入れない（ハッシュは入る） |
| `ENABLE_TYPE_INFO` | 詳しい型情報を必ず入れる（ハッシュが一致しない原因を調べられる） |
| `DISABLE_ALL_META_INFO` | ハッシュも入れない。一番小さいが、型のチェックも `compatible` も使えない |

```cpp
auto buffer = struct_pack::serialize<struct_pack::sp_config::DISABLE_ALL_META_INFO>(packet);
```

- 書くときと読むときで同じ設定を使います。
- 構造体の中に `static constexpr auto struct_pack_config = struct_pack::sp_config::DISABLE_ALL_META_INFO;` のように書いて、型ごとに設定することもできます（書き方はバージョンによって違います）。

## フラグ・オプション

| 設定 | 書く場所 | 意味 |
| --- | --- | --- |
| `sp_config`（上の表） | `serialize<設定>` / `deserialize<設定, T>` | 型情報・ハッシュを入れるか |
| `compatible<T, version>` | メンバの型 | 後から足したメンバ |
| `var_int32_t` など | メンバの型 | 可変長の整数 |
| `trivial_view<T>` | メンバの型 | 読み込みでコピーしない |
| `std::string_view` / `std::span` | メンバの型 | 読み込みでコピーしない（バッファを指す） |

## ゲームでの使いどころ

| 場面 | 使い方 |
| --- | --- |
| セーブデータ | 構造体のまま保存。後から足すメンバは `compatible` |
| オンラインの通信 | `deserialize_to` で受信用の構造体を使い回す。サーバーと型の形がずれると検出できる |
| 製品版のマスターデータ | 開発中の JSON / YAML を変換して保存 |
| ツールとゲームの間のデータ | 型のハッシュで、ツールとゲームのバージョン違いに気づける |
| セーブの一覧画面 | `get_field` でプレイヤー名だけ読む |

## よくあるミス

??? failure "メンバの型を変えて古いデータが読めなくなる"
    `int hp` を `float hp` に変えると、型のハッシュが変わって古いデータはすべてエラーになります。リリース後に形を変えるときは、`compatible` で足すか、古い形の構造体を残して変換します。

??? failure "compatible を途中に入れる"
    `compatible` のメンバは必ず構造体の最後に置きます。途中に入れると、正しく読めません。

??? failure "string_view のメンバでバッファを先に消す"
    `std::string_view` のメンバは、読み込むとバッファの中を指します。バッファを消すと壊れた文字列になります。保存するデータには `std::string` を使い、`string_view` は「読み込み直後にすぐ使う」場合だけにします。

??? failure "エラーを確認せずに value() を呼ぶ"
    `deserialize<T>(buffer).value()` は、失敗していると例外（またはプログラムの停止）になります。必ず `has_value()` で確認します。

??? failure "DISABLE_ALL_META_INFO で保存して compatible を使う"
    メタ情報を全部消すと、型のチェックも互換フィールドも使えません。通信のような「両側のプログラムが必ず同じ」場合だけにします。

## 類似ライブラリ

| ライブラリ | 違い |
| --- | --- |
| [zpp_bits](zpp-bits.md) | 同じくらい速い。型の情報を入れないぶん小さい。バージョン管理は自分で |
| [cereal](cereal.md) | クラスごとのバージョン番号と継承に対応。速さは劣る |
| [cista](cista.md) | 読み込みでコピーしない。専用の型を使う |
| FlatBuffers | スキーマファイルを書いてコードを生成。ゼロコピーで読め、他の言語とも使える |

## これだけ覚える

!!! abstract "まとめ"
    - [x] `struct_pack::serialize(obj)` で保存、`struct_pack::deserialize<T>(buffer)` で読み込み
    - [x] 読み込みは `expected`。`has_value()` を確認する
    - [x] 型のハッシュで、形の違うデータに気づける（名前は関係ない）
    - [x] 後から足すメンバは最後に `compatible<T, 番号>`
    - [x] private メンバは `YLT_REFL`
    - [x] `string_view` のメンバはバッファを指す

## 関連ページ

- [シリアライズの概要](../../engine/serialization/index.md)
- [zpp_bits（バイナリ・速さ重視）](zpp-bits.md)
- [cista（バイナリ・ゼロコピー）](cista.md)
- [std::expected](../../stl/utilities/expected.md)
- [yalantinglibs（GitHub）](https://github.com/alibaba/yalantinglibs)
- [struct_pack の説明（yalantinglibs ドキュメント）](https://alibaba.github.io/yalantinglibs/en/struct_pack/struct_pack_intro.html)
