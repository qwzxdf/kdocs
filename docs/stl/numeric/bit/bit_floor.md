---
title: std::bit_floor
summary: "自分以下で最大の、2 のべき乗に切り捨てる。"
order: 4
group: ビット操作（<bit>）
tags:
  - 数値
---

# std::bit_floor

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <bit>`
</div>

バッファの大きさを 2 の累乗にそろえたい。ハッシュテーブルの大きさ、リングバッファの長さ、テクスチャの一辺。2 の累乗なら、剰余を `& (n - 1)` というビット演算で済ませられて速いからです。

`std::bit_floor` は、<strong>値以下で最大の 2 の累乗</strong>を返します。100 なら 64 です。

!!! tip "ポイント"
    - `std::bit_floor(100u)` は 64、`std::bit_floor(64u)` は 64
    - `0` のときは 0
    - 符号なし整数型だけを受け取る
    - 切り上げたいときは `std::bit_ceil`

!!! info "このページを読む前に"
    [`<bit>`](../bit.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::bit_floor {#bit_floor}

<span class="ver ver-20">C++20</span>

```cpp
template <class T>
constexpr T bit_floor(T x) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 符号なし整数型 | 元の値 |

戻り値は `x` 以下で最大の 2 の累乗です。`x` がすでに 2 の累乗ならそのまま返します。`x` が 0 のときは 0 を返します。戻り値の型は引数と同じです。

符号なし整数型のみ受け取ります。符号つき整数や `bool`、`char` を渡すとコンパイルエラーです。

実装は、`bit_width` から 1 を引いて 1 を左シフトした値に相当します。自分で書くとシフトの幅を間違えやすい処理なので、標準の関数を使うのが安全です。

落とし穴は、「以下」で丸めることです。大きさが足りなくなっては困るバッファの確保には、切り上げの `bit_ceil` を使います。

## 実際に動かしてみる

```cpp
#include <bit>
#include <print>

int main() {
  std::println("bit_floor(100) = {}", std::bit_floor(100u));
  std::println("bit_floor(64)  = {}", std::bit_floor(64u));
  std::println("bit_floor(1)   = {}", std::bit_floor(1u));
  std::println("bit_floor(0)   = {}", std::bit_floor(0u));
}
```

```text title="実行結果"
bit_floor(100) = 64
bit_floor(64)  = 64
bit_floor(1)   = 1
bit_floor(0)   = 0
```

## ゲームでの使いどころ

「この範囲に収まる最大の 2 の累乗」を求めるときに使います。たとえば、画面の幅に収まる最大のテクスチャサイズを決めます。

```cpp
// ウィンドウ幅 1366 に収まる、2 の累乗のテクスチャ幅
const unsigned texture_size = std::bit_floor(1366u);   // 1024
```

リングバッファのように、サイズが 2 の累乗である必要がある構造では、要求された容量以上にしたいので、`bit_ceil` を使います。

## よくあるミス

??? failure "足りないバッファを確保してしまう"
    要求以上の大きさが必要なら、`std::bit_ceil` を使います。

??? failure "`int` を渡してコンパイルエラーになる"
    符号なし整数型にして渡します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`bit_width`](bit_width.md) | 必要なビット数 |
| [`bit_ceil`](bit_ceil.md) | 以上で最小の 2 の累乗 |

## コンパイラ対応

C++20 から使えます。GCC 9 以降、Clang 9 以降、Visual Studio 2019 16.3 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `bit_floor(x)` は `x` 以下で最大の 2 の累乗
    - [x] `0` なら 0。符号なし整数型のみ
    - [x] 切り上げは `bit_ceil`

## 関連ページ

- [`std::bit_ceil`](bit_ceil.md)
- [cpprefjp: std::bit_floor](https://cpprefjp.github.io/reference/bit/bit_floor.html)
- [cppreference: std::bit_floor](https://en.cppreference.com/w/cpp/numeric/bit_floor)
