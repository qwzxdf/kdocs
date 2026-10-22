---
title: std::index_sequence
summary: "0, 1, 2, … の番号の並びを、型で表す。"
order: 900
tags:
  - ユーティリティ
---

# std::index_sequence

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-14">C++14</span>
`#include <utility>`
</div>

タプルの要素を順番に取り出したいとき、`get<0>`、`get<1>`… と手で書くのは要素数が変わると破綻します。`index_sequence<0, 1, 2>` は、番号の並びを**テンプレート引数のパック**として持ち運べる型で、`get<I>(t)...` のように展開できます。

!!! tip "ポイント"
    - `std::index_sequence<I...>` は `integer_sequence<size_t, I...>` の別名。
    - 番号の並びは [`make_index_sequence`](make_index_sequence.md) で作る。
    - 関数の引数に `std::index_sequence<I...>` を受けて、パックとして展開する。

!!! info "このページを読む前に"
    [テンプレート](../../basics/template.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::index_sequence {#index_sequence}

```cpp
template <size_t... Is>
using index_sequence = integer_sequence<size_t, Is...>;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `Is...` | size_t のパック | 番号の並び |

- 戻り値: 型（値は持たない）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <print>
#include <tuple>
#include <utility>

template <class T, size_t... Is>
void PrintAll(const T& t, std::index_sequence<Is...>) {
  (std::println("{}", std::get<Is>(t)), ...);
}

int main() {
  std::tuple<int, double, const char*> t{1, 2.5, "abc"};
  PrintAll(t, std::make_index_sequence<3>{});
}
```

```text title="実行結果"
1
2.5
abc
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| タプルの全要素に同じ処理をする | `((f(std::get<I>(t))), ...);` を `index_sequence<I...>` の関数に書く |

## よくあるミス

??? failure "size_t 以外の番号にしたい"
    `index_sequence` は `size_t` 固定です。別の整数型なら [`integer_sequence`](integer_sequence.md) を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`integer_sequence`](integer_sequence.md) | 整数型を選べる |
| [`make_index_sequence`](make_index_sequence.md) | 0〜N-1 を作る |

## コンパイラ対応

C++14 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 番号の並びを型として持つ
    - [x] パックとして展開して使う
    - [x] 作るのは make_index_sequence

## 関連ページ

- [cpprefjp: std::index_sequence](https://cpprefjp.github.io/reference/utility/index_sequence.html)
- [cppreference: std::index_sequence](https://en.cppreference.com/w/cpp/utility/integer_sequence)
