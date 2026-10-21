---
title: std::prev
summary: "イテレータを n 個戻した位置を返す（元は変えない）。"
order: 2
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::prev

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <iterator>`
</div>

`std::prev(it, n)` は、**イテレータを n 個戻した位置を返す**関数です。`std::prev(v.end())` で、最後の要素を指すイテレータが取れます。双方向にたどれる範囲で使えます。

!!! tip "ポイント"
    - 最後の要素: `*std::prev(v.end())`（空では不可）。
    - begin より前へ戻ると未定義動作。

!!! info "このページを読む前に"
    [`<iterator>`](../iterator.md) の概要を先に読むと分かりやすいです。[イテレータ](../../../basics/iterator.md) の基本が前提です。

## 関数の詳しい説明

### std::prev {#prev}

```cpp
template <class BidirIt>
BidirIt prev(BidirIt it, std::iter_difference_t<BidirIt> n = 1);
```

- n 個前のイテレータを返します。`std::prev(v.end())` で最後の要素

<div class="anim" data-label="std::prev(it, 2)">
a b c *d # it は d を指す
a *b c d # 2 つ前を返す。it 自体は動かない
</div>

## 実際に動かしてみる

```cpp
#include <iterator>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3, 4};
  std::println("{} {}", *std::prev(v.end()), *std::prev(v.end(), 2));
}
```

```text title="実行結果"
4 3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 最後の要素を指す | `std::prev(v.end())` |

## よくあるミス

??? failure "空の範囲で prev(end())"
    未定義動作です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`next`](next.md) | 進む |

## コンパイラ対応

C++11 から使えます。`ssize` は C++20 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 戻した位置を返す
    - [x] 最後の要素は prev(end())
    - [x] 空では使えない

## 関連ページ

- [cpprefjp: std::prev](https://cpprefjp.github.io/reference/iterator/prev.html)
- [cppreference: std::prev](https://en.cppreference.com/w/cpp/iterator/prev)
