---
title: std::make_obj_using_allocator
summary: "アロケータを渡しながら、オブジェクトを作る。"
order: 900
tags:
  - メモリ
---

# std::make_obj_using_allocator

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <memory>`
</div>

型によって、アロケーターの渡し方は違います。先頭に `allocator_arg` と一緒に渡す型、末尾に渡す型、そもそも受け取れない型。それを自分で判断して `if constexpr` で書き分けるのは大変です。C++20 の `std::make_obj_using_allocator<T>(alloc, args...)` は、型に合わせた構築方法を選んで、オブジェクトを作ります。

!!! tip "ポイント"
    - `uses_allocator` の判定に従って、適切な形でアロケーターを渡して作る
    - 戻り値は `T` の値
    - 受け取れない型には、アロケーターなしで作る
    - C++20

!!! info "このページを読む前に"
    [`std::allocator`](allocator.md) など、アロケーターの基本を先に読んでください。

## 関数の詳しい説明

### std::make_obj_using_allocator {#make_obj_using_allocator}

<span class="ver ver-20">C++20</span>

```cpp
template <class T, class Alloc, class... Args>
constexpr T make_obj_using_allocator(const Alloc& alloc, Args&&... args);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | テンプレート引数 | 作る型 |
| `alloc` | アロケーター | 渡すアロケーター |
| `args` | 任意 | `T` の通常の構築の引数 |

型 `T` が `uses_allocator` を満たすかで、次のように選ばれます。

- 満たさない: `T(args...)`
- 満たし、先頭渡しに対応: `T(allocator_arg, alloc, args...)`
- 満たし、末尾渡しに対応: `T(args..., alloc)`

`std::pair` の場合は、各要素に対して、同じ規則で再帰的に適用されます。

戻り値は値なので、保証されたコピー省略で、ムーブなしに作られます。

## 実際に動かしてみる

```cpp
#include <memory_resource>
#include <print>
#include <vector>

int main() {
  std::byte buffer[1024];
  std::pmr::monotonic_buffer_resource pool(buffer, sizeof(buffer));
  std::pmr::polymorphic_allocator<int> alloc(&pool);

  // vector(3, 7, alloc) の形で作られる
  auto v = std::make_obj_using_allocator<std::pmr::vector<int>>(alloc, 3, 7);
  std::println("{} {} {}", v[0], v[1], v[2]);
  std::println("pool から確保: {}", v.get_allocator().resource() == &pool);

  // アロケーターを受け取れない型は、そのまま作られる
  auto n = std::make_obj_using_allocator<int>(alloc, 42);
  std::println("{}", n);
}
```

```text title="実行結果"
7 7 7
pool から確保: true
42
```

## ゲームでの使いどころ

自作のコンテナ ライブラリで、要素の型を問わずに、アロケーターを伝えながら作る関数を書くときに使います。

## よくあるミス

??? failure "受け取れる型だと思って、アロケーターが伝わらない"
    `allocator_type` を持たない型には、渡されません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`uses_allocator`](uses_allocator.md) | 判定の元 |
| [`allocator_arg`](allocator_arg.md) | 先頭渡しの印 |
| [`polymorphic_allocator`](pmr/polymorphic_allocator.md) | 使われるアロケーターの例 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::make_obj_using_allocator](https://cpprefjp.github.io/reference/memory/make_obj_using_allocator.html)
- [cppreference: std::make_obj_using_allocator](https://en.cppreference.com/w/cpp/memory/make_obj_using_allocator)
