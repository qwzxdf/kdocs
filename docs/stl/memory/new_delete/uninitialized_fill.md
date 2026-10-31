---
title: std::uninitialized_fill
summary: "未初期化のメモリの範囲を、同じ値のコピーで埋める。"
order: 900
group: new / delete まわり
tags:
  - メモリ
---

# std::uninitialized_fill

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <memory>`
</div>

生のメモリの範囲に、同じ値のコピーを作りたい。`std::uninitialized_fill(first, last, value)` は、`[first, last)` の各位置に、`value` のコピーを（コンストラクターで）作ります。`std::fill` と違い、領域はまだオブジェクトがない生のメモリです。

!!! tip "ポイント"
    - 生のメモリに、同じ値のコピーを作る
    - 途中でコンストラクターが例外を投げたら、作ったものを壊してから伝える
    - `std::fill`（作成済みのオブジェクトへの代入）とは別物
    - 壊すときは `destroy`

!!! info "このページを読む前に"
    [`construct_at`](construct_at.md) と [`destroy`](destroy.md) を先に読んでください。

## 関数の詳しい説明

### std::uninitialized_fill {#uninitialized_fill}

<span class="ver ver-11">C++98〜</span>

```cpp
template <class ForwardIt, class T>
void uninitialized_fill(ForwardIt first, ForwardIt last, const T& value);
```

`std::vector<T>(n, value)` が、内部で確保した領域を埋めるときに使う関数です。

`std::fill` との違いは、対象の状態です。`fill` は、すでにオブジェクトがある領域への代入です。`uninitialized_fill` は、オブジェクトがない領域に、新しく作ります。ない領域に代入すると、壊れたオブジェクトに代入することになります。

例外の保証があります。途中の要素のコンストラクターが例外を投げると、それまでに作った要素を全部壊してから、例外が伝わります。部分的に作られた状態は残りません。

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
  alignas(Tracer) unsigned char buf[sizeof(Tracer) * 4];
  auto* first = reinterpret_cast<Tracer*>(buf);

  const Tracer proto;
  std::uninitialized_fill(first, first + 4, proto);
  std::println("コピーを作った: {}", Tracer::alive);  // proto を含めて 5

  std::destroy(first, first + 4);
  std::println("壊した: {}", Tracer::alive);  // proto が 1 つ残る
}
```

```text title="実行結果"
コピーを作った: 5
壊した: 1
```

## ゲームでの使いどころ

自作の `vector` のような、容量を確保してから要素を作るコンテナで使います。

## よくあるミス

??? failure "fill と取り違える"
    生のメモリに `fill` を使うと、存在しないオブジェクトに代入します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`uninitialized_move`](uninitialized_move.md) | ムーブして作る |
| [`uninitialized_default_construct`](uninitialized_default_construct.md) | 既定の構築で作る |
| `std::fill` | 作成済みの要素に代入 |

## コンパイラ対応

C++98 から使えます。

## 関連ページ

- [cpprefjp: std::uninitialized_fill](https://cpprefjp.github.io/reference/memory/uninitialized_fill.html)
- [cppreference: std::uninitialized_fill](https://en.cppreference.com/w/cpp/memory/uninitialized_fill)
