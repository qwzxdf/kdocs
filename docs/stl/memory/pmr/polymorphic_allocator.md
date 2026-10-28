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

`std::pmr::polymorphic_allocator<T>` は、**実行時にメモリの取り先（メモリリソース）を切り替えられるアロケータ**です。`std::pmr::vector` などの pmr コンテナが内部で使っています。コンテナの型を変えずに取り先を変えられるのが特徴です。

!!! tip "ポイント"
    - 普通は直接使わず、`std::pmr::vector<int> v(&pool);` のようにリソースを渡すだけ。
    - リソースへのポインターを持つだけなので、コピーが軽い。
    - 自作のクラスでも、アロケータを受け取れば pmr に対応できる。

!!! info "このページを読む前に"
    [`std::pmr`](../pmr.md) の概要を先に読んでください。

## 関数の詳しい説明

### polymorphic_allocator {#polymorphic_allocator}

```cpp
template <class T>
class polymorphic_allocator {
 public:
  polymorphic_allocator() noexcept;                              // デフォルトのリソース
  polymorphic_allocator(memory_resource* r);                     // r を使う
  T* allocate(std::size_t n);
  void deallocate(T* p, std::size_t n);
  memory_resource* resource() const;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `r` | `std::pmr::memory_resource*` | 使うリソースへのポインタ（`nullptr` は不可） |

- 戻り値: `resource()` は持っているリソースへのポインタ
- 自作のクラスで「渡されたリソースを使ってメンバのコンテナを作りたい」ときは、コンストラクタに `std::pmr::memory_resource*` を受け取り、メンバのコンテナに渡します。
- **代入のとき、アロケータは移りません**（`propagate_on_*` が `false`）。`a = b` の後も、`a` は元のリソースを使い続けます。コピーされるのは要素だけです

### allocate {#allocate}

```cpp
T* allocate(std::size_t n);
```

- 計算量: リソースによる

`T` を `n` 個ぶんのメモリを内部のメモリリソースから確保します。

### deallocate {#deallocate}

```cpp
void deallocate(T* p, std::size_t n);
```

- 計算量: リソースによる

`allocate` で確保したメモリを返します。

### allocate_bytes {#allocate_bytes}

```cpp
void* allocate_bytes(std::size_t nbytes, std::size_t alignment = alignof(std::max_align_t));
```

- 計算量: リソースによる

バイト数と境界を指定して、生のメモリを確保します。

### deallocate_bytes {#deallocate_bytes}

```cpp
void deallocate_bytes(void* p, std::size_t nbytes, std::size_t alignment = alignof(std::max_align_t));
```

- 計算量: リソースによる

`allocate_bytes` で確保したメモリを返します。

### allocate_object {#allocate_object}

```cpp
template <class U>
U* allocate_object(std::size_t n = 1);
```

- 計算量: リソースによる

型 `U` を `n` 個ぶんのメモリを確保します（オブジェクトは作りません）。

### deallocate_object {#deallocate_object}

```cpp
template <class U>
void deallocate_object(U* p, std::size_t n = 1);
```

- 計算量: リソースによる

`allocate_object` で確保したメモリを返します。

### new_object {#new_object}

```cpp
template <class U, class... Args>
U* new_object(Args&&... args);
```

- 計算量: リソースによる + 構築

メモリを確保して、そこにオブジェクトを作ります。`new` のメモリリソース版です。

### delete_object {#delete_object}

```cpp
template <class U>
void delete_object(U* p);
```

- 計算量: リソースによる + 破棄

オブジェクトを破棄して、メモリを返します。`new_object` と対にします。

### construct {#construct}

```cpp
template <class U, class... Args>
void construct(U* p, Args&&... args);
```

- 計算量: 構築による

`p` の場所にオブジェクトを作ります。内部のメモリリソースを要素にも引き継ぎます（uses-allocator 構築）。

### resource {#resource}

```cpp
std::pmr::memory_resource* resource() const;
```

- 計算量: 定数

このアロケータが使っているメモリリソース。

### select_on_container_copy_construction {#select_on_container_copy_construction}

```cpp
polymorphic_allocator select_on_container_copy_construction() const;
```

- 計算量: 定数

コンテナをコピーするとき、コピー先が使うアロケータを返します。pmr では、既定のメモリリソースを使うアロケータです（元のリソースは引き継がれません）。

## 実際に動かしてみる

```cpp
#include <memory_resource>
#include <print>

int main() {
  std::pmr::monotonic_buffer_resource pool;
  std::pmr::polymorphic_allocator<int> alloc(&pool);

  int* p = alloc.new_object<int>(7);  // メモリの確保とオブジェクトの構築
  std::println("{}", *p);
  alloc.delete_object(p);
}
```

```text title="実行結果"
7
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| pmr コンテナにリソースを渡す | `std::pmr::vector<int> v(&pool);` |

## よくあるミス

??? failure "リソースを渡し忘れる"
    渡さないと、デフォルトのリソース（普通の new / delete）が使われます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::allocator`](../allocator.md) | 型ごとに取り先が決まる |
| [`memory_resource`](memory_resource.md) | 取り先の本体 |

## コンパイラ対応

C++17 の機能です。主要なコンパイラで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] リソースを実行時に切り替えるアロケータ
    - [x] 普段はリソースを渡すだけ
    - [x] コンテナの型が変わらない

## 関連ページ

- [cpprefjp: std::pmr::polymorphic_allocator](https://cpprefjp.github.io/reference/memory_resource/polymorphic_allocator.html)
- [cppreference: std::pmr::polymorphic_allocator](https://en.cppreference.com/w/cpp/memory/polymorphic_allocator)
