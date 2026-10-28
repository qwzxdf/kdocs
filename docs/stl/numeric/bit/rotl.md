---
title: std::rotl
summary: "ビットを左に回転させる（はみ出したビットが反対側に戻る）。"
order: 11
group: ビット操作（<bit>）
tags:
  - 数値
---

# std::rotl

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <bit>`
</div>

ビットを左にずらす `<<` は、あふれたビットを捨てます。ハッシュ関数や乱数生成器では、あふれたビットを反対側から戻す「回転」が使われます。情報を失わずにビットをかき混ぜられるからです。

`std::rotl` は、<strong>ビットを左に回転</strong>させます。

!!! tip "ポイント"
    - `std::rotl(x, s)` は `x` を左へ `s` ビット回転する
    - 左へずらして、あふれた上位ビットが下位に戻る
    - `s` が負なら右回転（`rotr`）になる
    - 符号なし整数型だけが対象

!!! info "このページを読む前に"
    [`<bit>`](../bit.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::rotl {#rotl}

<span class="ver ver-20">C++20</span>

```cpp
template <class T>
constexpr T rotl(T x, int s) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 符号なし整数型 | 回転する値 |
| `s` | `int` | 回転量（ビット数）。負なら逆向き |

戻り値は、`x` を左に `s` ビット回転した値です。左にずれて外にあふれる上位ビットが下位に入ります。`s` が型のビット幅以上でも、幅で割った余りに従います。`s` が 0 のときは `x` そのままです。

通常のシフトのように、あふれた情報を失わないので、ハッシュ関数（FNV、xxHash、MurmurHash など）や疑似乱数（xoshiro など）に使われます。

以前は `(x << s) | (x >> (32 - s))` と書いていましたが、`s` が 0 のときに右シフトの幅が 32 となり、未定義動作になる落とし穴がありました。`rotl` はこれを正しく扱います。

## 実際に動かしてみる

```cpp
#include <bit>
#include <cstdint>
#include <print>

int main() {
  const std::uint32_t x = 0x80000001u;
  std::println("rotl(x, 1)  = {:#x}", std::rotl(x, 1));    // 上位の 1 が下位に戻る
  std::println("rotl(x, 0)  = {:#x}", std::rotl(x, 0));
  std::println("rotl(x, -1) = {:#x}", std::rotl(x, -1));   // 右回転になる
}
```

```text title="実行結果"
rotl(x, 1)  = 0x3
rotl(x, 0)  = 0x80000001
rotl(x, -1) = 0xc0000000
```

## ゲームでの使いどころ

ハッシュ値や乱数の状態をかき混ぜる処理で使います。

```cpp
// xoshiro 系の乱数で使われる形
std::uint64_t Mix(std::uint64_t s) { return std::rotl(s * 5, 7) * 9; }
```

## よくあるミス

??? failure "`(x << s) | (x >> (32 - s))` で `s` が 0 のとき未定義動作"
    `std::rotl` を使います。

??? failure "符号つき整数を渡してコンパイルエラーになる"
    符号なしにします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`rotr`](rotr.md) | 右に回転 |
| [`byteswap`](byteswap.md) | バイト順を入れ替える |

## コンパイラ対応

C++20 から使えます。GCC 9 以降、Clang 9 以降、Visual Studio 2019 16.3 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `rotl(x, s)` は左回転。あふれたビットが下位に戻る
    - [x] `s` が負なら右回転
    - [x] ハッシュや乱数で使う

## 関連ページ

- [cpprefjp: std::rotl](https://cpprefjp.github.io/reference/bit/rotl.html)
- [cppreference: std::rotl](https://en.cppreference.com/w/cpp/numeric/rotl)
