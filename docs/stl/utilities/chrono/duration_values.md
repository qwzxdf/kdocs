---
title: std::chrono::duration_values
summary: "duration の rep について、0・最小・最大を返す。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::duration_values

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <chrono>`
</div>

`duration::zero()`、`min()`、`max()` の中身は、`rep` 型の 0・最小・最大です。それを決めているのが `duration_values<Rep>` で、自作の数値型を `rep` にするときに、特殊化して値を教えます。

!!! tip "ポイント"
    - `zero()` / `min()` / `max()` の 3 つの静的関数をもつ。
    - 普通は直接使わず、`duration::zero()` などを使う。

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要と [`duration`](duration.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::duration_values {#duration_values}

```cpp
template <class Rep>
struct duration_values {
  static constexpr Rep zero() noexcept;
  static constexpr Rep min() noexcept;
  static constexpr Rep max() noexcept;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `Rep` | 型 | 対象の数値型 |

- 戻り値: `rep` の 0・最小・最大
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using V = std::chrono::duration_values<int>;
  std::println("{} {}", V::zero(), V::max());
}
```

```text title="実行結果"
0 2147483647
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 自作の数値型を duration の rep にする | `duration_values<MyNum>` を特殊化する |

## よくあるミス

??? failure "min() を 0 に近い値だと思う"
    `min()` は**最小の（最も小さい）値**で、0 に近い正の値ではありません。整数なら負の最小値です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`duration`](duration.md) | 時間の長さ |
| [`treat_as_floating_point`](treat_as_floating_point.md) | rep が小数かの特性 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] rep の 0・最小・最大
    - [x] duration::zero() などの元
    - [x] 自作 rep では特殊化

## 関連ページ

- [cpprefjp: std::chrono::duration_values](https://cpprefjp.github.io/reference/chrono/duration_values.html)
- [cppreference: std::chrono::duration_values](https://en.cppreference.com/w/cpp/chrono/duration_values)
