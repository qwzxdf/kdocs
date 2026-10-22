---
title: std::assume_aligned
summary: "ポインタが N バイト境界にあると、コンパイラに約束する。"
order: 900
tags:
  - メモリ
---

# std::assume_aligned

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <memory>`
</div>

SIMD などで配列を速く処理するとき、コンパイラは「先頭アドレスが 16 バイト境界か」を知らないと、保守的なコードを出します。`assume_aligned<N>(p)` は、「このポインタは N バイト境界にある」と約束して、速いコードを出してもらう道具です。

!!! tip "ポイント"
    - 約束が嘘だと**未定義動作**になる。
    - N は 2 のべき乗。
    - 配列自体は `alignas(N)` や `aligned_alloc` で用意する。

!!! info "このページを読む前に"
    [ポインタ](../../basics/pointer.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::assume_aligned {#assume_aligned}

```cpp
template <size_t N, class T>
constexpr T* assume_aligned(T* ptr);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `N` | テンプレート引数 | 境界のバイト数（2 のべき乗） |
| `ptr` | T* | 約束するポインタ |

- 戻り値: `ptr` と同じ値のポインタ
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <memory>
#include <print>

int main() {
  alignas(16) float buf[4] = {1, 2, 3, 4};
  float* p = std::assume_aligned<16>(buf);
  std::println("{}", p[2]);
}
```

```text title="実行結果"
3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 16 バイト境界の float 配列を SIMD で処理する前に伝える | `float* p = std::assume_aligned<16>(buf);` |

## よくあるミス

??? failure "境界に合っていないポインタを渡す"
    約束が嘘だと未定義動作です。`alignas` で確保したものだけに使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`align`](align.md) | ポインタを境界に合わせる |
| [`aligned_alloc`](aligned_alloc.md) | 境界を指定して確保する |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 「N バイト境界にある」とコンパイラに約束する
    - [x] 嘘は未定義動作
    - [x] 確保は alignas / aligned_alloc で

## 関連ページ

- [cpprefjp: std::assume_aligned](https://cpprefjp.github.io/reference/memory/assume_aligned.html)
- [cppreference: std::assume_aligned](https://en.cppreference.com/w/cpp/memory/assume_aligned)
