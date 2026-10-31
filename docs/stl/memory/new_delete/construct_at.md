---
title: std::construct_at
summary: "確保済みのメモリの上に、オブジェクトを作る（配置 new の安全版）。"
order: 6
group: new / delete まわり
tags:
  - メモリ
---

# std::construct_at

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <memory>`
</div>

確保済みのメモリの上にオブジェクトを作るには、配置 new（`new (p) T(args)`）を使いますが、書き方が独特で、`constexpr` の関数の中では使えません。C++20 の `std::construct_at(p, args...)` は、同じことを関数として書け、`constexpr` の中でも使えます。

!!! tip "ポイント"
    - `std::construct_at(p, args...)` は、`p` の位置に `T(args...)` を作る
    - 確保はしない。メモリは自分で用意する
    - 壊すときは `std::destroy_at(p)`
    - `constexpr`。コンパイル時の計算でも使える

!!! info "このページを読む前に"
    [配置 new](placement_new.md) を先に読んでください。

## 関数の詳しい説明

### std::construct_at {#construct_at}

<span class="ver ver-20">C++20</span>

```cpp
template <class T, class... Args>
constexpr T* construct_at(T* p, Args&&... args);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `T*` | オブジェクトを作る位置。生存期間が始まる前の領域 |
| `args` | コンストラクターの引数 | `T` を作る引数 |

`::new (static_cast<void*>(p)) T(std::forward<Args>(args)...)` と同じです。戻り値は `p` です。

引数が `T*` なので、型が合わないポインタは渡せません。配置 new は `void*` を受けるので、型の取り違えを許してしまいますが、`construct_at` は防ぎます。

波括弧の初期化（`T{...}`）ではなく、丸括弧で作ります。集成体の初期化が必要なら、C++20 の丸括弧による集成体の初期化が使えます。

## 実際に動かしてみる

```cpp
#include <memory>
#include <new>
#include <print>

struct Tracer {
  static inline int alive = 0;
  Tracer() { ++alive; }
  Tracer(const Tracer&) { ++alive; }
  Tracer(Tracer&&) noexcept { ++alive; }
  ~Tracer() { --alive; }
};

struct Player {
  Player(int hp, int mp) : hp(hp), mp(mp) { ++Tracer::alive; }
  ~Player() { --Tracer::alive; }
  int hp;
  int mp;
};

int main() {
  alignas(Player) unsigned char buf[sizeof(Player)];
  Player* p = std::construct_at(reinterpret_cast<Player*>(buf), 30, 12);
  std::println("hp={} mp={} 生きている数={}", p->hp, p->mp, Tracer::alive);

  std::destroy_at(p);
  std::println("壊した: {}", Tracer::alive);
}
```

```text title="実行結果"
hp=30 mp=12 生きている数=1
壊した: 0
```

## ゲームでの使いどころ

自作のメモリ プールや、固定長のバッファの上に、オブジェクトを作るときに使います。

## よくあるミス

??? failure "メモリの確保を忘れる"
    `construct_at` は確保しません。バッファは自分で用意します。

??? failure "アライメントを守らない"
    `alignas(T)` で、型のアライメントを満たす領域にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [配置 new](placement_new.md) | 従来の書き方 |
| [`destroy_at`](destroy_at.md) | 壊す側 |
| `std::allocator_traits::construct` | アロケーター経由 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::construct_at](https://cpprefjp.github.io/reference/new/construct_at.html)
- [cppreference: std::construct_at](https://en.cppreference.com/w/cpp/memory/new/construct_at)
