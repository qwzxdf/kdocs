---
title: std::ranges::iterator_t
summary: "範囲のイテレータの型を取り出す型の別名。"
order: 900
tags:
  - 型・言語サポート
---

# std::ranges::iterator_t

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

テンプレートの中で、範囲の型 `R` から「要素の型」や「イテレータの型」を知りたいことがあります。`R::value_type` では、配列や view など `value_type` を持たない範囲に使えません。`iterator_t<R>` は、どんな範囲にも使える統一された書き方です。

!!! tip "ポイント"
    - `R` は `range` を満たす型。
    - `_t` が付いた型の別名（`typename` 不要）。
    - 配列にも view にも使える。

!!! info "このページを読む前に"
    [`std::ranges::range`](range.md) を先に読んでください。

## 関数の詳しい説明

### std::ranges::iterator_t {#iterator_t}

```cpp
template <ranges::range R>
using iterator_t = /* 範囲のイテレータの型 */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `R` | 型 | 範囲の型 |

- 戻り値: 範囲のイテレータの型
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <print>
#include <ranges>
#include <type_traits>
#include <vector>

int main() {
  using T = std::ranges::iterator_t<std::vector<int>>;
  std::println("{}", std::is_same_v<T, std::vector<int>::iterator>);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | ジェネリックな関数で、要素の型を取り出す |

## よくあるミス

??? failure "`R::value_type` を使う"
    配列や view には `value_type` がないことがあります。`range_value_t<R>` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`range`](range.md) | 範囲のコンセプト |
| [`std::iter_value_t`](../iterator/iter_value_t.md) | イテレータ側の型 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 範囲のイテレータの型を取り出す型の別名
    - [x] `R` は `range` を満たす型
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::ranges::iterator_t](https://cpprefjp.github.io/reference/ranges/iterator_t.html)
- [cppreference: std::ranges::iterator_t](https://en.cppreference.com/w/cpp/ranges/iterator_t)
