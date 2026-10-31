---
title: std::is_bind_expression
summary: "型が bind の式かどうかを調べる型特性。"
order: 900
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::is_bind_expression

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <functional>`
</div>

`std::bind` の引数に、別の `bind` の式を入れると、それが「入れ子の式」として扱われ、呼び出し時に先に評価されて、その結果が外側の引数に入ります。この「`bind` の式かどうか」の判定に使われるのが `std::is_bind_expression<T>` です。`T` が `bind` の戻り値の型なら `true`、そうでなければ `false` です。

!!! tip "ポイント"
    - `is_bind_expression<T>::value` は、`T` が `bind` の戻り値の型なら `true`
    - `std::is_bind_expression_v<T>` が短縮形（C++17）
    - 入れ子の `bind` は、外側を呼ぶときに先に評価される
    - 自作の型を `bind` の式として扱わせたいときに特殊化する

!!! info "このページを読む前に"
    [`bind`](bind.md) を先に読んでください。

## 関数の詳しい説明

### std::is_bind_expression {#is_bind_expression}

```cpp
template <class T>
struct is_bind_expression;

template <class T>
inline constexpr bool is_bind_expression_v = is_bind_expression<T>::value;   // C++17
```

`std::bind` の戻り値の型に対して `true`、それ以外（`int` やラムダなど）には `false` です。

この判定が重要になるのは、`bind` の入れ子のときです。

```cpp
auto outer = std::bind(Add, std::bind(Twice, _1), 1);
outer(5);   // Add(Twice(5), 1) = 11
```

`bind(Twice, _1)` は `bind` の式なので、外側の `outer(5)` を呼んだときに、`5` を渡して先に評価されます。その結果の `10` が、`Add` の第 1 引数に入ります。式でなければ、`bind(Twice, _1)` というオブジェクトそのものが、`Add` に渡されるだけです。

自作の関数オブジェクトの型を、`bind` の式として扱わせたいときは、`std::is_bind_expression` を特殊化して `true` にします。稀な使い方ですが、`bind` の入れ子の仕組みの正体が、この型特性です。

## 実際に動かしてみる

```cpp
#include <functional>
#include <print>

int Twice(int x) { return x * 2; }
int Add(int a, int b) { return a + b; }

int main() {
  using namespace std::placeholders;

  auto inner = std::bind(Twice, _1);
  auto lambda = [](int x) { return x; };

  std::println("bind の式: {}", std::is_bind_expression_v<decltype(inner)>);
  std::println("ラムダ: {}", std::is_bind_expression_v<decltype(lambda)>);
  std::println("int: {}", std::is_bind_expression_v<int>);

  // 入れ子の bind: 内側が先に評価される
  auto outer = std::bind(Add, std::bind(Twice, _1), 1);
  std::println("outer(5) = {}", outer(5));   // Add(Twice(5), 1) = 11
}
```

```text title="実行結果"
bind の式: true
ラムダ: false
int: false
outer(5) = 11
```

## ゲームでの使いどころ

`bind` を前提にした古いコードを読むときに、入れ子の `bind` がどう評価されるかを理解する助けになります。

## よくあるミス

??? failure "bind の結果を、入れ子のつもりでない所に渡す"
    `bind` の式を、別の `bind` の引数に渡すと、意図せず先に評価されます。そのまま渡したいときは、`std::ref` などで包みます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`bind`](bind.md) | 使う関数 |
| [`is_placeholder`](is_placeholder.md) | 印かどうかを調べる |
| [`placeholders`](placeholders.md) | 印そのもの |

## コンパイラ対応

C++11 から使えます。`is_bind_expression_v` は C++17 からです。

## 関連ページ

- [cpprefjp: std::is_bind_expression](https://cpprefjp.github.io/reference/functional/is_bind_expression.html)
- [cppreference: std::is_bind_expression](https://en.cppreference.com/w/cpp/utility/functional/is_bind_expression)
