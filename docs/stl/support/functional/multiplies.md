---
title: std::multiplies
summary: "掛け算をする関数オブジェクト（`*` の代わり）。"
order: 5
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::multiplies

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <functional>`
</div>

`std::multiplies<T>` は、**掛け算 `a * b` を関数オブジェクトとして使えるようにしたもの**です。積を取る `fold_left`、要素ごとの掛け算（`transform`）に渡します。

!!! tip "ポイント"
    - `std::ranges::fold_left(v, 1, std::multiplies{})` で積。
    - 初期値は 1（0 だと全部 0）。

!!! info "このページを読む前に"
    [`<functional>`](../functional.md) の概要を先に読むと分かりやすいです。[ラムダ式](../../../basics/lambda.md) も関係します。

## 関数の詳しい説明

### std::multiplies {#multiplies}

```cpp
template <class T = void>
struct multiplies;  // a * b
```

- `a * b`。ほかに `minus`、`divides`、`modulus`、`negate`、`logical_and` / `logical_or` / `logical_not`、`bit_and` / `bit_or` / `bit_xor`、`not_equal_to`、`greater_equal`、`less_equal` があります

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <functional>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3, 4};
  std::println("{} {}", std::multiplies{}(2, 3), std::ranges::fold_left(v, 1, std::multiplies{}));
}
```

```text title="実行結果"
6 24
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 倍率の積を取る | `fold_left(rates, 1.0f, std::multiplies{})` |

## よくあるミス

??? failure "初期値を 0 にする"
    積の初期値は 1 です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`plus`](plus.md) | 足し算 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `*` を関数オブジェクトにしたもの
    - [x] 積の初期値は 1
    - [x] fold に渡す

## 関連ページ

- [cpprefjp: std::multiplies](https://cpprefjp.github.io/reference/functional/multiplies.html)
- [cppreference: std::multiplies](https://en.cppreference.com/w/cpp/utility/functional/multiplies)
