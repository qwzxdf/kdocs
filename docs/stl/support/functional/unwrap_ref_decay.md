---
title: std::unwrap_ref_decay
summary: "decay してから、reference_wrapper を参照に戻す型変換。"
order: 900
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::unwrap_ref_decay

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <functional>`
</div>

`std::make_pair(a, b)` は、引数をコピーして `pair` に保存します。ただし、`std::ref(x)` で包んだ引数だけは、参照として保存したい。さらに、配列は先頭のポインターに、`const` は除いて保存したい。この「`reference_wrapper` なら参照に、それ以外は `decay` した型にする」型変換が `std::unwrap_ref_decay<T>` です。

!!! tip "ポイント"
    - `reference_wrapper<U>` なら `U&`、それ以外は `decay_t<T>`
    - `make_pair`・`make_tuple`・`thread` などが、値を保存する型を決めるのに使う
    - `unwrap_reference` との違いは、`decay` をするかどうか
    - C++20 で追加された

!!! info "このページを読む前に"
    [`<functional>`](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::unwrap_ref_decay {#unwrap_ref_decay}

<span class="ver ver-20">C++20</span>

```cpp
template <class T> struct unwrap_ref_decay;
template <class T> using unwrap_ref_decay_t = typename unwrap_ref_decay<T>::type;
```

`T` を `std::decay_t` に通した型が `std::reference_wrapper<U>` なら `U&`、そうでなければ `std::decay_t<T>` です。

`decay` は、参照を外し、`const` を除き、配列を先頭へのポインターに、関数を関数ポインターに変えます。値渡しの引数が受け取るときの変換と、同じです。`int[3]` は `int*` に、`const int&` は `int` になります。

`reference_wrapper` だけは例外で、`decay` したあとに参照へ戻します。`std::ref(x)` で包んだものは、コピーされず、`x` への参照として保存されます。

`std::make_pair(std::ref(x), 1)` の戻り値が `pair<int&, int>` になるのは、この型変換のおかげです。

## 実際に動かしてみる

```cpp
#include <functional>
#include <print>
#include <type_traits>
#include <utility>

int main() {
  static_assert(std::is_same_v<std::unwrap_ref_decay_t<int>, int>);
  static_assert(std::is_same_v<std::unwrap_ref_decay_t<const int&>, int>);   // 参照と const を除く
  static_assert(std::is_same_v<std::unwrap_ref_decay_t<int[3]>, int*>);      // 配列はポインターに
  static_assert(std::is_same_v<std::unwrap_ref_decay_t<std::reference_wrapper<int>>, int&>);

  // make_pair は、ref で包んだものだけを参照として保存する
  int hp = 10;
  auto p = std::make_pair(std::ref(hp), 1);
  p.first += 5;   // hp が書き換わる
  std::println("hp = {}", hp);

  static_assert(std::is_same_v<decltype(p), std::pair<int&, int>>);
}
```

```text title="実行結果"
hp = 15
```

## ゲームでの使いどころ

`make_pair`・`make_tuple` のような関数や、引数をコピーして保存する自作のラッパーで、保存する型を決めるときに使います。

## よくあるミス

??? failure "reference_wrapper を渡したつもりで普通の変数を渡す"
    `std::ref` で包まないと、コピーが保存されます。元の変数は変わりません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`unwrap_reference`](unwrap_reference.md) | `decay` をしない版 |
| [`reference_wrapper`](reference_wrapper.md) | 参照を持ち運ぶ型 |
| [`ref`](ref.md) | `reference_wrapper` を作る |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::unwrap_ref_decay](https://cpprefjp.github.io/reference/functional/unwrap_ref_decay.html)
- [cppreference: std::unwrap_ref_decay](https://en.cppreference.com/w/cpp/utility/functional/unwrap_ref_decay)
