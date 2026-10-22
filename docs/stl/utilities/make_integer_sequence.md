---
title: std::make_integer_sequence
summary: "0 から N-1 までの integer_sequence を、整数型を選んで作る。"
order: 900
tags:
  - ユーティリティ
---

# std::make_integer_sequence

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-14">C++14</span>
`#include <utility>`
</div>

`make_index_sequence` は番号の型が `size_t` 固定です。`int` や `unsigned` の番号が欲しいときは、`make_integer_sequence<T, N>` で整数型を指定します。

!!! tip "ポイント"
    - `make_integer_sequence<int, 4>` は `integer_sequence<int, 0, 1, 2, 3>`。
    - `size_t` なら [`make_index_sequence`](make_index_sequence.md) と同じ。

!!! info "このページを読む前に"
    [テンプレート](../../basics/template.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::make_integer_sequence {#make_integer_sequence}

```cpp
template <class T, T N>
using make_integer_sequence = integer_sequence<T, /* 0, 1, ..., N-1 */>;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 整数型 | 番号の型 |
| `N` | T | 番号の個数 |

- 戻り値: `integer_sequence<T, 0, ..., N-1>`
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <array>
#include <print>
#include <utility>

template <int... Is>
auto ToArray(std::integer_sequence<int, Is...>) {
  return std::array<int, sizeof...(Is)>{Is...};
}

int main() {
  std::println("{}", ToArray(std::make_integer_sequence<int, 4>{}));
}
```

```text title="実行結果"
[0, 1, 2, 3]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| int の番号列で配列を初期化する | `std::make_integer_sequence<int, 4>{}` |

## よくあるミス

??? failure "負の N を指定する"
    N は 0 以上の値です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`make_index_sequence`](make_index_sequence.md) | size_t 版 |
| [`integer_sequence`](integer_sequence.md) | 並びの型 |

## コンパイラ対応

C++14 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 整数型を選べる番号列
    - [x] size_t なら make_index_sequence
    - [x] N はコンパイル時の定数

## 関連ページ

- [cpprefjp: std::make_integer_sequence](https://cpprefjp.github.io/reference/utility/make_integer_sequence.html)
- [cppreference: std::make_integer_sequence](https://en.cppreference.com/w/cpp/utility/integer_sequence)
