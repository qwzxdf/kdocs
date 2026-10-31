---
title: std::uninitialized_default_construct
summary: "未初期化のメモリに、デフォルト初期化でオブジェクトを作る。"
order: 900
group: new / delete まわり
tags:
  - メモリ
---

# std::uninitialized_default_construct

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <memory>`
</div>

生のメモリの範囲に、既定の構築でオブジェクトを作りたい。`std::uninitialized_default_construct(first, last)` は、各位置に `T` を既定の初期化で作ります。`int` のような基本型は、値が初期化されません。

!!! tip "ポイント"
    - 既定の初期化で作る。基本型は不定の値
    - 値を 0 などで初期化したいなら `uninitialized_value_construct`
    - 速度が要る場面で、無駄な初期化を避けられる
    - 途中で例外が出たら、作ったものを壊す

!!! info "このページを読む前に"
    [`uninitialized_fill`](uninitialized_fill.md) を先に読んでください。

## 関数の詳しい説明

### std::uninitialized_default_construct {#uninitialized_default_construct}

<span class="ver ver-17">C++17</span>

```cpp
template <class ForwardIt>
void uninitialized_default_construct(ForwardIt first, ForwardIt last);
```

`::new (p) T` と同じです。クラスなら既定のコンストラクターが呼ばれますが、`int` などの基本型には、何も起きません。

`vector<int> v(1000)` が、全要素を 0 で初期化するのに対し、これを使うと、初期化を省けます。あとで全要素を上書きすることが分かっているなら、時間の節約になります。ただし、読む前に書き込まないと、不定の値を読みます。

`_n` 版（`uninitialized_default_construct_n`）が、個数を指定する形です。

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
  alignas(Tracer) unsigned char buf[sizeof(Tracer) * 3];
  auto* first = reinterpret_cast<Tracer*>(buf);

  std::uninitialized_default_construct(first, first + 3);
  std::println("既定の構築で作った: {}", Tracer::alive);

  std::destroy(first, first + 3);
  std::println("壊した: {}", Tracer::alive);
}
```

```text title="実行結果"
既定の構築で作った: 3
壊した: 0
```

## ゲームでの使いどころ

直後に全要素を書き込む大きなバッファの確保で、初期化の時間を省くために使います。

## よくあるミス

??? failure "基本型の値を読む"
    初期化されていません。書き込んでから読みます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`uninitialized_value_construct`](uninitialized_value_construct.md) | 値初期化で作る |
| [`uninitialized_fill`](uninitialized_fill.md) | 同じ値のコピーで作る |

## コンパイラ対応

C++17 から使えます。

## 関連ページ

- [cpprefjp: std::uninitialized_default_construct](https://cpprefjp.github.io/reference/memory/uninitialized_default_construct.html)
- [cppreference: std::uninitialized_default_construct](https://en.cppreference.com/w/cpp/memory/uninitialized_default_construct)
