---
title: std::pair
summary: "2 つの値を、1 つにまとめる。map の要素や、関数が 2 つの値を返すときに。"
order: 48
tags:
  - ユーティリティ
---

# std::pair

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="perf perf-4">◎ 速い</span>
<span class="ver ver-11">C++98〜</span>
`#include <utility>`
</div>

`std::pair` は、**2 つの値をひとまとめにする型**です。わざわざ構造体を作るほどでもない「ちょっとした組」を表すのに使います。[`std::map`](../containers/map.md) の要素（キーと値）も pair です。C++17 からは構造化束縛 `auto [a, b] = p;` で、中身に名前を付けて取り出せます。

!!! tip "ポイント"
    - <strong>関数から 2 つの値を返すとき、`map` の要素を扱うときに使う。</strong>
    - 取り出すのは構造化束縛 `auto [x, y] = pair;` が一番読みやすい。
    - 意味のある組なら、**名前付きのメンバを持つ構造体のほうが読みやすい**（`first` / `second` では何か分からない）。
    - `<` や `==` は 1 つ目から順に比べる。複数の条件での並べ替えにも使える。

## 宣言

```cpp
template <class T1, class T2>
struct pair;
```

| テンプレート引数 | 意味 |
| --- | --- |
| `T1`, `T2` | 1 つ目・2 つ目の型 |

## 関数の詳しい説明

### first / second {#first}

```cpp
T1 first;
T2 second;
```

- pair の 1 つ目と 2 つ目のメンバ変数です

```cpp
#include <print>
#include <utility>

int main() {
  std::pair<int, int> grid_pos = {3, 5};
  grid_pos.second += 1;
  std::println("({}, {})", grid_pos.first, grid_pos.second);
}
```

```text title="実行結果"
(3, 6)
```

### {a, b} で作る {#make}

```cpp
std::pair<int, std::string> p = {1, "one"};
std::tuple<int, float, bool> t = {1, 2.0f, true};
std::pair q(1, 2.0);  // 型を推論（std::pair<int, double>）
```

- 戻り値の型が決まっている関数では、`return {a, b};` だけで作れます

### 比較演算子 {#compare}

- `==`, `!=`, `<`, `<=`, `>`, `>=`, `<=>` が使えます。**1 つ目を比べて、同じなら 2 つ目を比べる**（辞書順）

```cpp
#include <print>
#include <utility>

int main() {
  std::pair<int, int> a = {1, 9};
  std::pair<int, int> b = {2, 0};
  std::println("{} {}", a < b, a == std::pair{1, 9});
}
```

```text title="実行結果"
true true
```

### swap {#swap}

```cpp
void swap(pair& other);
```

- 中身を交換します

<div class="anim" data-label="a.swap(b)">
1 2 | 3 4 # a と b
>3 >4 | >1 >2 # 要素ごとに入れ替える
</div>

## よくある使い方

### 関数から 2 つの値を返す

```cpp
#include <print>
#include <utility>

// (成功したか, 結果) を返す
std::pair<bool, int> TryParse(int raw) {
  if (raw < 0) {
    return {false, 0};
  }
  return {true, raw * 2};
}

int main() {
  auto [ok, value] = TryParse(21);
  std::println("{} {}", ok, value);
}
```

```text title="実行結果"
true 42
```

### map を回す

```cpp
#include <map>
#include <print>
#include <string>

int main() {
  std::map<std::string, int> price = {{"ポーション", 50}, {"剣", 300}};
  for (const auto& [name, yen] : price) {  // 要素は pair<const string, int>
    std::println("{}: {}", name, yen);
  }
}
```

```text title="実行結果"
ポーション: 50
剣: 300
```

### operator= {#op_assign}

```cpp
pair& operator=(const pair& other);
pair& operator=(pair&& other) noexcept(...);
```

- 計算量: 要素による

`first` と `second` をそれぞれ代入します。

### operator== {#op_eq}

```cpp
template <class T1, class T2>
bool operator==(const pair<T1, T2>& a, const pair<T1, T2>& b);
```

- 計算量: 要素による

`first` と `second` が両方等しければ `true`。

### operator<=> <span class="ver ver-20">C++20</span> {#op_cmp data-toc-label="operator<=>"}

```cpp
template <class T1, class T2>
auto operator<=>(const pair<T1, T2>& a, const pair<T1, T2>& b);
```

- 計算量: 要素による

まず `first` を比べ、等しければ `second` を比べる辞書順の三方比較。

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| map の要素の取り出し | `for (const auto& [key, value] : map)` |
| 関数が 2 つの値を返す（位置と成功フラグ） | `std::pair<Vec2, bool> Raycast(...)` |
| (スコア, 名前) の並べ替え | `std::pair<int, std::string>` を `sort` |

## よくあるミス

??? failure "first / second だと意味が分からない"
    `p.first` が「x」なのか「HP」なのか、読む人に伝わりません。意味があるなら構造体にします（`struct Pos { int x; int y; };`）。

??? failure "参照を持つ pair を返す"
    `std::pair<const int&, int>` のように参照を入れて返すと、元が消えたときにぶら下がります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::tuple`](tuple.md) | 3 つ以上の値をまとめる |
| 構造体 | 名前を付けられる。意味があるなら、こちら |
| [`std::array`](../containers/array.md) | 同じ型の値が固定個数 |

## コンパイラ対応

C++98 から使えます。構造化束縛は C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 2 つの値をまとめる型
    - [x] 取り出しは構造化束縛 `auto [a, b]`
    - [x] 意味があるなら構造体

## 関連ページ

- [cpprefjp: std::pair](https://cpprefjp.github.io/reference/utility/pair.html)
- [cppreference: std::pair](https://en.cppreference.com/w/cpp/utility/pair)
