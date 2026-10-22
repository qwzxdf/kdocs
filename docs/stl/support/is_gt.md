---
title: std::is_gt
summary: "順序型の結果が「大きい」かを `bool` で返す。"
order: 900
group: 比較（<compare>）
tags:
  - 型・言語サポート
---

# std::is_gt

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <compare>`
</div>

`<=>` の結果（`strong_ordering` など）は、`== 0` や `< 0` と書いて判定します。`is_gt(結果)` なら、その判定を名前つきの関数で書けます。`大きい` かを `bool` で返します。

!!! tip "ポイント"
    - `<compare>` の部品。
    - C++20 の三方比較（`<=>`）と組み合わせて使う。
    - ふつうは `=default` の `<=>` で足りる。

!!! info "このページを読む前に"
    [`<=>`（宇宙船演算子）](spaceship.md) を先に読んでください。

## 関数の詳しい説明

### std::is_gt {#is_gt}

```cpp
constexpr bool is_gt(std::partial_ordering cmp) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `cmp` | 順序型 | `<=>` の結果 |

- 戻り値: 大きいなら `true`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <compare>
#include <print>

int main() {
  std::println("{}", std::is_gt(std::strong_ordering::greater));
  std::println("{}", std::is_gt(std::strong_ordering::equal));
}
```

```text title="実行結果"
true
false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | `<=>` の結果を読みやすく判定する |

## よくあるミス

??? failure "順序型を `int` と比べる"
    `cmp < 0` と書けるのは `0` との比較だけです。他の整数とは比べられません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`spaceship`](spaceship.md) | `<=>` 演算子 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 順序型の結果が「大きい」かを `bool` で返す
    - [x] `<compare>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::is_gt](https://cpprefjp.github.io/reference/compare/is_gt.html)
- [cppreference: std::is_gt](https://en.cppreference.com/w/cpp/utility/is_gt)
