---
title: std::uses_allocator
summary: "型が、指定したアロケータを受け取れるかを調べる型特性。"
order: 900
tags:
  - メモリ
---

# std::uses_allocator

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <memory>`
</div>

コンテナの中に別のコンテナを入れたとき（`vector<string>`）、外側のアロケーターを、要素の `string` にも使わせたい。そのためには、「この型は、アロケーターを渡して作れるか」をコンパイル時に知る必要があります。`std::uses_allocator<T, Alloc>` は、その判定をする型特性です。

!!! tip "ポイント"
    - `T::allocator_type` があり、`Alloc` から変換できれば真
    - `std::uses_allocator_v<T, Alloc>` で値が取れる
    - `std::vector`、`std::string`、`std::pmr::*` は真
    - `int` などの基本型は偽

!!! info "このページを読む前に"
    [`std::allocator`](allocator.md) など、アロケーターの基本を先に読んでください。

## 関数の詳しい説明

### std::uses_allocator {#uses_allocator}

<span class="ver ver-11">C++11</span>

```cpp
template <class T, class Alloc> struct uses_allocator;
template <class T, class Alloc>
inline constexpr bool uses_allocator_v = uses_allocator<T, Alloc>::value;
```

判定は、`T::allocator_type` という型が存在し、`Alloc` がそれに変換できるかです。自作の型は、`using allocator_type = ...;` を書くと、真になります。

型が `allocator_type` を持たないのに、アロケーターを受け取れる場合は、`uses_allocator` を特殊化して `true` にします。

`polymorphic_allocator` を使う `pmr` のコンテナは、この判定のおかげで、外側のコンテナのリソースを、中の要素へ自動で伝えます。

## 実際に動かしてみる

```cpp
#include <memory>
#include <memory_resource>
#include <print>
#include <string>
#include <vector>

int main() {
  std::println("vector: {}", std::uses_allocator_v<std::vector<int>, std::allocator<int>>);
  std::println("string: {}", std::uses_allocator_v<std::string, std::allocator<char>>);
  std::println("int: {}", std::uses_allocator_v<int, std::allocator<int>>);

  // pmr の文字列は、polymorphic_allocator から作れる
  std::println("pmr::string: {}",
               std::uses_allocator_v<std::pmr::string, std::pmr::polymorphic_allocator<char>>);
}
```

```text title="実行結果"
vector: true
string: true
int: false
pmr::string: true
```

## ゲームでの使いどころ

自作のコンテナを、`pmr` や `scoped_allocator_adaptor` に対応させるときに、`allocator_type` を用意する理由を知るための特性です。

## よくあるミス

??? failure "allocator_type を持たない自作の型で、伝わらないのに気づかない"
    `using allocator_type` を書きます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`allocator_arg`](allocator_arg.md) | アロケーターを渡す印 |
| [`make_obj_using_allocator`](make_obj_using_allocator.md) | 判定に応じて作る |
| [`scoped_allocator_adaptor`](scoped_allocator_adaptor.md) | これを使って伝える |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::uses_allocator](https://cpprefjp.github.io/reference/memory/uses_allocator.html)
- [cppreference: std::uses_allocator](https://en.cppreference.com/w/cpp/memory/uses_allocator)
