---
title: simdjson（JSON・速さ重視）
tags:
  - 外部ライブラリ
  - シリアライズ
---

# simdjson（JSON・速さ重視）

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="perf perf-4">◎ 速い</span>
<span class="ver ver-17">C++17〜</span>
`#include <simdjson.h>`
</div>

**simdjson** は、JSON を世界最速クラスの速さで読むためのライブラリです。CPU の SIMD 命令（1 回の命令で 16〜64 バイトをまとめて処理する命令）を使って、1 秒間に数 GB の JSON を読めます。[nlohmann/json](nlohmann-json.md) と比べて十倍以上速いことも珍しくありません。その代わり、読み込み専用（JSON を作って書き出すのは基本的に別のライブラリ）で、「前から順番に読む」「読んだ文字列はパーサーが次の JSON を読むまでしか使えない」などの独特なルールがあります。巨大なステージデータ・マスターデータ・リプレイのログなど、「大量の JSON を、とにかく速く読みたい」ときの選択肢です。

!!! tip "ポイント"
    - <strong>読み込みだけ速くしたいときに使う。</strong> 書き出しは [nlohmann/json](nlohmann-json.md) などで行う。
    - 基本は **On-Demand API**（`simdjson::ondemand::parser`）。必要なところだけ、読むときに解析する。
    - 入力は `simdjson::padded_string` に入れる（後ろに余白が必要）。ファイルは `padded_string::load` で読む。
    - 取り出した `std::string_view` は、同じパーサーで次を読むまでしか使えない。 残したいなら `std::string` にコピーする。
    - 値は JSON に書かれた順番に読む のが一番速く、安全。1 つの値は 1 回しか読めない。
    - エラー処理は「例外」と「エラーコード（`.get(x)`）」の 2 通りから選べる。

!!! info "このページを読む前に"
    まず [nlohmann/json](nlohmann-json.md) で JSON の扱いに慣れてから読むのがおすすめです。[string_view](../../stl/utilities/string_view.md) の「元の文字列が消えると使えない」という性質を知っていると、このライブラリの注意点がよく分かります。

## 導入

### Visual Studio で導入する（最初に読む）

Visual Studio を使っているなら、ここから読みます。ライブラリを入れる基本の手順は [Visual Studio：外部ライブラリの入れ方](../../vs/libraries.md) にまとめています。ここでは simdjson だけの部分を書きます。

=== "ファイルを置く"

    1. [リリースページ](https://github.com/simdjson/simdjson/releases) の **`simdjson.h` と `simdjson.cpp`**（`singleheader` フォルダー）を `third_party/simdjson/` に置き、2 つともプロジェクトに追加（追加 → 既存の項目）する
    2. プロジェクトのプロパティを開き（[画面つきの手順](../../vs/include-dirs.md#additional)）、構成を すべての構成、プラットフォームを x64 にする
    3. C/C++ → 全般 → 追加のインクルード ディレクトリ に、`$(SolutionDir)third_party\simdjson` を追加する
    4. `#include <simdjson.h>` と書いてビルドする

=== "vcpkg"

    1. 初回だけ、Developer PowerShell で `vcpkg integrate install` を実行する（[準備](../../vs/libraries.md#vcpkg)）
    2. ライブラリを入れる

        ```powershell
        vcpkg install simdjson:x64-windows
        ```

        （マニフェスト モードなら、`vcpkg.json` の `dependencies` に `"simdjson"` を足す）
    3. プロジェクトには何も設定せずに、`#include <simdjson.h>` と書けば使える

!!! note "C++ の設定"
    C++17 以上が必要です。速さを測るときは必ず Release で測ります（Debug では何倍も遅くなります）。

### そのほかの方法（CMake など）

`simdjson.h` と `simdjson.cpp` の 2 ファイルだけで動きます（ヘッダオンリーではなく、`.cpp` もビルドする必要があります）。

=== "vcpkg"

    ```text
    vcpkg install simdjson
    ```

    ```cmake
    find_package(simdjson CONFIG REQUIRED)
    target_link_libraries(my_game PRIVATE simdjson::simdjson)
    ```

=== "CMake FetchContent"

    ```cmake
    include(FetchContent)
    FetchContent_Declare(
      simdjson
      GIT_REPOSITORY https://github.com/simdjson/simdjson.git
      GIT_TAG v3.13.0  # 最新版はリリースページで確認する
      GIT_SHALLOW TRUE)
    FetchContent_MakeAvailable(simdjson)
    target_link_libraries(my_game PRIVATE simdjson::simdjson)
    ```

=== "2 ファイルを直接置く"

    リポジトリの `singleheader/` フォルダにある `simdjson.h` と `simdjson.cpp` をプロジェクトにコピーし、`simdjson.cpp` をビルド対象に加えます。

!!! note "最適化を有効にしてビルドする"
    simdjson はデバッグビルド（`-O0`、Visual Studio の Debug）だと何倍も遅くなります。速さを測るときは必ずリリースビルドで測ります。また、どの SIMD 命令（AVX2、AVX-512、ARM の NEON など）を使うかは実行時に CPU を見て自動で選ぶので、特別なコンパイラオプションは要りません。

## 2 つの API

simdjson には 2 種類の読み方があります。

| API | 仕組み | 向いている場面 |
| --- | --- | --- |
| **On-Demand**（`simdjson::ondemand`） | 全体の構造だけ先に調べ、値は読むときに解析する | ほとんどの場合。こちらが基本で、速い |
| DOM（`simdjson::dom`） | 最初に全部解析して、木の形にしておく | 同じ値を何度も、好きな順番で読みたいとき |

このページでは主に On-Demand を説明し、DOM は [dom::parser](#dom_parser) で紹介します。

## 関数一覧

| 関数 | 重要度 | 何をする |
| --- | --- | --- |
| [`ondemand::parser`](#parser) | <span class="rank rank-must">必須</span> | パーサー。使い回すと速い |
| [`iterate`](#iterate) | <span class="rank rank-must">必須</span> | JSON を読み始める（ドキュメントを作る） |
| [`padded_string::load`](#padded_string_load) | <span class="rank rank-must">必須</span> | ファイルを余白付きで読み込む |
| [`padded_string`](#padded_string) | <span class="rank rank-must">必須</span> | 余白付きの文字列 |
| [`operator[]`](#operator_brackets) | <span class="rank rank-must">必須</span> | キーで値を取る（順番を気にしない） |
| [`get_int64`](#get_int64) | <span class="rank rank-must">必須</span> | 整数として取る |
| [`get_double`](#get_double) | <span class="rank rank-must">必須</span> | 小数として取る |
| [`get_string`](#get_string) | <span class="rank rank-must">必須</span> | 文字列として取る（`string_view`） |
| [`get_bool`](#get_bool) | <span class="rank rank-often">よく使う</span> | true / false として取る |
| [`get_array`](#get_array) | <span class="rank rank-often">よく使う</span> | 配列として取る |
| [`get_object`](#get_object) | <span class="rank rank-often">よく使う</span> | オブジェクトとして取る |
| [`get`](#get) | <span class="rank rank-often">よく使う</span> | 型を指定して取る・エラーコードを受け取る |
| [`error_message`](#error_message) | <span class="rank rank-often">よく使う</span> | エラーコードを説明の文字列にする |
| [`find_field`](#find_field) | <span class="rank rank-sometimes">たまに</span> | キーで値を取る（順番どおりに探す・速い） |
| [`get_uint64`](#get_uint64) | <span class="rank rank-sometimes">たまに</span> | 符号なし整数として取る |
| [`is_null`](#is_null) | <span class="rank rank-sometimes">たまに</span> | null か調べる |
| [`type`](#type) | <span class="rank rank-sometimes">たまに</span> | 値の種類を調べる |
| [`count_elements`](#count_elements) | <span class="rank rank-sometimes">たまに</span> | 配列の要素数を数える |
| [`count_fields`](#count_fields) | <span class="rank rank-rare">知ってるだけ</span> | オブジェクトのキーの数を数える |
| [`at_pointer`](#at_pointer) | <span class="rank rank-sometimes">たまに</span> | `"/a/0/b"` のパスで深い場所を取る |
| [`raw_json`](#raw_json) | <span class="rank rank-rare">知ってるだけ</span> | 値の元の JSON テキストを取る |
| [`rewind`](#rewind) | <span class="rank rank-rare">知ってるだけ</span> | ドキュメントを最初から読み直す |
| [`get_active_implementation`](#get_active_implementation) | <span class="rank rank-rare">知ってるだけ</span> | 使われている SIMD の種類を調べる |
| [`dom::parser`](#dom_parser) | <span class="rank rank-rare">知ってるだけ</span> | 全部先に解析する DOM API |

## よくある使い方

```cpp
#include <cstdint>
#include <print>
#include <string_view>

#include <simdjson.h>

int main() {
  // 本当はファイルから padded_string::load で読む
  simdjson::padded_string json(std::string_view(
      R"({"name": "Alice", "level": 12, "items": [101, 205, 330]})"));

  simdjson::ondemand::parser parser;  // 使い回すと速い
  simdjson::ondemand::document doc = parser.iterate(json);

  // JSON に書かれた順番に読むのが基本
  std::string_view name = doc["name"];
  std::int64_t level = doc["level"];
  std::println("{} Lv.{}", name, level);

  for (std::int64_t id : doc["items"]) {
    std::println("アイテム {}", id);
  }
}
```

```text title="実行結果"
Alice Lv.12
アイテム 101
アイテム 205
アイテム 330
```

`std::string_view name = doc["name"];` のように、**受け取る変数の型を書くと自動で変換**されます（失敗すると例外）。この書き方が一番短く、よく使います。

### 配列のオブジェクトを構造体に読む

ステージデータのような「オブジェクトの配列」を、ゲームの構造体に読み込む例です。

```cpp
#include <cstdint>
#include <print>
#include <string>
#include <string_view>
#include <vector>

#include <simdjson.h>

struct Enemy {
  std::string id;
  double x = 0.0;
  double y = 0.0;
  std::int64_t hp = 0;
};

std::vector<Enemy> LoadEnemies(simdjson::ondemand::parser& parser,
                               const simdjson::padded_string& json) {
  std::vector<Enemy> enemies;
  simdjson::ondemand::document doc = parser.iterate(json);
  for (simdjson::ondemand::object obj : doc["enemies"]) {
    Enemy enemy;
    // string_view はすぐ std::string にコピーする（パーサーの中を指しているため）
    enemy.id = std::string(std::string_view(obj["id"]));
    enemy.x = double(obj["x"]);
    enemy.y = double(obj["y"]);
    enemy.hp = std::int64_t(obj["hp"]);
    enemies.push_back(std::move(enemy));
  }
  return enemies;
}

int main() {
  simdjson::padded_string json(std::string_view(R"({"enemies": [
    {"id": "slime", "x": 1.5, "y": 0, "hp": 10},
    {"id": "bat", "x": -3, "y": 2.25, "hp": 6}
  ]})"));

  simdjson::ondemand::parser parser;
  for (const Enemy& e : LoadEnemies(parser, json)) {
    std::println("{} ({}, {}) HP{}", e.id, e.x, e.y, e.hp);
  }
}
```

```text title="実行結果"
slime (1.5, 0) HP10
bat (-3, 2.25) HP6
```

`"y": 0` のように整数で書かれた値も、`double` として読めば `0.0` になります（逆に、小数を整数として読むとエラーです）。

## On-Demand のルール（ここが一番大事）

simdjson が速い理由は、**必要なところだけを、前から 1 回だけ読む**からです。そのため、nlohmann/json のように自由には使えません。次のルールを守ります。

### ルール 1：string_view は次の iterate まで {#rule1}

`get_string()` で取った `std::string_view` は、パーサーの中のバッファを指しています。同じパーサーで次の JSON を `iterate` すると、中身が上書きされて使えなくなります（[ダングリング](../../basics/ub.md)）。

```cpp
std::string_view name = parser.iterate(json1)["name"];
auto doc2 = parser.iterate(json2);  // ここで name の指す中身が上書きされる
std::println("{}", name);           // 未定義動作
```

構造体に保存するときは、その場で `std::string` にコピーします。

### ルール 2：値は 1 回しか読めない

On-Demand の値は「読んだら消費される」ものです。同じ値を 2 回 `get_xxx` すると、エラー（または未定義の結果）になります。何度も使う値は、一度普通の変数に入れます。

```cpp
simdjson::ondemand::value v = doc["hp"];
std::int64_t a = v.get_int64();
std::int64_t b = v.get_int64();  // だめ：もう読んだ値
```

### ルール 3：前から順番に読む

ドキュメントは前から後ろへ進みながら読みます。

- 同じオブジェクトの中のキーは、`operator[]` なら順番が違っても探せます（必要なら最初に戻って探す）。ただし書かれた順番に読むのが一番速いです。
- 一度中に入って出てきた配列・オブジェクトに、後から戻ることはできません。戻りたいときは `doc.rewind()` で最初からやり直します。
- 子のオブジェクトを読んでいる途中で、親の別のキーを読むと `OUT_OF_ORDER_ITERATION` などのエラーになります。

### ルール 4：パーサーは 1 度に 1 つのドキュメント

1 つの `parser` で同時に 2 つの JSON を読むことはできません。2 つ同時に読みたいときは、パーサーを 2 つ作ります。逆に、順番に読むなら同じパーサーを使い回すと、内部のメモリを再確保しないので速くなります。

### ルール 5：パーサーはスレッドで共有しない

`parser` はスレッドセーフではありません。複数のスレッドで読み込むときは、スレッドごとにパーサーを持ちます（`thread_local` にするのが簡単です）。

## 余白（padding）とは

SIMD 命令は 32 バイトや 64 バイトをまとめて読むので、JSON の最後のあたりを読むときに、**文字列の終わりより少し先のメモリまで**読んでしまいます。そこが確保されていないとクラッシュするので、simdjson は入力の後ろに `SIMDJSON_PADDING`（64 バイト）の余白があることを要求します。

| 範囲 | 内容 |
| --- | --- |
| JSON の本体 | `{ "name": ... }` |
| 余白 64 バイト | 中身は何でもよい。ここまで読んでも安全なようにする |

`padded_string` は、この余白を自動で確保してくれる文字列です。`std::string` を `iterate` に渡すこともできますが、容量（`capacity`）が足りないと中でコピーや再確保が起きるので、最初から `padded_string` を使うのがおすすめです。

## エラー処理

simdjson は 2 つのエラー処理の方法を選べます。

| 方法 | 書き方 | 向いている場面 |
| --- | --- | --- |
| 例外 | `std::int64_t hp = doc["hp"];` | 短く書きたい。壊れたデータは読み込み全体を失敗にする |
| エラーコード | `auto error = doc["hp"].get(hp);` | 例外を使わないプロジェクト。1 つずつ失敗を確認したい |

例外の型は `simdjson::simdjson_error`（`std::exception` の子）で、`error()` でエラーコードが取れます。

```cpp
#include <cstdint>
#include <print>
#include <string_view>

#include <simdjson.h>

int main() {
  simdjson::padded_string json(std::string_view(R"({"hp": "100", "mp": 30})"));
  simdjson::ondemand::parser parser;
  simdjson::ondemand::document doc = parser.iterate(json);

  // エラーコードで受け取る：例外は投げられない
  std::int64_t hp = 0;
  if (auto error = doc["hp"].get_int64().get(hp); error) {
    std::println("hp: {}", simdjson::error_message(error));
  }

  std::int64_t mp = 0;
  if (auto error = doc["mp"].get(mp); !error) {
    std::println("mp: {}", mp);
  }

  std::int64_t sp = 0;
  if (auto error = doc["sp"].get(sp); error == simdjson::NO_SUCH_FIELD) {
    std::println("sp: キーがありません");
  }
}
```

```text title="実行結果"
hp: The JSON element does not have the requested type.
mp: 30
sp: キーがありません
```

よく出るエラーコードは次のとおりです。

| エラーコード | 意味 |
| --- | --- |
| `SUCCESS` | 成功（値は 0 なので `if (error)` で失敗が分かる） |
| `INCORRECT_TYPE` | 型が違う（文字列を整数として読んだ、など） |
| `NO_SUCH_FIELD` | キーが無い |
| `INDEX_OUT_OF_BOUNDS` | 配列の範囲外（`at_pointer` など） |
| `NUMBER_OUT_OF_RANGE` | 数値が型に入らない |
| `NUMBER_ERROR` | 数値の書き方がおかしい |
| `TAPE_ERROR` | JSON の構造（括弧の対応など）が壊れている |
| `UNCLOSED_STRING` | 文字列の `"` が閉じていない |
| `UTF8_ERROR` | UTF-8 として不正な文字がある |
| `EMPTY` | 入力が空 |
| `CAPACITY` | 入力がパーサーの最大サイズより大きい |
| `OUT_OF_ORDER_ITERATION` | 読む順番のルールを破った |
| `IO_ERROR` | ファイルが読めない（`padded_string::load`） |

!!! warning "読まなかった部分は細かくチェックされない"
    On-Demand は、括弧の対応などの**大きな構造**は最初に全部チェックしますが、読まなかった値の中身（数値の書き方など）はチェックしません。「読み込めたから JSON 全体が正しい」とは限らないことに注意します。全部を検証したいときは [DOM API](#dom_parser) を使います。

## 自作の型に読む

simdjson は**読み込み専用**なので、nlohmann/json の `from_json` のような「型ごとの読み込み関数」を自分で書くのが基本です。エラーコードを返す関数にしておくと、例外を使わないプロジェクトでも同じ形で使えます。

```cpp
simdjson::error_code ReadEnemy(simdjson::ondemand::object obj, Enemy& out) {
  std::string_view id;
  if (auto error = obj["id"].get(id)) {
    return error;
  }
  out.id = std::string(id);
  if (auto error = obj["hp"].get(out.hp)) {
    return error;
  }
  return simdjson::SUCCESS;
}
```

新しいバージョンの simdjson には、`tag_invoke` という仕組みで自作の型を `get<Enemy>()` で読めるようにする機能や、C++26 の静的リフレクションで構造体を自動で読み書きする機能も追加されています。ただし、まだ新しい機能なので、学生のうちは上のように普通の関数を書くのが分かりやすくおすすめです。

## 書き出しについて

simdjson は**読むためのライブラリ**です。JSON を書き出したいときは、次のようにします。

- 書き出しは [nlohmann/json](nlohmann-json.md) で行い、大きいファイルの読み込みだけ simdjson にする（一番多いパターン）
- 単純な形なら `std::format` で自分で書く（文字列のエスケープに注意）
- 最近のバージョンには文字列を組み立てる builder の機能もあるが、使い方が変わりやすい

## 速さの特徴

| 項目 | 特徴 |
| --- | --- |
| 読み込みの速さ | 1 秒間に数 GB。nlohmann/json の十倍以上になることが多い |
| メモリ | 値ごとのヒープ確保が無い。パーサーが内部バッファを持ち、使い回す |
| 一番速い使い方 | パーサーを使い回す。JSON に書かれた順番に読む。必要な値だけ読む |
| 遅くなる使い方 | 毎回パーサーを作る。キーを逆順に探す。デバッグビルド |

!!! note "ゲームのロードは JSON だけで遅いわけではない"
    ロードが遅いとき、原因は JSON の解析ではなく「ファイルを読む」「テクスチャを作る」「メモリを確保する」ことのほうが多いです。simdjson に変える前に、まず[プロファイラ](../../basics/cache.md)などで、本当に JSON の解析が遅いのかを確認します。

## 関数の詳しい説明

### ondemand::parser {#parser}

```cpp
class simdjson::ondemand::parser {
 public:
  explicit parser(size_t max_capacity = SIMDJSON_MAXSIZE_BYTES) noexcept;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `max_capacity` | `size_t` | 読める JSON の最大サイズ（バイト）。デフォルトは約 4 GB |

- JSON を読むための道具です。内部にバッファを持っていて、**使い回すほど速く**なります。
- 1 つの `parser` で同時に読める JSON は 1 つです。スレッドで共有してはいけません。
- コピーはできませんが、ムーブはできます。メンバ変数や `thread_local` で持つのが定番です。

### iterate {#iterate}

```cpp
simdjson_result<document> iterate(padded_string_view json) & noexcept;
simdjson_result<document> iterate(const padded_string& json) & noexcept;
simdjson_result<document> iterate(std::string& json) & noexcept;
simdjson_result<document> iterate(const char* json, size_t len,
                                  size_t capacity) & noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `json` | `padded_string_view` | 読む JSON。後ろに余白が必要 |
| `len` | `size_t` | JSON の長さ |
| `capacity` | `size_t` | 確保されているメモリの大きさ（`len + SIMDJSON_PADDING` 以上必要） |

- 戻り値: `simdjson_result<document>`。`document` を受け取る変数に入れると、失敗時は例外になる
- 計算量: 最初に全体の構造を調べるので O(n)。ただしとても速い
- 注意: `parser` が左辺値でないと呼べません（`&` 修飾）。`ondemand::parser().iterate(...)` のように一時オブジェクトで呼ぶことはできません。また、入力の文字列は document を使い終わるまで消してはいけません。

### padded_string::load {#padded_string_load}

```cpp
static simdjson_result<padded_string> load(std::string_view path) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `path` | `std::string_view` | 読むファイルのパス |

- 戻り値: ファイルの中身を余白付きで持つ `padded_string`。読めないと `IO_ERROR`

```cpp
simdjson::padded_string json;
if (auto error = simdjson::padded_string::load("data/stage1.json").get(json)) {
  std::println("読めません: {}", simdjson::error_message(error));
  return;
}
```

例外を使うなら `simdjson::padded_string json = simdjson::padded_string::load("stage1.json");` と 1 行で書けます。

### padded_string {#padded_string}

```cpp
class simdjson::padded_string {
 public:
  explicit padded_string(size_t length) noexcept;
  padded_string(const char* data, size_t length) noexcept;
  padded_string(std::string_view sv) noexcept;
  padded_string(const std::string& str) noexcept;
  size_t size() const noexcept;
  const char* data() const noexcept;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `length` | `size_t` | 確保する長さ（中身は自分で書く） |
| `data`, `length` | `const char*`, `size_t` | コピー元の文字とその長さ |
| `sv` / `str` | `std::string_view` | コピー元の文字列 |

- 中身をコピーして、後ろに余白を付けた文字列を作ります。
- テストでは `R"({"a": 1})"_padded` のように、文字列リテラルの後ろに `_padded` を付けて作ることもできます。
- ネットワークから受け取ったデータなど、すでにメモリにある JSON を読むときに使います。

### operator[] {#operator_brackets}

```cpp
simdjson_result<value> operator[](std::string_view key) & noexcept;
// find_field_unordered(key) と同じ
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `key` | `std::string_view` | 探すキー |

- 戻り値: キーの値。無ければ `NO_SUCH_FIELD` のエラー
- 計算量: 書かれた順番に読めば O(1)、逆順だと最初に戻って探すので O(キーの数)
- 順番を気にせず探せるので、普段はこれを使います。キーの順番が決まっているなら [find_field](#find_field) の方が少し速くなります。
- 配列の番号で取る `operator[](size_t)` はありません。配列は範囲 for で回すか、[at_pointer](#at_pointer) を使います。

### get_int64 {#get_int64}

```cpp
simdjson_result<int64_t> get_int64() noexcept;
```

- 戻り値: 64 ビットの符号付き整数
- エラー: 小数（`1.5`）、文字列、範囲外の数は `INCORRECT_TYPE` または `NUMBER_OUT_OF_RANGE`
- `int` に入れたいときは、受け取ってから範囲を確認して `static_cast<int>` します。
- 受け取る変数を `std::int64_t` にして `std::int64_t hp = obj["hp"];` と書くと、自動でこの関数が呼ばれます。

### get_double {#get_double}

```cpp
simdjson_result<double> get_double() noexcept;
```

- 戻り値: `double`。`3` のような整数で書かれた数も読める
- `float` が欲しいときは `static_cast<float>(obj["x"].get_double())` のように変換します（`get_float` はありません）。

### get_string {#get_string}

```cpp
simdjson_result<std::string_view> get_string(bool allow_replacement = false) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `allow_replacement` | `bool` | `true` にすると、不正なサロゲートペア（`\uD800` など）を `U+FFFD` に置き換えて読む |

- 戻り値: エスケープ（`\n`、`あ` など）を戻した文字列の `string_view`
- 注意: 指している先はパーサーのバッファです。同じパーサーで次を読むと使えなくなります（[ルール 1](#rule1)）。
- `std::string` に直接入れる `get_string(std::string& out)` もあります（コピーされるので安全）。

### get_bool {#get_bool}

```cpp
simdjson_result<bool> get_bool() noexcept;
```

- 戻り値: `true` か `false`。`0` / `1` や `"true"`（文字列）は `INCORRECT_TYPE`

### get_array {#get_array}

```cpp
simdjson_result<array> get_array() & noexcept;
```

- 戻り値: 配列。範囲 for で要素を回す
- 範囲 for に `doc["items"]` を直接書くと、自動でこれが呼ばれます。
- 配列は前から 1 回だけ回せます。2 回回したいときは、1 回目で `std::vector` にコピーしておきます。

### get_object {#get_object}

```cpp
simdjson_result<object> get_object() & noexcept;
```

- 戻り値: オブジェクト。`operator[]` でキーを探すか、範囲 for で全部のキーを回す

```cpp
// キーと値を全部回す（キーの名前が決まっていないとき）
for (auto field : doc["prices"].get_object()) {
  std::string_view key = field.unescaped_key();  // キーの名前
  std::int64_t price = field.value();
  std::println("{}: {}", key, price);
}
```

`field.key()` はエスケープ前の生の文字列なので、普通は `unescaped_key()` を使います。

### get {#get}

```cpp
template <typename T>
simdjson_result<T> get() noexcept;

template <typename T>
error_code get(T& out) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型引数 | 取りたい型（`int64_t`、`uint64_t`、`double`、`bool`、`std::string_view`、`ondemand::object`、`ondemand::array` など） |
| `out` | `T&` | 値を入れる変数。型から `T` が決まる |

- 戻り値: `get<T>()` は値（またはエラー）、`get(out)` はエラーコード
- エラーコード方式の基本の書き方は `if (auto error = obj["hp"].get(hp)) { ... }` です。
- `simdjson_result` に対しても `.get(out)` が使えるので、`doc["hp"].get_int64().get(hp)` のように「取る → エラーを受け取る」をつなげて書けます。

### error_message {#error_message}

```cpp
const char* simdjson::error_message(error_code error) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `error` | `error_code` | エラーコード |

- 戻り値: 英語の説明の文字列。ログに出すときに使う
- `std::println("{}", error)` のように直接出すことはできないので、これで文字列にします。

### find_field {#find_field}

```cpp
simdjson_result<value> find_field(std::string_view key) & noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `key` | `std::string_view` | 探すキー |

- 戻り値: キーの値。今の位置から後ろだけを探す
- `operator[]` と違って、最初に戻って探しません。キーが JSON に書かれた順番で読むと決まっているなら、少しだけ速くなります。順番が違うと見つからない（`NO_SUCH_FIELD`）ので、自分で JSON を出力していて形が決まっているときに使います。

### get_uint64 {#get_uint64}

```cpp
simdjson_result<uint64_t> get_uint64() noexcept;
```

- 戻り値: 64 ビットの符号なし整数。負の数は `INCORRECT_TYPE`
- ID やハッシュ値など、`int64_t` の最大値を超える数があり得るときに使います。

### is_null {#is_null}

```cpp
simdjson_result<bool> is_null() noexcept;
```

- 戻り値: 値が `null` なら `true`。`null` でなければ値は消費されないので、続けて別の型で読める

### type {#type}

```cpp
simdjson_result<json_type> type() noexcept;
```

- 戻り値: `json_type::array`、`object`、`number`、`string`、`boolean`、`null` のどれか
- 値を消費しないので、種類を見てから読み方を変えられます。数値をさらに細かく調べるときは `get_number_type()` を使います。

```cpp
switch (value.type()) {
  case simdjson::ondemand::json_type::number:
    damage = value.get_double();
    break;
  case simdjson::ondemand::json_type::string:
    damage_formula = std::string(value.get_string().value());
    break;
  default:
    break;
}
```

### count_elements {#count_elements}

```cpp
simdjson_result<size_t> count_elements() & noexcept;  // array
```

- 戻り値: 配列の要素の数
- 計算量: O(n)。数えるために配列を一度最後まで見る
- 回す前に `std::vector::reserve` したいときに使います。数えた後、配列はまた最初から回せます。

### count_fields {#count_fields}

```cpp
simdjson_result<size_t> count_fields() & noexcept;  // object
```

- 戻り値: オブジェクトのキーの数。計算量は O(n)

### at_pointer {#at_pointer}

```cpp
simdjson_result<value> at_pointer(std::string_view json_pointer) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `json_pointer` | `std::string_view` | `"/stages/0/name"` のような `/` 区切りのパス。配列は番号 |

- 戻り値: その場所の値。無ければ `NO_SUCH_FIELD` か `INDEX_OUT_OF_BOUNDS`
- ドキュメントに使うと、毎回最初から探し直します。深い場所の値を 1 つだけ欲しいときに便利です。

```cpp
std::string_view boss = doc.at_pointer("/stages/2/boss/name");
```

### raw_json {#raw_json}

```cpp
simdjson_result<std::string_view> raw_json() noexcept;
```

- 戻り値: 値の元の JSON テキスト（`{"a": 1}` などそのまま）
- ある部分だけを simdjson で読まずに、別のライブラリ（nlohmann/json）に渡したいときに使います。

### rewind {#rewind}

```cpp
void rewind() noexcept;  // document のメンバ
```

- ドキュメントを最初から読み直せる状態に戻します。
- 「まずヘッダの `version` だけ読んで、バージョンに合わせた読み方で最初から読み直す」ときに使います。
- rewind する前に取った `string_view` は使えなくなることがあるので、必要なものはコピーしておきます。

### get_active_implementation {#get_active_implementation}

```cpp
const implementation* simdjson::get_active_implementation() noexcept;
```

- 戻り値: 今使われている実装。`->name()` で `"haswell"`（AVX2）、`"icelake"`（AVX-512）、`"arm64"`、`"fallback"`（SIMD なし）などが分かる
- 「思ったより遅い」ときに、SIMD が使われているかを確認できます。

```cpp
std::println("{}", simdjson::get_active_implementation()->name());
```

### dom::parser {#dom_parser}

```cpp
class simdjson::dom::parser {
 public:
  simdjson_result<element> parse(const padded_string& s) & noexcept;
  simdjson_result<element> load(std::string_view path) & noexcept;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `s` | `std::string_view` | 読む JSON |
| `path` | `std::string_view` | 読むファイルのパス |

- 戻り値: 全部解析済みの値（`dom::element`）。好きな順番で、何度でも読める
- On-Demand より使いやすい代わりに、全部を解析するので少し遅く、メモリも使います。
- `dom::element` は `element["key"]`、`element.at(0)`、`element.get_int64()` などで読みます。On-Demand と違い、配列を番号で取れるのが便利です。
- 返った値は、その `parser` が次を解析するまで有効です（On-Demand と同じ注意）。

## フラグ・オプション

### 設定マクロ（include の前、またはビルド設定で定義する）

| マクロ | 意味 |
| --- | --- |
| `SIMDJSON_EXCEPTIONS=0` | 例外を使わない。`std::int64_t hp = doc["hp"];` のような自動変換が使えなくなり、`get(x)` で書く |
| `SIMDJSON_DEVELOPMENT_CHECKS=1` | 読む順番のルール違反などを、デバッグ時に assert で見つける。開発中はオンにするのがおすすめ |
| `SIMDJSON_IMPLEMENTATION_xxx=0` | 特定の実装（`ICELAKE` など）を入れない。実行ファイルを小さくしたいとき |

### 定数

| 定数 | 値・意味 |
| --- | --- |
| `SIMDJSON_PADDING` | 入力の後ろに必要な余白のバイト数（64） |
| `SIMDJSON_MAXSIZE_BYTES` | パーサーが読める最大サイズのデフォルト（約 4 GB） |

## ゲームでの使いどころ

| 場面 | 使い方 |
| --- | --- |
| 巨大なステージ・ワールドデータ（数十 MB） | 読み込みを simdjson に。書き出し（エディタ側）は nlohmann/json |
| マスターデータを起動時に大量に読む | パーサー 1 つを使い回して、全ファイルを順番に読む |
| ログ・リプレイの解析ツール | 大量の JSON Lines（1 行 1 JSON）を `iterate_many` で高速に読む |
| サーバーから受け取る大きなレスポンス | 必要なキーだけ On-Demand で読む |

!!! note "iterate_many"
    `parser.iterate_many(json)` を使うと、`{...}{...}{...}` や 1 行に 1 つの JSON が並んだデータ（JSON Lines）を、まとめて速く読めます。ログファイルの解析で便利です。

## よくあるミス

??? failure "string_view を構造体にそのまま保存する"
    `enemy.name = obj["name"].get_string();` の `name` を `std::string_view` にしていると、次の JSON を読んだときに中身が壊れます。保存するメンバは `std::string` にしてコピーします。

??? failure "毎回 parser を作る"
    関数の中で `simdjson::ondemand::parser parser;` を毎回作ると、毎回内部のバッファを確保するので遅くなります。メンバ変数などにして使い回します。

??? failure "同じ値を 2 回読む"
    `obj["hp"]` で取った値に `get_int64()` を 2 回呼ぶのはルール違反です。1 回読んで変数に入れます。

??? failure "padded_string を先に消す"
    `parser.iterate(simdjson::padded_string(text))` のように一時オブジェクトを渡すと、文の終わりで入力が消えて、document が壊れたメモリを指します（そもそもコンパイルエラーになることが多いです）。入力は document を使い終わるまで変数として残しておきます。

??? failure "小数を整数として読む"
    `"hp": 10.0` を `get_int64()` で読むと `INCORRECT_TYPE` です。nlohmann/json と違って、数値の型を勝手に変換してくれません。小数かもしれない値は `get_double()` で読みます。

??? failure "デバッグビルドで速さを比べる"
    simdjson はインライン化と最適化が前提です。デバッグビルドでは遅く、nlohmann/json と差が出ないこともあります。

## 類似ライブラリ

| ライブラリ | 違い |
| --- | --- |
| [nlohmann/json](nlohmann-json.md) | 書きやすさ優先。読み書き両方。遅い |
| RapidJSON | 速く、読み書き両方できる。書き方が冗長 |
| Glaze | 構造体と JSON を自動で変換し、読み書きとも速い（C++23） |
| yyjson（C 言語） | simdjson と並ぶ速さの C ライブラリ。読み書き両方 |

## これだけ覚える

!!! abstract "まとめ"
    - [x] 大量の JSON を速く読むときに使う。書き出しは別のライブラリ
    - [x] `padded_string::load` → `parser.iterate` → `doc["key"]`
    - [x] パーサーは使い回す。スレッドごとに 1 つ
    - [x] `string_view` は次の iterate まで。保存するなら `std::string` にコピー
    - [x] 値は書かれた順番に、1 回だけ読む
    - [x] エラーは例外か `.get(x)` のエラーコード

## 関連ページ

- [シリアライズの概要](../../engine/serialization/index.md)
- [nlohmann/json（JSON・定番）](nlohmann-json.md)
- [string_view](../../stl/utilities/string_view.md)
- [simdjson（GitHub）](https://github.com/simdjson/simdjson)
- [simdjson On-Demand API の説明](https://github.com/simdjson/simdjson/blob/master/doc/basics.md)
