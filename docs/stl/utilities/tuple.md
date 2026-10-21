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

`std::tuple` は、**いくつでも、型がバラバラの値をひとまとめにする型**です。[`std::pair`](pair.md) の仲間で、3 つ以上でも使えます。関数が複数の値を返したり、テンプレートで引数の並びをまとめて扱ったりするときに使います。

!!! tip "ポイント"
    - **3 つ以上の値を返す**なら tuple。ただし意味のある組なら、名前付きの構造体のほうが読みやすい。
    - 取り出しは構造化束縛 `auto [a, b, c] = t;` か [`std::get`](get.md)。
    - 複数の条件で比べる比較関数には [`std::tie`](tie.md)。

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

- 中身を順番に、名前を付けた変数として取り出します。**名前の数と要素数は同じ**である必要があります
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

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| (ID, 名前, HP) を一時的にまとめる | `std::tuple<int, std::string, int>` |
| 可変引数テンプレートで、引数をまとめて保存する | `std::tuple<Args...>` と [`apply`](apply.md) |

## よくあるミス

??? failure "要素が増えて読めなくなる"
    4 個以上になったら、構造体にします。`std::get<3>` では何の値か分かりません。

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
    - [x] 型がバラバラの値を、いくつでもまとめる
    - [x] 取り出しは構造化束縛か `std::get`
    - [x] 4 個以上なら構造体

## 関連ページ

- [cpprefjp: std::tuple](https://cpprefjp.github.io/reference/tuple/tuple.html)
- [cppreference: std::tuple](https://en.cppreference.com/w/cpp/utility/tuple)
