---
title: std::pointer_traits
summary: "ポインタ（生ポインタやスマートポインタ）の性質を、同じ書き方で調べる。"
order: 900
tags:
  - メモリ
---

# std::pointer_traits

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <memory>`
</div>

生のポインター（`int*`）と、スマート ポインター風の型（アロケーターが返す「ファンシー ポインター」）を、同じように扱いたい。`std::pointer_traits<Ptr>` は、どちらのポインターについても、指す先の型（`element_type`）や、参照からポインターを作る関数（`pointer_to`）を、統一して提供します。

!!! tip "ポイント"
    - `element_type`: 指す先の型
    - `pointer_to(r)`: 参照 `r` から、ポインターを作る
    - `pointer_traits<T*>` は、生のポインター用の特殊化
    - 自作コンテナで、ファンシー ポインターに対応するときに使う

!!! info "このページを読む前に"
    [`std::allocator`](allocator.md) など、アロケーターの基本を先に読んでください。

## 関数の詳しい説明

### std::pointer_traits {#pointer_traits}

<span class="ver ver-11">C++11</span>

```cpp
template <class Ptr>
struct pointer_traits {
  using pointer = Ptr;
  using element_type = /* Ptr が指す型 */;
  using difference_type = /* ポインターの差の型 */;
  static pointer pointer_to(element_type& r);
};
```

生のポインター `T*` では、`element_type` は `T`、`difference_type` は `std::ptrdiff_t`、`pointer_to(r)` は `&r`（`std::addressof(r)`）です。

ファンシー ポインターは、アロケーターが返す、ポインター風のクラスです。共有メモリ上のオフセット ポインターなどがあります。そのクラスに `element_type` が定義されていれば、それが使われます。

`rebind<U>` は、同じ種類のポインターで、指す先が `U` のものを作ります。

C++20 の `std::to_address` が、ポインター風の型から生のポインターを取り出します。

## 実際に動かしてみる

```cpp
#include <memory>
#include <print>
#include <type_traits>

int main() {
  using Traits = std::pointer_traits<int*>;
  static_assert(std::is_same_v<Traits::element_type, int>);
  static_assert(std::is_same_v<Traits::difference_type, std::ptrdiff_t>);

  int x = 42;
  int* p = Traits::pointer_to(x);
  std::println("{}", *p);
  std::println("アドレスは同じ: {}", p == &x);

  // shared_ptr のような型の element_type
  using SP = std::pointer_traits<std::shared_ptr<double>>;
  static_assert(std::is_same_v<SP::element_type, double>);
}
```

```text title="実行結果"
42
アドレスは同じ: true
```

## ゲームでの使いどころ

自作のコンテナを、生のポインター以外のファンシー ポインターにも対応させるときに使います。

## よくあるミス

??? failure "生のポインターだけを想定して書く"
    `T*` を直接使うと、ファンシー ポインターを受け付けません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`to_address`](to_address.md) | 生のポインターを取り出す |
| [`allocator_traits`](allocator_traits.md) | アロケーターの窓口 |
| [`addressof`](../utilities/addressof.md) | 本当のアドレスを取る |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::pointer_traits](https://cpprefjp.github.io/reference/memory/pointer_traits.html)
- [cppreference: std::pointer_traits](https://en.cppreference.com/w/cpp/memory/pointer_traits)
