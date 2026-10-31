---
title: std::iter_difference_t
summary: "イテレータの差の型を取り出す型の別名。"
order: 900
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::iter_difference_t

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

2 つのイテレータの距離（`it2 - it1`）を保存する変数の型は、何にすればよいでしょう。`int` では足りないことも、符号の問題が起きることもあります。`std::iter_difference_t<I>` は、そのイテレータの「距離」を表す型を返します。普通は符号つきの整数（`std::ptrdiff_t`）です。

!!! tip "ポイント"
    - イテレータの距離を表す型を返す
    - 符号つきの整数に準ずる型
    - `std::distance` の戻り値の型
    - C++20

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) を先に読んでください。

## 関数の詳しい説明

### std::iter_difference_t {#iter_difference_t}

<span class="ver ver-20">C++20</span>

```cpp
template <class I>
using iter_difference_t = /* I の距離の型 */;
```

`std::weakly_incrementable<I>` を満たす `I` に使えます。`I::difference_type` があればそれ、なければ `std::iterator_traits<I>::difference_type` が元になります。

多くの環境で `std::ptrdiff_t` です。`size_t` ではなく符号つきである点に注意します。`it2 - it1` が負になることがあるからです。

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
  static_assert(std::is_same_v<std::iter_difference_t<std::vector<int>::iterator>, std::ptrdiff_t>);
  static_assert(std::is_signed_v<std::iter_difference_t<int*>>);

  std::vector<int> v = {1, 2, 3, 4};
  std::iter_difference_t<decltype(v.begin())> n = v.end() - v.begin();
  std::println("距離: {}", n);
}
```

```text title="実行結果"
距離: 4
```

## ゲームでの使いどころ

イテレータの距離を保存する変数の型を、テンプレートの中で決めるときに使います。

## よくあるミス

??? failure "距離を int や size_t で受ける"
    大きな範囲や負の距離で、あふれたり巻き戻ったりします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`iter_value_t`](iter_value_t.md) | 要素の型 |
| [`distance`](distance.md) | 距離を求める |
| [`advance`](advance.md) | 距離だけ進める |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::iter_difference_t](https://cpprefjp.github.io/reference/iterator/iter_difference_t.html)
- [cppreference: std::iter_difference_t](https://en.cppreference.com/w/cpp/iterator/iter_difference_t)
