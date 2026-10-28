---
title: std::tuple
summary: "3 つ以上の値を、型がバラバラのまま 1 つにまとめる。"
order: 49
tags:
  - ユーティリティ
---

# std::tuple

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="perf perf-4">◎ 速い</span>
<span class="ver ver-11">C++11</span>
`#include <tuple>`
</div>

関数から 3 つ以上の値を返したい。`pair` は 2 つしか入りません。構造体を新しく作るのは大げさで、`out` 引数を増やすのは読みにくくなります。`std::tuple` は、いくつでも、型がバラバラの値をひとまとめにする型です。`pair` の仲間で、3 つ以上でも使えます。構造化束縛 `auto [a, b, c] = t;` で、中身に名前を付けて取り出せます。

!!! tip "ポイント"
    - **3 つ以上の値を返す**なら tuple。ただし意味のある組なら、名前付きの構造体のほうが読みやすい。
    - 取り出しは構造化束縛 `auto [a, b, c] = t;` か [`std::get`](get.md)。
    - 複数の条件で比べる比較関数には [`std::tie`](tie.md)。

!!! info "このページを読む前に"
    [`std::pair`](pair.md) を先に読んでください。`tuple` は、その 3 つ以上の版です。

## 宣言

```cpp
template <class... Types>
class tuple;
```

| テンプレート引数 | 意味 |
| --- | --- |
| `Types...` | 入れる型を何個でも |

## 関数の詳しい説明

### 構造化束縛 <span class="ver ver-17">C++17</span> {#structured-binding data-toc-label="構造化束縛"}

```cpp
auto [a, b] = pair_or_tuple;        // コピー
auto& [a, b] = pair_or_tuple;       // 参照（書き換えると元も変わる）
const auto& [a, b] = pair_or_tuple; // 読むだけ
```

- 中身を順番に名前を付けた変数として取り出します。**名前の数と要素数は同じ**である必要があります
- pair / tuple のほか、構造体や配列にも使えます

```cpp
#include <print>
#include <tuple>

int main() {
  std::tuple<int, float, char> data = {1, 2.5f, 'x'};
  auto& [id, value, tag] = data;
  value *= 2.0f;  // 参照なので data も変わる
  std::println("{} {} {}", id, std::get<1>(data), tag);
}
```

```text title="実行結果"
1 5 x
```

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

## よくある使い方

### 作って、取り出す

```cpp
#include <print>
#include <string>
#include <tuple>

int main() {
  std::tuple<int, std::string, float> enemy = {1, "スライム", 1.5f};

  auto [id, name, speed] = enemy;  // 構造化束縛で取り出す
  std::println("{} {} {}", id, name, speed);
  std::println("{}", std::tuple_size_v<decltype(enemy)>);
}
```

```text title="実行結果"
1 スライム 1.5
3
```

### swap {#swap}

```cpp
void swap(tuple& other);
```

- 計算量: 要素数に比例

2 つのタプルの要素を 1 つずつ入れ替えます。

### operator= {#op_assign}

```cpp
tuple& operator=(const tuple& other);
tuple& operator=(tuple&& other);
```

- 計算量: 要素数に比例

要素ごとに代入します。`pair` や、型が変換できるタプルからも代入できます。

### operator== {#op_eq}

```cpp
template <class... T, class... U>
bool operator==(const tuple<T...>& lhs, const tuple<U...>& rhs);
```

- 計算量: 要素数に比例

全ての要素が順に等しければ `true`。

### operator<=> <span class="ver ver-20">C++20</span> {#op_cmp data-toc-label="operator<=>"}

```cpp
template <class... T, class... U>
auto operator<=>(const tuple<T...>& lhs, const tuple<U...>& rhs);
```

- 計算量: 要素数に比例

要素を先頭から順に比べる、辞書順の三方比較。

## ゲームでの使いどころ

関数が複数の値を返すときに使います。ただし、意味のある組なら、名前付きのメンバーを持つ構造体のほうが、ずっと読みやすくなります。`get<0>` では、何が入っているかが分かりません。

テンプレートの内部では、引数の並びをまとめて扱うのに使います。可変長テンプレートの引数をまとめて保存し、あとで `std::apply` で呼び出す、といった使い方です。

複数の条件での比較には、`std::tie` を使います。`tuple` の比較は、先頭の要素から順に行われます。

## よくあるミス

??? failure "要素が増えて読めなくなる"
    4 個以上になったら、構造体にします。`std::get<3>` では何の値か分かりません。

??? failure "意味のある組を `tuple` で表して、読みにくくなる"
    `std::get<2>(t)` が何だったのかを後から思い出せなくなります。3 つ以上の意味のある組は、構造体にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::pair`](pair.md) | 2 つだけ |
| 構造体 | 名前を付けられる |
| [`std::variant`](variant.md) | 複数の型のうちどれか 1 つ（tuple は全部持つ） |

## コンパイラ対応

C++11 から使えます。構造化束縛は C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 型がバラバラの値をいくつでもまとめる
    - [x] 取り出しは構造化束縛か `std::get`
    - [x] 4 個以上なら構造体

## 関連ページ

- [cpprefjp: std::tuple](https://cpprefjp.github.io/reference/tuple/tuple.html)
- [cppreference: std::tuple](https://en.cppreference.com/w/cpp/utility/tuple)
