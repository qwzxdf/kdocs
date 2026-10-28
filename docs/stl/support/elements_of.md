---
title: std::ranges::elements_of
summary: "generator の中で、別の範囲の要素を全部取り出す目印。"
order: 900
tags:
  - 型・言語サポート
---

# std::ranges::elements_of

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <generator>`
</div>

`generator` の中で、別の `generator` や `vector` の要素を全部出したいことがあります。`for` で 1 つずつ `co_yield` するのは冗長です。`co_yield std::ranges::elements_of(range)` と書くと、範囲の要素を全部取り出せます。再帰的な木の探索で、子の結果をまとめて出すのに便利です。

!!! tip "ポイント"
    - `co_yield` の中で使う。
    - 別の `generator` を渡すと、再帰が効率よく展開される。
    - C++23 の機能。

!!! info "このページを読む前に"
    [`std::generator`](generator.md) を先に読んでください。

## 関数の詳しい説明

### std::ranges::elements_of {#elements_of}

```cpp
template <ranges::range R, class Allocator = allocator<void>>
elements_of(R&&, Allocator = {}) -> elements_of<R&&, Allocator>;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `range` | 範囲 | 展開する範囲 |

- 戻り値: `co_yield` に渡す目印
- 計算量: 要素数に比例


## 実際に動かしてみる

```cpp
#include <generator>
#include <print>
#include <ranges>

std::generator<int> Inner() {
  co_yield 1;
  co_yield 2;
}

std::generator<int> Outer() {
  co_yield 0;
  co_yield std::ranges::elements_of(Inner());
  co_yield 3;
}

int main() {
  int sum = 0;
  for (int x : Outer()) sum += x;
  std::println("{}", sum);
}
```

```text title="実行結果"
6
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 木を深さ優先でたどる | `co_yield std::ranges::elements_of(Walk(child));` |

## よくあるミス

??? failure "`generator` の外で使う"
    コルーチンの中（`co_yield`）でだけ使えます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::generator`](generator.md) | generator の本体 |

## コンパイラ対応

C++23 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 別の範囲の要素を全部取り出す
    - [x] co_yield と使う
    - [x] 再帰の展開に便利

## 関連ページ

- [cpprefjp: std::ranges::elements_of](https://cpprefjp.github.io/reference/generator/elements_of.html)
- [cppreference: std::ranges::elements_of](https://en.cppreference.com/w/cpp/coroutine/elements_of)
