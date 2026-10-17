---
title: std::generator（コルーチン）
tags:
  - 型・言語サポート
---

# std::generator（コルーチン）

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <generator>`
</div>

`std::generator<T>` は、**値を 1 つずつ「出して（co_yield）」は一時停止し、次を求められたら続きから再開する関数**（コルーチン）を作るための型です。普通の関数は全部の結果を vector に入れて返しますが、generator は必要になった分だけ、その場で作って渡します。範囲 for でそのまま回せるので、「無限に続く数列」や「迷路の探索手順を 1 歩ずつ」のような処理を素直に書けます。

!!! tip "ポイント"
    - 戻り値の型を `std::generator<T>` にして、中で `co_yield 値;` と書くと、範囲 for で回せる関数になる。
    - 結果を全部メモリに持たないので、無限の列や大きな列に向いている。
    - C++23 の新しい機能で、対応しているコンパイラが限られる（GCC 14 / MSVC 17.13 以降）。

!!! info "このページを読む前に"
    [範囲 for](../../basics/range-for.md) と [ranges とビュー](../../basics/ranges.md) を先に読むと分かりやすいです。

## 関数一覧

| 名前 | 重要度 | 何をする |
| --- | --- | --- |
| [`std::generator<T>`](#generator) | <span class="rank rank-rare">知ってるだけ</span> | 値を順に作り出すコルーチンの戻り値の型 |
| [`co_yield`](#co_yield) | <span class="rank rank-rare">知ってるだけ</span> | 値を 1 つ出して一時停止する |
| [`co_return`](#co_return) | <span class="rank rank-rare">知ってるだけ</span> | 途中で終わる |
| [`std::ranges::elements_of`](#elements_of) | <span class="rank rank-rare">知ってるだけ</span> | 別の範囲の要素を全部出す |

## よくある使い方

```cpp
#include <generator>
#include <print>
#include <ranges>

// 無限に続く 1, 2, 4, 8, ...
std::generator<int> PowersOfTwo() {
  int x = 1;
  while (true) {
    co_yield x;  // x を出して、ここで一時停止する
    x *= 2;      // 次を求められたら、ここから再開
  }
}

int main() {
  for (int p : PowersOfTwo() | std::views::take(6)) {  // 必要な分だけ作られる
    std::print("{} ", p);
  }
  std::println("");
}
```

```text title="実行結果"
1 2 4 8 16 32 
```

## 詳しい説明

### std::generator {#generator}

<span class="ver ver-23">C++23</span>

```cpp
template <class Ref, class V = void, class Allocator = void>
class generator;
```

| テンプレート引数 | 意味 |
| --- | --- |
| `Ref` | 出す値の型（`int`、`const std::string&` など） |

- 関数の戻り値をこの型にして、中で `co_yield` を使うとコルーチンになります
- 1 回しか回せません（入力範囲）

### co_yield {#co_yield}

```cpp
co_yield 式;
```

- 値を 1 つ呼び出し側に渡して、関数を一時停止します。ローカル変数はそのまま保たれ、次に再開すると続きから動きます

### co_return {#co_return}

```cpp
co_return;
```

- generator を終わらせます（範囲 for が終わる）

```cpp
#include <generator>
#include <print>
#include <string>

// 迷路の道順を 1 歩ずつ出す（途中で終わる）
std::generator<std::string> Path() {
  co_yield "右";
  co_yield "右";
  co_yield "上";
  co_return;  // ここで終わり
  co_yield "ここには来ない";
}

int main() {
  for (const std::string& step : Path()) {
    std::print("{} ", step);
  }
  std::println("");
}
```

```text title="実行結果"
右 右 上 
```

### std::ranges::elements_of {#elements_of}

```cpp
co_yield std::ranges::elements_of(range);
```

- 別の範囲（vector や別の generator）の要素を、1 つずつ全部出します。再帰的な木の探索を書くのに便利です

```cpp
#include <generator>
#include <print>
#include <ranges>
#include <vector>

struct Node {
  int value;
  std::vector<Node> children;
};

// 木を深さ優先でたどる
std::generator<int> Walk(const Node& node) {
  co_yield node.value;
  for (const Node& child : node.children) {
    co_yield std::ranges::elements_of(Walk(child));  // 子の結果を全部出す
  }
}

int main() {
  Node root{1, {{2, {{4, {}}}}, {3, {}}}};
  for (int v : Walk(root)) {
    std::print("{} ", v);
  }
  std::println("");
}
```

```text title="実行結果"
1 2 4 3 
```

## フラグ・オプション

フラグはありません。

## ゲームでの使いどころ

| 場面 | 例 |
| --- | --- |
| 木の探索 | シーングラフ・UI の階層を順にたどる |
| 手続き型生成 | 部屋を 1 つずつ生成して出す |
| 時間をまたぐ処理 | 会話イベントの手順（ゲーム用の自作コルーチンの考え方の入門として） |

## よくあるミス

??? failure "参照で出したローカル変数が消える"
    `std::generator<const std::string&>` で一時的な文字列を出すと、再開したときには消えています。値の型（`std::generator<std::string>`）にするほうが安全です。

??? failure "2 回回そうとする"
    generator は 1 回しか回せません。もう一度回すなら、関数をもう一度呼びます。

## 理解度チェック

!!! question "Q1. vector に全部入れて返す関数と比べた generator の利点は？"
    <div class="spoiler" markdown>

    **答え:** 必要な分だけ作るので、無限の列や巨大な列でもメモリを使いません。途中で止めれば、残りは作られません。

    </div>

## これだけ覚える

!!! abstract "まとめ"
    - [x] 戻り値を std::generator<T> にして co_yield で値を出す
    - [x] 範囲 for で回せる。必要な分だけ作られる

## 関連ページ

- [ranges とビュー](../../basics/ranges.md)
- [cppreference: std::generator](https://en.cppreference.com/w/cpp/coroutine/generator)
