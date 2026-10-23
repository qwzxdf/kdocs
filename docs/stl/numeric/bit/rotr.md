---
title: std::rotr
summary: "ビットを右に回転させる（はみ出したビットが反対側に戻る）。"
order: 12
group: ビット操作（<bit>）
tags:
  - 数値
---

# std::rotr

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <bit>`
</div>

右へのシフト `>>` は、下位からあふれたビットを捨てます。回転なら、あふれたビットが上位に戻るので、情報が消えません。ハッシュや乱数、暗号の部品で使われる操作です。

`std::rotr` は、<strong>ビットを右に回転</strong>させます。

!!! tip "ポイント"
    - `std::rotr(x, s)` は `x` を右へ `s` ビット回転する
    - 下位からあふれたビットが上位に戻る
    - `s` が負なら左回転（`rotl`）になる
    - 符号なし整数型だけが対象

!!! info "このページを読む前に"
    [`<bit>`](../bit.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::rotr {#rotr}

<span class="ver ver-20">C++20</span>

```cpp
template <class T>
constexpr T rotr(T x, int s) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 符号なし整数型 | 回転する値 |
| `s` | `int` | 回転量（ビット数）。負なら逆向き |

戻り値は、`x` を右に `s` ビット回転した値です。右へずれて外にあふれる下位ビットが、上位に入ります。`s` がビット幅以上のときは幅で割った余りに従い、0 なら `x` そのままです。

自分で `(x >> s) | (x << (32 - s))` と書く方法は、`s` が 0 のときにシフト幅が型の幅になり、未定義動作です。`rotr` はこの落とし穴がありません。

`rotl(x, -s)` と同じ意味です。

## 実際に動かしてみる

```cpp
#include <bit>
#include <cstdint>
#include <print>

int main() {
  const std::uint32_t x = 0x00000003u;
  std::println("rotr(x, 1) = {:#x}", std::rotr(x, 1));    // 下位の 1 が上位に戻る
  std::println("rotr(x, 0) = {:#x}", std::rotr(x, 0));
}
```

```text title="実行結果"
rotr(x, 1) = 0x80000001
rotr(x, 0) = 0x3
```

## ゲームでの使いどころ

ハッシュ関数の混ぜ合わせで使います。

```cpp
// SHA-256 などで使われる右回転の部品
std::uint32_t Sigma(std::uint32_t x) { return std::rotr(x, 2) ^ std::rotr(x, 13) ^ std::rotr(x, 22); }
```

## よくあるミス

??? failure "`s` が 0 のときに自作の回転で未定義動作"
    `std::rotr` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`rotl`](rotl.md) | 左に回転 |
| [`byteswap`](byteswap.md) | バイト順を入れ替える |

## コンパイラ対応

C++20 から使えます。GCC 9 以降、Clang 9 以降、Visual Studio 2019 16.3 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `rotr(x, s)` は右回転。あふれたビットが上位に戻る
    - [x] `s` が負なら左回転
    - [x] ハッシュや暗号の部品で使う

## 関連ページ

- [cpprefjp: std::rotr](https://cpprefjp.github.io/reference/bit/rotr.html)
- [cppreference: std::rotr](https://en.cppreference.com/w/cpp/numeric/rotr)
