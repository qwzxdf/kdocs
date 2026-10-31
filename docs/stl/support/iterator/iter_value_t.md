---
title: std::iter_value_t
summary: "イテレータが指す値の型を取り出す型の別名。"
order: 900
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::iter_value_t

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

イテレータが指す要素の型を知りたい。`std::vector<int>::iterator` なら `int`、`const int*` でも `int` です。この型を取り出すのが `std::iter_value_t<I>` で、C++17 までの `std::iterator_traits<I>::value_type` の、範囲ライブラリ向けの新しい書き方です。

!!! tip "ポイント"
    - イテレータが指す要素の型（cv 修飾なし）を返す
    - `const int*` でも `int`（`const` は付かない）
    - `iterator_traits` と違い、プロキシ参照のイテレータでも正しく動く
    - C++20

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) を先に読んでください。

## 関数の詳しい説明

### std::iter_value_t {#iter_value_t}

<span class="ver ver-20">C++20</span>

```cpp
template <class I>
using iter_value_t = /* I が指す要素の型 */;
```

`std::indirectly_readable<I>` を満たす `I` に使えます。`I::value_type` があればそれ、なければ `std::iterator_traits<I>::value_type` が元になります。

参照と値の区別が大切です。`iter_value_t<I>` は、コピーして保存できる「値」の型です。参照の型は `iter_reference_t<I>` です。`vector<bool>` では、値は `bool`、参照はプロキシ型で、別々の型です。

テンプレートの中で、要素を一時的に保存する変数の型を決めるときに、`std::iter_value_t<I> tmp = *it;` と書きます。

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
  static_assert(std::is_same_v<std::iter_value_t<std::vector<int>::iterator>, int>);
  static_assert(std::is_same_v<std::iter_value_t<const int*>, int>);  // const は付かない
  static_assert(std::is_same_v<std::iter_value_t<std::vector<bool>::iterator>, bool>);

  // 要素を一時保存する変数の型に使う
  std::vector<std::string> v = {"a", "b"};
  std::iter_value_t<decltype(v.begin())> tmp = *v.begin();
  std::println("{}", tmp);
}
```

```text title="実行結果"
a
```

## ゲームでの使いどころ

要素を一時的に保存する変数の型を、テンプレートの中で決めるときに使います。

## よくあるミス

??? failure "値の型と参照の型を混同する"
    値は保存用、参照はアクセス用です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`iter_reference_t`](iter_reference_t.md) | 参照の型 |
| [`iter_difference_t`](iter_difference_t.md) | 距離の型 |
| [`iterator_traits`](iterator_traits.md) | 従来の書き方 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::iter_value_t](https://cpprefjp.github.io/reference/iterator/iter_value_t.html)
- [cppreference: std::iter_value_t](https://en.cppreference.com/w/cpp/iterator/iter_value_t)
