---
title: std::cmp_equal
summary: "符号の違う整数どうしを、正しく比べる（等しいか）。"
order: 3
group: 小さな便利機能（<utility>）
tags:
  - 型・言語サポート
---

# std::cmp_equal

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <utility>`
</div>

`std::cmp_equal(a, b)` は、**符号つきと符号なしの整数どうしでも、数学的に正しく `a == b` を判定する**関数です。`-1 == 0xFFFFFFFFu` が `true` になる事故を防ぎます。

!!! tip "ポイント"
    - `cmp_not_equal`、`cmp_less_equal` などの仲間がある。
    - C++20 の機能。

!!! info "このページを読む前に"
    [小さな便利機能](utility-misc.md) の概要と合わせて読むと分かりやすいです。

## 関数の詳しい説明

### std::cmp_equal {#cmp_equal}

<span class="ver ver-20">C++20</span>

```cpp
template <class T, class U>
constexpr bool cmp_equal(T t, U u) noexcept;
```

- 符号の違う整数を正しく `==` で比べます（`-1 == 0xFFFFFFFFu` は普通の `==` だと true になる）

## 実際に動かしてみる

```cpp
#include <print>
#include <utility>

int main() {
  // 普通の == は、-1 が巨大な符号なしの値に変換されて true になる
  std::println("{} {}", static_cast<unsigned>(-1) == 4294967295u, std::cmp_equal(-1, 4294967295u));
}
```

```text title="実行結果"
true false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ID（符号なし）と int の比較 | `std::cmp_equal(id, other)` |

## よくあるミス

??? failure "符号の混ざった == を放置する"
    予期しない `true` になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`cmp_less`](cmp_less.md) | 小さいか |

## コンパイラ対応

C++17〜C++23 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 符号の混ざった等値を正しく
    - [x] `cmp_less` の仲間
    - [x] C++20

## 関連ページ

- [cpprefjp: std::cmp_equal](https://cpprefjp.github.io/reference/utility/cmp_equal.html)
- [cppreference: std::cmp_equal](https://en.cppreference.com/w/cpp/utility/cmp_equal)
