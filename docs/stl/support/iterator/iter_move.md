---
title: std::iter_move
summary: "イテレータが指す要素を、右辺値として取り出す。"
order: 900
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::iter_move

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

`std::move(*it)` と書くと、プロキシ型のイテレータ（`vector<bool>` など）でうまくいかないことがあります。`ranges::iter_move(it)` は、イテレータごとの正しい方法で、要素を右辺値にして返します。

!!! tip "ポイント"
    - `<iterator>` の部品。
    - ふつうは補助関数（`back_inserter` など）経由で使う。
    - アルゴリズムの出力先や入力元に渡す。

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::iter_move {#iter_move}

```cpp
inline constexpr /* カスタマイズポイント */ ranges::iter_move;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `it` | イテレータ | 要素を指すイテレータ |

- 戻り値: 右辺値の参照（または値）
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <iterator>
#include <print>
#include <ranges>
#include <type_traits>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3};
  std::println("{}", std::is_rvalue_reference_v<decltype(std::ranges::iter_move(v.begin()))>);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | ジェネリックなアルゴリズムで要素をムーブする |

## よくあるミス

??? failure "`std::move(*it)` と書く"
    プロキシ型のイテレータでは `std::move(*it)` が正しくありません。`iter_move` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`iter_swap`](../../algorithms/iter_swap.md) | 要素を入れ替える |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] イテレータが指す要素を右辺値として取り出す
    - [x] `<iterator>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::iter_move](https://cpprefjp.github.io/reference/iterator/iter_move.html)
- [cppreference: std::iter_move](https://en.cppreference.com/w/cpp/iterator/iter_move)
