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

`std::make_shared<T>(args...)` は、制御ブロックとオブジェクトを、標準のアロケーターで 1 回の確保にまとめて作ります。独自のアロケーター（メモリ プール、`pmr` のリソース）で確保したいときは、`std::allocate_shared<T>(alloc, args...)` を使います。`make_shared` のアロケーター指定版です。

!!! tip "ポイント"
    - 第 1 引数にアロケーターを渡す
    - 制御ブロックとオブジェクトを、そのアロケーターで 1 回の確保にまとめる
    - 解放も、同じアロケーターで行われる
    - `pmr` のアロケーターと組み合わせると、メモリ プールに入れられる

!!! info "このページを読む前に"
    [`std::shared_ptr`](shared_ptr.md) と、アロケーター（[メモリ](../memory/allocator.md)）を先に読んでください。

## 関数の詳しい説明

### std::allocate_shared {#allocate_shared}

<span class="ver ver-11">C++11</span>

```cpp
template <class T, class Alloc, class... Args>
std::shared_ptr<T> allocate_shared(const Alloc& alloc, Args&&... args);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `alloc` | アロケーター | 確保に使うアロケーター |
| `args` | コンストラクターの引数 | `T` を作る引数 |

`alloc` を、制御ブロックとオブジェクトを合わせた型に再束縛（`rebind`）して、1 回の確保を行います。`shared_ptr` が破棄されるときは、同じアロケーターで解放します。

アロケーターは、制御ブロックの中にコピーして保存されます。アロケーターが状態を持つ（メモリ プールへのポインタなど）なら、そのコピーが、解放のときにも使われます。

標準の `std::allocator<T>` を渡すと、`make_shared` と同じ動作です。`pmr::polymorphic_allocator<T>` を渡せば、`pmr` のメモリ リソース（単調増加バッファなど）から確保できます。

C++20 から、配列の `T[]` や `T[N]` も扱えます。

## 実際に動かしてみる

```cpp
#include <memory>
#include <memory_resource>
#include <print>

struct Enemy {
  Enemy(int hp, int power) : hp(hp), power(power) {}
  int hp;
  int power;
};

int main() {
  // 標準のアロケーター: make_shared と同じ動き
  auto a = std::allocate_shared<Enemy>(std::allocator<Enemy>(), 10, 3);
  std::println("hp={} power={}", a->hp, a->power);

  // pmr: 固定のバッファから確保する
  std::byte buffer[256];
  std::pmr::monotonic_buffer_resource pool(buffer, sizeof(buffer));
  std::pmr::polymorphic_allocator<Enemy> alloc(&pool);

  auto b = std::allocate_shared<Enemy>(alloc, 20, 5);
  std::println("hp={} power={}", b->hp, b->power);

  // バッファの中に確保されている
  const auto* p = reinterpret_cast<const std::byte*>(b.get());
  std::println("バッファの中: {}", p >= buffer && p < buffer + sizeof(buffer));
}
```

```text title="実行結果"
hp=10 power=3
hp=20 power=5
バッファの中: true
```

`monotonic_buffer_resource` は、渡したバッファから順に確保します。`shared_ptr` が使う領域が、その内側に入っています。

## ゲームでの使いどころ

1 フレームだけ生きるオブジェクトを、フレーム用のメモリ プールから確保して、フレームの終わりにまとめて破棄するときに使います。

## よくあるミス

??? failure "プールを先に破棄する"
    `shared_ptr` が生きている間は、プールも生かします。プールが先に消えると、解放が壊れます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::make_shared`](make_shared.md) | 標準のアロケーター |
| `std::pmr::polymorphic_allocator` | 実行時にメモリ リソースを選べるアロケーター |
| `std::allocate_unique` | C++ に標準では存在しない（自作する） |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::allocate_shared](https://cpprefjp.github.io/reference/memory/allocate_shared.html)
- [cppreference: std::allocate_shared](https://en.cppreference.com/w/cpp/memory/shared_ptr/allocate_shared)
