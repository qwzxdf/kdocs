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

ゲームでは、フレームごとに使い捨てるメモリや、ステージの間だけ生きるメモリなど、寿命の違う領域を使い分けたくなります。`std::pmr::memory_resource` は、「メモリの取り先」を表す基底クラスで、`pmr` のコンテナ（`std::pmr::vector` など）に渡すと、その取り先から確保します。自分で派生クラスを作れば、独自のアリーナ アロケーターを `pmr` に載せられます。

!!! tip "ポイント"
    - `allocate` / `deallocate` / `is_equal` の 3 つの公開関数と、実装する 3 つの `do_` 関数
    - コンテナの型を変えずに、取り先を変えられる
    - ポインターで渡す。リソースはコンテナより長く生かす
    - 標準のリソース: `new_delete_resource`、`monotonic_buffer_resource`、プール

!!! info "このページを読む前に"
    [`std::pmr`](../pmr.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::pmr::memory_resource {#memory_resource}

<span class="ver ver-17">C++17</span>

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

`allocate` は `do_allocate` を、`deallocate` は `do_deallocate` を呼ぶだけです。派生クラスは `do_` 側を実装します。

`do_allocate` は、`bytes` バイトを `alignment` の境界で返し、確保できなければ `std::bad_alloc` を投げます。`do_deallocate` は、`allocate` で返した領域を、同じ `bytes` と `alignment` で受け取ります。大きさを渡してくれるので、アロケーター側に大きさを記録する手間がありません。

`do_is_equal` は、「2 つのリソースが、互いのメモリを解放できるか」を答えます。普通は `this == &other` です。

コピーできず、ポインターで扱うので、リソースの寿命の管理は、使う側の責任です。コンテナよりリソースを先に破棄すると、コンテナの解放が壊れます。

## 実際に動かしてみる

```cpp
#include <memory_resource>
#include <print>
#include <vector>

// 確保の回数を数える、自作のリソース
class CountingResource : public std::pmr::memory_resource {
 public:
  explicit CountingResource(std::pmr::memory_resource* up) : upstream_(up) {}
  int allocations() const { return allocations_; }

 private:
  void* do_allocate(std::size_t bytes, std::size_t align) override {
    ++allocations_;
    return upstream_->allocate(bytes, align);
  }
  void do_deallocate(void* p, std::size_t bytes, std::size_t align) override {
    upstream_->deallocate(p, bytes, align);
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
  for (int i = 0; i < 100; ++i) v.push_back(i);

  std::println("要素数: {}", v.size());
  std::println("確保した: {}", counter.allocations() > 0);
}
```

```text title="実行結果"
要素数: 100
確保した: true
```

## ゲームでの使いどころ

1 フレームだけ使う一時データ用のアリーナや、確保の統計を取るデバッグ用のリソースを作るときに、派生クラスを書きます。

## よくあるミス

??? failure "リソースを先に破棄する"
    コンテナの解放が、消えたリソースを使って壊れます。コンテナより長く生かします。

??? failure "do_deallocate で大きさを無視して別の領域に解放する"
    `allocate` と同じ大きさ・アライメントで返ってくる前提で作ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`polymorphic_allocator`](polymorphic_allocator.md) | コンテナが使うアロケーター |
| [`monotonic_buffer_resource`](monotonic_buffer_resource.md) | 単調増加のリソース |
| [`new_delete_resource`](new_delete_resource.md) | グローバルな new / delete |

## コンパイラ対応

C++17 から使えます。

## 関連ページ

- [cpprefjp: std::pmr::memory_resource](https://cpprefjp.github.io/reference/memory_resource/memory_resource.html)
- [cppreference: std::pmr::memory_resource](https://en.cppreference.com/w/cpp/memory/memory_resource)
