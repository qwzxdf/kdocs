---
title: nlohmann/json（JSON・定番）
tags:
  - ゲームエンジン
  - シリアライズ
---

# nlohmann/json（JSON・定番）

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="perf perf-2">△ やや重い</span>
<span class="ver ver-11">C++11〜</span>
`#include <nlohmann/json.hpp>`
</div>

**nlohmann/json** は、C++ で JSON を扱うライブラリの中で**一番有名で、一番書きやすい**ライブラリです。`json j; j["hp"] = 100;` のように、まるで Python や JavaScript の辞書のように JSON を読み書きできます。ヘッダ 1 つで使えて、`std::vector` や `std::map` などの STL の型をそのまま JSON にでき、自作の構造体もマクロ 1 行で JSON と相互変換できます。速さは JSON ライブラリの中では遅い方ですが、ゲームの設定ファイル・セーブデータ・ステージデータ程度なら全く問題になりません。「C++ で JSON を使うなら、まずこれ」という定番です。

!!! tip "結論"
    - **JSON はまずこれ。** 読み書き両方でき、STL の型と自作の構造体をほぼ自動で変換できる。
    - 自作の構造体は **`NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE_WITH_DEFAULT`** マクロ 1 行で対応させる（キーが無くても落ちない）。
    - 読み込みは **`json::parse`**、書き出しは **`dump(2)`**（2 は字下げの幅）。
    - 値を取るときは、無いかもしれないキーには **`value("key", デフォルト)`**、必ずあるキーには **`at("key")`**。`[]` で読むのは危ない。
    - エラーは**例外**で来る。ファイルを読む処理は `try` / `catch (const json::exception&)` で囲む。
    - 大量の JSON を速く読みたいときだけ [simdjson](simdjson.md) を検討する。

!!! info "このページを読む前に"
    [シリアライズの概要](index.md) を先に読むと、なぜ JSON を使うのかが分かります。例外については [標準の例外](../../stl/support/exceptions.md)、STL の型は [vector](../../stl/containers/vector.md) と [map](../../stl/containers/map.md) を見てください。

## 導入

ヘッダオンリー（`.hpp` を include するだけ）なので、ビルドの設定はとても簡単です。どれか 1 つの方法で入れます。

=== "vcpkg"

    ```text
    vcpkg install nlohmann-json
    ```

    ```cmake
    find_package(nlohmann_json CONFIG REQUIRED)
    target_link_libraries(my_game PRIVATE nlohmann_json::nlohmann_json)
    ```

=== "CMake FetchContent"

    ```cmake
    include(FetchContent)
    FetchContent_Declare(
      json
      URL https://github.com/nlohmann/json/releases/download/v3.12.0/json.tar.xz)
    FetchContent_MakeAvailable(json)
    target_link_libraries(my_game PRIVATE nlohmann_json::nlohmann_json)
    ```

=== "ヘッダを直接置く"

    [リリースページ](https://github.com/nlohmann/json/releases) から `json.hpp` を 1 つダウンロードして、プロジェクトの `include/nlohmann/json.hpp` に置きます。Visual Studio のプロジェクトでも、インクルードディレクトリを追加するだけで使えます。

!!! note "コンパイル時間に注意"
    `json.hpp` はとても大きい（約 2 万 5 千行）ので、たくさんの `.cpp` で include するとビルドが遅くなります。ヘッダ（`.h`）では `#include <nlohmann/json_fwd.hpp>`（前方宣言だけの軽いヘッダ）を使い、`.cpp` でだけ本体を include すると速くなります。

## 関数一覧

| 関数 | 重要度 | 何をする |
| --- | --- | --- |
| [`json::parse`](#parse) | <span class="rank rank-must">必須</span> | 文字列・ファイルから JSON を読む |
| [`dump`](#dump) | <span class="rank rank-must">必須</span> | JSON を文字列にする |
| [`get`](#get) | <span class="rank rank-must">必須</span> | JSON を C++ の型に変換する |
| [`value`](#value) | <span class="rank rank-must">必須</span> | キーが無ければデフォルト値を返す |
| [`at`](#at) | <span class="rank rank-must">必須</span> | キー・番号で取る（無ければ例外） |
| [`operator[]`](#operator_brackets) | <span class="rank rank-must">必須</span> | キー・番号で取る・作る |
| [`contains`](#contains) | <span class="rank rank-often">よく使う</span> | キーがあるか調べる |
| [`get_to`](#get_to) | <span class="rank rank-often">よく使う</span> | 既存の変数に変換して入れる |
| [`is_object`](#is_object) | <span class="rank rank-often">よく使う</span> | オブジェクト（`{...}`）か調べる |
| [`is_array`](#is_array) | <span class="rank rank-often">よく使う</span> | 配列（`[...]`）か調べる |
| [`is_string`](#is_string) | <span class="rank rank-often">よく使う</span> | 文字列か調べる |
| [`is_number`](#is_number) | <span class="rank rank-often">よく使う</span> | 数値か（整数・小数どちらでも）調べる |
| [`is_number_integer`](#is_number_integer) | <span class="rank rank-sometimes">たまに</span> | 整数か（符号あり・なしどちらでも）調べる |
| [`is_number_float`](#is_number_float) | <span class="rank rank-sometimes">たまに</span> | 小数か調べる |
| [`is_boolean`](#is_boolean) | <span class="rank rank-sometimes">たまに</span> | true / false か調べる |
| [`is_null`](#is_null) | <span class="rank rank-sometimes">たまに</span> | null か調べる |
| [`is_discarded`](#is_discarded) | <span class="rank rank-sometimes">たまに</span> | parse に失敗した値か（allow_exceptions=false のとき）調べる |
| [`items`](#items) | <span class="rank rank-often">よく使う</span> | オブジェクトのキーと値を両方回す |
| [`push_back`](#push_back) | <span class="rank rank-often">よく使う</span> | 配列の最後に追加する |
| [`emplace_back`](#emplace_back) | <span class="rank rank-sometimes">たまに</span> | 配列の最後にその場で作って追加する |
| [`size`](#size) | <span class="rank rank-often">よく使う</span> | 要素の数 |
| [`empty`](#empty) | <span class="rank rank-sometimes">たまに</span> | 空かどうか |
| [`erase`](#erase) | <span class="rank rank-sometimes">たまに</span> | キー・要素を消す |
| [`find`](#find) | <span class="rank rank-sometimes">たまに</span> | キーを探してイテレータを返す |
| [`json::array`](#json_array) | <span class="rank rank-sometimes">たまに</span> | 空の配列を作る |
| [`json::object`](#json_object) | <span class="rank rank-sometimes">たまに</span> | 空のオブジェクトを作る |
| [`json::accept`](#accept) | <span class="rank rank-sometimes">たまに</span> | 正しい JSON か調べるだけ |
| [`type_name`](#type_name) | <span class="rank rank-sometimes">たまに</span> | 値の種類の名前（エラー表示用） |
| [`json_pointer`](#json_pointer) | <span class="rank rank-rare">知ってるだけ</span> | `"/a/b/0"` のようなパスで深い場所を取る |
| [`json::to_cbor`](#to_cbor) | <span class="rank rank-rare">知ってるだけ</span> | バイナリ形式（CBOR）に変換する |
| [`json::from_cbor`](#from_cbor) | <span class="rank rank-rare">知ってるだけ</span> | CBOR から読む |
| [`json::to_msgpack`](#to_msgpack) | <span class="rank rank-rare">知ってるだけ</span> | バイナリ形式（MessagePack）に変換する |
| [`merge_patch`](#merge_patch) | <span class="rank rank-rare">知ってるだけ</span> | 別の JSON で上書きする（設定の差分適用） |

## よくある使い方

ほとんどの場面は「構造体にマクロを付けて、`json` と変換して、ファイルに読み書きする」だけです。

```cpp
#include <print>
#include <string>
#include <vector>

#include <nlohmann/json.hpp>

using json = nlohmann::json;

struct Player {
  std::string name;
  int level = 1;
  std::vector<int> items;
};
// この 1 行で Player <-> json の変換が自動で作られる
NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE_WITH_DEFAULT(Player, name, level, items)

int main() {
  Player player{"Alice", 12, {101, 205}};

  json j = player;                  // 構造体 -> json
  std::println("{}", j.dump());     // json -> 文字列（1 行）

  Player loaded = j.get<Player>();  // json -> 構造体
  std::println("{} Lv.{} アイテム {} 個", loaded.name, loaded.level,
               loaded.items.size());
}
```

```text title="実行結果"
{"items":[101,205],"level":12,"name":"Alice"}
Alice Lv.12 アイテム 2 個
```

出力のキーが `items`、`level`、`name` の**アルファベット順**になっていることに注意してください（[オブジェクトのキーの順番](#key_order)）。

ファイルに保存・読み込みするときは、`std::ofstream` / `std::ifstream` とそのまま組み合わせられます。

```cpp
#include <fstream>
#include <print>

#include <nlohmann/json.hpp>

using json = nlohmann::json;

bool SaveSettings(const json& settings, const char* path) {
  std::ofstream file(path);
  if (!file) {
    return false;
  }
  file << settings.dump(2);  // 2 文字ずつ字下げして、人が読みやすくする
  return static_cast<bool>(file);
}

json LoadSettings(const char* path) {
  std::ifstream file(path);
  if (!file) {
    return json::object();  // ファイルが無いときは空の設定
  }
  try {
    return json::parse(file);
  } catch (const json::parse_error& e) {
    std::println("設定ファイルが壊れています: {}", e.what());
    return json::object();
  }
}
```

## JSON と C++ の型の対応

nlohmann/json は、次の型を**何も書かずに**変換できます。

| JSON | C++ の型（読み書きできるもの） |
| --- | --- |
| `null` | `nullptr`、空の `std::optional`（後述） |
| `true` / `false` | `bool` |
| 数値（整数） | `int`、`std::int64_t`、`unsigned` など全ての整数型 |
| 数値（小数） | `float`、`double` |
| 文字列 | `std::string`、`const char*`（書くときだけ）、`std::string_view`（書くときだけ） |
| 配列 | `std::vector`、`std::array`、`std::list`、`std::deque`、`std::set`、`std::pair`、`std::tuple` など |
| オブジェクト | `std::map<std::string, T>`、`std::unordered_map<std::string, T>` |
| 文字列（enum） | `NLOHMANN_JSON_SERIALIZE_ENUM` を書いた enum |

!!! note "std::optional"
    `std::optional` は最近のバージョンでは標準で対応していて、値が無いときは `null` になります。古い版でコンパイルエラーになる場合は、`nlohmann::adl_serializer<std::optional<T>>` を特殊化して変換方法を自分で書きます。

内部では、1 つの `json` オブジェクトが「今どの種類の値を持っているか」を覚えていて（`std::variant` に近い仕組み）、種類は次の 8 つです。

| 種類（`value_t`） | 内部の C++ の型 |
| --- | --- |
| `null` | なし |
| `object` | `std::map<std::string, json>` |
| `array` | `std::vector<json>` |
| `string` | `std::string` |
| `boolean` | `bool` |
| `number_integer` | `std::int64_t` |
| `number_unsigned` | `std::uint64_t` |
| `number_float` | `double` |

### オブジェクトのキーの順番 {#key_order}

`nlohmann::json` のオブジェクトは内部が `std::map` なので、**キーは自動でアルファベット順（辞書順）に並び替えられます**。書いた順番を保ちたいときは、代わりに **`nlohmann::ordered_json`** を使います。

```cpp
#include <print>

#include <nlohmann/json.hpp>

int main() {
  nlohmann::json sorted;
  sorted["name"] = "Alice";
  sorted["hp"] = 100;

  nlohmann::ordered_json ordered;  // 入れた順番を覚えている
  ordered["name"] = "Alice";
  ordered["hp"] = 100;

  std::println("{}", sorted.dump());
  std::println("{}", ordered.dump());
}
```

```text title="実行結果"
{"hp":100,"name":"Alice"}
{"name":"Alice","hp":100}
```

人が手で編集する設定ファイルは、`ordered_json` の方が「書いた順のまま保存される」ので読みやすくなります。ただし `ordered_json` はキーを探すのが線形探索（O(n)）なので、キーがとても多いオブジェクトでは少し遅くなります。

## 自作の型を JSON にする

### マクロで書く（一番よく使う）

構造体のメンバがそのまま JSON のキーになってよいなら、マクロを 1 行書くだけです。マクロは**構造体の外**（同じ名前空間の中）に書きます。

| マクロ | 書く場所 | キーが無いとき | private メンバ |
| --- | --- | --- | --- |
| `NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE_WITH_DEFAULT` | 構造体の外 | デフォルト値のまま | 使えない |
| `NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE` | 構造体の外 | 例外（out_of_range） | 使えない |
| `NLOHMANN_DEFINE_TYPE_INTRUSIVE_WITH_DEFAULT` | クラスの中 | デフォルト値のまま | 使える |
| `NLOHMANN_DEFINE_TYPE_INTRUSIVE` | クラスの中 | 例外（out_of_range） | 使える |
| `NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE_ONLY_SERIALIZE` | 構造体の外 | （書き出しだけ） | 使えない |

ゲームでは**後からメンバを足すことが多い**ので、`_WITH_DEFAULT` 付きを使うのがおすすめです。古いセーブファイルに新しいキーが無くても、そのメンバは構造体のデフォルト値のまま読み込めます（[バージョン管理](#versioning)）。

`_WITH_DEFAULT` を使うには、構造体が**デフォルトコンストラクタを持ち**、メンバにデフォルト値（`int level = 1;` など）を書いておく必要があります。

```cpp
class Enemy {
 public:
  Enemy() = default;
  Enemy(std::string name, int hp) : name_(std::move(name)), hp_(hp) {}

 private:
  std::string name_;
  int hp_ = 10;

  // クラスの中に書くと private メンバも変換できる
  NLOHMANN_DEFINE_TYPE_INTRUSIVE_WITH_DEFAULT(Enemy, name_, hp_)
};
```

この場合、JSON のキーは `"name_"`、`"hp_"` のようにメンバ名そのままになります。キーの名前を変えたいときは、次の「自分で関数を書く」方法を使います。

### 自分で to_json / from_json を書く

キーの名前を変えたい、計算した値を保存したい、古い形式にも対応したい、というときは、**同じ名前空間**に `to_json` と `from_json` という名前の関数を書きます。nlohmann/json がこの名前の関数を自動で探して使います（ADL という仕組み）。

```cpp
#include <print>
#include <string>

#include <nlohmann/json.hpp>

using json = nlohmann::json;

namespace game {

struct Vec2 {
  float x = 0.0f;
  float y = 0.0f;
};

// Vec2 -> json。[x, y] の配列として短く保存する
void to_json(json& j, const Vec2& v) { j = json::array({v.x, v.y}); }

// json -> Vec2
void from_json(const json& j, Vec2& v) {
  j.at(0).get_to(v.x);
  j.at(1).get_to(v.y);
}

struct Spawn {
  std::string enemy_id;
  Vec2 position;
};

void to_json(json& j, const Spawn& s) {
  j = json{{"enemy", s.enemy_id}, {"pos", s.position}};  // キーの名前を変える
}

void from_json(const json& j, Spawn& s) {
  j.at("enemy").get_to(s.enemy_id);
  s.position = j.value("pos", Vec2{});  // 無ければ (0, 0)
}

}  // namespace game

int main() {
  game::Spawn spawn{"slime", {3.5f, -2.0f}};
  json j = spawn;
  std::println("{}", j.dump());

  auto back = j.get<game::Spawn>();
  std::println("{} ({}, {})", back.enemy_id, back.position.x, back.position.y);
}
```

```text title="実行結果"
{"enemy":"slime","pos":[3.5,-2.0]}
slime (3.5, -2)
```

!!! warning "関数名は小文字のスネークケース固定"
    Google C++ Style では関数名は `ToJson` のように書きますが、この 2 つの関数は**ライブラリが名前で探す**ので、必ず `to_json` / `from_json` と書きます。また、変換したい型と**同じ名前空間**に書かないと見つけてもらえません。

### enum を文字列で保存する

enum をそのまま保存すると数値（`0`、`1`…）になります。enum の順番を入れ替えたり途中に追加したりすると、古いデータの意味が変わってしまうので、**文字列で保存する**のがおすすめです。

```cpp
#include <print>

#include <nlohmann/json.hpp>

using json = nlohmann::json;

enum class Element { kNone, kFire, kIce };

// 対応表を書く。最初の行は「知らない文字列が来たとき」の値になる
NLOHMANN_JSON_SERIALIZE_ENUM(Element, {
    {Element::kNone, nullptr},
    {Element::kFire, "fire"},
    {Element::kIce, "ice"},
})

int main() {
  json j = Element::kIce;
  std::println("{}", j.dump());

  auto e = json("thunder").get<Element>();  // 表に無い文字列
  std::println("{}", e == Element::kNone);
}
```

```text title="実行結果"
"ice"
true
```

表に無い文字列を読むと、例外にはならず**表の最初の値**になります。最初の行に「なし」や「不明」を置いておくと安全です。

## エラー処理

nlohmann/json はエラーを**例外**で知らせます。すべて `nlohmann::json::exception`（`std::exception` の子）を継承していて、`id` で種類が分かります。

| 例外の型 | よくある id | 起きる場面 |
| --- | --- | --- |
| `json::parse_error` | 101 | JSON の文法が間違っている（カンマ忘れ、閉じ括弧忘れ） |
| `json::type_error` | 302 | 型が違う（文字列を `get<int>()` した） |
| `json::type_error` | 316 | `dump` で UTF-8 として不正な文字列が入っていた |
| `json::out_of_range` | 403 | `at("key")` でキーが無い |
| `json::out_of_range` | 401 | `at(10)` で配列の範囲外 |
| `json::invalid_iterator` | 2xx | イテレータの使い方が間違っている |
| `json::other_error` | 5xx | JSON Patch の失敗など |

```cpp
#include <print>

#include <nlohmann/json.hpp>

using json = nlohmann::json;

int main() {
  try {
    json j = json::parse(R"({"hp": "100"})");  // hp が文字列になっている
    int hp = j.at("hp").get<int>();
    std::println("{}", hp);
  } catch (const json::exception& e) {
    std::println("id={} {}", e.id, e.what());
  }
}
```

```text title="実行結果"
id=302 [json.exception.type_error.302] type must be number, but is string
```

### 例外を使わずに読む

プロジェクトで例外を使わない方針のときは、`parse` の第 3 引数に `false` を渡します。失敗すると例外の代わりに **discarded**（捨てられた）という特別な値が返るので、`is_discarded()` で調べます。

```cpp
json j = json::parse(text, nullptr, false);
if (j.is_discarded()) {
  // 文法エラー
}
```

ただし、これで防げるのは `parse` の文法エラーだけです。`at` や `get` の型違いは例外のままなので、`contains` と `is_xxx` で先に確認してから読みます。

!!! note "例外を完全に切る"
    コンパイラの設定で例外を無効にしている（`-fno-exceptions`）場合、nlohmann/json は例外を投げる代わりに `abort()` します。その場合は `JSON_NOEXCEPTION` を定義し、読む前に必ず型を確認するコードを書きます。

## バージョン管理と互換性 {#versioning}

ゲームの開発中、セーブデータや設定の形は何度も変わります。JSON は**キーの名前**でデータを探すので、バイナリと比べて互換性を保つのがとても簡単です。

| 変更 | 古いデータを読むと | 対策 |
| --- | --- | --- |
| メンバを追加した | キーが無い | `_WITH_DEFAULT` マクロ、または `value()` でデフォルトにする |
| メンバを削除した | 余計なキーがある | 何もしなくてよい（知らないキーは無視される） |
| メンバの名前を変えた | 新しいキーが無い | `from_json` で古い名前も見る |
| 型を変えた（int → float） | 数値どうしなら変換される | 文字列 ↔ 数値などは `from_json` で分岐 |
| 意味を変えた | 読めるが値がおかしい | `version` キーを見て変換する |

```cpp
void from_json(const json& j, SaveData& s) {
  int version = j.value("version", 1);
  s.player_name = j.at("player_name").get<std::string>();
  if (version >= 2) {
    s.gold = j.at("gold").get<int>();
  } else {
    s.gold = j.value("money", 0);  // v1 では money という名前だった
  }
}
```

最初から `"version": 1` のようなキーを入れておくと、あとで困りません。

## 速さとメモリの特徴

nlohmann/json は**書きやすさを最優先**にしたライブラリなので、速さは JSON ライブラリの中で遅い方です。

- `json` の値 1 つ 1 つが、オブジェクトなら `std::map`、文字列なら `std::string` を**ヒープに確保**します。小さい値がたくさんある JSON では、メモリ確保が多くなります。
- 読み込みの速さは、[simdjson](simdjson.md) と比べると**十倍以上遅い**ことも珍しくありません。
- メモリも、元の JSON テキストより数倍大きくなることがあります。

とはいえ、数 MB までの JSON なら一瞬で読めます。ゲームで問題になるのは、次のような場合だけです。

| 状況 | 対策 |
| --- | --- |
| 数十 MB 以上の JSON を読む | 読み込みだけ [simdjson](simdjson.md) にする |
| 毎フレーム JSON を作る・読む | JSON はロード時だけにして、実行中は普通の構造体を使う |
| 製品版のロード時間を短くしたい | 開発中は JSON、製品版はビルド時にバイナリ（[zpp_bits](zpp-bits.md) など）に変換 |
| サイズを小さくしたい | `to_cbor` / `to_msgpack` でバイナリにする（読み書きのコードは同じ） |

## 関数の詳しい説明

### json::parse {#parse}

```cpp
template <typename InputType>
static basic_json parse(InputType&& i,
                        const parser_callback_t cb = nullptr,
                        const bool allow_exceptions = true,
                        const bool ignore_comments = false,
                        const bool ignore_trailing_commas = false);

template <typename IteratorType>
static basic_json parse(IteratorType first, IteratorType last, /* 同じ引数 */);
```

| 引数 | 意味 |
| --- | --- |
| `i` | 読む元。`std::string`、`std::string_view`、`const char*`、`std::istream`（`std::ifstream` など）、`std::vector<std::uint8_t>` など |
| `cb` | 読んでいる途中に呼ばれる関数。特定の要素を読み捨てるときに使う（ほぼ使わない） |
| `allow_exceptions` | `false` にすると、失敗時に例外ではなく discarded の値を返す |
| `ignore_comments` | `true` にすると `//` と `/* */` のコメントを許す |
| `ignore_trailing_commas` | `true` にすると `[1, 2,]` のような最後のカンマを許す（3.12〜） |

- **戻り値:** 読み込んだ `json`
- **計算量:** 入力の長さに比例 O(n)
- **例外:** 文法エラーで `json::parse_error`

```cpp
#include <print>

#include <nlohmann/json.hpp>

using json = nlohmann::json;

int main() {
  // 人が書く設定ファイルではコメントを許すと便利
  const char* text = R"({
    // 音量は 0〜100
    "volume": 80,
    "fullscreen": true
  })";
  json config = json::parse(text, nullptr, true, true);
  std::println("{} {}", config["volume"].get<int>(), config["fullscreen"].get<bool>());
}
```

```text title="実行結果"
80 true
```

!!! tip "文字列リテラルから作る"
    `using namespace nlohmann::literals;` を書くと、`R"({"a": 1})"_json` のように文字列の後ろに `_json` を付けて JSON を作れます。テストコードで便利です。

### dump {#dump}

```cpp
string_t dump(const int indent = -1,
              const char indent_char = ' ',
              const bool ensure_ascii = false,
              const error_handler_t error_handler = error_handler_t::strict) const;
```

| 引数 | 意味 |
| --- | --- |
| `indent` | 字下げの幅。`-1`（デフォルト）は改行なしの 1 行。`0` は改行だけ。`2` や `4` で読みやすくなる |
| `indent_char` | 字下げに使う文字。`'\t'` でタブにできる |
| `ensure_ascii` | `true` にすると日本語などを `あ` のようにエスケープして ASCII だけにする |
| `error_handler` | 不正な UTF-8 があったときの動き（[フラグ](#flags)） |

- **戻り値:** JSON の文字列（`std::string`）
- **計算量:** 中身の大きさに比例 O(n)

```cpp
#include <print>

#include <nlohmann/json.hpp>

using json = nlohmann::json;

int main() {
  json j = {{"name", "勇者"}, {"items", {1, 2}}};
  std::println("{}", j.dump());
  std::println("{}", j.dump(2));
  std::println("{}", j.dump(-1, ' ', true));
}
```

```text title="実行結果"
{"items":[1,2],"name":"勇者"}
{
  "items": [
    1,
    2
  ],
  "name": "勇者"
}
{"items":[1,2],"name":"勇者"}
```

- ファイルに保存するときは `dump(2)` か `dump(4)` が定番です。差分（Git）でも見やすくなります。
- 通信やログで小さくしたいときは `dump()`（1 行）。
- `std::cout << j` でも出力できます。`std::cout << std::setw(2) << j` とすると `dump(2)` と同じになります。

### get {#get}

```cpp
template <typename ValueType>
ValueType get() const;
```

| 引数 | 意味 |
| --- | --- |
| `ValueType`（テンプレート引数） | 変換したい C++ の型 |

- **戻り値:** 変換した値（コピー）
- **例外:** 型が合わないと `json::type_error`（302 など）

```cpp
json j = json::parse(R"({"hp": 100, "name": "Alice", "pos": [1.5, 2.0]})");
int hp = j["hp"].get<int>();
auto name = j["name"].get<std::string>();
auto pos = j["pos"].get<std::vector<float>>();
```

- 数値どうしは**勝手に変換されます**。`3.7` を `get<int>()` すると `3` になり、エラーにはなりません。
- `int x = j["hp"];` のように**暗黙の変換**でも取れますが、型が分かりにくくなり、思わぬオーバーロードが選ばれることがあるので、`get<T>()` と書くのがおすすめです（`JSON_USE_IMPLICIT_CONVERSIONS=0` で禁止できます）。

### value {#value}

```cpp
template <typename ValueType>
ValueType value(const typename object_t::key_type& key,
                const ValueType& default_value) const;

template <typename ValueType>
ValueType value(const json_pointer& ptr, const ValueType& default_value) const;
```

| 引数 | 意味 |
| --- | --- |
| `key` | 探すキー |
| `ptr` | `"/a/b"` のような JSON Pointer（深い場所を一度に探す） |
| `default_value` | キーが無いときに返す値。この型が戻り値の型になる |

- **戻り値:** キーがあればその値（`default_value` の型に変換）、無ければ `default_value`
- **例外:** キーはあるが型が違うと `json::type_error`。オブジェクトでない値に使うと `json::type_error`（306）

```cpp
#include <print>

#include <nlohmann/json.hpp>

using json = nlohmann::json;

int main() {
  json config = json::parse(R"({"volume": 80})");
  int volume = config.value("volume", 100);              // ある
  bool vsync = config.value("vsync", true);              // 無い -> true
  std::string lang = config.value("language", "ja");     // 無い -> "ja"
  std::println("{} {} {}", volume, vsync, lang);
}
```

```text title="実行結果"
80 true ja
```

- **設定ファイルの読み込みはほぼ全部 `value` で書けます。** 項目が増えても古い設定ファイルで落ちません。
- `value("language", "ja")` のように文字列リテラルを渡すと、戻り値は `std::string` になります。
- 「キーは無くてもいいが、あるなら型は正しくないとダメ」という動きなので、`"volume": "大"` のような間違いは例外になります。

### at {#at}

```cpp
reference at(const typename object_t::key_type& key);
const_reference at(const typename object_t::key_type& key) const;
reference at(size_type idx);
const_reference at(size_type idx) const;
reference at(const json_pointer& ptr);
```

| 引数 | 意味 |
| --- | --- |
| `key` | オブジェクトのキー |
| `idx` | 配列の番号（0 から） |
| `ptr` | JSON Pointer |

- **戻り値:** 要素への参照
- **計算量:** キーは O(log n)、番号は O(1)
- **例外:** 無ければ `json::out_of_range`（403 / 401）、種類が違えば `json::type_error`

**必ずあるはずのキー**は `at` で取ります。無かったときに例外で分かるので、データの間違いにすぐ気づけます。

### operator[] {#operator_brackets}

```cpp
reference operator[](const typename object_t::key_type& key);
const_reference operator[](const typename object_t::key_type& key) const;
reference operator[](size_type idx);
const_reference operator[](size_type idx) const;
```

| 引数 | 意味 |
| --- | --- |
| `key` | オブジェクトのキー |
| `idx` | 配列の番号 |

- **戻り値:** 要素への参照
- **書くときは `[]`、読むときは `at` / `value`** と覚えます。

`[]` は `std::map` の `[]` と同じで、**キーが無ければ null の要素を作ってしまいます**。

```cpp
json j;
j["player"]["name"] = "Alice";  // 書くとき: 途中のオブジェクトも自動で作られて便利
j["items"][2] = 10;             // 配列も自動で広がる: [null, null, 10]

int hp = j["hp"];               // 読むとき: "hp": null が作られ、null を int にして例外
```

さらに、**`const json` に存在しないキーで `[]` を使うと未定義動作**です（デバッグビルドでは assert で止まります）。関数の引数で `const json&` を受け取ったときは、特に `[]` で読まないようにします。

### contains {#contains}

```cpp
bool contains(const typename object_t::key_type& key) const;
bool contains(const json_pointer& ptr) const;
```

| 引数 | 意味 |
| --- | --- |
| `key` | 調べるキー |
| `ptr` | JSON Pointer（深い場所があるか） |

- **戻り値:** キーがあれば `true`。オブジェクトでない値に使うと常に `false`
- **計算量:** O(log n)

```cpp
if (j.contains("boss") && j["boss"].is_object()) {
  LoadBoss(j["boss"]);
}
```

### get_to {#get_to}

```cpp
template <typename ValueType>
ValueType& get_to(ValueType& v) const;
```

| 引数 | 意味 |
| --- | --- |
| `v` | 値を入れる先の変数 |

- **戻り値:** `v` への参照
- **例外:** `get` と同じ

`from_json` の中で、メンバに直接入れるときに使います。型を書かなくてよいので、メンバの型を変えたときに直す場所が減ります。

```cpp
void from_json(const json& j, Player& p) {
  j.at("name").get_to(p.name);    // p.name の型（std::string）に合わせて変換
  j.at("level").get_to(p.level);
}
```

### is_object {#is_object}

```cpp
bool is_object() const noexcept;
```

- **戻り値:** オブジェクト（`{...}`）なら `true`
- 外から来たデータ（MOD、ユーザーが書いた設定）を読むときは、`get` の前に種類を確認すると、例外を使わずに安全に読めます。

```cpp
if (!j.is_object()) {
  std::println("一番外側は {{ }} のはずですが {} でした", j.type_name());
  return;
}
```

### is_array {#is_array}

```cpp
bool is_array() const noexcept;
```

- **戻り値:** 配列（`[...]`）なら `true`
- 「1 つでも配列でも書ける」設定（`"drops": "potion"` と `"drops": ["potion", "gel"]`）を両方受け付けるときに使います。

### is_string {#is_string}

```cpp
bool is_string() const noexcept;
```

- **戻り値:** 文字列なら `true`

### is_number {#is_number}

```cpp
bool is_number() const noexcept;
```

- **戻り値:** 数値なら `true`（整数・小数どちらでも）
- `get<int>()` も `get<float>()` も、数値ならどちらでも読めます（勝手に変換されます）。

### is_number_integer {#is_number_integer}

```cpp
bool is_number_integer() const noexcept;
```

- **戻り値:** 整数なら `true`（符号あり・なしどちらでも）
- `3` は `true`、`3.0` は `false` です。「整数で書かないとダメ」なデータの確認に使います。
- `is_number_unsigned()` は、0 以上の整数で `true` です。

### is_number_float {#is_number_float}

```cpp
bool is_number_float() const noexcept;
```

- **戻り値:** 小数なら `true`
- `3.0` や `1e5` のように、小数点か指数があると `true` です。

### is_boolean {#is_boolean}

```cpp
bool is_boolean() const noexcept;
```

- **戻り値:** true / false なら `true`
- `"true"`（文字列）や `1` は `false` です。

### is_null {#is_null}

```cpp
bool is_null() const noexcept;
```

- **戻り値:** null なら `true`
- 空の `json`（`json j;`）や、`[]` で作られただけの要素も null です。

### is_discarded {#is_discarded}

```cpp
bool is_discarded() const noexcept;
```

- **戻り値:** parse に失敗した値なら `true`（allow_exceptions=false のとき）
- `json::parse(text, nullptr, false)` が失敗したときだけ `true` になります（[例外を使わずに読む](#例外を使わずに読む)）。

### items {#items}

```cpp
iteration_proxy<iterator> items() noexcept;
iteration_proxy<const_iterator> items() const noexcept;
```

- **戻り値:** 範囲 for で回せるもの。各要素で `key()` と `value()` が使える

```cpp
#include <print>

#include <nlohmann/json.hpp>

using json = nlohmann::json;

int main() {
  json prices = json::parse(R"({"potion": 50, "ether": 120})");
  for (const auto& [name, price] : prices.items()) {  // 構造化束縛も使える
    std::println("{}: {}G", name, price.get<int>());
  }
}
```

```text title="実行結果"
ether: 120G
potion: 50G
```

- 普通の範囲 for（`for (auto& v : j)`）だと、オブジェクトの**値だけ**が回ります。キーも欲しいときは `items()` を使います。
- 配列に使うと、キーは `"0"`、`"1"` という文字列になります。

### push_back {#push_back}

```cpp
void push_back(basic_json&& val);
void push_back(const basic_json& val);
void push_back(const typename object_t::value_type& val);  // オブジェクトに {キー, 値} を追加
void push_back(initializer_list_t init);
```

| 引数 | 意味 |
| --- | --- |
| `val` | 追加する値 |

- **計算量:** 償却 O(1)（配列のとき）
- null の値に使うと、自動で配列になります。
- `+=` 演算子でも同じことができます（`j["log"] += "start";`）。

### emplace_back {#emplace_back}

```cpp
template <class... Args>
reference emplace_back(Args&&... args);
```

| 引数 | 意味 |
| --- | --- |
| `args` | 要素の `json` を作るための引数 |

- **戻り値:** 追加した要素への参照（3.7〜）
- 戻り値の参照にそのまま書き込めるので、「配列に空のオブジェクトを足して中身を埋める」ときに便利です。

```cpp
json& enemy = stage["enemies"].emplace_back(json::object());
enemy["id"] = "slime";
enemy["x"] = 10;
```

### size {#size}

```cpp
size_type size() const noexcept;
```

- **戻り値:** 配列・オブジェクトなら要素の数、`null` なら 0、それ以外（数値・文字列など）は **1**
- 文字列の長さではないことに注意（`json("abc").size()` は 1）。文字列の長さは `get<std::string>().size()` で取ります。

### empty {#empty}

```cpp
bool empty() const noexcept;
```

- **戻り値:** 要素が無ければ `true`。`null` は `true`、数値・文字列は常に `false`

### erase {#erase}

```cpp
size_type erase(const typename object_t::key_type& key);
void erase(const size_type idx);
IteratorType erase(IteratorType pos);
IteratorType erase(IteratorType first, IteratorType last);
```

| 引数 | 意味 |
| --- | --- |
| `key` | 消すキー（オブジェクト） |
| `idx` | 消す番号（配列） |
| `pos` / `first`, `last` | 消す位置・範囲 |

- **戻り値:** キー版は消した数（0 か 1）
- **例外:** 種類が違うと `json::type_error`、配列の範囲外は `json::out_of_range`
- 保存する前にデバッグ用のキーを消す、といった使い方をします。

### find {#find}

```cpp
iterator find(const typename object_t::key_type& key);
const_iterator find(const typename object_t::key_type& key) const;
```

| 引数 | 意味 |
| --- | --- |
| `key` | 探すキー |

- **戻り値:** 見つかればその要素のイテレータ、無ければ `end()`
- `contains` + `at` で 2 回探すのを、1 回にできます。

```cpp
if (auto it = j.find("boss"); it != j.end()) {
  LoadBoss(*it);
}
```

### json::array {#json_array}

```cpp
static basic_json array(initializer_list_t init = {});
```

| 引数 | 意味 |
| --- | --- |
| `init` | 最初に入れる要素 |

`json j = {1, 2};` のような書き方は、中身によって配列になったりオブジェクトになったりして分かりにくいことがあります（[よくあるミス](#mistakes)）。**確実に配列にしたいとき**に使います。`json::array()` で空の配列 `[]` が作れます。

### json::object {#json_object}

```cpp
static basic_json object(initializer_list_t init = {});
```

| 引数 | 意味 |
| --- | --- |
| `init` | `{キー, 値}` のペアの並び |

空の `json` は `null` です。`dump` したときに `{}` と出したいなら `json::object()` で作ります。

### json::accept {#accept}

```cpp
template <typename InputType>
static bool accept(InputType&& i, const bool ignore_comments = false,
                   const bool ignore_trailing_commas = false);
```

| 引数 | 意味 |
| --- | --- |
| `i` | 調べる入力 |
| `ignore_comments` | コメントを許すか |
| `ignore_trailing_commas` | 最後のカンマを許すか（3.12〜） |

- **戻り値:** 正しい JSON なら `true`。値は作らないので `parse` より軽い

### type_name {#type_name}

```cpp
const char* type_name() const noexcept;
```

- **戻り値:** `"null"`、`"object"`、`"array"`、`"string"`、`"boolean"`、`"number"` など
- エラーメッセージを作るときに使います。

```cpp
if (!j["hp"].is_number()) {
  std::println("hp は数値のはずですが {} でした", j["hp"].type_name());
}
```

### json_pointer {#json_pointer}

```cpp
explicit json_pointer(const string_t& s = "");
// 使う側: at(ptr)、value(ptr, default)、contains(ptr)、operator[](ptr)
```

| 引数 | 意味 |
| --- | --- |
| `s` | `"/stages/0/name"` のような、`/` 区切りのパス。配列は番号で書く |

深い場所を 1 回で取るときに使います。`"/stages/0/name"_json_pointer` と書くこともできます（`nlohmann::literals` が必要）。

```cpp
auto name = j.at(json::json_pointer("/stages/0/name")).get<std::string>();
```

### json::to_cbor {#to_cbor}

```cpp
static std::vector<std::uint8_t> to_cbor(const basic_json& j);
```

| 引数 | 意味 |
| --- | --- |
| `j` | 変換する JSON |

- **戻り値:** CBOR（JSON と同じ構造を持つバイナリ形式）のバイト列
- 同じ仲間に `to_msgpack`、`to_bson`、`to_ubjson`、`to_bjdata` があります。
- テキストの JSON より小さく、数値を文字に変換しないので読むのも少し速くなります。読み書きのコード（`to_json` / `from_json`）はそのまま使えるのが利点です。

### json::from_cbor {#from_cbor}

```cpp
template <typename InputType>
static basic_json from_cbor(InputType&& i, const bool strict = true,
                            const bool allow_exceptions = true);
```

| 引数 | 意味 |
| --- | --- |
| `i` | CBOR のバイト列 |
| `strict` | `true` なら、データの後ろに余計なバイトがあるとエラー |
| `allow_exceptions` | `false` なら失敗時に discarded を返す |

### json::to_msgpack {#to_msgpack}

```cpp
static std::vector<std::uint8_t> to_msgpack(const basic_json& j);
```

- **戻り値:** MessagePack 形式のバイト列。読むのは `json::from_msgpack`
- MessagePack は他の言語（C#、Python、JavaScript）にもライブラリが多いので、サーバーとの通信に使いやすい形式です。

### merge_patch {#merge_patch}

```cpp
void merge_patch(const basic_json& apply_patch);
```

| 引数 | 意味 |
| --- | --- |
| `apply_patch` | 上書きする内容。値が `null` のキーは削除される |

「デフォルト設定」に「ユーザーの設定」を上書きする、という処理が 1 行で書けます。

```cpp
#include <print>

#include <nlohmann/json.hpp>

using json = nlohmann::json;

int main() {
  json config = json::parse(R"({"volume": 100, "lang": "ja", "debug": true})");
  json user = json::parse(R"({"volume": 30, "debug": null})");
  config.merge_patch(user);  // volume を上書き、debug を削除
  std::println("{}", config.dump());
}
```

```text title="実行結果"
{"lang":"ja","volume":30}
```

## フラグ・オプション {#flags}

### dump の error_handler

| 値 | 不正な UTF-8 があったとき |
| --- | --- |
| `json::error_handler_t::strict`（デフォルト） | `json::type_error`（316）を投げる |
| `json::error_handler_t::replace` | 不正なバイトを `U+FFFD`（�）に置き換える |
| `json::error_handler_t::ignore` | 不正なバイトを捨てる |

Windows で Shift_JIS（CP932）の文字列をそのまま入れると、UTF-8 として不正なので `dump` が例外を投げます。ソースファイルを UTF-8 で保存し、MSVC では `/utf-8` オプションを付けます。

### 設定マクロ（include の前に定義する）

| マクロ | 意味 |
| --- | --- |
| `JSON_USE_IMPLICIT_CONVERSIONS=0` | `int x = j;` のような暗黙の変換を禁止し、`get<T>()` を強制する |
| `JSON_DIAGNOSTICS=1` | 例外のメッセージに、エラーが起きた場所のパス（`/stages/0/hp` など）を付ける。デバッグに便利だが少し重い |
| `JSON_NOEXCEPTION` | 例外を使わない（エラー時は `abort`） |
| `JSON_USE_GLOBAL_UDLS=0` | `_json` リテラルをグローバルに置かない |

### 型の別名

| 型 | 違い |
| --- | --- |
| `nlohmann::json` | 普通。オブジェクトのキーはアルファベット順 |
| `nlohmann::ordered_json` | 入れた順番を保つ |
| `nlohmann::basic_json<...>` | 中で使う型（map、string、数値型）を自分で指定できる。上の 2 つはこれの別名 |

## ゲームでの使いどころ

| 場面 | 使い方 |
| --- | --- |
| 設定ファイル（音量・画面・キー設定） | `ordered_json` + `value()` で、無い項目はデフォルト |
| セーブデータ | 構造体にマクロ、`version` キーを入れる |
| ステージ・敵の配置（エディタ出力） | `from_json` で読み、ゲームの構造体に変換 |
| マスターデータ（アイテム・敵の表） | 開発中は JSON。量が増えたら製品版はバイナリに変換 |
| デバッグ表示・ログ | 状態を `dump(2)` で書き出して確認 |
| ImGui のエディタの保存 | 構造体ごと JSON に |

## よくあるミス {#mistakes}

??? failure "`[]` で読んでキーが増える・落ちる"
    `int hp = j["hp"];` は、キーが無いと `null` の要素を**作ってから**変換に失敗します。`const json&` だと未定義動作です。読むときは `at` か `value` を使います。

??? failure "キーの順番が変わって差分が読みにくい"
    `json` はキーをアルファベット順に並べます。設定ファイルを書いた順で保存したいなら `ordered_json` を使います。

??? failure "波括弧の初期化で配列とオブジェクトを間違える"
    `json j = {{"a", 1}, {"b", 2}};` はオブジェクト `{"a":1,"b":2}` になりますが、`json j = {{"a", 1}, {"b", 2, 3}};` は配列 `[["a",1],["b",2,3]]` になります。「すべての要素が `{文字列, 値}` の 2 つ組」のときだけオブジェクトになるからです。確実にしたいときは `json::array()` / `json::object()` を使います。

??? failure "float を保存すると桁が増える"
    `j["speed"] = 0.1f;` を `dump` すると `0.10000000149011612` になります。`float` を `double` に広げてから、`double` として正確に書き出すためです。読み戻せば同じ `0.1f` になるので壊れてはいませんが、見た目が気になるなら最初から `double` で持つか、整数（ミリ単位など）で保存します。

??? failure "マクロを名前空間の外に書く"
    `NON_INTRUSIVE` 系のマクロや `to_json` / `from_json` は、**型と同じ名前空間**に書く必要があります。`namespace game { struct Player ... }` に対してグローバルにマクロを書くと、「変換方法が見つからない」という長いコンパイルエラーになります。

??? failure "Shift_JIS の文字列を dump して例外"
    MSVC でソースが UTF-8 でないと、日本語の文字列リテラルが Shift_JIS になり、`dump` で `type_error.316` になります。ソースを UTF-8 で保存し、`/utf-8` を付けます。

??? failure "数値の型の変換に気づかない"
    `3.7` を `get<int>()` すると黙って `3` になります。`-1` を `get<unsigned>()` すると大きな値になります。外から来るデータは `is_number_integer()` などで確認します。

## 理解度チェック

!!! question "Q1. このコードの何がだめ？"
    ```cpp
    void ApplyConfig(const json& config) {
      int volume = config["volume"];
      SetVolume(volume);
    }
    ```

    <div class="spoiler" markdown>

    **答え:** `const json` に対して `[]` で読んでいます。`"volume"` が無いと**未定義動作**です。`config.value("volume", 100)` のように、デフォルト値付きで読みます。

    </div>

!!! question "Q2. 次のコードの出力は？"
    ```cpp
    json j;
    j["zeta"] = 1;
    j["alpha"] = 2;
    std::println("{}", j.dump());
    ```

    <div class="spoiler" markdown>

    **答え:** `{"alpha":2,"zeta":1}` です。`json` はキーをアルファベット順に並べます。入れた順にしたいなら `ordered_json` を使います。

    </div>

!!! question "Q3. セーブデータの構造体に `int gold = 0;` を追加しました。古いセーブファイルを読んでも落ちないようにするには、どのマクロを使う？"
    <div class="spoiler" markdown>

    **答え:** `NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE_WITH_DEFAULT` です。キーが無いメンバはデフォルト値（`0`）のままになります。`_WITH_DEFAULT` の無いマクロだと `out_of_range` の例外になります。

    </div>

## 類似ライブラリ

| ライブラリ | 違い |
| --- | --- |
| [simdjson](simdjson.md) | 読み込みが非常に速い。読み込み専用で、書き方が少し難しい |
| [rapidyaml](rapidyaml.md) | YAML（と JSON）を速く読み書きする。人が書く設定ファイル向け |
| RapidJSON | 速い JSON ライブラリ。書き方が冗長で古いスタイル |
| Glaze | 構造体を自動で JSON にする、とても速い新しいライブラリ（C++23 が必要） |
| [cereal](cereal.md) | 主にバイナリ。JSON アーカイブもあるが、出力の形は自由に決められない |

## これだけ覚える

!!! abstract "まとめ"
    - [x] 構造体は `NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE_WITH_DEFAULT` で 1 行
    - [x] 読み込みは `json::parse`、保存は `dump(2)`
    - [x] 読むときは `value`（無くてもいい）か `at`（必ずある）。`[]` は書くときだけ
    - [x] エラーは `json::exception` で受ける
    - [x] 順番を保ちたいなら `ordered_json`
    - [x] `version` キーを最初から入れる

## 関連ページ

- [シリアライズの概要](index.md)
- [simdjson（JSON・速さ重視）](simdjson.md)
- [rapidyaml（YAML）](rapidyaml.md)
- [ファイル入出力](../../basics/file-io.md)
- [nlohmann/json（GitHub）](https://github.com/nlohmann/json)
- [nlohmann/json 公式ドキュメント](https://json.nlohmann.me/)
