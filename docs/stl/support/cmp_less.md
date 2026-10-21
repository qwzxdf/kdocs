---
title: std::cmp_less
summary: "符号の違う整数どうしを、正しく比べる（小さいか）。"
order: 2
group: 小さな便利機能（<utility>）
tags:
  - 型・言語サポート
---

# std::cmp_less

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <utility>`
</div>

`std::cmp_less(a, b)` は、**符号つきと符号なしの整数どうしでも、数学的に正しく `a < b` を判定する**関数です。普通の `<` は、符号つきを符号なしに変換して比べるので、`-1 < 1u` が `false` になる事故が起きます。仲間に `cmp_equal`、`cmp_greater` などがあります。

!!! tip "ポイント"
    - `-1 < 1u` は `false`（-1 が巨大な値になる）。`std::cmp_less(-1, 1u)` は `true`。
    - `size()`（符号なし）と `int` の比較に便利。
    - C++20 の機能。

!!! info "このページを読む前に"
    [小さな便利機能](utility-misc.md) の概要と合わせて読むと分かりやすいです。

## 関数の詳しい説明

### std::cmp_less {#cmp_less}

<span class="ver ver-20">C++20</span>

```cpp
template <class T, class U>
constexpr bool cmp_less(T t, U u) noexcept;
```

- 符号付きと符号なしの整数を、**数学的に正しく**比べます。普通の `<` では、`-1 < 3u` が false になります（-1 が巨大な符号なし数に変換されるため）
- ほかに `cmp_greater`、`cmp_less_equal`、`cmp_greater_equal`、`cmp_not_equal` があります

```cpp
#include <print>
#include <utility>
#include <vector>

int main() {
  int index = -1;
  std::vector<int> v = {1, 2, 3};
  std::println("< の結果: {}", index < static_cast<long long>(v.size()));
  std::println("普通の比較だと -1 < 3u は {}", -1 < 3u);  // 警告も出る
  std::println("cmp_less(-1, 3u) は {}", std::cmp_less(index, v.size()));
}
```

```text title="実行結果"
< の結果: true
普通の比較だと -1 < 3u は false
cmp_less(-1, 3u) は true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| `int i` と `v.size()` を比べる | `std::cmp_less(i, v.size())` |

## よくあるミス

??? failure "符号の混ざった比較で警告を無視する"
    `-Wsign-compare` の警告は、本当にバグです。`cmp_less` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`cmp_equal`](cmp_equal.md) | 等しいか |
| [`in_range`](in_range.md) | 範囲に収まるか |

## コンパイラ対応

C++17〜C++23 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 符号の混ざった整数を正しく比べる
    - [x] `-1 < 1u` の事故を防ぐ
    - [x] C++20

## 関連ページ

- [cpprefjp: std::cmp_less](https://cpprefjp.github.io/reference/utility/cmp_less.html)
- [cppreference: std::cmp_less](https://en.cppreference.com/w/cpp/utility/cmp_less)
