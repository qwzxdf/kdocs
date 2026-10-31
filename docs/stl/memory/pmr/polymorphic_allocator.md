---
title: std::pmr::polymorphic_allocator
summary: "メモリリソースを実行時に切り替えられるアロケータ。pmr コンテナが使う。"
order: 2
group: pmr のメモリリソースと部品
tags:
  - メモリ
---

# std::pmr::polymorphic_allocator

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <memory_resource>`
</div>

`std::vector<int>` と、自作のアリーナから確保する `std::vector<int>` は、アロケーターの型が違うので、別の型になります。関数の引数にすると、型が合わず困ります。`std::pmr::polymorphic_allocator<T>` は、取り先を「実行時に」切り替えられるアロケーターで、`std::pmr::vector<int>` の型は、取り先が何であっても同じです。

!!! tip "ポイント"
    - `memory_resource*` を持つだけのアロケーター。コピーが軽い
    - `std::pmr::vector<T>` は `std::vector<T, polymorphic_allocator<T>>` の別名
    - 要素が `pmr::string` なら、コンテナの取り先が、要素にも伝わる
    - コンテナにリソースを渡すだけでよく、直接触ることは少ない

!!! info "このページを読む前に"
    [`std::pmr`](../pmr.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::pmr::polymorphic_allocator {#polymorphic_allocator}

<span class="ver ver-17">C++17</span>

```cpp
template <class T>
class polymorphic_allocator {
 public:
  polymorphic_allocator() noexcept;                              // default_resource() を使う
  polymorphic_allocator(std::pmr::memory_resource* r);           // 暗黙に変換できる
  std::pmr::memory_resource* resource() const;
  T* allocate(std::size_t n);
  void deallocate(T* p, std::size_t n);
};
```

既定の構築では、`std::pmr::get_default_resource()` が返すリソースを使います。リソースのポインターから暗黙に変換できるので、`std::pmr::vector<int> v(&pool);` と書けます。

注目したいのは、`construct` です。要素の型が「アロケーターを受け取れる型」（`uses_allocator`）なら、コンテナのアロケーターを、要素の構築に渡します。`pmr::vector<pmr::string>` の要素の文字列は、コンテナと同じリソースから確保されます。

リソースが違うコンテナどうしの代入やムーブは、リソースの違いで、要素のコピーが必要になることがあります。`is_equal` が真なら、ポインターの付け替えだけで済みます。

## 実際に動かしてみる

```cpp
#include <memory_resource>
#include <print>
#include <string>
#include <vector>

int main() {
  std::byte buffer[4096];
  std::pmr::monotonic_buffer_resource pool(buffer, sizeof(buffer));

  // リソースを渡すだけ
  std::pmr::vector<std::pmr::string> names(&pool);
  names.emplace_back("Hero, the brave warrior of the northern kingdom");

  std::println("コンテナのリソース: {}", names.get_allocator().resource() == &pool);
  std::println("要素の文字列も同じ: {}", names[0].get_allocator().resource() == &pool);

  // 既定のリソースは new / delete
  std::pmr::vector<int> def;
  std::println("既定: {}", def.get_allocator().resource() == std::pmr::new_delete_resource());
}
```

```text title="実行結果"
コンテナのリソース: true
要素の文字列も同じ: true
既定: true
```

## ゲームでの使いどころ

フレーム用のアリーナから確保するコンテナを、関数の引数に使う型（`std::pmr::vector<T>`）のまま、取り先だけ変えられる、という使い方をします。

## よくあるミス

??? failure "リソースより長くコンテナを生かす"
    コンテナの破棄時に、消えたリソースへ解放して壊れます。

??? failure "pmr でないコンテナに混ぜる"
    `std::vector<std::pmr::string>` の要素は、リソースが伝わりません。外側も `pmr::vector` にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`memory_resource`](memory_resource.md) | 取り先の基底クラス |
| [`pmr_containers`](pmr_containers.md) | `pmr` のコンテナ |
| `std::allocator` | 型に取り先が固定される |

## コンパイラ対応

C++17 から使えます。

## 関連ページ

- [cpprefjp: std::pmr::polymorphic_allocator](https://cpprefjp.github.io/reference/memory_resource/polymorphic_allocator.html)
- [cppreference: std::pmr::polymorphic_allocator](https://en.cppreference.com/w/cpp/memory/polymorphic_allocator)
