---
title: std::allocate_shared
summary: "アロケータを指定して、オブジェクトを作って shared_ptr にする。"
order: 52
tags:
  - ユーティリティ
---

# std::allocate_shared

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <memory>`
</div>

`std::allocate_shared` は、[`make_shared`](make_shared.md) の「アロケータを指定する版」です。メモリの確保先（フレーム用の領域、プール）を自分で選べます。ゲームでは、メモリプールから `shared_ptr` を作りたいときに使います。

!!! tip "ポイント"
    - `std::allocate_shared<T>(アロケータ, 引数...)`。
    - 本体と参照カウントを、指定したアロケータから 1 回で確保する。
    - 普通の `make_shared` で足りるなら、使わなくてよい。

!!! info "このページを読む前に"
    - [stl/index.md](../index.md)（STL 全体の地図（どこに何があるか））
    - [ムーブ（コピーとムーブ）](../../basics/move.md)（ムーブの基礎）

## 関数の詳しい説明

### std::allocate_shared {#allocate_shared}

```cpp
template <class T, class Alloc, class... Args>
std::shared_ptr<T> allocate_shared(const Alloc& alloc, Args&&... args);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `alloc` | アロケータ | メモリの確保先 |
| `args...` | 可変個 | コンストラクタの引数 |

- 戻り値: `T` を指す `shared_ptr`
- 計算量: 確保 1 回 + コンストラクタ

```cpp
#include <memory>
#include <memory_resource>
#include <print>

int main() {
  std::pmr::monotonic_buffer_resource pool;           // 使い捨てのメモリ領域
  std::pmr::polymorphic_allocator<int> alloc(&pool);

  auto p = std::allocate_shared<int>(alloc, 42);      // pool から確保する
  std::println("{}", *p);
}
```

```text title="実行結果"
42
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 専用のメモリプールから共有オブジェクトを作る | `allocate_shared<Particle>(pool_allocator)` |

## よくあるミス

??? failure "アロケータより長生きする"
    `shared_ptr` が使うメモリは、アロケータから出ます。アロケータ（プール）を先に破棄すると、あとで解放できません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::make_shared`](make_shared.md) | 普通のアロケータで作る |
| [`std::pmr`](../memory/pmr.md) | アロケータの切り替えを楽にする仕組み |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] アロケータを指定して `shared_ptr` を作る
    - [x] プールからの確保に使う
    - [x] アロケータの寿命に注意

## 関連ページ

- [cpprefjp: std::allocate_shared](https://cpprefjp.github.io/reference/memory/allocate_shared.html)
- [cppreference: std::allocate_shared](https://en.cppreference.com/w/cpp/memory/shared_ptr/allocate_shared)
