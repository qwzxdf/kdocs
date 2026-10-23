---
title: std::mblen
summary: "マルチバイト文字の 1 文字目のバイト数を返す。"
order: 900
tags:
  - 数値
---

# std::mblen

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdlib>`
</div>

UTF-8 のようなマルチバイト文字列で、先頭の文字が何バイトかを知りたい。`std::mblen` は、<strong>文字列の先頭の 1 文字のバイト数</strong>を返します。

!!! tip "ポイント"
    - `std::mblen(s, n)` は先頭の 1 文字のバイト数
    - null 文字は 0、不正なら −1 を返す
    - ロケールに依存する。UTF-8 には UTF-8 ロケールが要る
    - 内部に状態を持つので、スレッドセーフではない

!!! info "このページを読む前に"
    [STL](../../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::mblen {#mblen}

```cpp
int mblen(const char* s, std::size_t n);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `s` | `const char*` | 文字列の先頭。`nullptr` なら状態のリセットと問い合わせ |
| `n` | `size_t` | 調べてよい最大のバイト数 |

戻り値は、`s` の先頭の文字のバイト数です。`s` が null 文字を指すなら 0、不正なバイト列なら −1 です。

現在のロケールのマルチバイト規則で解釈します。既定の "C" ロケールでは 1 文字 1 バイトなので、日本語の UTF-8 の文字でも 1 を返します。UTF-8 を正しく扱うには、`setlocale(LC_ALL, ".UTF-8")`（環境によって名前が違う）で変える必要があります。

内部に変換状態を持つため、複数のスレッドから呼ぶと干渉します。スレッドセーフな `mbrlen` を使います。UTF-8 を扱うなら、先頭バイトの上位ビットを見る方法（`0xxxxxxx` なら 1 バイト、`110xxxxx` なら 2 バイト…）のほうが、ロケールに依存せず確実です。

## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <print>

int main() {
  std::println("mblen(\"a\", 1) = {}", std::mblen("a", 1));
  std::println("mblen(\"\", 1)  = {}", std::mblen("", 1));   // null 文字は 0
}
```

```text title="実行結果"
mblen("a", 1) = 1
mblen("", 1)  = 0
```

## ゲームでの使いどころ

UTF-8 の文字数を数えたいとき、先頭バイトから自分で判定する関数のほうが、ロケールに頼らず安全です。

```cpp
// UTF-8 の先頭バイトから、その文字のバイト数を求める
int Utf8Length(unsigned char lead) {
  if (lead < 0x80) return 1;
  if ((lead >> 5) == 0x6) return 2;
  if ((lead >> 4) == 0xE) return 3;
  return 4;
}
```

## よくあるミス

??? failure "既定のロケールで日本語を調べ、1 が返る"
    ロケールに依存しない方法で判定します。

??? failure "複数のスレッドから呼ぶ"
    `mbrlen` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`mbtowc`](mbtowc.md) | マルチバイト文字をワイド文字に変換 |
| [`mbstowcs`](mbstowcs.md) | 文字列全体を変換 |

## コンパイラ対応

C++98 から使えます（C 言語由来）。`<cstdlib>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `mblen` は先頭の文字のバイト数を返す
    - [x] ロケール依存でスレッドセーフでない
    - [x] UTF-8 は先頭バイトで自分で判定する

## 関連ページ

- [cpprefjp: std::mblen](https://cpprefjp.github.io/reference/cstdlib/mblen.html)
- [cppreference: std::mblen](https://en.cppreference.com/w/cpp/c/mblen)
