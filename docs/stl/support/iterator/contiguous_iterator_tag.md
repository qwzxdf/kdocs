---
title: std::contiguous_iterator_tag
summary: "連続イテレータ（メモリ上で連続した要素を指す）を表すタグの型。"
order: 900
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::contiguous_iterator_tag

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

`std::vector` や配列のイテレータは、要素がメモリ上で連続していることを保証します。その性質を表す、中身のない空の構造体が `std::contiguous_iterator_tag` です。C++20 で追加されました。

!!! tip "ポイント"
    - `random_access_iterator_tag` から派生する、空の構造体
    - `iterator_category` ではなく、`iterator_concept` に入る
    - `vector`、`array`、`string`、ポインターのイテレータが持つ
    - `std::contiguous_iterator` コンセプトの判定に使われる

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) を先に読んでください。

## 関数の詳しい説明

### std::contiguous_iterator_tag {#contiguous_iterator_tag}

<span class="ver ver-20">C++20</span>

```cpp
struct contiguous_iterator_tag : random_access_iterator_tag {};
```

`iterator_category` を `contiguous_iterator_tag` にすると、C++17 以前のコードが、知らないタグを見て壊れる恐れがあります。そこで、旧来の `iterator_category` は `random_access_iterator_tag` のままにして、新しい `iterator_concept` に `contiguous_iterator_tag` を入れる、という分け方になっています。

そのため、`std::iterator_traits<It>::iterator_category` を見ても、連続性は分かりません。`std::contiguous_iterator<It>` コンセプトで調べます。

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
  using It = std::vector<int>::iterator;
  using Traits = std::iterator_traits<It>;

  std::println("iterator_category は random_access: {}",
               std::is_same_v<Traits::iterator_category, std::random_access_iterator_tag>);
  std::println("連続している: {}", std::contiguous_iterator<It>);
  std::println("継承している: {}",
               std::is_base_of_v<std::random_access_iterator_tag, std::contiguous_iterator_tag>);
}
```

```text title="実行結果"
iterator_category は random_access: true
連続している: true
継承している: true
```

## ゲームでの使いどころ

連続したメモリであることを前提にする処理（`memcpy`、C の API）を、コンセプトで制約するときに関わります。

## よくあるミス

??? failure "iterator_category で連続性を調べる"
    `random_access_iterator_tag` のままです。コンセプトで調べます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`contiguous_iterator`](../concepts/contiguous_iterator.md) | 対応するコンセプト |
| [`random_access_iterator_tag`](random_access_iterator_tag.md) | 親のタグ |
| [`iterator_traits`](iterator_traits.md) | タグを取り出す |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::contiguous_iterator_tag](https://cpprefjp.github.io/reference/iterator/contiguous_iterator_tag.html)
- [cppreference: std::contiguous_iterator_tag](https://en.cppreference.com/w/cpp/iterator/contiguous_iterator_tag)
