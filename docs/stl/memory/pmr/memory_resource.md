---
title: std::pmr::memory_resource
summary: "メモリの取り先を表す、抽象基底クラス。"
order: 7
group: pmr のメモリリソースと部品
tags:
  - メモリ
---

# std::pmr::memory_resource

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <memory_resource>`
</div>

`std::pmr::memory_resource` は、**メモリの取り先を表す基底クラス**です。`monotonic_buffer_resource` などはこれを継承しています。自分で派生クラスを作れば、独自のメモリ管理（ゲーム用のアリーナなど）を pmr に載せられます。

!!! tip "ポイント"
    - `do_allocate` / `do_deallocate` / `do_is_equal` の 3 つを実装すると、自作のリソースになる。
    - ポインターで渡すので、寿命に注意。

!!! info "このページを読む前に"
    [`std::pmr`](../pmr.md) の概要を先に読んでください。

## 関数の詳しい説明

### memory_resource {#memory_resource}

```cpp
class memory_resource {
 public:
  void* allocate(std::size_t bytes, std::size_t alignment = alignof(std::max_align_t));
  void deallocate(void* p, std::size_t bytes, std::size_t alignment = alignof(std::max_align_t));
  bool is_equal(const memory_resource& other) const noexcept;

 private:
  virtual void* do_allocate(std::size_t bytes, std::size_t alignment) = 0;
  virtual void do_deallocate(void* p, std::size_t bytes, std::size_t alignment) = 0;
  virtual bool do_is_equal(const memory_resource& other) const noexcept = 0;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `bytes` | `std::size_t` | 確保するバイト数（**要素の数ではない**） |
| `alignment` | `std::size_t` | 置き場所の約束（2 の累乗）。デフォルトは一番大きい型の約束 |
| `p` | `void*` | `allocate` が返したポインタ |

- 自作のリソースを作るときの基底クラスです。3 つの `do_` 関数を実装します
- 戻り値: `allocate` は `bytes` 個の生のメモリへのポインタ
- **アロケータとの違い:** アロケータは `T` の数で確保しますが、`memory_resource` は**バイト数とアラインメント**で確保します

```cpp
#include <cstddef>
#include <memory_resource>
#include <print>

// 確保の回数を数えながら、上流に任せるリソース
class CountingResource : public std::pmr::memory_resource {
 public:
  explicit CountingResource(std::pmr::memory_resource* upstream) : upstream_(upstream) {}
  int allocations() const { return allocations_; }

 private:
  void* do_allocate(std::size_t bytes, std::size_t alignment) override {
    ++allocations_;
    return upstream_->allocate(bytes, alignment);
  }
  void do_deallocate(void* p, std::size_t bytes, std::size_t alignment) override {
    upstream_->deallocate(p, bytes, alignment);
  }
  bool do_is_equal(const memory_resource& other) const noexcept override {
    return this == &other;
  }

  std::pmr::memory_resource* upstream_;
  int allocations_ = 0;
};

int main() {
  CountingResource counter(std::pmr::new_delete_resource());
  std::pmr::vector<int> v(&counter);
  v.reserve(100);
  std::println("確保 {} 回", counter.allocations());
}
```

```text title="実行結果"
確保 1 回
```

### allocate {#allocate}

```cpp
void* allocate(std::size_t bytes, std::size_t alignment = alignof(std::max_align_t));
```

- 計算量: リソースによる

`bytes` バイトのメモリを確保します。内部で、派生クラスの `do_allocate` を呼びます。失敗すると例外を投げます。

### deallocate {#deallocate}

```cpp
void deallocate(void* p, std::size_t bytes, std::size_t alignment = alignof(std::max_align_t));
```

- 計算量: リソースによる

`allocate` で確保したメモリを返します。内部で、派生クラスの `do_deallocate` を呼びます。

### is_equal {#is_equal}

```cpp
bool is_equal(const memory_resource& other) const noexcept;
```

- 計算量: 定数

2 つのリソースが、互いのメモリを解放できる（同じ）ものなら `true`。

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 自作のアリーナを pmr に対応させる | `class MyArena : public std::pmr::memory_resource` |

## よくあるミス

??? failure "do_is_equal を適当に書く"
    異なるリソースを同じと判定すると、解放先を取り違えます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`polymorphic_allocator`](polymorphic_allocator.md) | リソースを使うアロケータ |

## コンパイラ対応

C++17 の機能です。主要なコンパイラで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] メモリの取り先の基底クラス
    - [x] 3 つの do_ を実装
    - [x] 自作リソースを作れる

## 関連ページ

- [cpprefjp: std::pmr::memory_resource](https://cpprefjp.github.io/reference/memory_resource/memory_resource.html)
- [cppreference: std::pmr::memory_resource](https://en.cppreference.com/w/cpp/memory/memory_resource)
