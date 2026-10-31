---
title: std::allocator_traits
summary: "アロケータの機能を、足りない部分を補って一様に使えるようにする窓口。"
order: 20
tags:
  - メモリ
---

# std::allocator_traits

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <memory>`
</div>

アロケーターには `allocate` と `deallocate` さえあればよく、`construct` や `destroy`、`rebind` などは省略できます。コンテナは省略された部分を毎回調べるのが面倒です。`std::allocator_traits<Alloc>` はアロケーターの統一的な窓口で、省略された機能を既定の動作で補ってくれます。

!!! tip "ポイント"
    - コンテナはアロケーターを直接ではなく、`allocator_traits` 経由で呼ぶ
    - `allocate`、`deallocate`、`construct`、`destroy`、`max_size` などがある
    - アロケーターが `construct` を持たなければ、配置 new で代用する
    - 自作のアロケーターは最小限の `allocate` と `deallocate` で済む

!!! info "このページを読む前に"
    [`std::allocator`](allocator.md) などアロケーターの基本を先に読んでください。

## 関数の詳しい説明

### std::allocator_traits {#allocator_traits}

<span class="ver ver-11">C++11</span>

```cpp
template <class Alloc>
struct allocator_traits {
  using value_type = typename Alloc::value_type;
  using pointer = /* ... */;
  static pointer allocate(Alloc& a, std::size_t n);
  static void deallocate(Alloc& a, pointer p, std::size_t n);
  template <class T, class... Args>
  static void construct(Alloc& a, T* p, Args&&... args);
  template <class T>
  static void destroy(Alloc& a, T* p);
  static std::size_t max_size(const Alloc& a) noexcept;
};
```

`construct` はアロケーターが `construct` を持てばそれを持たなければ `std::construct_at` を呼びます。`destroy` も同様です。

自作のアロケーターは `value_type`、`allocate`、`deallocate`、`==` だけでコンテナに使えます。`pointer` や `rebind` は型から推論されて補われます。

型の別名には `rebind_alloc<U>` があり `value_type` が違う型用のアロケーターを作ります（リストのノード用のアロケーターなど）。

## 実際に動かしてみる

```cpp
#include <memory>
#include <print>

int main() {
  using Traits = std::allocator_traits<std::allocator<int>>;
  static_assert(std::is_same_v<Traits::value_type, int>);

  std::allocator<int> a;
  int* p = Traits::allocate(a, 3);  // 生の領域

  for (int i = 0; i < 3; ++i) Traits::construct(a, p + i, i * 10);
  std::println("{} {} {}", p[0], p[1], p[2]);

  for (int i = 0; i < 3; ++i) Traits::destroy(a, p + i);
  Traits::deallocate(a, p, 3);
}
```

```text title="実行結果"
0 10 20
```

## ゲームでの使いどころ

自作のコンテナを書くときアロケーターの呼び出しを `allocator_traits` 経由にして、あらゆるアロケーターに対応させます。

## よくあるミス

??? failure "アロケーターを直接呼ぶ"
    `construct` を持たないアロケーターで失敗します。`allocator_traits` を通します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`allocator`](allocator.md) | 標準のアロケーター |
| [`scoped_allocator_adaptor`](scoped_allocator_adaptor.md) | 入れ子への伝播 |
| [`pointer_traits`](pointer_traits.md) | ポインターの特性 |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::allocator_traits](https://cpprefjp.github.io/reference/memory/allocator_traits.html)
- [cppreference: std::allocator_traits](https://en.cppreference.com/w/cpp/memory/allocator_traits)
