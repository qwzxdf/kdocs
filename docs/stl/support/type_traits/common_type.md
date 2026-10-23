---
title: std::common_type
summary: "複数の型に共通する型（どちらにも変換できる型）を調べる。"
order: 18
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::common_type

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <type_traits>`
</div>

2 つの異なる型の値を混ぜて計算するとき、結果はどの型になるでしょうか。`int` と `double` を足すと `double` です。この「共通の型」を型として取り出したいときに使うのが `std::common_type` です。`std::gcd` や `std::min` のようなテンプレートの戻り値の型を決めるときに使われます。

!!! tip "ポイント"
    - `std::common_type_t<int, double>` は `double`
    - 三項演算子 `cond ? a : b` の結果の型と同じ規則
    - 引数は 1 個以上いくつでも渡せる
    - 共通の型がなければ、エラー

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::common_type_t {#common_type}

<span class="ver ver-11">C++11</span>

```cpp
template <class... T>
using common_type_t = typename common_type<T...>::type;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T...` | 型の並び | 共通の型を求めたい型 |

`common_type_t<A, B>` は、`A` と `B` の値を混ぜて計算したときの共通の型です。算術型なら、通常の算術変換と同じ結果です。`int` と `long` なら `long`、`char` と `short` なら `int`、`int` と `double` なら `double` です。

3 つ以上の型は、左から順に 2 つずつ共通の型を求めます。共通の型が存在しない組み合わせは、型が存在せず、エラーになります。

`decay` された型を返す点に注意します。参照や `const` は外れます。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("int, double  -> double : {}", std::is_same_v<std::common_type_t<int, double>, double>);
  std::println("int, long    -> long   : {}", std::is_same_v<std::common_type_t<int, long>, long>);
  std::println("char, short  -> int    : {}", std::is_same_v<std::common_type_t<char, short>, int>);
}
```

```text title="実行結果"
int, double  -> double : true
int, long    -> long   : true
char, short  -> int    : true
```

## ゲームでの使いどころ

2 つの型を受け取る汎用の関数で、戻り値の型を決めます。

```cpp
template <class A, class B>
std::common_type_t<A, B> Max(A a, B b) {
  return a > b ? a : b;   // 共通の型で返す
}
```

## よくあるミス

??? failure "参照や `const` が残ると思う"
    `decay` された型が返ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`conditional`](conditional.md) | 条件で型を選ぶ |
| [`decay`](decay.md) | 型の変換 |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `common_type_t<A, B...>` は共通の型
    - [x] 算術型は通常の算術変換と同じ
    - [x] 参照や `const` は外れる

## 関連ページ

- [cpprefjp: std::common_type](https://cpprefjp.github.io/reference/type_traits/common_type.html)
- [cppreference: std::common_type](https://en.cppreference.com/w/cpp/types/common_type)
