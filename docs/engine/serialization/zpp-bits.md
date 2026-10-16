---
title: zpp_bits（バイナリ・速さ重視）
tags:
  - ゲームエンジン
  - シリアライズ
---

# zpp_bits（バイナリ・速さ重視）

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="perf perf-4">◎ 速い</span>
<span class="ver ver-20">C++20〜</span>
`#include <zpp_bits.h>`
</div>

**zpp_bits** は、**とても速いバイナリシリアライザ**です。ヘッダ 1 ファイルだけで使え、**構造体（集成体）なら何も書かなくても**そのまま保存・読み込みできます。C++20 の機能（コンセプト、構造化束縛の仕組み、`constexpr` の強化）をフルに使って、保存・読み込みの処理を**コンパイル時にほぼ全部組み立てる**ので、実行時の無駄がほとんどありません。ベンチマークでは、[cereal](cereal.md) より何倍も速く、手で `memcpy` を書いたのと近い速さになることもあります。その代わり、データに**型の情報やバージョン番号は入らない**（自分で入れる）ので、「何を書いたか」を自分で管理する必要があります。通信・リプレイ・製品版のマスターデータなど、「形が決まっていて、とにかく速く・小さく」したいときに向いています。

!!! tip "結論"
    - **構造体なら何も書かずに保存できる。** `auto [data, in, out] = zpp::bits::data_in_out();` → `out(obj)` → `in(obj)`。
    - 結果は**エラーコード**で返る。`.or_throw()` を付けると失敗時に例外になる。
    - 文字列・vector の要素数は**デフォルトで 4 バイト**。オプションで 1・2・8 バイトや可変長にもできる。
    - **バージョン管理の仕組みは無い。** 先頭にバージョン番号を自分で書く。
    - private メンバがあるクラスは `using serialize = zpp::bits::members<N>;` か `serialize` 関数で対応させる。
    - 信用できないデータを読むときは **`alloc_limit`** で確保するメモリの上限を決める。

!!! info "このページを読む前に"
    [シリアライズの概要](index.md) と [cereal](cereal.md) を先に読むと、バイナリシリアライザの考え方（書いた順番に読む）が分かります。[テンプレート](../../basics/template.md) の concepts と、[std::expected](../../stl/utilities/expected.md) のような「エラーを戻り値で返す」書き方も関係します。

## 導入

ヘッダ 1 ファイル（`zpp_bits.h`）だけです。C++20 が必要です（GCC 11 以降、Clang 12 以降、Visual Studio 2022 以降）。

=== "ヘッダを直接置く"

    [GitHub](https://github.com/eyalz800/zpp_bits) から `zpp_bits.h` をダウンロードして、プロジェクトのインクルードディレクトリに置きます。一番簡単です。

=== "CMake FetchContent"

    ```cmake
    include(FetchContent)
    FetchContent_Declare(
      zpp_bits
      GIT_REPOSITORY https://github.com/eyalz800/zpp_bits.git
      GIT_TAG main  # 本番ではコミットやタグを固定する
      GIT_SHALLOW TRUE)
    FetchContent_MakeAvailable(zpp_bits)
    target_include_directories(my_game PRIVATE ${zpp_bits_SOURCE_DIR})
    target_compile_features(my_game PRIVATE cxx_std_20)
    ```

=== "vcpkg"

    ```text
    vcpkg install zpp-bits
    ```

    ポートの名前やターゲット名は vcpkg のバージョンで変わることがあるので、`vcpkg search zpp` で確認します。ヘッダ 1 つなので、直接置く方法でも十分です。

## 仕組み：構造体を自動で分解する

zpp_bits は、構造体を**構造化束縛**（`auto [a, b, c] = obj;`）と同じ仕組みでメンバに分解して、前から順番に書きます。そのため、構造体に何も書かなくても動きます。

```text
struct Player { std::string name; int level; std::vector<int> items; };

      ┌── name ───────────┐┌ level ┐┌── items ────────────────────────┐
data: [05 00 00 00][A l i c e][0C 00 00 00][03 00 00 00][101][205][330]
       長さ(4バイト)  中身      int(4バイト)  要素数(4バイト)  int × 3
```

| 型 | 書き方 |
| --- | --- |
| `int`、`float`、`bool` などの数値 | メモリ上のバイトそのまま（リトルエンディアン） |
| `std::string`、`std::vector` など | 要素数（デフォルト 4 バイト）+ 中身 |
| 数値だけの配列（`std::vector<int>` など） | 中身を**まとめて 1 回の memcpy** でコピー（速い） |
| 構造体 | メンバを前から順番に |
| `std::optional` | 値があるか（1 バイト）+ 値 |
| `std::variant` | どの型か（番号）+ 値 |
| `std::unique_ptr` | `std::optional` と同じ |

数値や「数値だけの構造体」が並んだ vector は、1 つずつではなく**まとめて memcpy**されるので、大きな配列ほど速さの差が出ます。

## 関数一覧

| 関数・型 | 重要度 | 何をする |
| --- | --- | --- |
| [`data_in_out`](#data_in_out) | <span class="rank rank-must">必須</span> | バッファと in / out をまとめて作る |
| [`out`](#out) | <span class="rank rank-must">必須</span> | 書き込み用のアーカイブ |
| [`in`](#in) | <span class="rank rank-must">必須</span> | 読み込み用のアーカイブ |
| [`アーカイブの operator()`](#archive_call) | <span class="rank rank-must">必須</span> | 値を書く・読む |
| [`or_throw`](#or_throw) | <span class="rank rank-must">必須</span> | 失敗したら例外を投げる |
| [`failure`](#failure) | <span class="rank rank-often">よく使う</span> | 結果が失敗か調べる |
| [`members`](#members) | <span class="rank rank-often">よく使う</span> | メンバの数を教えて自動で対応させる |
| [`serialize` 関数](#serialize_function) | <span class="rank rank-often">よく使う</span> | 保存するメンバと順番を自分で決める |
| [`access`](#access) | <span class="rank rank-sometimes">たまに</span> | private メンバを保存できるようにする |
| [`position`](#position) | <span class="rank rank-sometimes">たまに</span> | 今何バイト目にいるか |
| [`alloc_limit`](#alloc_limit) | <span class="rank rank-sometimes">たまに</span> | 読み込みで確保するメモリの上限 |
| [`size1b`](#size1b) | <span class="rank rank-sometimes">たまに</span> | 要素数を 1 バイトで書く |
| [`size2b`](#size2b) | <span class="rank rank-sometimes">たまに</span> | 要素数を 2 バイトで書く |
| [`size8b`](#size8b) | <span class="rank rank-rare">知ってるだけ</span> | 要素数を 8 バイトで書く |
| [`size_varint`](#size_varint) | <span class="rank rank-sometimes">たまに</span> | 要素数を可変長で書く |
| [`varint`](#varint) | <span class="rank rank-sometimes">たまに</span> | 小さい数を少ないバイトで書く整数型 |
| [`endian::big`](#endian_big) | <span class="rank rank-rare">知ってるだけ</span> | ビッグエンディアンで書く |
| [`in_out`](#in_out) | <span class="rank rank-sometimes">たまに</span> | 自分で用意したバッファに in / out を作る |
| [`to_bytes`](#to_bytes) | <span class="rank rank-rare">知ってるだけ</span> | コンパイル時にバイト列にする |
| [`from_bytes`](#from_bytes) | <span class="rank rank-rare">知ってるだけ</span> | コンパイル時にバイト列から作る |

## よくある使い方

```cpp
#include <print>
#include <string>
#include <vector>

#include <zpp_bits.h>

struct Player {
  std::string name;
  int level = 1;
  std::vector<int> items;
};  // 何も書かなくてよい

int main() {
  // data: std::vector<std::byte>、in / out: data を使うアーカイブ
  auto [data, in, out] = zpp::bits::data_in_out();

  out(Player{"Alice", 12, {101, 205, 330}}).or_throw();  // 書く
  std::println("{} バイト", data.size());

  Player loaded;
  in(loaded).or_throw();  // 読む
  std::println("{} Lv.{} {}", loaded.name, loaded.level, loaded.items);
}
```

```text title="実行結果"
29 バイト
Alice Lv.12 [101, 205, 330]
```

29 バイトの内訳は、`name`（長さ 4 + 中身 5）、`level`（4）、`items`（要素数 4 + 中身 12）です。[cereal](cereal.md) は要素数を 8 バイトで書くので 37 バイトでしたが、zpp_bits は 4 バイトなので少し小さくなります。

### ファイルに保存する

zpp_bits はメモリ上のバッファに書くライブラリなので、ファイルには**バッファをまとめて書き込み**ます。

```cpp
#include <cstddef>
#include <fstream>
#include <vector>

#include <zpp_bits.h>

bool SaveGame(const SaveData& save, const char* path) {
  std::vector<std::byte> data;
  zpp::bits::out out(data);
  if (zpp::bits::failure(out(save))) {
    return false;
  }
  std::ofstream file(path, std::ios::binary);
  file.write(reinterpret_cast<const char*>(data.data()),
             static_cast<std::streamsize>(data.size()));
  return static_cast<bool>(file);
}

bool LoadGame(SaveData& save, const char* path) {
  std::ifstream file(path, std::ios::binary | std::ios::ate);  // 最後から開いて大きさを知る
  if (!file) {
    return false;
  }
  std::vector<std::byte> data(static_cast<std::size_t>(file.tellg()));
  file.seekg(0);
  file.read(reinterpret_cast<char*>(data.data()),
            static_cast<std::streamsize>(data.size()));
  zpp::bits::in in(data);
  return !zpp::bits::failure(in(save));
}
```

## バージョン管理

zpp_bits のデータには、**型の名前もバージョン番号も入りません**。書いた順番どおりのバイトが並ぶだけです。後から構造体の形を変えると、古いデータは正しく読めません。そのため、**バージョン番号を自分で先頭に書く**のが基本です。

```cpp
#include <cstdint>
#include <print>
#include <string>

#include <zpp_bits.h>

// 古い形は消さずに残しておく
struct SaveV1 {
  std::string name;
  int level = 1;
};

struct SaveV2 {
  std::string name;
  int level = 1;
  int gold = 0;  // バージョン 2 で追加
};

using SaveData = SaveV2;  // 今の形
constexpr std::uint32_t kSaveVersion = 2;

SaveData Upgrade(const SaveV1& v1) { return {v1.name, v1.level, 0}; }

int main() {
  // 古いバージョン（1）で保存されたデータを作る
  auto [data, in, out] = zpp::bits::data_in_out();
  out(std::uint32_t{1}, SaveV1{"Alice", 12}).or_throw();

  // 読み込み：まずバージョンを読んで、形を選ぶ
  std::uint32_t version = 0;
  in(version).or_throw();
  SaveData save;
  if (version == 1) {
    SaveV1 old;
    in(old).or_throw();
    save = Upgrade(old);  // 新しい形に変換
  } else if (version == kSaveVersion) {
    in(save).or_throw();
  }
  std::println("v{} -> {} Lv.{} {}G", version, save.name, save.level, save.gold);
}
```

```text title="実行結果"
v1 -> Alice Lv.12 0G
```

- **古い形の構造体は消さずに残しておき**、読んだ後で新しい形に変換します。
- 「最後に追加したメンバだけ」なら、読み込みでデータが足りなくなったところで止める、という方法もありますが、分かりにくいのでおすすめしません。
- 形が頻繁に変わるデータ（開発中のセーブなど）は、JSON（[nlohmann/json](nlohmann-json.md)）にしておき、形が固まったら zpp_bits にする、という使い分けもよくあります。

## エラー処理

zpp_bits は、**結果を戻り値で返します**（例外を投げません）。`out(...)` / `in(...)` は `zpp::bits::errc` という結果を返します。

| 書き方 | 失敗したとき |
| --- | --- |
| `out(x).or_throw();` | 例外を投げる |
| `if (zpp::bits::failure(in(x))) { ... }` | `if` の中に入る |
| `auto result = in(x);` と書いて後で調べる | 中のエラーコード（`std::errc`）で原因が分かる |

| よくある失敗 | 原因 |
| --- | --- |
| データが足りない | 途中で切れたファイル、読む型の間違い。`std::errc::result_out_of_range` |
| バッファが足りない | 固定の大きさのバッファ（`std::array`）に書いて、入りきらなかった |
| 確保の上限を超えた | `alloc_limit` で決めた上限より大きい要素数を読んだ |
| `variant` の番号が範囲外 | 壊れたデータ |

!!! danger "壊れたデータ・信用できないデータ"
    zpp_bits は、データの「要素数」を読んで、その数だけメモリを確保します。壊れたデータや悪意のあるデータで要素数が 40 億になっていると、巨大なメモリを確保しようとします。ネットワークから来るデータなど、**信用できないデータを読むときは、必ず [alloc_limit](#alloc_limit) を付けます**。セーブデータにも、マジックナンバーとチェックサムを付けておくと安全です。

## 自作のクラスを対応させる

構造体（集成体：すべて public で、コンストラクタを自分で書いていないもの）は、メンバが 50 個までなら**何も書かなくても**自動で対応します。それ以外のクラスは、次のどれかで対応させます。

| 方法 | 使う場面 |
| --- | --- |
| 何も書かない | 集成体（`struct` で全部 public） |
| `using serialize = zpp::bits::members<N>;` | コンストラクタがあるクラス。全メンバをそのまま保存してよい |
| `friend zpp::bits::access;` + 上のどちらか | private メンバがある |
| `serialize` 関数を書く | 保存するメンバや順番を選びたい |

```cpp
class Enemy {
 public:
  Enemy() = default;
  Enemy(std::string name, int hp) : name_(std::move(name)), hp_(hp) {}

  // メンバが 3 つあることを教える
  using serialize = zpp::bits::members<3>;

 private:
  friend zpp::bits::access;  // private メンバを読み書きできるようにする

  std::string name_;
  int hp_ = 10;
  float speed_ = 1.0f;
};
```

## 速さとサイズの特徴

| 項目 | 特徴 |
| --- | --- |
| 速さ | 非常に速い。保存・読み込みの処理がコンパイル時に組み立てられ、数値の配列は memcpy になる |
| サイズ | 型情報やキー名が無いので小さい。`size_varint` や `varint` でさらに小さくできる |
| コンパイル時間 | テンプレートを多く使うので、少し長くなる |
| バッファ | メモリ上の `std::vector<std::byte>` などに書く。ストリームは使わない |

## 関数の詳しい説明

### data_in_out {#data_in_out}

```cpp
template <typename ByteType = std::byte, typename... Options>
constexpr auto data_in_out(Options&&... options);
```

| 引数 | 意味 |
| --- | --- |
| `ByteType` | バッファの要素の型（`std::byte`、`char`、`unsigned char`） |
| `options` | `in` / `out` に渡すオプション（[フラグ](#flags)） |

- **戻り値:** `std::vector<ByteType>` のバッファと、それを使う `in`、`out` の 3 つ組。構造化束縛で受け取る
- `in` と `out` は**バッファを参照している**ので、バッファより長く使ってはいけません。
- 書いてすぐ読む（テスト、ネットワーク）ときに便利です。保存と読み込みが別の場所なら、[out](#out) と [in](#in) を別々に作ります。

### out {#out}

```cpp
template <typename ByteView, typename... Options>
class out {
 public:
  constexpr explicit out(ByteView&& view, Options&&... options);
};
```

| 引数 | 意味 |
| --- | --- |
| `view` | 書き込み先のバッファ。`std::vector<std::byte>` なら**自動で大きくなる**。`std::array` や `std::span` なら大きさは固定 |
| `options` | 要素数の大きさ・エンディアンなどのオプション |

- バッファの**今の位置から**書き足していきます。同じ `out` で何回も呼ぶと、後ろにつながっていきます。
- 固定の大きさのバッファ（`std::array<std::byte, 256>` など）に書くと、メモリ確保が一切起きません。通信のパケットに便利です。

### in {#in}

```cpp
template <typename ByteView, typename... Options>
class in {
 public:
  constexpr explicit in(ByteView&& view, Options&&... options);
};
```

| 引数 | 意味 |
| --- | --- |
| `view` | 読み込み元のバッファ |
| `options` | 書いたときと**同じ**オプションを渡す |

- 前から順番に読みます。**書いたときと同じ型・同じ順番・同じオプション**で読まないと、正しく読めません。

### アーカイブの operator() {#archive_call}

```cpp
template <typename... Args>
constexpr auto operator()(Args&&... args);
```

| 引数 | 意味 |
| --- | --- |
| `args` | 書く・読む値。何個でも並べられる |

- **戻り値:** `zpp::bits::errc`（成功か失敗か）
- `out(a, b, c)` は `a`、`b`、`c` を順番に書きます。`in(a, b, c)` は同じ順番で読みます。
- 戻り値は `[[nodiscard]]` なので、無視すると警告が出ます。必ず `or_throw()` か `failure()` で確認します。

### or_throw {#or_throw}

```cpp
constexpr void or_throw() const;  // errc のメンバ
```

- 結果が失敗なら、例外（`std::system_error`）を投げます。成功なら何もしません。
- 例外を使ってよいプロジェクトなら、全部の `in` / `out` にこれを付けるのが一番簡単です。

### failure {#failure}

```cpp
constexpr bool failure(errc code);
constexpr bool success(errc code);  // 反対
```

| 引数 | 意味 |
| --- | --- |
| `code` | `in` / `out` の結果 |

- **戻り値:** 失敗なら `true`
- 例外を使わないプロジェクトでは、これで確認します。

```cpp
if (auto result = in(save); zpp::bits::failure(result)) {
  std::println("セーブデータが壊れています");
  return false;
}
```

### members {#members}

```cpp
template <std::size_t Count>
struct members;

// クラスの中で使う
using serialize = zpp::bits::members<3>;
```

| 引数 | 意味 |
| --- | --- |
| `Count` | クラスのメンバ変数の数 |

- 集成体でないクラス（コンストラクタがある、など）でも、メンバを宣言順に自動で保存できるようになります。
- メンバの数が合っていないとコンパイルエラーになります。メンバを足したら数も変えます。
- クラスを変更できないときは、クラスの外に `auto serialize(const Enemy&) -> zpp::bits::members<3>;` と**宣言だけ**書く方法もあります。

### serialize 関数 {#serialize_function}

```cpp
constexpr static auto serialize(auto& archive, auto& self) {
  return archive(self.member1, self.member2);
}
```

| 引数 | 意味 |
| --- | --- |
| `archive` | `in` か `out` |
| `self` | 保存・読み込みするオブジェクト（保存のときは `const`） |

- **戻り値:** `archive(...)` の結果をそのまま返す
- 保存するメンバや順番を自分で決めたいときに書きます。キャッシュなどのメンバを保存から外せます。
- `static` 関数で、`self` を受け取る形なのが他のライブラリと違うところです（1 つの関数で `const` と非 `const` の両方に対応するため）。

```cpp
struct Tilemap {
  std::vector<std::uint16_t> tiles;
  std::vector<bool> collision_cache;  // 保存しない

  constexpr static auto serialize(auto& archive, auto& self) {
    return archive(self.tiles);
  }
};
```

### access {#access}

```cpp
friend zpp::bits::access;
```

- クラスの中に書くと、zpp_bits が private メンバや private な `serialize` 関数を使えるようになります。

### position {#position}

```cpp
constexpr std::size_t& position();
constexpr std::size_t position() const;
```

- **戻り値:** 今何バイト目まで書いた・読んだか
- 読み込みが終わった後に `in.position() == data.size()` を確かめると、「データの後ろに余計なものがある（形が違うかもしれない）」ことに気づけます。

### alloc_limit {#alloc_limit}

```cpp
template <std::size_t Limit>
struct alloc_limit;

zpp::bits::in in(data, zpp::bits::alloc_limit<1024 * 1024>{});
```

| 引数 | 意味 |
| --- | --- |
| `Limit` | 1 つのコンテナで確保してよい最大のバイト数 |

- 壊れたデータで巨大な要素数を読んでも、上限を超えたらエラーにして止めます。
- ネットワークから受け取るデータには必ず付けます。

### size1b {#size1b}

```cpp
zpp::bits::out out(data, zpp::bits::size1b{});
zpp::bits::in in(data, zpp::bits::size1b{});
```

- 文字列・コンテナの要素数を **1 バイト**（最大 255）で書きます。
- 短い名前やタグしか無いデータで、サイズを小さくできます。255 を超えると失敗します。
- 書くときと読むときで、同じオプションを渡します。

### size2b {#size2b}

```cpp
zpp::bits::out out(data, zpp::bits::size2b{});
```

- 要素数を **2 バイト**（最大 65535）で書きます。通信のパケットなどでよく使います。

### size8b {#size8b}

```cpp
zpp::bits::out out(data, zpp::bits::size8b{});
```

- 要素数を **8 バイト**で書きます。40 億を超える要素数があり得るときだけ使います。

### size_varint {#size_varint}

```cpp
zpp::bits::out out(data, zpp::bits::size_varint{});
```

- 要素数を**可変長**（小さい数は 1 バイト、大きくなると増える）で書きます。
- ほとんどのコンテナは要素数が小さいので、サイズが小さくなります。少しだけ遅くなります。

### varint {#varint}

```cpp
template <std::integral Type, varint_encoding Encoding = varint_encoding::normal>
struct varint;

using vint32_t = varint<std::int32_t>;
using vuint32_t = varint<std::uint32_t>;
using vint64_t = varint<std::int64_t>;
using vsint32_t = varint<std::int32_t, varint_encoding::zig_zag>;  // 負の数も小さく
```

| 引数 | 意味 |
| --- | --- |
| `Type` | 中身の整数型 |
| `Encoding` | `normal`（普通）か `zig_zag`（負の数も小さくなる） |

- 値が小さいほど少ないバイトで書く整数型です（0〜127 なら 1 バイト）。
- メンバの型を `zpp::bits::vuint32_t` にすると、そのメンバだけ可変長で保存されます。ID や個数など、小さい数が多いデータで便利です。

### endian::big {#endian_big}

```cpp
zpp::bits::out out(data, zpp::bits::endian::big{});
```

- 数値をビッグエンディアン（大きい桁が先）で書きます。`endian::network{}` も同じ意味です。
- ネットワークのプロトコルで決められているときや、他のプログラムと形式を合わせるときに使います。普通はデフォルト（リトルエンディアン）のままで大丈夫です。

### in_out {#in_out}

```cpp
template <typename ByteView, typename... Options>
constexpr auto in_out(ByteView&& view, Options&&... options);
```

| 引数 | 意味 |
| --- | --- |
| `view` | 自分で用意したバッファ |
| `options` | オプション |

- **戻り値:** そのバッファを使う `in` と `out` の組
- `data_in_out` と違って、バッファを自分で用意します（`std::array` など）。

```cpp
std::array<std::byte, 128> packet{};
auto [in, out] = zpp::bits::in_out(packet);
```

### to_bytes {#to_bytes}

```cpp
template <auto Object, typename... Options>
constexpr auto to_bytes();
```

| 引数 | 意味 |
| --- | --- |
| `Object` | バイト列にする値（コンパイル時の定数） |

- **戻り値:** `std::array<std::byte, N>`。コンパイル時に計算される
- テストで「この構造体はこのバイト列になる」と確かめるときなどに使います。学生のゲームではほぼ使いません。

### from_bytes {#from_bytes}

```cpp
template <auto Data, typename Type, typename... Options>
constexpr auto from_bytes();
```

| 引数 | 意味 |
| --- | --- |
| `Data` | バイト列（コンパイル時の定数） |
| `Type` | 作る型 |

- **戻り値:** `Type` の値。コンパイル時に計算される

## フラグ・オプション {#flags}

`in` / `out` / `data_in_out` の後ろの引数に渡します。**書くときと読むときで同じものを渡す**必要があります。

| オプション | 意味 |
| --- | --- |
| `zpp::bits::size1b{}` | 要素数を 1 バイトで |
| `zpp::bits::size2b{}` | 要素数を 2 バイトで |
| `zpp::bits::size4b{}` | 要素数を 4 バイトで（デフォルト） |
| `zpp::bits::size8b{}` | 要素数を 8 バイトで |
| `zpp::bits::size_native{}` | 要素数を `std::size_t` の大きさで |
| `zpp::bits::size_varint{}` | 要素数を可変長で |
| `zpp::bits::no_size{}` | 要素数を書かない（読む側が数を知っているとき） |
| `zpp::bits::endian::big{}` | ビッグエンディアン |
| `zpp::bits::endian::little{}` | リトルエンディアン |
| `zpp::bits::endian::network{}` | ネットワークの順番（ビッグエンディアン） |
| `zpp::bits::endian::swapped{}` | 今の CPU と逆の順番 |
| `zpp::bits::alloc_limit<N>{}` | 読み込みで確保する上限（バイト） |
| `zpp::bits::append{}` | `out` で、バッファの最後から書き足す |

## ゲームでの使いどころ

| 場面 | 使い方 |
| --- | --- |
| オンラインの通信 | 固定バッファ + `size2b` + `alloc_limit`。パケットの種類は `std::variant` で |
| リプレイ | 毎フレームの入力の構造体を vector に溜めて、まとめて保存 |
| 製品版のマスターデータ | 開発中の JSON / YAML を、ビルド時に zpp_bits のバイナリに変換 |
| セーブデータ | 先頭にマジックナンバーとバージョン番号を書く |
| ゲームの状態のスナップショット | ロールバック（巻き戻し）のために毎フレーム状態を保存 |

!!! note "RPC と Protocol Buffers 互換"
    zpp_bits には、関数呼び出しをシリアライズする **RPC** の仕組みと、Google の **Protocol Buffers** 互換の形式（`zpp::bits::pb`）で読み書きする機能も入っています。サーバーと通信するときに便利ですが、まずは普通の使い方に慣れてからにします。

## よくあるミス

??? failure "結果を確認しない"
    `in(save);` だけ書くと、失敗しても気づきません（`[[nodiscard]]` の警告が出ます）。`.or_throw()` か `failure()` で必ず確認します。

??? failure "構造体の形を変えて古いデータを読む"
    メンバを追加・削除・並べ替えると、古いデータは読めません。エラーにならずにでたらめな値になることもあります。先頭にバージョン番号を書き、古い形の構造体を残しておきます。

??? failure "書くときと読むときでオプションが違う"
    `out(data, zpp::bits::size2b{})` で書いたものを、オプションなしの `in(data)` で読むと、要素数を 4 バイトとして読んでしまい、ずれます。

??? failure "int のつもりで long を使う"
    `long` は Windows では 4 バイト、Linux では 8 バイトです。他の環境とデータをやり取りするなら、`std::int32_t` など大きさの決まった型を使います。

??? failure "ポインタを保存しようとする"
    普通のポインタはコンパイルエラーです。所有しているなら `std::unique_ptr`、参照しているだけなら ID で保存します。

??? failure "in / out をバッファより長く使う"
    `data_in_out` の `in` と `out` は `data` を参照しています。`data` をムーブしたり消したりした後に使うと未定義動作です。

## 理解度チェック

!!! question "Q1. `struct Pos { float x; float y; };` を zpp_bits で保存すると何バイト？ `std::vector<Pos>` に 3 個入れたら？"
    <div class="spoiler" markdown>

    **答え:** `Pos` は 8 バイト（float 4 バイト × 2）です。`std::vector<Pos>` に 3 個なら、要素数 4 バイト + 8 × 3 = **28 バイト**です。`Pos` は数値だけの構造体なので、3 個がまとめて memcpy されます。

    </div>

!!! question "Q2. このコードの何がだめ？"
    ```cpp
    struct Save { std::string name; int level; };
    // リリース後に変更
    struct Save { std::string name; int gold; int level; };
    ```

    <div class="spoiler" markdown>

    **答え:** メンバの間に `gold` を入れたので、古いデータの `level` の 4 バイトが `gold` として読まれ、`level` を読むところでデータが足りなくなります（エラーになるか、でたらめな値になります）。zpp_bits にはバージョン管理が無いので、先頭にバージョン番号を書き、古い形の構造体を残して変換します。

    </div>

!!! question "Q3. ネットワークから受け取ったデータを zpp_bits で読むとき、何を付けるべき？"
    <div class="spoiler" markdown>

    **答え:** `zpp::bits::alloc_limit<N>{}` です。壊れたデータや悪意のあるデータで巨大な要素数を読んでも、確保するメモリに上限を付けられます。

    </div>

## 類似ライブラリ

| ライブラリ | 違い |
| --- | --- |
| [struct_pack](struct-pack.md) | 同じくらい速い。型のハッシュでデータの形をチェックでき、互換フィールドでメンバを足せる |
| [cereal](cereal.md) | バージョン管理と継承に対応。速さは劣る |
| [cista](cista.md) | 読み込みでコピーしない。専用の型を使う |
| bitsery | ゲーム・通信向け。ビット単位で詰められる。C++11 から使える |
| alpaca | zpp_bits に似た、構造体を自動で保存するライブラリ。バージョンのチェック機能がある |

## これだけ覚える

!!! abstract "まとめ"
    - [x] `auto [data, in, out] = zpp::bits::data_in_out();` → `out(x).or_throw()` → `in(x).or_throw()`
    - [x] 構造体なら何も書かなくてよい。クラスは `members<N>` か `serialize` 関数
    - [x] 結果は必ず確認する（`or_throw` / `failure`）
    - [x] バージョン番号は自分で先頭に書く。古い形の構造体は残す
    - [x] 書くときと読むときで同じオプション
    - [x] 信用できないデータには `alloc_limit`

## 関連ページ

- [シリアライズの概要](index.md)
- [yalantinglibs（struct_pack）](struct-pack.md)
- [cereal（バイナリ・定番）](cereal.md)
- [cista（バイナリ・ゼロコピー）](cista.md)
- [zpp_bits（GitHub）](https://github.com/eyalz800/zpp_bits)
