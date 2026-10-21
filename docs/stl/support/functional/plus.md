---
title: std::plus
summary: "足し算をする関数オブジェクト（`+` の代わり）。"
order: 4
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::plus

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <functional>`
</div>

`std::plus<T>` は、**足し算 `a + b` を関数オブジェクトとして使えるようにしたもの**です。`std::accumulate` や `fold_left` に渡して、合計を取るときに使います。引き算の `minus`、`multiplies`、`divides`、`modulus`、`negate` も同じ仲間です。

!!! tip "ポイント"
    - `std::ranges::fold_left(v, 0, std::plus{})` で合計。
    - 掛け算は [`multiplies`](multiplies.md)。
    - ラムダ式 `[](auto a, auto b) { return a + b; }` と同じ。

!!! info "このページを読む前に"
    [`<functional>`](../functional.md) の概要を先に読むと分かりやすいです。[ラムダ式](../../../basics/lambda.md) も関係します。

## 関数の詳しい説明

### std::plus {#plus}

```cpp
template <class T = void>
struct plus;  // a + b
```

- `a + b`。[`std::ranges::fold_left`](../../algorithms/fold_left.md#fold_left) に合計の方法として渡します

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <functional>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3, 4};
  std::println("{} {}", std::plus{}(2, 3), std::ranges::fold_left(v, 0, std::plus{}));
}
```

```text title="実行結果"
5 10
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 合計を取る | `fold_left(v, 0, std::plus{})` |

## よくあるミス

??? failure "型を省略しないと型が固定される"
    `std::plus<int>` は `int` 固定です。`std::plus<>` なら型を推論します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`multiplies`](multiplies.md) | 掛け算 |
| [`std::ranges::fold_left`](../../algorithms/fold_left.md) | 合計の関数 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `+` を関数オブジェクトにしたもの
    - [x] fold に渡して合計
    - [x] `std::plus<>` が楽

## 関連ページ

- [cpprefjp: std::plus](https://cpprefjp.github.io/reference/functional/plus.html)
- [cppreference: std::plus](https://en.cppreference.com/w/cpp/utility/functional/plus)
