---
title: std::make_index_sequence
summary: "0 から N-1 までの index_sequence を作る。"
order: 900
tags:
  - ユーティリティ
---

# std::make_index_sequence

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-14">C++14</span>
`#include <utility>`
</div>

`index_sequence<0, 1, 2, 3>` を手で書くのは大変です。`make_index_sequence<4>` と書けば、同じ型が作られます。タプルやパックの展開に使う番号列を作るときの入り口です。

!!! tip "ポイント"
    - `make_index_sequence<N>` は `index_sequence<0, 1, ..., N-1>`。
    - N が 0 なら空の列。
    - `N` は定数式でなければならない。

!!! info "このページを読む前に"
    [テンプレート](../../basics/template.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::make_index_sequence {#make_index_sequence}

```cpp
template <size_t N>
using make_index_sequence = make_integer_sequence<size_t, N>;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `N` | size_t | 番号の個数 |

- 戻り値: `index_sequence<0, ..., N-1>`
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <array>
#include <print>
#include <utility>

template <size_t... Is>
auto ToArray(std::index_sequence<Is...>) {
  return std::array<size_t, sizeof...(Is)>{Is...};
}

int main() {
  std::println("{}", ToArray(std::make_index_sequence<4>{}));
}
```

```text title="実行結果"
[0, 1, 2, 3]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| タプルのサイズぶんの番号列を作る | `std::make_index_sequence<std::tuple_size_v<T>>{}` |

## よくあるミス

??? failure "N を実行時の値にする"
    N はコンパイル時の定数です。実行時に決まる回数のループには使えません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`index_sequence`](index_sequence.md) | 番号の並びの型 |
| [`index_sequence_for`](index_sequence_for.md) | 型のパックの個数ぶん |

## コンパイラ対応

C++14 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 0〜N-1 の番号列を作る
    - [x] N はコンパイル時の定数
    - [x] タプル展開の入り口

## 関連ページ

- [cpprefjp: std::make_index_sequence](https://cpprefjp.github.io/reference/utility/make_index_sequence.html)
- [cppreference: std::make_index_sequence](https://en.cppreference.com/w/cpp/utility/integer_sequence)
