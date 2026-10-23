---
title: std::intptr_t
summary: "ポインタをそのまま入れられる大きさの符号付き整数。"
order: 900
tags:
  - 数値
---

# std::intptr_t

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cstdint>`
</div>

ポインタ（アドレス）を整数として扱いたい場面があります。アドレスの下位ビットを調べる、アドレスをハンドルとして持ち回る、ポインタどうしの差を測る。`int` や `long` ではポインタが入りきらない環境があるので、専用の型が必要です。

`std::intptr_t` は、<strong>ポインタを入れても欠けない符号つき整数型</strong>です。

!!! tip "ポイント"
    - `void*` を変換して戻しても、元のポインタに戻る大きさ
    - 64 ビット環境では 64 ビット、32 ビット環境では 32 ビット
    - `std::uintptr_t` は符号なし版
    - `reinterpret_cast` で変換する。整数にしたら、元の型に戻す以外の使い方はしない

!!! info "このページを読む前に"
    [`<cstdint>`](../cstdint.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::intptr_t {#intptr_t}

<span class="ver ver-11">C++11</span>

```cpp
using intptr_t = /* ポインタを保持できる符号つき整数型 */;
```

`std::intptr_t` は、`void*` を `reinterpret_cast` で整数に変換したとき、情報が欠けない大きさの符号つき整数型です。ポインタと同じ幅になるのが普通で、64 ビット環境では 64 ビットです。

この型は<strong>オプション</strong>（環境によって用意されない）ですが、PC・コンソール・スマホの環境では必ず用意されています。

アドレスを数として扱うと、並べ替えやハッシュには使えますが、元のポインタに戻す以外の目的に使うのは危険です。たとえば、整数に変えたアドレスにオフセットを足して、ポインタに戻す方法は、規格では保証されていません。

Win32 API の古い型 `LONG_PTR` は、`intptr_t` と同じ大きさです。

## 実際に動かしてみる

```cpp
#include <cstdint>
#include <print>

int main() {
  int value = 0;
  const auto address = reinterpret_cast<std::intptr_t>(&value);   // ポインタを整数に
  int* back = reinterpret_cast<int*>(address);                    // 整数をポインタに戻す
  std::println("元に戻る: {}", back == &value);
  std::println("ポインタと同じ幅: {}", sizeof(std::intptr_t) == sizeof(void*));
}
```

```text title="実行結果"
元に戻る: true
ポインタと同じ幅: true
```

## ゲームでの使いどころ

ハンドルや ID として、ポインタを整数のかたちで持ち回る場面で使います。

```cpp
// 外部ライブラリが整数 1 個しか受け取らない「ユーザーデータ」に、ポインタを入れる
std::intptr_t user_data = reinterpret_cast<std::intptr_t>(this);
```

ポインタの下位ビットを使ったフラグ（タグ付きポインタ）のような高度な技にも使いますが、配置が崩れるとバグになりやすいため、注意が要ります。

## よくあるミス

??? failure "`int` にポインタを入れて、64 ビット環境で上位が欠ける"
    `std::intptr_t` を使います。

??? failure "整数に変えたアドレスで、ポインタの演算をする"
    元のポインタに戻す用途に限ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`uintptr_t`](uintptr_t.md) | 符号なし版 |
| [`ptrdiff_t`](../../support/ptrdiff_t.md) | ポインタどうしの差を表す型 |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ポインタを保持できる大きさの符号つき整数
    - [x] 64 ビット環境では 64 ビット
    - [x] 整数に変えたら、元のポインタに戻す以外にしない

## 関連ページ

- [cpprefjp: std::intptr_t](https://cpprefjp.github.io/reference/cstdint/intptr_t.html)
- [cppreference: std::intptr_t](https://en.cppreference.com/w/cpp/types/integer)
