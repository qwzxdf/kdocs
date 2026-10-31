---
title: std::common_iterator
summary: "イテレータと sentinel（終端）を、1 つの型にまとめる。"
order: 900
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::common_iterator

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

イテレータと番兵が別の型だと、`std::vector(first, last)` のような、2 つの引数が同じ型であることを要求する古い API に渡せません。`std::common_iterator<I, S>` は、イテレータ `I` と番兵 `S` のどちらも表せる、1 つの型にまとめるアダプターです。

!!! tip "ポイント"
    - `I` か `S` のどちらかを持つ、1 つの型
    - 古い API（引数が同じ型の `begin` / `end`）に、イテレータと番兵の組を渡せる
    - 比較で、`I` と `S` の組が正しく判定される
    - 少し大きく、少し遅い

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) を先に読んでください。

## 関数の詳しい説明

### std::common_iterator {#common_iterator}

<span class="ver ver-20">C++20</span>

```cpp
template <std::input_or_output_iterator I, std::sentinel_for<I> S>
  requires (!std::same_as<I, S>) && std::copyable<I>
class common_iterator;
```

内部は `std::variant<I, S>` に近い形で、現在どちらを持つかを覚えています。比較では、両方が `S` なら等しく、片方が `I`、もう片方が `S` なら `I == S` の結果が使われます。

C++17 以前の API（`std::vector` のコンストラクター、`std::accumulate` など）は、`first` と `last` が同じ型であることを要求します。`views::common` が、範囲を `common_iterator` に包んで、そうした API へ渡せる範囲を作ります。

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
  std::vector<int> src = {1, 2, 3, 4, 5};

  // 先頭 3 個: イテレータは counted_iterator、終端は default_sentinel (別の型)
  using CI = std::common_iterator<std::counted_iterator<std::vector<int>::iterator>, std::default_sentinel_t>;
  CI first(std::counted_iterator(src.begin(), 3));
  CI last(std::default_sentinel);

  // 2 つの引数が同じ型 CI なので、古い API に渡せる
  std::vector<int> dst(first, last);
  std::println("{}", dst);
}
```

```text title="実行結果"
[1, 2, 3]
```

## ゲームでの使いどころ

範囲ライブラリのビューの結果を、古いコンテナのコンストラクターに渡すときに、裏で使われます。

## よくあるミス

??? failure "I と S が同じ型"
    使えません（`!same_as<I, S>` の制約）。

??? failure "速さを期待する"
    分岐のコストが増えます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`counted_iterator`](counted_iterator.md) | イテレータ側の例 |
| [`default_sentinel`](default_sentinel.md) | 番兵側の例 |
| [`common`](../../algorithms/views/common.md) | 範囲を共通の型にするビュー |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::common_iterator](https://cpprefjp.github.io/reference/iterator/common_iterator.html)
- [cppreference: std::common_iterator](https://en.cppreference.com/w/cpp/iterator/common_iterator)
