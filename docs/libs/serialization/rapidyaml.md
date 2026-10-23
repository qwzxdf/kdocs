---
title: rapidyaml（YAML）
tags:
  - 外部ライブラリ
  - シリアライズ
---

# rapidyaml（YAML）

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="perf perf-3">○ 普通</span>
<span class="ver ver-11">C++11〜</span>
`#include <ryml.hpp>` / `#include <ryml_std.hpp>`
</div>

**rapidyaml**（略して ryml、「ライムル」）は、YAML を速く読み書きするライブラリです。YAML は、JSON と同じデータを括弧やカンマをほとんど使わず、字下げで書ける形式で、コメントも書けるので、人が手で書く設定ファイルやゲームのデータ（敵のパラメータ、ステージの配置、会話のスクリプト）にとても向いています。rapidyaml は、YAML ライブラリの中でも飛び抜けて速く（有名な yaml-cpp の数十倍以上）、メモリの確保もとても少ないのが特徴です。また JSON も読み書きできます。その代わり、文字列を `std::string` ではなく独自の `csubstr`（`string_view` のようなもの）で扱うなど、少しクセがあります。

!!! tip "ポイント"
    - <strong>人が書くデータ（設定・パラメータ表・会話）を YAML で持ちたいときに使う。</strong>
    - 読み込みは **`ryml::parse_in_arena`**（文字列をコピーして持つ。安全）。
    - 値は `node["key"] >> 変数;`<strong> で読み、</strong>`node["key"] << 値;` で書く。
    - `#include <ryml_std.hpp>` を書くと、`std::string` と `std::vector` がそのまま使える。
    - 無いかもしれないキーは `has_child` で確認してから読む。 無いキーを読むとエラー。
    - デフォルトのエラー処理はプログラムを止める（abort）。例外にしたいなら設定を変える。

!!! info "このページを読む前に"
    [シリアライズの概要](../../engine/serialization/index.md) と [nlohmann/json](nlohmann-json.md) を先に読むと、「木の形のデータを、キーで取り出す」という考え方がつかみやすいです。[string_view](../../stl/utilities/string_view.md) を知っていると `csubstr` が分かりやすくなります。

## YAML とは

YAML（ヤムル）は、**字下げで構造を表す**テキスト形式です。同じデータを JSON と YAML で書き比べてみます。

=== "YAML"

    ```yaml
    # スライムの設定（コメントが書ける）
    name: スライム
    hp: 10
    speed: 1.5
    drops:
      - potion
      - gel
    ai:
      type: wander
      range: 3
    ```

=== "JSON"

    ```json
    {
      "name": "スライム",
      "hp": 10,
      "speed": 1.5,
      "drops": ["potion", "gel"],
      "ai": {"type": "wander", "range": 3}
    }
    ```

| YAML の書き方 | 意味 | JSON で書くと |
| --- | --- | --- |
| `キー: 値` | マップ（オブジェクト） | `{"キー": 値}` |
| `- 値`（字下げして並べる） | シーケンス（配列） | `[値, ...]` |
| `[1, 2, 3]` | 1 行で書くシーケンス（フロー形式） | `[1, 2, 3]` |
| `{x: 1, y: 2}` | 1 行で書くマップ（フロー形式） | `{"x": 1, "y": 2}` |
| `# ...` | コメント | 書けない |
| `"..."` / `'...'` | 文字列（`:` や `#` を含むときは囲む） | `"..."` |
| `|` の後に複数行 | 改行を残した複数行の文字列 | `"1行目\n2行目"` |
| `&name` / `*name` | アンカーと参照（同じ内容を使い回す） | 無い |

JSON の文法はほぼそのまま YAML としても正しいので、YAML のライブラリは JSON も読めます。

!!! warning "YAML のよくある落とし穴"
    - 字下げにタブは使えません。 必ずスペースで書きます。
    - `キー:値` のように `:` の後にスペースが無いと、マップになりません。
    - `#` の前にスペースがあると、その後ろはコメントになります。`#` を含む文字列（`color: #ff0000`）は `"#ff0000"` と囲みます。
    - `yes` / `no` / `on` / `off` を真偽値として扱うかどうかはライブラリによって違います。真偽値は `true` / `false` と書くのが安全です。

## 導入

### Visual Studio で導入する（最初に読む）

Visual Studio を使っているなら、ここから読みます。ライブラリを入れる基本の手順は [Visual Studio：外部ライブラリの入れ方](../../vs/libraries.md) にまとめています。ここでは rapidyaml だけの部分を書きます。

=== "ファイルを置く"

    1. [リリースページ](https://github.com/biojppm/rapidyaml/releases) の **単一ヘッダ版**（`rapidyaml-x.y.z.hpp`）を `third_party/rapidyaml/` に置き、1 つの `.cpp` だけで、include の前に `#define RYML_SINGLE_HDR_DEFINE_NOW` を書く
    2. プロジェクトのプロパティを開き（[画面つきの手順](../../vs/include-dirs.md#additional)）、構成を すべての構成、プラットフォームを x64 にする
    3. C/C++ → 全般 → 追加のインクルード ディレクトリ に、`$(SolutionDir)third_party

=== "vcpkg"

    1. 初回だけ、Developer PowerShell で `vcpkg integrate install` を実行する（[準備](../../vs/libraries.md#vcpkg)）
    2. ライブラリを入れる

        ```powershell
        vcpkg install ryml:x64-windows
        ```

        （マニフェスト モードなら、`vcpkg.json` の `dependencies` に `"ryml"` を足す）
    3. プロジェクトには何も設定せずに、`#include <ryml.hpp>` と書けば使える

apidyaml` を追加する
    4. `#include <ryml.hpp>` と書いてビルドする

!!! note "C++ の設定"
    C++11 以上で動きます。エラーで落とさず例外にしたいときは、プロジェクトの「プリプロセッサの定義」に `RYML_DEFAULT_CALLBACK_USES_EXCEPTIONS` を追加します。

### そのほかの方法（CMake など）

=== "vcpkg"

    ```text
    vcpkg install ryml
    ```

    ```cmake
    find_package(ryml CONFIG REQUIRED)
    target_link_libraries(my_game PRIVATE ryml::ryml)
    ```

=== "CMake FetchContent"

    ```cmake
    include(FetchContent)
    FetchContent_Declare(
      ryml
      GIT_REPOSITORY https://github.com/biojppm/rapidyaml.git
      GIT_TAG v0.9.0  # 最新版はリリースページで確認する
      GIT_SHALLOW FALSE  # 中で使っている c4core（サブモジュール）も取ってくる
      GIT_SUBMODULES_RECURSE TRUE)
    FetchContent_MakeAvailable(ryml)
    target_link_libraries(my_game PRIVATE ryml::ryml)
    ```

=== "1 ファイル版"

    [リリースページ](https://github.com/biojppm/rapidyaml/releases) から `rapidyaml-<バージョン>.hpp`（全部を 1 ファイルにまとめたもの）をダウンロードします。どれか 1 つの .cpp だけで、include の前に `#define RYML_SINGLE_HDR_DEFINE_NOW` を書きます（ここで関数の本体が作られます）。他の `.cpp` では普通に include するだけです。

## 3 つの大事な型

rapidyaml を使うには、まず次の 3 つの型を覚えます。

| 型 | 何か | 似ているもの |
| --- | --- | --- |
| `ryml::Tree` | YAML 全体を持つ木。ノードと文字列（アリーナ）をまとめて持つ | `nlohmann::json` の一番外側 |
| `ryml::NodeRef` / `ryml::ConstNodeRef` | 木の中の 1 つのノードを指すもの。軽くてコピーしてよい | イテレータ・ポインタ |
| `ryml::csubstr` / `ryml::substr` | 文字列の一部を指すもの（`const` 付きと無し） | `std::string_view` |

<svg class="fig flow" viewBox="0 0 604 280" role="img" aria-label="rapidyaml：ノードの配列と、文字列置き場"><defs><marker id="fl73747" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">rapidyaml：ノードの配列と、文字列置き場</text><line x1="107.0" y1="133.3" x2="235.9" y2="87.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl73747)"/><line x1="107.0" y1="162.7" x2="235.9" y2="209.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl73747)"/><line x1="493.0" y1="64.0" x2="435.0" y2="64.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl73747)"/><text x="464.0" y="58.0" text-anchor="middle" style="font-size:12px">番号で指す</text><line x1="493.0" y1="232.0" x2="404.0" y2="232.0" stroke="currentColor" stroke-width="2" marker-end="url(#fl73747)"/><text x="448.5" y="226.0" text-anchor="middle" style="font-size:12px">ここを指す</text><rect x="28.0" y="128.0" width="76" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="66.0" y="148.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">Tree</text><rect x="168.0" y="44.0" width="264" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="300.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">ノードの配列 [root][name][hp]...</text><rect x="199.0" y="212.0" width="202" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="300.0" y="232.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">アリーナ （文字列置き場）</text><rect x="496.0" y="44.0" width="80" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="536.0" y="64.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">NodeRef</text><rect x="496.0" y="212.0" width="80" height="40" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="536.0" y="232.0" text-anchor="middle" dominant-baseline="central" style="font-weight:600">csubstr</text></svg>

rapidyaml が速いのは、ノードを**1 つの配列にまとめて**持ち、文字列も元の入力（またはアリーナ）を指すだけで、値ごとにメモリを確保しないからです。その代わり、`csubstr` が指している先（入力やアリーナ）が消えると使えなくなります。

## 関数一覧

| 関数 | 重要度 | 何をする |
| --- | --- | --- |
| [`parse_in_arena`](#parse_in_arena) | <span class="rank rank-must">必須</span> | YAML をコピーして読む（安全） |
| [`rootref`](#rootref) | <span class="rank rank-must">必須</span> | 一番上のノード（書き込みもできる） |
| [`crootref`](#crootref) | <span class="rank rank-often">よく使う</span> | 一番上のノード（読むだけ） |
| [`operator[]`](#operator_brackets) | <span class="rank rank-must">必須</span> | キー・番号で子ノードを取る |
| [`operator>>`](#operator_read) | <span class="rank rank-must">必須</span> | ノードの値を変数に読む |
| [`operator<<`](#operator_write) | <span class="rank rank-must">必須</span> | 変数の値をノードに書く |
| [`has_child`](#has_child) | <span class="rank rank-must">必須</span> | キーがあるか調べる |
| [`emitrs_yaml`](#emitrs_yaml) | <span class="rank rank-must">必須</span> | 木を YAML の文字列にする |
| [`operator|=`](#operator_or_assign) | <span class="rank rank-often">よく使う</span> | ノードをマップ・シーケンスにする |
| [`children`](#children) | <span class="rank rank-often">よく使う</span> | 子ノードを範囲 for で回す |
| [`num_children`](#num_children) | <span class="rank rank-often">よく使う</span> | 子ノードの数 |
| [`key`](#key) | <span class="rank rank-often">よく使う</span> | ノードのキーの文字列 |
| [`val`](#val) | <span class="rank rank-often">よく使う</span> | ノードの値の文字列 |
| [`append_child`](#append_child) | <span class="rank rank-often">よく使う</span> | 子ノードを最後に追加する |
| [`ryml::key`](#ryml_key) | <span class="rank rank-often">よく使う</span> | キーを読み書きする目印 |
| [`find_child`](#find_child) | <span class="rank rank-sometimes">たまに</span> | キーで子を探す（無ければ無効なノード） |
| [`is_map`](#is_map) | <span class="rank rank-sometimes">たまに</span> | マップか調べる |
| [`is_seq`](#is_seq) | <span class="rank rank-sometimes">たまに</span> | シーケンスか調べる |
| [`parse_in_place`](#parse_in_place) | <span class="rank rank-sometimes">たまに</span> | 入力の文字列を直接使って読む（コピーなし） |
| [`emitrs_json`](#emitrs_json) | <span class="rank rank-sometimes">たまに</span> | 木を JSON の文字列にする |
| [`emit_yaml`](#emit_yaml) | <span class="rank rank-sometimes">たまに</span> | 木をファイル（`FILE*`）に書く |
| [`operator=`](#operator_assign) | <span class="rank rank-sometimes">たまに</span> | 文字列をコピーせずにノードに設定する |
| [`resolve`](#resolve) | <span class="rank rank-rare">知ってるだけ</span> | アンカー・参照（`&` / `*`）を展開する |
| [`to_csubstr`](#to_csubstr) | <span class="rank rank-sometimes">たまに</span> | `std::string` などを `csubstr` にする |
| [`set_callbacks`](#set_callbacks) | <span class="rank rank-rare">知ってるだけ</span> | エラー時の動きを変える |

## よくある使い方

### 読む

```cpp
#include <print>
#include <string>
#include <vector>

#include <ryml.hpp>
#include <ryml_std.hpp>  // std::string / std::vector に読み書きできるようにする

int main() {
  std::string text = R"(
name: Alice
level: 12
items: [101, 205, 330]
)";

  // 文字列をコピーして木を作る（text は後で消しても大丈夫）
  ryml::Tree tree = ryml::parse_in_arena(ryml::to_csubstr(text));
  ryml::ConstNodeRef root = tree.crootref();

  std::string name;
  int level = 0;
  std::vector<int> items;
  root["name"] >> name;    // >> で変数に読む
  root["level"] >> level;  // 文字列 "12" を int に変換してくれる
  root["items"] >> items;

  std::println("{} Lv.{} アイテム {} 個", name, level, items.size());
}
```

```text title="実行結果"
Alice Lv.12 アイテム 3 個
```

### 書く

```cpp
#include <print>
#include <string>

#include <ryml.hpp>
#include <ryml_std.hpp>

int main() {
  ryml::Tree tree;
  ryml::NodeRef root = tree.rootref();
  root |= ryml::MAP;  // 一番上をマップにする

  root["name"] << "Alice";  // << は値をアリーナにコピーして書く
  root["level"] << 12;

  ryml::NodeRef items = root["items"];
  items |= ryml::SEQ;  // シーケンス（配列）にする
  items.append_child() << 101;
  items.append_child() << 205;

  std::string yaml = ryml::emitrs_yaml<std::string>(tree);
  std::print("{}", yaml);
}
```

```text title="実行結果"
name: Alice
level: 12
items:
  - 101
  - 205
```

`root["name"]` のように**まだ無いキー**を `NodeRef` で取ると、「これから作るノード（シード）」が返ります。そこに `<<` で書くと、初めてノードが作られます。

## 値の読み書きの仕組み

rapidyaml の中では、**すべての値は文字列**として持っています（`level: 12` の `12` も、文字列 `"12"`）。`>>` で読むときに、受け取る変数の型に合わせて変換します。

| 受け取る型 | 変換 |
| --- | --- |
| `int`、`unsigned`、`std::int64_t` など | 整数として読む。`0x1F`（16 進）なども読める |
| `float`、`double` | 小数として読む |
| `bool` | `true` / `false` などを読む |
| `std::string`（`ryml_std.hpp` が必要） | 文字列をコピー |
| `ryml::csubstr` | コピーせずに指すだけ（木が消えると使えない） |
| `std::vector<T>`（`ryml_std.hpp` が必要） | シーケンスを読む |
| `std::map<K, V>`（`ryml_std.hpp` が必要） | マップを読む |
| 自作の型 | `read` 関数を書く（[自作の型](#custom)） |

この仕組みのおかげで、`version: 1.10` を文字列として読めば `"1.10"` のまま取れます（数値として先に解釈してしまうライブラリでは `1.1` になってしまうことがあります）。

## 自作の型を読み書きする {#custom}

自作の型と**同じ名前空間**に、`write` と `read` という名前の関数を書くと、`<<` と `>>` で使えるようになります。

```cpp
#include <print>
#include <string>
#include <vector>

#include <ryml.hpp>
#include <ryml_std.hpp>

namespace game {

struct EnemyParam {
  std::string name;
  int hp = 1;
  float speed = 1.0f;
  std::vector<std::string> drops;
};

// EnemyParam -> ノード
void write(ryml::NodeRef* n, const EnemyParam& e) {
  *n |= ryml::MAP;
  n->append_child() << ryml::key("name") << e.name;
  n->append_child() << ryml::key("hp") << e.hp;
  n->append_child() << ryml::key("speed") << e.speed;
  n->append_child() << ryml::key("drops") << e.drops;
}

// ノード -> EnemyParam。無いキーはデフォルトのまま
bool read(const ryml::ConstNodeRef& n, EnemyParam* e) {
  n["name"] >> e->name;  // name は必須
  if (n.has_child("hp")) {
    n["hp"] >> e->hp;
  }
  if (n.has_child("speed")) {
    n["speed"] >> e->speed;
  }
  if (n.has_child("drops")) {
    n["drops"] >> e->drops;
  }
  return true;
}

}  // namespace game

int main() {
  std::string text = R"(
enemies:
  - name: スライム
    hp: 10
    drops: [potion, gel]
  - name: コウモリ
    speed: 2.5
)";
  ryml::Tree tree = ryml::parse_in_arena(ryml::to_csubstr(text));

  std::vector<game::EnemyParam> enemies;
  tree.crootref()["enemies"] >> enemies;  // vector<EnemyParam> も自動で読める

  for (const auto& e : enemies) {
    std::println("{} HP{} 速さ{} ドロップ{}個", e.name, e.hp, e.speed, e.drops.size());
  }
}
```

```text title="実行結果"
スライム HP10 速さ1 ドロップ2個
コウモリ HP1 速さ2.5 ドロップ0個
```

!!! warning "関数名と引数の形は決まっている"
    `write(ryml::NodeRef*, const T&)` と `bool read(const ryml::ConstNodeRef&, T*)` という形で書きます（ライブラリが名前で探すので、Google Style の `Write` にはできません）。`read` の第 2 引数がポインタなのが他のライブラリと違うところです。古いバージョン（0.4 以前）では `read` の第 1 引数が `const ryml::NodeRef&` でした。

## エラー処理

rapidyaml のデフォルトのエラー処理は、<strong>エラーメッセージを出してプログラムを止める（abort）</strong> です。ゲームで「設定ファイルを 1 文字間違えたらゲームが落ちる」のは困るので、例外を投げるように設定を変えるのがおすすめです。

一番簡単なのは、ビルド設定で次のマクロを定義する方法です。エラーのときに `std::runtime_error` が投げられるようになります。

```cmake
target_compile_definitions(my_game PRIVATE RYML_DEFAULT_CALLBACK_USES_EXCEPTIONS)
```

```cpp
try {
  ryml::Tree tree = ryml::parse_in_arena(ryml::to_csubstr(text));
  int hp = 0;
  tree.crootref()["hp"] >> hp;
} catch (const std::exception& e) {
  std::println("設定ファイルのエラー: {}", e.what());
}
```

自分のエラー処理関数（ログに出す、エディタにエラーを表示する、など）を使いたいときは、[set_callbacks](#set_callbacks) で登録します。

| よくあるエラー | 原因 |
| --- | --- |
| 文法エラー（parse error） | 字下げのずれ、タブ、閉じていない括弧や引用符 |
| 無いキーを読んだ | `ConstNodeRef` の `[]` で存在しないキーを取った |
| 変換できない | `hp: たくさん` を `int` で読んだ |
| 種類が違う | マップのノードを `std::vector` で読んだ |

!!! note "無いキーの扱い"
    `ConstNodeRef` に対して存在しないキーで `[]` を使うと、エラーになります（設定によっては assert で止まります）。無いかもしれないキーは、必ず `has_child` か `find_child` で確認してから読みます。

## バージョン管理と互換性

YAML も JSON と同じく**キーの名前**で値を探すので、互換性を保つのは簡単です。

- メンバを追加した: `read` で `has_child` を見て、無ければデフォルトのまま
- メンバを削除した: 何もしなくてよい（知らないキーは読まないだけ）
- 名前を変えた: `read` で新しい名前と古い名前の両方を見る
- 大きく形を変えた: 一番上に `version: 2` を書き、`read` で分岐する

人が書くデータでは、書き間違ったキー（`hpp: 10`）に気づけないという問題もあります。開発中は、知っているキー以外があったら警告を出すチェックを入れると、ミスにすぐ気づけます。

```cpp
for (ryml::ConstNodeRef child : node.children()) {
  ryml::csubstr k = child.key();
  if (k != "name" && k != "hp" && k != "speed" && k != "drops") {
    std::println("知らないキー: {}", std::string_view(k.str, k.len));
  }
}
```

## 速さの特徴

| 項目 | 特徴 |
| --- | --- |
| 読み込みの速さ | YAML としては速い。yaml-cpp より数十倍以上速いことが多い |
| JSON を読むとき | nlohmann/json より速いことが多いが、[simdjson](simdjson.md) ほどではない |
| メモリ | ノードを 1 つの配列で持つので、確保の回数がとても少ない |
| 一番速い使い方 | `parse_in_place` で入力を直接使う。`Tree` を使い回す（`clear()` して再利用） |

## 関数の詳しい説明

### parse_in_arena {#parse_in_arena}

```cpp
Tree parse_in_arena(csubstr yaml);
Tree parse_in_arena(csubstr filename, csubstr yaml);
void parse_in_arena(csubstr yaml, Tree* t);
void parse_in_arena(csubstr filename, csubstr yaml, Tree* t);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `yaml` | `csubstr` | 読む YAML（または JSON）の文字列 |
| `filename` | `csubstr` | エラーメッセージに表示するファイル名（読むファイルではない） |
| `t` | `ryml::Tree*` | 結果を入れる木。使い回すとメモリの再確保が減る |

- **戻り値:** 読み込んだ木
- 計算量: O(n)
- 入力を木のアリーナにコピーしてから読むので、元の文字列はすぐ消してかまいません。迷ったらこちらを使います。
- ファイルから読むときは、[ifstream](../../stl/io/fstream.md) などで `std::string` に読んでから渡します（rapidyaml 自体にはファイルを開く関数がありません）。
- `filename` を渡しておくと、エラーのときに「`enemies.yml:12:3`」のように場所が分かるので便利です。

### rootref {#rootref}

```cpp
NodeRef Tree::rootref();
```

- 戻り値: 一番上のノード。値の読み書きができる
- 書き込みをするときに使います。

### crootref {#crootref}

```cpp
ConstNodeRef Tree::crootref() const;
```

- 戻り値: 一番上のノード（読むだけ）
- 読むだけなら、間違えて書き込んだりシードを作ったりしないように、`ConstNodeRef` を使うのがおすすめです。

### operator[] {#operator_brackets}

```cpp
NodeRef NodeRef::operator[](csubstr key);
NodeRef NodeRef::operator[](size_t pos);
ConstNodeRef ConstNodeRef::operator[](csubstr key) const;
ConstNodeRef ConstNodeRef::operator[](size_t pos) const;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `key` | `csubstr` | マップのキー |
| `pos` | `size_t` | シーケンスの番号（0 から） |

- 戻り値: 子ノード
- 計算量: キーは O(子の数)（前から順に探す）、番号も O(番号)（リストをたどる）
- `NodeRef` で無いキーを取ると「シード」（これから作るノード）が返り、書き込むとノードが作られます。読もうとするとエラーです。
- `ConstNodeRef` で無いキーを取るとエラーです。

!!! note "子が多いノードで [] を何度も使わない"
    `[]` は子を前から探すので、子が 1000 個あるノードで `node[i]` をループすると O(n²) になります。全部を回すときは [children](#children) を使います。

### operator>> {#operator_read}

```cpp
template <class T>
ConstNodeRef const& operator>>(ConstNodeRef const& node, T& v);
// ryml::key(v) を渡すとキーを読む
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `v` | `T&` | 値を入れる変数。この型に合わせて変換される |

- 戻り値: ノード自身（`>>` をつなげられる）
- 変換できないと（`"abc"` を `int` に）エラーです。

### operator<< {#operator_write}

```cpp
template <class T>
NodeRef& operator<<(NodeRef& node, T const& v);
// ryml::key(v) を渡すとキーを書く
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `v` | `const T&` | 書く値。文字列に変換してアリーナにコピーされる |

- 戻り値: ノード自身（`<< ryml::key("hp") << 10` のようにつなげられる）
- 値がコピーされるので、一時的な `std::string` や数値も安全に書けます。

### has_child {#has_child}

```cpp
bool has_child(csubstr key) const;
bool has_child(size_t pos) const;  // 番号の子があるか（バージョンによる）
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `key` | `csubstr` | 調べるキー |

- 戻り値: その名前の子があれば `true`
- 無いかもしれないキーを読む前に、必ずこれで確認します。

### emitrs_yaml {#emitrs_yaml}

```cpp
template <class CharOwningContainer>
CharOwningContainer emitrs_yaml(Tree const& t);

template <class CharOwningContainer>
CharOwningContainer emitrs_yaml(ConstNodeRef const& n);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `CharOwningContainer` | 型引数 | 結果を入れる型。`std::string` か `std::vector<char>` |
| `t` / `n` | `const Tree&` / `ConstNodeRef` | 書き出す木・ノード（ノードならその下だけ） |

- 戻り値: YAML の文字列
- 名前の `rs` は「resize」の意味で、「コンテナを必要な大きさに広げて書く」という意味です。
- 読み込んだ木を書き出すと、元の書き方（フロー形式 `[1, 2]` かブロック形式 `- 1` か）はなるべく保たれますが、コメントは消えます。

### operator|= {#operator_or_assign}

```cpp
NodeRef& operator|=(NodeRef& node, NodeType_e type);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `type` | `NodeType_e` | `ryml::MAP`（マップ）か `ryml::SEQ`（シーケンス）。`ryml::FLOW_SL` などのスタイルを ` | ` で足せる |

- 新しく作ったノードを、子を持てるマップかシーケンスにします。書き込むときは、子を足す前にまずこれをします。
- `items |= ryml::SEQ | ryml::FLOW_SL;` とすると、`items: [101, 205]` のように 1 行で書き出されます（スタイルのフラグはバージョンによって名前が違うことがあります）。

### children {#children}

```cpp
children_view children();
const_children_view children() const;
```

- 戻り値: 子ノードを範囲 for で回せるもの
- 計算量: 全体で O(子の数)

```cpp
#include <print>
#include <string>
#include <string_view>

#include <ryml.hpp>
#include <ryml_std.hpp>

int main() {
  std::string text = "potion: 50\nether: 120\nelixir: 1000\n";
  ryml::Tree tree = ryml::parse_in_arena(ryml::to_csubstr(text));

  for (ryml::ConstNodeRef item : tree.crootref().children()) {
    ryml::csubstr name = item.key();
    int price = 0;
    item >> price;
    // csubstr は std::println に直接渡せないので string_view にする
    std::println("{}: {}G", std::string_view(name.str, name.len), price);
  }
}
```

```text title="実行結果"
potion: 50G
ether: 120G
elixir: 1000G
```

nlohmann/json と違って、マップの子は書いた順番のまま並んでいます。

### num_children {#num_children}

```cpp
size_t num_children() const;
```

- 戻り値: 子の数
- 計算量: O(子の数)（数えるので、ループの条件に毎回書かない）

### key {#key}

```cpp
csubstr key() const;
```

- 戻り値: ノードのキーの文字列（`csubstr`）。キーを持たないノード（シーケンスの要素など）に使うとエラー
- 指しているのは木の中（アリーナか入力）なので、木が消えると使えません。保存するなら `std::string(k.str, k.len)` でコピーします。

### val {#val}

```cpp
csubstr val() const;
```

- 戻り値: ノードの値の文字列（`csubstr`）。変換しない生の文字列
- 値を持たないノード（マップやシーケンス）に使うとエラーです。
- `csubstr` には `==`（文字列リテラルと比べられる）、`begins_with`、`ends_with`、`find`、`trim` などの便利な関数があります。

### append_child {#append_child}

```cpp
NodeRef append_child();
```

- 戻り値: 最後に追加された空の子ノード
- シーケンスに要素を足すとき、マップに `<< ryml::key(...)` でキー付きの子を足すときに使います。

### ryml::key {#ryml_key}

```cpp
template <class K>
Key<K> key(K& k);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `k` | `T&` | キーとして読み書きする変数・値 |

- `node << ryml::key("hp") << 10;` で「キーが hp、値が 10」の子を書きます。
- `child >> ryml::key(name);` でキーを `name` に読みます。

### find_child {#find_child}

```cpp
NodeRef find_child(csubstr key);
ConstNodeRef find_child(csubstr key) const;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `key` | `csubstr` | 探すキー |

- 戻り値: 見つかった子。無ければ無効なノード（`invalid()` が `true`）
- `has_child` と `[]` で 2 回探すのを 1 回にできます。

```cpp
if (ryml::ConstNodeRef hp = node.find_child("hp"); !hp.invalid()) {
  hp >> e->hp;
}
```

### is_map {#is_map}

```cpp
bool is_map() const;
```

- 戻り値: マップ（`キー: 値` の集まり）なら `true`
- 人が書いたデータの形が正しいかを確認するときに使います。

### is_seq {#is_seq}

```cpp
bool is_seq() const;
```

- 戻り値: シーケンス（`- 値` の並び、`[...]`）なら `true`
- 他にも `has_val()`（値を持つ）、`has_key()`（キーを持つ）、`is_keyval()`（キーと値を持つ）、`val_is_null()`（値が `~` や `null`）などがあります。

### parse_in_place {#parse_in_place}

```cpp
Tree parse_in_place(substr yaml);
Tree parse_in_place(csubstr filename, substr yaml);
void parse_in_place(substr yaml, Tree* t);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `yaml` | `substr` | 読む YAML。書き換え可能な文字列（`char` の配列や `std::string` の中身） |
| `filename` | `csubstr` | エラー表示用の名前 |
| `t` | `Tree*` | 結果を入れる木 |

- 入力の文字列をコピーせずに、そのまま木の文字列として使います（エスケープの処理などで中身が書き換えられます）。
- 一番速い読み方ですが、入力の文字列を木より長く残しておく必要があります。入力が先に消えると、木の中の `csubstr` がすべて壊れます。

```cpp
std::string text = LoadFile("enemies.yml");
ryml::Tree tree = ryml::parse_in_place(ryml::to_substr(text));
// text は tree を使い終わるまで消さない・変更しない
```

### emitrs_json {#emitrs_json}

```cpp
template <class CharOwningContainer>
CharOwningContainer emitrs_json(Tree const& t);
```

- 戻り値: JSON の文字列
- 「人は YAML で書き、ゲームやツールには JSON で渡す」という変換にも使えます。

### emit_yaml {#emit_yaml}

```cpp
size_t emit_yaml(Tree const& t, FILE* f = nullptr);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `f` | `FILE*` | 書き込む先のファイル。`nullptr` なら標準出力 |

- 戻り値: 書いたバイト数
- `std::cout << tree;` でも出力できます。デバッグ表示に便利です。

### operator= {#operator_assign}

```cpp
void NodeRef::operator=(csubstr v);
void NodeRef::operator=(std::nullptr_t);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `v` | `csubstr` | ノードに設定する値の文字列。コピーされない |

- 値をコピーせずにノードに設定します。文字列リテラルなら速くて安全ですが、一時的な `std::string` を渡すと、木の中で壊れた文字列になります。
- 迷ったら、コピーしてくれる `<<` を使います。

```cpp
root["mode"] = "easy";            // OK: 文字列リテラルはずっと残る
std::string s = MakeName();
root["name"] = ryml::to_csubstr(s);  // 危ない: s が消えると壊れる
root["name"] << s;                  // OK: アリーナにコピーされる
```

### resolve {#resolve}

```cpp
void Tree::resolve();
```

- YAML のアンカー（`&base`）と参照（`*base`）、マージ（`<<: *base`）を展開して、普通のノードにします。
- アンカーを使った YAML を読むときは、読み込んだ直後に呼びます。

```yaml
base_enemy: &base
  hp: 10
  speed: 1.0
slime:
  <<: *base   # base_enemy の内容をここにコピー
  speed: 0.5  # 一部だけ上書き
```

パラメータ表で「共通の設定を書いて、一部だけ変える」ときにとても便利です。

### to_csubstr {#to_csubstr}

```cpp
csubstr to_csubstr(const std::string& s);   // ryml_std.hpp
csubstr to_csubstr(const char* s);
substr to_substr(std::string& s);            // 書き換え可能
```

- 戻り値: 文字列を指す `csubstr` / `substr`（コピーはしない）
- `std::string` を rapidyaml の関数に渡すときに使います。

### set_callbacks {#set_callbacks}

```cpp
void set_callbacks(Callbacks const& c);
Callbacks const& get_callbacks();
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `c` | `ryml::Callbacks` | メモリ確保・解放・エラー処理の関数をまとめたもの |

- エラーのときに呼ばれる関数を、自分の関数に置き換えます。ログに出して例外を投げる、などができます。
- エラー処理関数の引数の形はバージョンによって変わっているので、使っているバージョンの `ryml::Callbacks` の定義を確認して書きます。簡単に済ませたいなら、[エラー処理](#エラー処理) の `RYML_DEFAULT_CALLBACK_USES_EXCEPTIONS` を使います。

## フラグ・オプション

### ノードの種類（operator|= に渡す）

| フラグ | 意味 |
| --- | --- |
| `ryml::MAP` | マップにする |
| `ryml::SEQ` | シーケンスにする |
| `ryml::FLOW_SL` | 1 行のフロー形式（`[1, 2]`、`{a: 1}`）で書き出す |
| `ryml::BLOCK` | 複数行のブロック形式で書き出す（デフォルト） |
| `ryml::VAL_DQUO` / `VAL_SQUO` | 値を `"..."` / `'...'` で囲んで書き出す |
| `ryml::VAL_LITERAL` | 値を `|` の複数行形式で書き出す |

スタイルのフラグは 0.7 以降のもので、古いバージョンでは名前が違います。

### 設定マクロ

| マクロ | 意味 |
| --- | --- |
| `RYML_DEFAULT_CALLBACK_USES_EXCEPTIONS` | エラーで abort せず `std::runtime_error` を投げる |
| `RYML_SINGLE_HDR_DEFINE_NOW` | 1 ファイル版で、関数の本体をこの `.cpp` に作る |
| `RYML_USE_ASSERT` | ライブラリ内部の assert を有効にする（デバッグ用） |

## ゲームでの使いどころ

| 場面 | 使い方 |
| --- | --- |
| 敵・アイテムのパラメータ表 | YAML で書き、アンカーで共通部分をまとめる。起動時に構造体に読む |
| 会話・イベントのスクリプト | 複数行の文字列（`|`）で台詞を書く |
| ゲームの設定ファイル | コメントで各項目の説明を書いておける |
| ビルド・ツールの設定 | アセット変換ツールの設定を YAML で |
| 製品版への変換 | YAML を読み、ビルド時にバイナリ（[zpp_bits](zpp-bits.md) など）に変換する |

## よくあるミス

??? failure "ConstNodeRef で無いキーを読む"
    `root["boss"] >> boss;` で `boss` が無いとエラーで止まります。`has_child` や `find_child` で確認してから読みます。

??? failure "parse_in_place の入力を先に消す"
    `ryml::parse_in_place` は入力をそのまま使うので、入力の `std::string` が消えると木の中の文字列が全部壊れます。分からなければ `parse_in_arena` を使います。

??? failure "operator= で一時的な文字列を設定する"
    `node = ryml::to_csubstr(std::to_string(10));` は、一時的な文字列がすぐ消えるので壊れます。値を書くときは `<<` を使います。

??? failure "csubstr をそのまま println する"
    `csubstr` は `std::format` に対応していないので、`std::println("{}", node.val())` はコンパイルエラーになります（バージョンによる）。`std::string_view(s.str, s.len)` にしてから渡します。

??? failure "YAML にタブを使う"
    エディタの設定でタブが入ると、文法エラーになります。YAML ファイルはスペースで字下げするように、エディタ（`.editorconfig`）で設定しておきます。

??? failure "エラーで突然ゲームが落ちる"
    デフォルトではエラーで abort します。人が書くデータを読むなら、`RYML_DEFAULT_CALLBACK_USES_EXCEPTIONS` などでエラーを受け取れるようにしておきます。

## 類似ライブラリ

| ライブラリ | 違い |
| --- | --- |
| yaml-cpp | 一番有名な YAML ライブラリ。書きやすいが、とても遅くメモリも多く使う |
| [nlohmann/json](nlohmann-json.md) | JSON なら一番書きやすい。コメントは（オプションで）読めるが書き出せない |
| toml++ | TOML 形式（`[section]` と `key = value`）。設定ファイル向けで分かりやすい |
| [simdjson](simdjson.md) | JSON をとても速く読む。YAML は読めない |

## これだけ覚える

!!! abstract "まとめ"
    - [x] 人が書くデータは YAML。コメントとアンカーが便利
    - [x] 読むのは `parse_in_arena`、取り出すのは `node["key"] >> 変数`
    - [x] 書くのは `|= ryml::MAP` してから `node["key"] << 値`
    - [x] `ryml_std.hpp` で `std::string` と `std::vector` に対応
    - [x] 無いかもしれないキーは `has_child` で確認
    - [x] エラーで abort しないように設定する

## 関連ページ

- [シリアライズの概要](../../engine/serialization/index.md)
- [nlohmann/json（JSON・定番）](nlohmann-json.md)
- [ファイル入出力](../../basics/file-io.md)
- [rapidyaml（GitHub）](https://github.com/biojppm/rapidyaml)
- [rapidyaml ドキュメント](https://rapidyaml.readthedocs.io/)
