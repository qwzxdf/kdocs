---
title: std::counted_iterator
summary: "残りの個数を数えながら進むイテレータ。"
order: 900
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::counted_iterator

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

イテレータに「あと何個進めるか」を持たせたい。`std::counted_iterator<I>` は、元のイテレータと残りの個数を持つアダプターで、`++` するたびに残りが減り、0 になると `std::default_sentinel` と等しくなります。範囲の先頭から `n` 個だけを扱うときに使います。

!!! tip "ポイント"
    - 元のイテレータと残りの個数を持つ
    - `++` で残りが 1 減る
    - 残りが 0 で `default_sentinel` と等しい
    - `count()` で残りの個数、`base()` で元のイテレータを取れる

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) を先に読んでください。

## 関数の詳しい説明

### std::counted_iterator {#counted_iterator}

<span class="ver ver-20">C++20</span>

```cpp
template <std::input_or_output_iterator I>
class counted_iterator {
 public:
  constexpr counted_iterator(I x, std::iter_difference_t<I> n);
  constexpr std::iter_difference_t<I> count() const noexcept;
  constexpr const I& base() const& noexcept;
};
```

`views::counted` や `views::take` は、内部でこれを使うことがあります。

残りの個数以上に進めると未定義動作です。`count()` が 0 になった時点で、`default_sentinel` と比べて止めます。元のイテレータの種類を引き継ぐので、ランダム アクセスのイテレータなら、`counted_iterator` もランダム アクセスです。

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <deque>
#include <forward_list>
#include <iterator>
#include <list>
#include <print>
#include <ranges>
#include <sstream>
#include <string>
#include <type_traits>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3, 4, 5};

  std::counted_iterator it(v.begin(), 3);
  std::println("残り: {}", it.count());

  ++it;
  std::println("1 つ進めた後の残り: {}", it.count());
  std::println("今の要素: {}", *it);

  ++it;
  ++it;
  std::println("終わり: {}", it == std::default_sentinel);
}
```

```text title="実行結果"
残り: 3
1 つ進めた後の残り: 2
今の要素: 2
終わり: true
```

## ゲームでの使いどころ

範囲の先頭から `n` 個だけを処理するアルゴリズムの内部で使われます。

## よくあるミス

??? failure "残りを超えて進める"
    未定義動作です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`default_sentinel`](default_sentinel.md) | 終わりの番兵 |
| [`counted`](../../algorithms/views/counted.md) | ビューの版 |
| [`take`](../../algorithms/views/take.md) | 先頭から n 個を取るビュー |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::counted_iterator](https://cpprefjp.github.io/reference/iterator/counted_iterator.html)
- [cppreference: std::counted_iterator](https://en.cppreference.com/w/cpp/iterator/counted_iterator)
