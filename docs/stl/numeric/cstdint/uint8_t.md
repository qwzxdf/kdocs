---
title: std::uint8_t
summary: "ちょうど 8 ビットの符号なし整数。"
order: 900
tags:
  - 数値
---

# std::uint8_t

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-11">C++11</span>
`#include <cstdint>`
</div>

`int` の大きさは、環境で違うことがあります。ファイルに書いた数値を別の環境で読んだら、桁数が合わない、という事故は、ゲームのセーブデータや通信でよく起きます。

`std::uint8_t` は、<strong>ちょうど 8 ビットの符号なし整数</strong>を表す型です。どの環境でも大きさが同じなので、ファイルや通信のデータ形式に使えます。

!!! tip "ポイント"
    - ちょうど 8 ビットの符号なし整数。範囲は 0 〜 255
    - `<cstdint>` で定義される（C++11 から）
    - 普通の計算には `int` で足りる。ファイル・通信・ビット操作で、大きさを固定したいときに使う
    - 該当する型がない環境では定義されない（ただし、実際のゲーム用の環境にはある）

!!! info "このページを読む前に"
    [`<cstdint>`](../cstdint.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::uint8_t {#uint8_t}

<span class="ver ver-11">C++11</span>

```cpp
using uint8_t = /* 8 ビットの符号なし整数型 */;
```

`std::uint8_t` は型の別名（`using`）で、実体は環境の整数型です。多くの環境では `unsigned char` と同じです。幅がちょうど 8 ビットで、符号なし整数であることが保証されます。範囲は 0 〜 255 です。

符号なしの型は、範囲を超えると 2 のべき乗の余りに折り返されます（オーバーフローしても未定義動作にならない）。

落とし穴は、符号なしの引き算です。`std::uint8_t` で 0 から 1 を引くと、負にならず 255 になります。引き算の結果が負になりうる値は、符号つきにします。

「`optional` な型」と呼ばれるのは、ちょうど 8 ビットの整数型を持たない環境では、この型が定義されない、という意味です。PC やコンソールでは、実際に定義されないことはまず無いので、ゲームではそのまま使えます。

8 ビットの型は、実体が `char` 系の型なので、`std::cout` に渡すと数ではなく文字として出力されます。`std::println` は数として出力しますが、`std::cout` で数値として見るには `int` にキャストします。

## 実際に動かしてみる

```cpp
#include <cstdint>
#include <limits>
#include <print>

int main() {
  std::println("{} ビット", sizeof(std::uint8_t) * 8);
  std::println("最小 {}", static_cast<long long>(std::numeric_limits<std::uint8_t>::min()));
  std::println("最大 {}", static_cast<unsigned long long>(std::numeric_limits<std::uint8_t>::max()));
}
```

```text title="実行結果"
8 ビット
最小 0
最大 255
```

## ゲームでの使いどころ

バイト列、色の 1 チャンネル（0〜255）、フラグ。`unsigned char` の代わりに、意味を明確にして使う。

```cpp
std::uint8_t red = 255;   // 色の 1 成分
```

計算の途中では、`int` や `float` で足ります。ファイルの形式、通信のパケット、ビット演算のように、大きさが意味を持つ場面だけで固定幅の型を使います。

## よくあるミス

??? failure "普通の計算まで固定幅の型にして、読みにくくなる"
    ループの回数や一時変数は `int` で足ります。

??? failure "符号なしの引き算で負の値を期待する"
    符号なしの 0 − 1 は最大値になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`int`](../../../basics/index.md) | 環境で大きさが変わる標準の整数型 |
| [`<cstdint>`](../cstdint.md) | 固定幅の整数型の一覧 |
| [`<limits>`](../limits.md) | 型の最小値・最大値を調べる |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ちょうど 8 ビットの符号なし整数。範囲は 0 〜 255
    - [x] ファイル・通信・ビット操作で大きさを固定したいときに使う
    - [x] 普通の計算は `int` で足りる

## 関連ページ

- [cpprefjp: std::uint8_t](https://cpprefjp.github.io/reference/cstdint/uint8_t.html)
- [cppreference: std::uint8_t](https://en.cppreference.com/w/cpp/types/integer)
