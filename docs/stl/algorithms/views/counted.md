---
title: std::views::counted
summary: "先頭の位置と個数から、範囲を作る。"
order: 19
group: ビュー（std::views）
tags:
  - アルゴリズム
---

# std::views::counted

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

先頭のイテレータと個数から、その範囲だけを見るビューを作りたい。`std::views::counted(it, n)` は、`it` から `n` 個の要素を、1 つの範囲として扱います。`vector` の途中から数個、生のポインターから数個、といった指定が簡単にできます。

!!! tip "ポイント"
    - `counted(開始, 個数)` で、その範囲のビューを作る
    - 連続したイテレータ（ポインターなど）なら `std::span` になる
    - それ以外は `subrange` や `counted_iterator` の組になる
    - 個数が実際の範囲を超えると未定義動作

!!! info "このページを読む前に"
    [ビュー](../views.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::views::counted {#counted}

<span class="ver ver-20">C++20</span>

```cpp
inline constexpr /* 未規定 */ counted = /* 未規定 */;
// views::counted(it, n)
```

戻り値の型は、イテレータの種類で変わります。

| イテレータ | 戻り値 |
| --- | --- |
| 連続（ポインター、`vector` のイテレータ） | `std::span<要素, std::dynamic_extent>` |
| ランダム アクセス | `subrange<It>` |
| それ以外 | `subrange<counted_iterator<It>, default_sentinel_t>` |

`take(n)` との違いは、`take` が範囲に対するアダプターなのに対し、`counted` はイテレータと個数から作る点です。C の API が返した、ポインターと個数の組を、範囲として扱うときに便利です。

個数が範囲を超えるかは、検査されません。

## 実際に動かしてみる

```cpp
#include <print>
#include <ranges>
#include <vector>

int main() {
  const std::vector<int> v = {10, 20, 30, 40, 50};

  // 2 番目から 3 個
  auto part = std::views::counted(v.begin() + 1, 3);
  std::println("個数: {}", part.size());
  for (int x : part) std::println("{}", x);

  // 生のポインターと個数から
  const int raw[] = {1, 2, 3, 4};
  std::println("{}", std::views::counted(raw, 2).size());
}
```

```text title="実行結果"
個数: 3
20
30
40
2
```

## ゲームでの使いどころ

C の API が返した「ポインターと個数」を、範囲として扱うときに使います。

## よくあるミス

??? failure "個数が範囲を超える"
    検査されず、未定義動作です。

## 類似

| 名前 | 違い |
| --- | --- |
| `views::take` | 範囲の先頭から n 個 |
| [`subrange`](subrange.md) | イテレータの組 |
| [`all`](all.md) | 範囲全体のビュー |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::ranges::counted_view](https://cpprefjp.github.io/reference/ranges/counted_view.html)
- [cppreference: std::ranges::counted_view](https://en.cppreference.com/w/cpp/ranges/counted_view)
