---
title: std::scoped_allocator_adaptor
summary: "入れ子のコンテナの全体に、同じアロケータを渡してくれる。"
order: 900
tags:
  - メモリ
---

# std::scoped_allocator_adaptor

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <memory>`
</div>

`std::vector<std::vector<int>>` に、独自のアロケーターを指定しても、外側の `vector` が使うだけで、中の `vector<int>` は標準のアロケーターに戻ります。`std::scoped_allocator_adaptor` は、外側のアロケーターを、入れ子の要素にも伝えるためのアダプターです。

!!! tip "ポイント"
    - 外側のコンテナのアロケーターを、要素の構築にも渡す
    - `scoped_allocator_adaptor<外側, 内側...>` の形
    - 入れ子の段数ぶん、アロケーターを指定できる
    - `pmr` のコンテナは、この仕組みなしで、自動で伝わる

!!! info "このページを読む前に"
    [`std::allocator`](allocator.md) など、アロケーターの基本を先に読んでください。

## 関数の詳しい説明

### std::scoped_allocator_adaptor {#scoped_allocator_adaptor}

<span class="ver ver-11">C++11</span>

```cpp
template <class OuterAlloc, class... InnerAllocs>
class scoped_allocator_adaptor;
```

要素を構築する `construct` が、`uses_allocator` を調べ、要素がアロケーターを受け取れるなら、内側のアロケーターを渡して作ります。内側を指定しなければ、外側と同じものが使われます。

`std::vector<std::vector<int, A>, std::scoped_allocator_adaptor<A>>` のように、外側のコンテナのアロケーターの型を `scoped_allocator_adaptor` で包むだけで、中の `vector` にも同じアロケーターが伝わります。

C++17 で `std::pmr::polymorphic_allocator` が入ったあとは、同じ目的に `pmr` を使うほうが簡単です。`pmr::vector<pmr::vector<int>>` は、何もしなくても、外側のリソースが伝わります。

## 実際に動かしてみる

```cpp
#include <memory>
#include <print>
#include <scoped_allocator>
#include <vector>

int g_allocs = 0;

// 確保の回数を数えるアロケーター
template <class T>
struct CountingAlloc {
  using value_type = T;
  CountingAlloc() = default;
  template <class U>
  CountingAlloc(const CountingAlloc<U>&) {}
  T* allocate(std::size_t n) {
    ++g_allocs;
    return std::allocator<T>().allocate(n);
  }
  void deallocate(T* p, std::size_t n) { std::allocator<T>().deallocate(p, n); }
  template <class U>
  bool operator==(const CountingAlloc<U>&) const { return true; }
};

int main() {
  using Inner = std::vector<int, CountingAlloc<int>>;
  using Outer = std::vector<Inner, std::scoped_allocator_adaptor<CountingAlloc<Inner>>>;

  Outer outer;
  outer.reserve(1);                  // 外側の確保: 1 回
  outer.emplace_back();              // 中の vector を作る
  const int before = g_allocs;
  outer[0].push_back(1);             // 中の vector の確保が、数えられる
  std::println("中の vector の確保も数えられた: {}", g_allocs > before);
}
```

```text title="実行結果"
中の vector の確保も数えられた: true
```

## ゲームでの使いどころ

C++17 以降は `pmr` を使うほうが簡単です。古いコードや、`pmr` を使えない環境で、入れ子のコンテナにアロケーターを伝えるときに使います。

## よくあるミス

??? failure "外側だけにアロケーターを指定する"
    中の要素には伝わりません。`scoped_allocator_adaptor` で包みます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`polymorphic_allocator`](pmr/polymorphic_allocator.md) | 自動で伝わる |
| [`uses_allocator`](uses_allocator.md) | 判定 |
| [`allocator_traits`](allocator_traits.md) | アロケーターの共通の窓口 |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::scoped_allocator_adaptor](https://cpprefjp.github.io/reference/scoped_allocator/scoped_allocator_adaptor.html)
- [cppreference: std::scoped_allocator_adaptor](https://en.cppreference.com/w/cpp/memory/scoped_allocator_adaptor)
