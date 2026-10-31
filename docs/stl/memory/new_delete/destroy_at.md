---
title: std::destroy_at
summary: "オブジェクトのデストラクターを呼ぶ（メモリは解放しない）。"
order: 7
group: new / delete まわり
tags:
  - メモリ
---

# std::destroy_at

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <memory>`
</div>

確保済みのメモリの上に作ったオブジェクトは、`delete` では壊せません（メモリは別の方法で確保したため）。デストラクターだけを呼ぶ必要があります。`std::destroy_at(p)` は、`p->~T()` と同じで、メモリは解放しません。

!!! tip "ポイント"
    - デストラクターを呼ぶだけ。メモリは解放しない
    - `p->~T()` の書き方を、型名を書かずに済ませられる
    - `construct_at` / 配置 new と対で使う
    - C++20 から `constexpr`

!!! info "このページを読む前に"
    [`construct_at`](construct_at.md) を先に読んでください。

## 関数の詳しい説明

### std::destroy_at {#destroy_at}

<span class="ver ver-17">C++17</span>

```cpp
template <class T>
constexpr void destroy_at(T* p);
```

`T` が配列型のときは、各要素を壊します（C++20）。

デストラクターが自明な型（`int` など）なら、何もしません。

`destroy_at` を呼んだあとの領域は、オブジェクトの寿命が終わった生のメモリです。同じ領域に、また `construct_at` で作れます。壊したあとのオブジェクトを読むと、未定義動作です。

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

int main() {
  alignas(Tracer) unsigned char buf[sizeof(Tracer)];
  Tracer* p = std::construct_at(reinterpret_cast<Tracer*>(buf));
  std::println("作った: {}", Tracer::alive);

  std::destroy_at(p);
  std::println("壊した: {}", Tracer::alive);

  // 同じ領域に作り直せる
  p = std::construct_at(reinterpret_cast<Tracer*>(buf));
  std::println("作り直した: {}", Tracer::alive);
  std::destroy_at(p);
}
```

```text title="実行結果"
作った: 1
壊した: 0
作り直した: 1
```

## ゲームでの使いどころ

メモリ プールから取ったオブジェクトを返却するときに、デストラクターを呼ぶために使います。

## よくあるミス

??? failure "delete p を呼ぶ"
    メモリを自分で確保していないので、未定義動作です。

??? failure "壊した後に使う"
    寿命が終わっています。

## 類似

| 名前 | 違い |
| --- | --- |
| [`construct_at`](construct_at.md) | 作る側 |
| [`destroy`](destroy.md) | 範囲を壊す |
| [`destroy_n`](destroy_n.md) | 個数を指定して壊す |

## コンパイラ対応

C++17 から使えます。

## 関連ページ

- [cpprefjp: std::destroy_at](https://cpprefjp.github.io/reference/new/destroy_at.html)
- [cppreference: std::destroy_at](https://en.cppreference.com/w/cpp/memory/new/destroy_at)
