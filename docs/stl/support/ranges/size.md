---
title: std::ranges::size
summary: "範囲の要素数を取る。"
order: 3
group: ranges の基本部品
tags:
  - 型・言語サポート
---

# std::ranges::size

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

`std::ranges::size(r)` は、**範囲の要素数を取る**関数オブジェクトです。`size()` メンバ関数、配列、`end - begin` が使えるものに対応します。要素数を O(1) で取れない範囲（`filter` の結果など）にはコンパイルエラーになります。

!!! tip "ポイント"
    - 配列にも使える（`std::size` と同じ）。
    - `views::filter` の結果には使えない。個数を数えるなら `ranges::distance`。
    - 符号つきが欲しければ `ranges::ssize`。

!!! info "このページを読む前に"
    [テンプレートとコンセプト](../../../basics/template.md) の基本が前提です。

## 関数の詳しい説明

### std::ranges::size {#size}

```cpp
inline constexpr /*unspecified*/ ranges::size;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `r` | 範囲 | 要素数を知りたい範囲 |

- 戻り値: 要素数
- 計算量: O(1)

```cpp
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3};
  std::println("{} {}", std::ranges::size(v), std::ranges::size(std::views::iota(0, 5)));
}
```

```text title="実行結果"
3 5
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 範囲の個数をテンプレートで取る | `std::ranges::size(r)` |

## よくあるミス

??? failure "filter の結果に使う"
    コンパイルエラーです。`std::ranges::distance(r)` で数えます（O(n)）。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::size`](../iterator/size.md) | 従来の関数 |
| [`ranges::begin`](begin.md) | 先頭 |

## コンパイラ対応

C++20 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 要素数を O(1) で取る
    - [x] filter の結果には使えない
    - [x] 数えるなら distance

## 関連ページ

- [cpprefjp: std::ranges::size](https://cpprefjp.github.io/reference/ranges/size.html)
- [cppreference: std::ranges::size](https://en.cppreference.com/w/cpp/ranges/size)
