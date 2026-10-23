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

`std::allocator_traits<Alloc>` は、**アロケータの機能（確保、解放、構築、破棄）を、足りない関数を自動で補いながら、一様に使えるようにする窓口**です。自作のアロケーターは `allocate` と `deallocate` だけ書けば、残りは `allocator_traits` が補ってくれます。コンテナの内部で、アロケーターを使うときの入口です。

!!! tip "ポイント"
    - 自作のアロケーターは最低限 `allocate` / `deallocate` と `value_type` だけでよい。
    - コンテナは、アロケーターを直接ではなく、`allocator_traits` 経由で使う。
    - 自分で使うのは、自作コンテナを作るとき。

!!! info "このページを読む前に"
    - [stl/index.md](../index.md)（STL 全体の地図（どこに何があるか））
    - [所有権（誰が消すのか）](../../basics/ownership.md)（所有権の考え方）

## 関数の詳しい説明

### std::allocator_traits {#allocator_traits}

```cpp
template <class Alloc>
struct allocator_traits {
  static pointer allocate(Alloc& a, size_type n);
  static void deallocate(Alloc& a, pointer p, size_type n);
  template <class T, class... Args>
  static void construct(Alloc& a, T* p, Args&&... args);
  template <class T> static void destroy(Alloc& a, T* p);
};
```

- 戻り値: （静的関数の集まり）
- 計算量: アロケーターによる

```cpp
#include <memory>
#include <print>

int main() {
  std::allocator<int> alloc;
  using Traits = std::allocator_traits<std::allocator<int>>;

  int* p = Traits::allocate(alloc, 1);   // 1 個ぶんのメモリ（未初期化）
  Traits::construct(alloc, p, 7);        // その上にオブジェクトを作る
  std::println("{}", *p);
  Traits::destroy(alloc, p);
  Traits::deallocate(alloc, p, 1);
}
```

```text title="実行結果"
7
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 自作コンテナを、どんなアロケーターでも使えるようにする | `allocator_traits<Alloc>::allocate(...)` |

## よくあるミス

??? failure "アロケーターの関数を直接呼ぶ"
    自作のアロケーターには `construct` が無いことがあります。`allocator_traits` 経由なら補われます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::allocator`](allocator.md) | 標準のアロケーター |
| [`std::pmr`](pmr.md) | 実行時に切り替えられる |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] アロケーターの窓口
    - [x] 足りない関数を補う
    - [x] コンテナの内部で使われる

## 関連ページ

- [cpprefjp: std::allocator_traits](https://cpprefjp.github.io/reference/memory/allocator_traits.html)
- [cppreference: std::allocator_traits](https://en.cppreference.com/w/cpp/memory/allocator_traits)
