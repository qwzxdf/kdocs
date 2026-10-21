---
title: calloc
summary: "0 で初期化して、メモリを確保する。"
order: 22
group: C の確保関数（<cstdlib>）
tags:
  - メモリ
---

# calloc

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdlib>`
</div>

`calloc` は、**要素数と 1 つあたりのバイト数を指定して、0 で初期化したメモリを確保する**関数です。`malloc` に `memset` を足したものと同じですが、掛け算のオーバーフローも検出してくれます。

!!! tip "ポイント"
    - `calloc(個数, サイズ)` の 2 引数。
    - 中身は全ビット 0。
    - 失敗すると `nullptr`。

!!! info "このページを読む前に"
    [ポインタ](../../basics/pointer.md) が分かると読みやすいです。

## 関数の詳しい説明

### calloc {#calloc}

```cpp
void* calloc(std::size_t count, std::size_t size);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `count` | `std::size_t` | 要素の数 |
| `size` | `std::size_t` | 1 要素のバイト数 |

- 戻り値: `count * size` バイトの領域。**すべて 0 で埋められている**。失敗したら `nullptr`
- `malloc(count * size)` + 0 埋め、と同じ意味ですが、**`count * size` がオーバーフローするときは、失敗（`nullptr`）として扱ってくれる**のが安全な点です
- 整数や構造体の配列を 0 で始めたいときに便利です。ただし、**浮動小数点やポインタの「全ビット 0」が 0.0 / `nullptr` とは限らない**環境がありえます（実際の PC やゲーム機ではそうなっています）

## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <print>

int main() {
  int* p = static_cast<int*>(std::calloc(3, sizeof(int)));  // 0 で初期化される
  std::println("{} {} {}", p[0], p[1], p[2]);
  std::free(p);
}
```

```text title="実行結果"
0 0 0
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 0 で初期化した配列を C のAPI 向けに作る | `calloc(n, sizeof(Item))` |

## よくあるミス

??? failure "浮動小数点やポインターの 0 を前提にする"
    全ビット 0 が `0.0` や `nullptr` になるのが普通ですが、規格上の保証はありません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`malloc`](malloc.md) | 初期化しない |
| [`free`](free.md) | 解放 |

## コンパイラ対応

C 由来の関数です。`aligned_alloc` は C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 0 初期化つきで確保
    - [x] 2 引数
    - [x] `free` で解放

## 関連ページ

- [cpprefjp: calloc](https://cpprefjp.github.io/reference/cstdlib/calloc.html)
- [cppreference: calloc](https://en.cppreference.com/w/cpp/memory/c/calloc)
