---
title: std::bidirectional_iterator
summary: "前後どちらにも進めるイテレータを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::bidirectional_iterator

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

`--it` で後ろにも戻れるイテレータが、`std::bidirectional_iterator` です。`std::list` のイテレータが典型です。`std::ranges::reverse` のように、両端から詰めていくアルゴリズムは、これを要求します。

!!! tip "ポイント"
    - `++it` に加えて、`--it` と `it--` が使える
    - `forward_iterator` の機能をすべて持つ
    - `std::list`、`std::map`、`std::set` のイテレータが満たす
    - `std::forward_list` のイテレータは満たさない

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::bidirectional_iterator {#bidirectional_iterator}

<span class="ver ver-20">C++20</span>

```cpp
template <class I>
concept bidirectional_iterator = std::forward_iterator<I>
    && std::derived_from</* ITER_CONCEPT(I) */, std::bidirectional_iterator_tag>
    && requires(I i) {
      { --i } -> std::same_as<I&>;
      { i-- } -> std::same_as<I>;
    };
```

満たすべき条件は、次のとおりです。

- `std::forward_iterator<I>`
- `iterator_concept` が `std::bidirectional_iterator_tag` から派生している
- `--i` が `I&` を返し、`i--` が `I` を返す

`std::ranges::reverse_view` や `std::reverse_iterator` は、元のイテレータが双方向であることを要求します。

`std::ranges::prev_permutation` のような、後ろにも戻りながら並べ替えるアルゴリズムも、これを要求します。

## 実際に動かしてみる

```cpp
#include <concepts>
#include <deque>
#include <forward_list>
#include <iterator>
#include <list>
#include <print>
#include <sstream>
#include <vector>

#include <map>

int main() {
  std::println("list: {}", std::bidirectional_iterator<std::list<int>::iterator>);
  std::println("map: {}", std::bidirectional_iterator<std::map<int, int>::iterator>);
  std::println("forward_list: {}", std::bidirectional_iterator<std::forward_list<int>::iterator>);
  std::println("vector: {}", std::bidirectional_iterator<std::vector<int>::iterator>);
}
```

```text title="実行結果"
list: true
map: true
forward_list: false
vector: true
```

## ゲームでの使いどころ

`list` や `map` のイテレータも受け付けて、逆向きにも進める関数を書くときに使います。

## よくあるミス

??? failure "forward_list に逆順の処理をかける"
    後ろに戻れないので、満たしません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`forward_iterator`](forward_iterator.md) | 前にだけ進む |
| [`random_access_iterator`](random_access_iterator.md) | 任意の距離を一度に動ける |
| [`reverse_iterator`](../iterator/reverse_iterator.md) | 逆向きに進めるアダプター |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::bidirectional_iterator](https://cpprefjp.github.io/reference/iterator/bidirectional_iterator.html)
- [cppreference: std::bidirectional_iterator](https://en.cppreference.com/w/cpp/iterator/bidirectional_iterator)
