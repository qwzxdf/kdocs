---
title: cereal（バイナリ・定番）
tags:
  - ゲームエンジン
  - シリアライズ
---

# cereal（バイナリ・定番）

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="perf perf-3">○ 普通</span>
<span class="ver ver-11">C++11〜</span>
`#include <cereal/archives/binary.hpp>`
</div>

**cereal**（シリアル）は、C++ のオブジェクトを**バイナリ・JSON・XML**に保存して、また読み戻すためのライブラリです。自分の型に `serialize` という関数を 1 つ書くだけで、**同じ関数で保存と読み込みの両方**ができるのが最大の特徴です（書く順番と読む順番がずれるミスが起きません）。`std::vector`、`std::map`、`std::string` などの STL のコンテナや、`std::shared_ptr`・`std::unique_ptr`、さらに**継承したクラス（ポリモーフィズム）** の保存にも対応していて、**クラスごとのバージョン番号**の仕組みも最初から入っています。ヘッダオンリーで導入も簡単なので、「C++ でセーブデータをバイナリで保存する」ときの定番になっています。

!!! tip "結論"
    - **バイナリのセーブデータはまずこれ。** 型に `serialize` を 1 つ書けば、保存と読み込みの両方ができる。
    - 使う型に合わせて **`cereal/types/vector.hpp`** などのヘッダを include する（忘れるとコンパイルエラー）。
    - **アーカイブはスコープ `{}` で囲んで、必ず破棄してから**ファイルやデータを使う。
    - 後から形が変わる型には **`CEREAL_CLASS_VERSION`** と `serialize(Archive&, std::uint32_t version)` でバージョンを付ける。
    - 普通のポインタ（`T*`）は保存できない。`unique_ptr` / `shared_ptr` にするか、ID で保存する。
    - 違う CPU（エンディアン）の間でやり取りするなら `PortableBinaryArchive`。

!!! info "このページを読む前に"
    [シリアライズの概要](index.md) の「自作の簡単なバイナリシリアライザ」を読むと、cereal が中で何をしているかが分かります。[テンプレート](../../basics/template.md) と [継承と仮想関数](../../basics/virtual.md)、[unique_ptr](../../stl/utilities/unique_ptr.md) も関係します。

## 導入

ヘッダオンリーです。

=== "vcpkg"

    ```text
    vcpkg install cereal
    ```

    ```cmake
    find_package(cereal CONFIG REQUIRED)
    target_link_libraries(my_game PRIVATE cereal::cereal)
    ```

=== "CMake FetchContent"

    ```cmake
    include(FetchContent)
    FetchContent_Declare(
      cereal
      GIT_REPOSITORY https://github.com/USCiLab/cereal.git
      GIT_TAG v1.3.2
      GIT_SHALLOW TRUE)
    set(JUST_INSTALL_CEREAL ON)  # テストやサンプルをビルドしない
    FetchContent_MakeAvailable(cereal)
    target_link_libraries(my_game PRIVATE cereal::cereal)
    ```

=== "フォルダを直接置く"

    [GitHub](https://github.com/USCiLab/cereal) の `include/cereal` フォルダをまるごとプロジェクトにコピーし、インクルードディレクトリに追加します。

## 仕組み：アーカイブと serialize 関数

cereal は**アーカイブ**（保存先・読み込み元の形式）と、型ごとの **`serialize` 関数**の 2 つでできています。

```text
            serialize 関数（型ごとに 1 つ）
                 ar(name, level, items);
                       │
       ┌───────────────┼────────────────┐
       ▼               ▼                ▼
 BinaryOutputArchive  JSONOutputArchive  BinaryInputArchive
   （保存・バイナリ）    （保存・JSON）      （読み込み・バイナリ）
```

`ar(name, level, items);` という同じ 1 行が、**保存用のアーカイブ**が渡されたときは「書く」、**読み込み用のアーカイブ**が渡されたときは「読む」になります。そのため、保存と読み込みで順番がずれることがありません。アーカイブを入れ替えれば、同じ `serialize` 関数でバイナリにも JSON にもなります。

## 関数一覧

| 関数・マクロ | 重要度 | 何をする |
| --- | --- | --- |
| [`serialize`（メンバ）](#serialize_member) | <span class="rank rank-must">必須</span> | 保存と読み込みを 1 つの関数で書く |
| [`アーカイブの operator()`](#archive_call) | <span class="rank rank-must">必須</span> | 値をアーカイブに通す（`ar(x, y)`） |
| [`BinaryOutputArchive`](#binary_output) | <span class="rank rank-must">必須</span> | バイナリで保存する |
| [`BinaryInputArchive`](#binary_input) | <span class="rank rank-must">必須</span> | バイナリを読み込む |
| [`CEREAL_CLASS_VERSION`](#class_version) | <span class="rank rank-must">必須</span> | 型にバージョン番号を付ける |
| [`serialize`（メンバ以外）](#serialize_nonmember) | <span class="rank rank-often">よく使う</span> | 変更できない型（ライブラリの型）に保存方法を付ける |
| [`save`](#save) | <span class="rank rank-often">よく使う</span> | 保存の処理だけを書く（load と組で使う） |
| [`load`](#load) | <span class="rank rank-often">よく使う</span> | 読み込みの処理だけを書く（save と組で使う） |
| [`CEREAL_NVP`](#cereal_nvp) | <span class="rank rank-often">よく使う</span> | JSON・XML でメンバ名をキーにする |
| [`make_nvp`](#make_nvp) | <span class="rank rank-often">よく使う</span> | 好きな名前をキーにする |
| [`JSONOutputArchive`](#json_output) | <span class="rank rank-often">よく使う</span> | JSON で保存する |
| [`JSONInputArchive`](#json_input) | <span class="rank rank-often">よく使う</span> | JSON を読み込む |
| [`CEREAL_REGISTER_TYPE`](#register_type) | <span class="rank rank-sometimes">たまに</span> | 継承したクラスを登録する |
| [`CEREAL_REGISTER_POLYMORPHIC_RELATION`](#register_relation) | <span class="rank rank-sometimes">たまに</span> | 親子関係を登録する |
| [`PortableBinaryOutputArchive`](#portable_binary) | <span class="rank rank-sometimes">たまに</span> | エンディアンをそろえて保存する |
| [`save_minimal`](#save_minimal) | <span class="rank rank-sometimes">たまに</span> | 型を 1 つの値（文字列・数値）として保存する |
| [`load_minimal`](#load_minimal) | <span class="rank rank-sometimes">たまに</span> | 1 つの値から型を読み込む |
| [`load_and_construct`](#load_and_construct) | <span class="rank rank-rare">知ってるだけ</span> | デフォルトコンストラクタが無い型を読む |
| [`binary_data`](#binary_data) | <span class="rank rank-sometimes">たまに</span> | 配列をまとめてバイトのまま保存する |
| [`make_size_tag`](#make_size_tag) | <span class="rank rank-rare">知ってるだけ</span> | 自作のコンテナで要素数を保存する |
| [`XMLOutputArchive`](#xml_output) | <span class="rank rank-rare">知ってるだけ</span> | XML で保存する |

## よくある使い方

```cpp
#include <print>
#include <sstream>
#include <string>
#include <vector>

#include <cereal/archives/binary.hpp>
#include <cereal/types/string.hpp>  // std::string を使うので必要
#include <cereal/types/vector.hpp>  // std::vector を使うので必要

struct Player {
  std::string name;
  int level = 1;
  std::vector<int> items;

  // 保存にも読み込みにも使われる
  template <class Archive>
  void serialize(Archive& ar) {
    ar(name, level, items);
  }
};

int main() {
  std::stringstream stream;  // 本当は std::ofstream / std::ifstream（binary モード）

  {
    Player player{"Alice", 12, {101, 205, 330}};
    cereal::BinaryOutputArchive archive(stream);
    archive(player);
  }  // ここでアーカイブが破棄されて、書き込みが完了する

  std::println("{} バイト", stream.str().size());

  Player loaded;
  {
    cereal::BinaryInputArchive archive(stream);
    archive(loaded);
  }
  std::println("{} Lv.{} {}", loaded.name, loaded.level, loaded.items);
}
```

```text title="実行結果"
37 バイト
Alice Lv.12 [101, 205, 330]
```

37 バイトの内訳は、次のとおりです。cereal のバイナリは、**要素の数を 8 バイト（`std::uint64_t`）** で書きます。

| 中身 | バイト数 |
| --- | --- |
| `name` の長さ（5） | 8 |
| `name` の中身 `Alice` | 5 |
| `level`（`int`） | 4 |
| `items` の要素数（3） | 8 |
| `items` の中身（`int` × 3） | 12 |
| **合計** | **37** |

### ファイルに保存する

```cpp
#include <fstream>

#include <cereal/archives/binary.hpp>

bool SaveGame(const SaveData& data, const char* path) {
  std::ofstream file(path, std::ios::binary);  // binary を忘れない
  if (!file) {
    return false;
  }
  {
    cereal::BinaryOutputArchive archive(file);
    archive(data);
  }
  return static_cast<bool>(file);
}

bool LoadGame(SaveData& data, const char* path) {
  std::ifstream file(path, std::ios::binary);
  if (!file) {
    return false;
  }
  try {
    cereal::BinaryInputArchive archive(file);
    archive(data);
  } catch (const cereal::Exception& e) {
    return false;  // 途中で切れている、形が違う など
  }
  return true;
}
```

本番のセーブでは、[壊れない保存](../../basics/file-io.md#壊れない保存一時ファイル--rename)（一時ファイルに書いてから名前を変える）と組み合わせます。

## 型に対応させるヘッダ

cereal は、**使う型ごとにヘッダを include する**必要があります。忘れると、`cereal could not find any output serialization functions` のような長いエラーになります。

| ヘッダ | 対応する型 |
| --- | --- |
| `cereal/types/string.hpp` | `std::string` |
| `cereal/types/vector.hpp` | `std::vector` |
| `cereal/types/array.hpp` | `std::array` |
| `cereal/types/map.hpp` | `std::map`、`std::multimap` |
| `cereal/types/unordered_map.hpp` | `std::unordered_map` |
| `cereal/types/set.hpp` / `unordered_set.hpp` | `std::set` / `std::unordered_set` |
| `cereal/types/deque.hpp` / `list.hpp` | `std::deque` / `std::list` |
| `cereal/types/utility.hpp` | `std::pair` |
| `cereal/types/tuple.hpp` | `std::tuple` |
| `cereal/types/memory.hpp` | `std::unique_ptr`、`std::shared_ptr`、`std::weak_ptr` |
| `cereal/types/optional.hpp` | `std::optional` |
| `cereal/types/variant.hpp` | `std::variant` |
| `cereal/types/chrono.hpp` | `std::chrono::duration`、`time_point` |
| `cereal/types/bitset.hpp` | `std::bitset` |
| `cereal/types/polymorphic.hpp` | 継承したクラスをポインタで保存する |

`int`、`float`、`bool`、enum、C 配列（`int a[4]`）などの基本の型は、何も include しなくても使えます。

## アーカイブの種類

| アーカイブ | ヘッダ | 形式 | 特徴 |
| --- | --- | --- | --- |
| `BinaryOutputArchive` / `BinaryInputArchive` | `cereal/archives/binary.hpp` | バイナリ | 一番小さく速い。同じ種類の CPU 同士でだけ読める |
| `PortableBinaryOutputArchive` / `...InputArchive` | `cereal/archives/portable_binary.hpp` | バイナリ | エンディアンが違っても読める。少しだけ遅い |
| `JSONOutputArchive` / `JSONInputArchive` | `cereal/archives/json.hpp` | JSON | 人が読める。デバッグに便利。大きく遅い |
| `XMLOutputArchive` / `XMLInputArchive` | `cereal/archives/xml.hpp` | XML | 人が読める。ほぼ使わない |

開発中は JSON アーカイブで保存して中身を確認し、製品版ではバイナリにする、という使い分けが同じ `serialize` 関数のままできます。

## 自作の型を対応させる 5 つの書き方

| 書き方 | 使う場面 |
| --- | --- |
| メンバ関数 `serialize` | ほとんどの場合（自分で書いたクラス） |
| メンバ以外の関数 `serialize` | 自分では変更できない型（他のライブラリの `Vec3` など） |
| `save` と `load` を組で書く | 保存と読み込みで処理が違う（読み込み後に再計算するなど） |
| `save_minimal` と `load_minimal` を組で書く | 型を 1 つの数値・文字列で表したい（ID、色など） |
| `load_and_construct` | デフォルトコンストラクタが無い型 |

どれも、1 つの型に対して**1 つの書き方だけ**を使います（2 つ書くと「どれを使えばいいか分からない」というエラーになります）。

## バージョン管理

cereal には**クラスごとのバージョン番号**の仕組みがあります。

```cpp
#include <cstdint>
#include <print>
#include <sstream>
#include <string>

#include <cereal/archives/binary.hpp>
#include <cereal/types/string.hpp>

struct SaveData {
  std::string player_name;
  int level = 1;
  int gold = 0;  // バージョン 2 で追加

  template <class Archive>
  void serialize(Archive& ar, const std::uint32_t version) {
    ar(player_name, level);
    if (version >= 2) {
      ar(gold);  // 保存するときは常に最新（2）なので必ず書かれる
    }
  }
};
CEREAL_CLASS_VERSION(SaveData, 2);  // 今のバージョン

int main() {
  std::stringstream stream;
  {
    cereal::BinaryOutputArchive archive(stream);
    archive(SaveData{"Alice", 12, 500});
  }
  SaveData loaded;
  {
    cereal::BinaryInputArchive archive(stream);
    archive(loaded);
  }
  std::println("{} Lv.{} {}G", loaded.player_name, loaded.level, loaded.gold);
}
```

```text title="実行結果"
Alice Lv.12 500G
```

- 保存するとき、cereal は**その型のバージョン番号**（4 バイト）をデータに書きます。同じ型が何度出てきても、書くのは最初の 1 回だけです。
- 読み込むときは、**データに書かれていたバージョン番号**が `version` に入ってきます。古いセーブ（バージョン 1）を読むと `version` は 1 なので、`gold` は読まれずデフォルトの 0 のままになります。
- `CEREAL_CLASS_VERSION` を書かない型はバージョン 0 として扱われ、バージョン番号はデータに書かれません。

!!! warning "最初からバージョンを付けておく"
    バージョンを付けていなかった型に後から `CEREAL_CLASS_VERSION` を付けると、**古いデータにはバージョン番号の 4 バイトが無い**ので、読み込みがずれて壊れます。リリースする（他の人に配る）型には、**最初から** `CEREAL_CLASS_VERSION(T, 1)` を付けておきます。

!!! note "バイナリは「順番」が全て"
    バイナリアーカイブには、名前もデータの種類も書かれていません。**書いた順番に読むだけ**です。メンバの順番を入れ替える、型を `int` から `std::int64_t` に変える、といった変更は、必ずバージョンで分岐させます。

## 継承したクラスを保存する（ポリモーフィズム）

`std::vector<std::unique_ptr<Enemy>>` に `Slime` や `Bat` が入っている、というような「親のポインタで子のオブジェクトを持つ」場合も保存できます。cereal は**型の名前**も保存して、読み込むときに正しい子のクラスを作り直してくれます。

```cpp
#include <memory>
#include <print>
#include <sstream>
#include <vector>

#include <cereal/archives/binary.hpp>
#include <cereal/types/base_class.hpp>
#include <cereal/types/memory.hpp>
#include <cereal/types/polymorphic.hpp>
#include <cereal/types/vector.hpp>

class Enemy {
 public:
  virtual ~Enemy() = default;
  virtual void Print() const = 0;

  template <class Archive>
  void serialize(Archive& ar) {
    ar(hp_);
  }

 protected:
  int hp_ = 10;
};

class Slime : public Enemy {
 public:
  void Print() const override { std::println("スライム HP{} 分裂{}", hp_, split_); }

  template <class Archive>
  void serialize(Archive& ar) {
    ar(cereal::base_class<Enemy>(this), split_);  // 親の部分も保存する
  }

 private:
  int split_ = 2;
};

class Bat : public Enemy {
 public:
  void Print() const override { std::println("コウモリ HP{}", hp_); }

  template <class Archive>
  void serialize(Archive& ar) {
    ar(cereal::base_class<Enemy>(this));
  }
};

// 子のクラスを登録する（型の名前が保存される）
CEREAL_REGISTER_TYPE(Slime)
CEREAL_REGISTER_TYPE(Bat)
CEREAL_REGISTER_POLYMORPHIC_RELATION(Enemy, Slime)
CEREAL_REGISTER_POLYMORPHIC_RELATION(Enemy, Bat)

int main() {
  std::stringstream stream;
  {
    std::vector<std::unique_ptr<Enemy>> enemies;
    enemies.push_back(std::make_unique<Slime>());
    enemies.push_back(std::make_unique<Bat>());
    cereal::BinaryOutputArchive archive(stream);
    archive(enemies);
  }

  std::vector<std::unique_ptr<Enemy>> loaded;
  {
    cereal::BinaryInputArchive archive(stream);
    archive(loaded);
  }
  for (const auto& enemy : loaded) {
    enemy->Print();
  }
}
```

```text title="実行結果"
スライム HP10 分裂2
コウモリ HP10
```

- `cereal::base_class<Enemy>(this)` で、**親クラスの部分**も一緒に保存します。忘れると親のメンバ（`hp_`）が保存されません。
- 登録マクロは、**ヘッダではなく .cpp に書く**か、アーカイブのヘッダを include した後に書きます。DLL や静的ライブラリをまたぐときは `CEREAL_REGISTER_DYNAMIC_INIT` も必要になることがあります。
- 登録した型の名前（`"Slime"`）がデータに保存されるので、**クラス名を変えると古いデータが読めなくなります**。`CEREAL_REGISTER_TYPE_WITH_NAME(Slime, "slime")` で名前を固定しておくと安全です。

## ポインタの扱い

| 型 | 保存できるか | 注意 |
| --- | --- | --- |
| `T*`（普通のポインタ） | **できない**（コンパイルエラー） | 所有者がはっきりしないため。ID で保存する |
| `std::unique_ptr<T>` | できる | 中身が保存される。`nullptr` も保存できる |
| `std::shared_ptr<T>` | できる | **同じオブジェクトを指す shared_ptr は 1 回だけ保存**され、読み込み後も共有された状態に戻る |
| `std::weak_ptr<T>` | できる | 指している shared_ptr も一緒に保存されている必要がある |

ゲームのオブジェクト同士の参照（「この弾は敵 3 番が撃った」）は、ポインタではなく [ハンドルや ID](../handle.md) で保存するのが基本です。

## エラー処理

cereal はエラーを**例外**（`cereal::Exception`、`std::runtime_error` の子）で知らせます。

| 状況 | 結果 |
| --- | --- |
| データが途中で切れている | `cereal::Exception`（`Failed to read N bytes from input stream!`） |
| JSON のキーが見つからない | `cereal::Exception`（JSON アーカイブのとき） |
| 型や順番がずれている（バイナリ） | **エラーにならないことがある**。おかしな値が読まれたり、巨大な要素数を読んでメモリ不足（`std::bad_alloc`）になったりする |

!!! danger "バイナリアーカイブは「間違ったデータ」を見分けられない"
    バイナリアーカイブは、データの中に型の情報を持っていません。違う型のデータや壊れたデータを読むと、エラーにならずにでたらめな値になることがあります。特に、要素数が壊れていると「40 億個の vector を確保しようとする」などが起きます。セーブデータには、**先頭にマジックナンバー（`'SAVE'` などの決まった値）とバージョン**、**最後にチェックサム（CRC32 など）** を付けて、壊れていたら読まないようにします。インターネットから来るデータなど、**信用できないデータを cereal のバイナリで読むのは危険**です。

## 速さとサイズの特徴

| 項目 | 特徴 |
| --- | --- |
| 速さ | バイナリアーカイブは十分速い。ただし `std::ostream` / `std::istream` を通すので、[zpp_bits](zpp-bits.md) や [struct_pack](struct-pack.md) よりは遅い |
| サイズ | 要素数が 8 バイト固定なので、短い文字列や小さい vector が多いと少し大きくなる |
| JSON アーカイブ | 中で RapidJSON を使う。バイナリよりずっと大きく遅いが、デバッグに便利 |
| コンパイル時間 | テンプレートを多く使うので、少し長くなる |

学生のゲームのセーブデータなら、速さが問題になることはまずありません。

## 関数の詳しい説明

### serialize（メンバ） {#serialize_member}

```cpp
template <class Archive>
void serialize(Archive& ar);

template <class Archive>
void serialize(Archive& ar, const std::uint32_t version);
```

| 引数 | 意味 |
| --- | --- |
| `ar` | アーカイブ。保存のときは出力用、読み込みのときは入力用が渡される |
| `version` | 読み込むときはデータに書かれたバージョン、保存するときは `CEREAL_CLASS_VERSION` の値 |

- `private` にしたいときは、クラスの中に `friend class cereal::access;` を書きます。
- 保存のときは `const` なオブジェクトでも呼ばれます（cereal が中で `const` を外して呼びます）。この関数の中で、メンバの値を**変更してはいけません**。

```cpp
class Inventory {
 private:
  friend class cereal::access;  // cereal から private の serialize を呼べるようにする

  template <class Archive>
  void serialize(Archive& ar) {
    ar(items_, gold_);
  }

  std::vector<int> items_;
  int gold_ = 0;
};
```

### アーカイブの operator() {#archive_call}

```cpp
template <class... Types>
ArchiveType& operator()(Types&&... args);
```

| 引数 | 意味 |
| --- | --- |
| `args` | 保存・読み込みする値。何個でも並べられる |

- **戻り値:** アーカイブ自身
- `ar(a, b, c);` は `ar(a); ar(b); ar(c);` と同じです。
- `ar << x;`（出力アーカイブ）、`ar >> x;`（入力アーカイブ）、`ar & x;`（両方）という書き方もできますが、`ar(x)` が一番よく使われます。

### BinaryOutputArchive {#binary_output}

```cpp
class BinaryOutputArchive {
 public:
  explicit BinaryOutputArchive(std::ostream& stream);
};
```

| 引数 | 意味 |
| --- | --- |
| `stream` | 書き込み先。`std::ofstream`（`std::ios::binary` で開く）や `std::stringstream` |

- 値を**そのままのバイト**（メモリ上の表現）で書きます。整数はその CPU のエンディアン、`int` は 4 バイト、`long` は環境によって 4 か 8 バイトです。
- 違う環境で読むかもしれないデータには、`int`・`long` ではなく `std::int32_t`・`std::int64_t` を使います。
- アーカイブを**破棄したとき**に処理が完了します。必ずスコープ `{}` で囲みます。

### BinaryInputArchive {#binary_input}

```cpp
class BinaryInputArchive {
 public:
  explicit BinaryInputArchive(std::istream& stream);
};
```

| 引数 | 意味 |
| --- | --- |
| `stream` | 読み込み元。`std::ifstream`（`std::ios::binary`）など |

- **例外:** データが足りないと `cereal::Exception`
- 読み込み先のオブジェクトは、**事前に作っておく**必要があります（デフォルトコンストラクタで作ってから、中身を上書きする）。

### CEREAL_CLASS_VERSION {#class_version}

```cpp
CEREAL_CLASS_VERSION(TYPE, VERSION_NUMBER);
```

| 引数 | 意味 |
| --- | --- |
| `TYPE` | バージョンを付ける型 |
| `VERSION_NUMBER` | 今のバージョン番号（`std::uint32_t`） |

- 型の定義の後、**名前空間の外（グローバル）** に書きます。型が名前空間の中にあるなら `CEREAL_CLASS_VERSION(game::SaveData, 2);` と書きます。
- これを書いた型は、`serialize` に `version` 引数を付けて受け取れます（付けなくても動きます）。

### serialize（メンバ以外） {#serialize_nonmember}

```cpp
template <class Archive>
void serialize(Archive& ar, T& value);

template <class Archive>
void serialize(Archive& ar, T& value, const std::uint32_t version);
```

| 引数 | 意味 |
| --- | --- |
| `ar` | アーカイブ |
| `value` | 保存・読み込みする値 |
| `version` | バージョン |

- 自分では変更できない型（数学ライブラリの `glm::vec3` など）に使います。
- **その型と同じ名前空間**か、`cereal` 名前空間に書きます。

```cpp
namespace glm {

template <class Archive>
void serialize(Archive& ar, vec3& v) {
  ar(v.x, v.y, v.z);
}

}  // namespace glm
```

### save {#save}

```cpp
template <class Archive>
void save(Archive& ar) const;

template <class Archive>
void save(Archive& ar, const std::uint32_t version) const;
```

| 引数 | 意味 |
| --- | --- |
| `ar` | 出力用のアーカイブ |
| `version` | 保存するバージョン（`CEREAL_CLASS_VERSION` の値） |

- 保存のときだけ呼ばれます。`serialize` の代わりに、**`load` と必ず組で**書きます。`serialize` と同時に書いてはいけません。
- `const` メンバ関数にします（保存でオブジェクトを変えないため）。
- 保存するときに計算した値を書く、キャッシュなど保存しなくてよいメンバを飛ばす、といったときに使います。

```cpp
template <class Archive>
void save(Archive& ar) const {
  ar(tiles_);  // 当たり判定のデータ（collision_）は保存しない
}
```

### load {#load}

```cpp
template <class Archive>
void load(Archive& ar);

template <class Archive>
void load(Archive& ar, const std::uint32_t version);
```

| 引数 | 意味 |
| --- | --- |
| `ar` | 入力用のアーカイブ |
| `version` | データに書かれていたバージョン |

- 読み込みのときだけ呼ばれます。`save` と**同じ順番**で読みます。
- 読み込んだ後に、保存しなかったデータを作り直すのに使います。

```cpp
template <class Archive>
void load(Archive& ar) {
  ar(tiles_);
  RebuildCollision();  // 読み込んだ後に当たり判定を作り直す
}
```

### CEREAL_NVP {#cereal_nvp}

```cpp
#define CEREAL_NVP(T) ::cereal::make_nvp(#T, T)
```

| 引数 | 意味 |
| --- | --- |
| `T` | メンバ（変数名がそのままキーになる） |

- NVP は「Name-Value Pair（名前と値の組）」の略です。JSON・XML アーカイブで、キーの名前になります。
- バイナリアーカイブでは名前は**無視される**ので、付けても大きさは変わりません。JSON でも使うかもしれないなら、最初から付けておくと便利です。
- 名前を付けないと、JSON では `"value0"`、`"value1"` という名前になります。

### make_nvp {#make_nvp}

```cpp
template <class T>
NameValuePair<T> make_nvp(const std::string& name, T&& value);
```

| 引数 | 意味 |
| --- | --- |
| `name` | キーの名前 |
| `value` | 値 |

- メンバ名と違う名前をキーにしたいときに使います（`m_hp` を `"hp"` として保存する、など）。

### JSONOutputArchive {#json_output}

```cpp
class JSONOutputArchive {
 public:
  explicit JSONOutputArchive(std::ostream& stream,
                             Options const& options = Options::Default());
};
```

| 引数 | 意味 |
| --- | --- |
| `stream` | 書き込み先 |
| `options` | 字下げや小数の桁数の設定（[フラグ](#flags)） |

```cpp
#include <print>
#include <sstream>
#include <string>
#include <vector>

#include <cereal/archives/json.hpp>
#include <cereal/types/string.hpp>
#include <cereal/types/vector.hpp>

struct Player {
  std::string name;
  int level = 1;
  std::vector<int> items;

  template <class Archive>
  void serialize(Archive& ar) {
    ar(CEREAL_NVP(name), CEREAL_NVP(level), CEREAL_NVP(items));
  }
};

int main() {
  std::stringstream stream;
  {
    cereal::JSONOutputArchive archive(stream);
    archive(cereal::make_nvp("player", Player{"Alice", 12, {101, 205}}));
  }  // 破棄されたときに最後の } が書かれる
  std::println("{}", stream.str());
}
```

```text title="実行結果"
{
    "player": {
        "name": "Alice",
        "level": 12,
        "items": [
            101,
            205
        ]
    }
}
```

- 出力の一番外側は、必ずオブジェクト `{ }` になります。
- **アーカイブを破棄するまで、最後の `}` が書かれません。** スコープを閉じる前に `stream.str()` を見ると、途中までの JSON になっています。
- キーの順番は書いた順番になります。

### JSONInputArchive {#json_input}

```cpp
class JSONInputArchive {
 public:
  explicit JSONInputArchive(std::istream& stream);
};
```

| 引数 | 意味 |
| --- | --- |
| `stream` | 読み込み元 |

- **例外:** JSON が壊れている、キーが見つからない、型が違うと `cereal::Exception`
- 名前付き（NVP）の値は、名前で探して読みます。ただし、基本は**書いたときと同じ順番**で読む前提です。順番が違うとその分だけ探すので遅くなります。
- 人が書いた JSON を読むのには向いていません（キーが足りないとエラーになるため）。人が書く JSON は [nlohmann/json](nlohmann-json.md) で読みます。

### CEREAL_REGISTER_TYPE {#register_type}

```cpp
CEREAL_REGISTER_TYPE(T)
CEREAL_REGISTER_TYPE_WITH_NAME(T, Name)
```

| 引数 | 意味 |
| --- | --- |
| `T` | 登録する子のクラス |
| `Name` | 保存する型の名前（文字列）。クラス名を変えても古いデータを読めるようにする |

- 親のポインタ（`unique_ptr<Enemy>` など）で保存する子のクラスを、すべて登録します。
- 登録していない子のクラスを保存しようとすると、実行時に `cereal::Exception`（`Trying to save an unregistered polymorphic type`）になります。

### CEREAL_REGISTER_POLYMORPHIC_RELATION {#register_relation}

```cpp
CEREAL_REGISTER_POLYMORPHIC_RELATION(Base, Derived)
```

| 引数 | 意味 |
| --- | --- |
| `Base` | 親のクラス |
| `Derived` | 子のクラス |

- 親子関係を cereal に教えます。子の `serialize` で `cereal::base_class<Base>(this)` を使っていれば、自動で分かるので省略できることもありますが、書いておくと確実です。

### PortableBinaryOutputArchive {#portable_binary}

```cpp
class PortableBinaryOutputArchive {
 public:
  explicit PortableBinaryOutputArchive(std::ostream& stream,
                                       Options const& options = Options::Default());
};
// 読み込みは PortableBinaryInputArchive
```

| 引数 | 意味 |
| --- | --- |
| `stream` | 書き込み先 |
| `options` | 保存するエンディアン（`Options::LittleEndian()` / `BigEndian()` / `Default()`） |

- 先頭にエンディアンの情報を書き、読み込むときに必要なら並び替えます。PC と、エンディアンが違う機械の間でデータをやり取りするときに使います。
- 今の PC・スマホ・ゲーム機はほぼすべてリトルエンディアンなので、普通は `BinaryArchive` で十分です。

### save_minimal {#save_minimal}

```cpp
template <class Archive>
ValueType save_minimal(const Archive& ar) const;
```

| 引数 | 意味 |
| --- | --- |
| `ar` | アーカイブ（`const`。読み書きには使わない） |

- **戻り値:** 保存する値。数値か `std::string`
- 型を**1 つの数値か文字列**として保存します。JSON では `"id": {"value0": 7}` ではなく `"id": 7` のように、オブジェクトにならずに値そのものになります。
- ID 型、色（`"#ff0000"`）、enum の名前などに便利です。`load_minimal` と組で書きます。

```cpp
struct ItemId {
  std::uint32_t value = 0;

  template <class Archive>
  std::uint32_t save_minimal(const Archive&) const {
    return value;
  }

  template <class Archive>
  void load_minimal(const Archive&, const std::uint32_t& v) {
    value = v;
  }
};
```

### load_minimal {#load_minimal}

```cpp
template <class Archive>
void load_minimal(const Archive& ar, const ValueType& value);
```

| 引数 | 意味 |
| --- | --- |
| `ar` | アーカイブ（`const`） |
| `value` | 読み込まれた値。型は `save_minimal` の戻り値と同じにする |

- `save_minimal` で保存した値から、オブジェクトを作り直します。
- `value` の型が `save_minimal` の戻り値の型と違うと、コンパイルエラーになります。

### load_and_construct {#load_and_construct}

```cpp
template <class Archive>
static void load_and_construct(Archive& ar, cereal::construct<T>& construct);
```

| 引数 | 意味 |
| --- | --- |
| `ar` | 入力アーカイブ |
| `construct` | 読んだ値でオブジェクトを作る道具。`construct(引数...)` でコンストラクタを呼ぶ |

- **デフォルトコンストラクタが無い型**を、`unique_ptr` / `shared_ptr` 経由で読み込むときに使います。
- 普通は、デフォルトコンストラクタを用意する方が簡単です。

### binary_data {#binary_data}

```cpp
template <class T>
BinaryData<T> binary_data(T&& data, std::size_t size);
```

| 引数 | 意味 |
| --- | --- |
| `data` | 配列の先頭のポインタ |
| `size` | **バイト数**（要素の数ではない） |

- 配列を 1 要素ずつではなく、**まとめてバイトのまま**保存します。地形の高さマップなど、大きな数値の配列で速くなります。
- バイナリアーカイブ専用です（JSON では Base64 の文字列になります）。要素数は保存されないので、別に保存しておきます。

```cpp
template <class Archive>
void save(Archive& ar) const {
  ar(static_cast<std::uint64_t>(heights_.size()));
  ar(cereal::binary_data(heights_.data(), heights_.size() * sizeof(float)));
}
```

### make_size_tag {#make_size_tag}

```cpp
template <class T>
SizeTag<T> make_size_tag(T&& sz);
```

| 引数 | 意味 |
| --- | --- |
| `sz` | 要素の数（保存のときは値、読み込みのときは受け取る変数） |

- 自作のコンテナを保存するときに、要素数を保存します。JSON アーカイブでは配列として正しく出力されるようになります。

### XMLOutputArchive {#xml_output}

```cpp
class XMLOutputArchive {
 public:
  explicit XMLOutputArchive(std::ostream& stream,
                            Options const& options = Options::Default());
};
// 読み込みは XMLInputArchive
```

| 引数 | 意味 |
| --- | --- |
| `stream` | 書き込み先 |
| `options` | 小数の桁数、字下げ、型の情報を出すかなど |

- XML で保存します。ゲームで使うことはほとんどありません。

## フラグ・オプション {#flags}

### JSONOutputArchive::Options

```cpp
JSONOutputArchive::Options(int precision = std::numeric_limits<double>::max_digits10,
                           IndentChar indentChar = IndentChar::space,
                           unsigned int indentLength = 4);
```

| 設定 | 意味 |
| --- | --- |
| `Options::Default()` | 小数は正確に戻せる桁数、スペース 4 つで字下げ |
| `Options::NoIndent()` | 改行・字下げなしの 1 行 |
| `precision` | 小数の桁数 |
| `IndentChar::space` / `tab` / `newline` / `carriage_return` | 字下げに使う文字 |
| `indentLength` | 字下げの文字数 |

### PortableBinaryOutputArchive::Options

| 設定 | 意味 |
| --- | --- |
| `Options::Default()` | 今の CPU のエンディアンで保存 |
| `Options::LittleEndian()` | リトルエンディアンで保存 |
| `Options::BigEndian()` | ビッグエンディアンで保存 |

### 設定マクロ

| マクロ | 意味 |
| --- | --- |
| `CEREAL_THREAD_SAFE=1` | 複数のスレッドで同時にアーカイブを使うときに、内部の登録情報をロックで守る |
| `CEREAL_SERIALIZE_FUNCTION_NAME` など | `serialize` / `save` / `load` の関数名を変える（Google Style の名前に合わせたいときなど） |
| `CEREAL_RAPIDJSON_NAMESPACE` | 中で使う RapidJSON の名前空間を変える（自分でも RapidJSON を使っていてぶつかるとき） |

## ゲームでの使いどころ

| 場面 | 使い方 |
| --- | --- |
| セーブデータ | バイナリアーカイブ + `CEREAL_CLASS_VERSION` + マジックナンバー + チェックサム |
| エディタで作ったシーン | 開発中は JSON アーカイブ、製品版はバイナリ |
| 継承を使ったオブジェクトの保存 | `unique_ptr<Base>` の vector をそのまま保存 |
| ゲームの状態のスナップショット | デバッグで「この瞬間の状態」を保存して再現する |

## よくあるミス

??? failure "型のヘッダを include し忘れる"
    `std::vector` のメンバを保存するのに `cereal/types/vector.hpp` を include していないと、とても長いコンパイルエラーになります。エラーの中に `could not find any output serialization functions` と出ていたら、まずヘッダを疑います。

??? failure "アーカイブを破棄する前にデータを使う"
    JSON アーカイブは破棄されるまで最後の `}` を書きません。バイナリでも、ファイルを閉じる前にアーカイブを破棄するのが安全です。アーカイブは必ず `{ }` のスコープの中で作ります。

??? failure "ファイルを binary モードで開かない"
    Windows でファイルを `std::ios::binary` なしで開くと、`\n`（0x0A）のバイトが `\r\n` に変換されて、データが壊れます。

??? failure "後からバージョンを付ける"
    `CEREAL_CLASS_VERSION` の無い状態でリリースした型に、後からバージョンを付けると、古いデータが読めなくなります。最初から付けておきます。

??? failure "普通のポインタを保存しようとする"
    `Enemy* target;` はコンパイルエラーになります。所有しているなら `unique_ptr`、参照しているだけなら ID で保存します。

??? failure "子クラスで base_class を忘れる"
    子の `serialize` で `cereal::base_class<Enemy>(this)` を書かないと、親のメンバが保存されません。エラーにはならないので気づきにくいです。

## 理解度チェック

!!! question "Q1. このコードの何がだめ？"
    ```cpp
    std::stringstream stream;
    cereal::JSONOutputArchive archive(stream);
    archive(CEREAL_NVP(player));
    SaveToFile(stream.str());
    ```

    <div class="spoiler" markdown>

    **答え:** アーカイブが破棄される前に `stream.str()` を使っているので、JSON の最後の `}` が書かれていません。アーカイブを `{ }` で囲み、スコープを抜けてから `stream.str()` を使います。

    </div>

!!! question "Q2. `CEREAL_CLASS_VERSION(SaveData, 3);` の型で、`serialize` の `version` に 1 が入ってくるのはどんなとき？"
    <div class="spoiler" markdown>

    **答え:** バージョン 1 のときに保存されたデータを読み込むときです。保存するときは常に今のバージョン（3）が渡されます。

    </div>

!!! question "Q3. cereal のバイナリアーカイブで `std::string name = "Bob";` を保存すると何バイトになる？"
    <div class="spoiler" markdown>

    **答え:** 11 バイトです。長さが `std::uint64_t` で 8 バイト、中身の `Bob` が 3 バイトです。

    </div>

## 類似ライブラリ

| ライブラリ | 違い |
| --- | --- |
| Boost.Serialization | cereal の元になった考え方。機能は多いが Boost が必要で重い |
| [zpp_bits](zpp-bits.md) | とても速く、構造体なら関数も書かなくてよい。バージョン管理は自分で |
| [struct_pack](struct-pack.md) | とても速く、型のチェックと互換フィールドがある |
| [cista](cista.md) | 読み込みでコピーしない。専用の型（`cista::offset::vector` など）を使う |
| bitsery | ゲーム向けのバイナリシリアライザ。ビット単位で詰めて小さくできる。通信向け |
| FlatBuffers / Protocol Buffers | スキーマファイルを書いてコードを生成する。他の言語ともやり取りできる |

## これだけ覚える

!!! abstract "まとめ"
    - [x] `template <class Archive> void serialize(Archive& ar) { ar(a, b, c); }` で保存も読み込みも
    - [x] 使う型のヘッダ（`cereal/types/vector.hpp` など）を include
    - [x] アーカイブは `{ }` で囲んで破棄してから使う
    - [x] `CEREAL_CLASS_VERSION` を最初から付ける
    - [x] 普通のポインタは保存できない。継承は登録マクロで
    - [x] バイナリは壊れたデータを見分けられない。マジックナンバーとチェックサムを付ける

## 関連ページ

- [シリアライズの概要](index.md)
- [zpp_bits（バイナリ・速さ重視）](zpp-bits.md)
- [ファイル入出力](../../basics/file-io.md)
- [継承と仮想関数](../../basics/virtual.md)
- [cereal 公式ドキュメント](https://uscilab.github.io/cereal/)
- [cereal（GitHub）](https://github.com/USCiLab/cereal)
