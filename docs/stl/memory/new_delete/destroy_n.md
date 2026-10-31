---
title: std::destroy_n
summary: "先頭から n 個のオブジェクトのデストラクタを呼ぶ。"
order: 900
group: new / delete まわり
tags:
  - メモリ
---

# std::destroy_n

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <memory>`
</div>

`destroy` が範囲で壊すのに対し、`std::destroy_n(first, n)` は、先頭から `n` 個を壊し、壊したあとの次の位置を返します。個数が分かっているコンテナで使います。

!!! tip "ポイント"
    - 先頭から `n` 個のデストラクターを呼ぶ
    - 戻り値は、壊した最後の要素の次の位置
    - `destroy(first, first + n)` と同じ働き
    - メモリは解放しない

!!! info "このページを読む前に"
    [`destroy`](destroy.md) を先に読んでください。

## 関数の詳しい説明

### std::destroy_n {#destroy_n}

<span class="ver ver-17">C++17</span>

```cpp
template <class ForwardIt, class Size>
constexpr ForwardIt destroy_n(ForwardIt first, Size n);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `first` | 前方イテレータ | 先頭 |
| `n` | 整数 | 壊す個数 |

`n` が 0 や負なら、何もせず `first` を返します。

戻り値を使うと、壊した範囲の続きから、次の処理を始められます。

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
  auto* p = reinterpret_cast<Tracer*>(buf);
  for (int i = 0; i < 3; ++i) std::construct_at(p + i);

  auto* end = std::destroy_n(p, 3);
  std::println("生きている数: {} 次の位置までの距離: {}", Tracer::alive, end - p);
}
```

```text title="実行結果"
生きている数: 0 次の位置までの距離: 3
```

## ゲームでの使いどころ

個数を保持する自作のコンテナのデストラクターで使います。

## よくあるミス

??? failure "n が実際に作った数より大きい"
    作っていない領域を壊して、未定義動作になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`destroy`](destroy.md) | 範囲で指定する |
| [`destroy_at`](destroy_at.md) | 1 つ |

## コンパイラ対応

C++17 から使えます。

## 関連ページ

- [cpprefjp: std::destroy_n](https://cpprefjp.github.io/reference/memory/destroy_n.html)
- [cppreference: std::destroy_n](https://en.cppreference.com/w/cpp/memory/destroy_n)
