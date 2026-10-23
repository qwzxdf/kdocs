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

関数から 2 つの値を返したい。ただし、そのためだけに構造体を作るのも大げさだ。そんなときに使うのが、`std::pair` です。2 つの値を 1 つにまとめた型で、`first` と `second` で取り出せます。`std::map` の要素（キーと値）も `pair` です。C++17 の構造化束縛 `auto [a, b] = p;` を使うと、中身に名前を付けて取り出せます。

!!! tip "ポイント"
    - <strong>関数から 2 つの値を返すとき、`map` の要素を扱うときに使う。</strong>
    - 取り出すのは構造化束縛 `auto [x, y] = pair;` が一番読みやすい。
    - 意味のある組なら、**名前付きのメンバを持つ構造体のほうが読みやすい**（`first` / `second` では何か分からない）。
    - `<` や `==` は 1 つ目から順に比べる。複数の条件での並べ替えにも使える。

!!! info "このページを読む前に"
    構造体の基本と、[`std::map`](../containers/map.md) の要素が `pair` であることを知っておくと、読みやすいです。

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

`map` を回すときに、一番よく出てきます。`for (const auto& [name, hp] : stats)` と書くと、`pair` が構造化束縛で展開され、キーと値に名前が付きます。

関数が 2 つの値を返すときにも使います。成功したかと値を一緒に返す、位置と半径を返す、といった小さな組です。ただし、意味のある組なら、名前付きのメンバーを持つ構造体にしたほうが、`first`、`second` よりずっと読みやすくなります。

`pair` の比較は、1 つ目の要素から順に行われるため、「スコアと名前」の組を `sort` すると、スコア順（同点なら名前順）に並べられます。この性質は、手軽な複数条件の並べ替えに使えます。

## よくあるミス

??? failure "`first` と `second` の意味を忘れる"
    数日後に `p.first` が何だったかを思い出せなくなります。関数の戻り値など、境界になるところでは、名前付きの構造体を使います。

??? failure "`map` を回すときに、コピーしてしまう"
    `for (auto kv : m)` は、要素の `pair` をコピーします。`for (const auto& kv : m)` と、参照で受けます。キーが const であることも、`pair<const Key, Value>` として表れます。

??? failure "`make_pair` で型を指定しようとする"
    C++17 以降は、`std::pair p(1, 2.0);` とクラステンプレートの推論が使えます。`make_pair` は必須ではありません。

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
    - [x] 2 つの値をまとめる。取り出しは構造化束縛が読みやすい。
    - [x] 意味のある組は、名前付きの構造体にする。
    - [x] `map` を回すときは `const auto&` で受ける。

## 関連ページ

- [cpprefjp: std::pair](https://cpprefjp.github.io/reference/utility/pair.html)
- [cppreference: std::pair](https://en.cppreference.com/w/cpp/utility/pair)
