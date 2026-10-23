---
title: std::c32rtomb
summary: "c32 → mb：UTF-32（コードポイント、`char32_t`）を、ロケールのマルチバイト文字列に変換します。"
order: 900
tags:
  - 数値
---

# std::c32rtomb

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cuchar>`
</div>

文字列の符号化（エンコード）は、ゲームの作りに深く関わります。内部は UTF-8 の `std::string`、OS の API は UTF-16 の `wchar_t`、というように、形式の違う文字列の間で変換が必要になる場面があります。`std::c32rtomb` は、<strong>UTF-32 をマルチバイト文字に</strong>変換する関数です。1 文字ずつ処理する、低水準の関数です。

!!! tip "ポイント"
    - UTF-32 のコード単位（`char32_t`）を、マルチバイト文字（UTF-8 など）に変換
    - 変換の途中状態を `std::mbstate_t` に持つ（最初は `{}` で 0 初期化）
    - 戻り値は、読んだ（書いた）バイト数。エラーは `static_cast<std::size_t>(-1)`
    - 文字列全体を変換したいなら、標準では扱いづらい。Windows API や専用のライブラリを使う

!!! info "このページを読む前に"
    [STL](../../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::c32rtomb {#c32rtomb}

<span class="ver ver-11">C++11</span>

```cpp
std::size_t c32rtomb(char* s, char32_t c32, std::mbstate_t* ps);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `s` | `char*` | 書き込み先。`MB_LEN_MAX` バイト以上 |
| `c32` | `char32_t` | 変換する UTF-32 のコード単位 |
| `ps` | `mbstate_t*` | 変換の状態。最初は 0 で初期化する |

UTF-32 のコード単位（`char32_t`）を、マルチバイト文字（UTF-8 など）に変換します。

戻り値は読み書きしたバイト数ですが、特別な値があります。`0` は null 文字の処理、`static_cast<std::size_t>(-1)` は変換エラー、`static_cast<std::size_t>(-2)` は入力が途中で終わって続きが必要、`static_cast<std::size_t>(-3)` は前回の呼び出しで残っていた続きのコード単位を返した、です。

`ps` に渡す `std::mbstate_t` は、複数回の呼び出しで状態を引き継ぐための変数です。最初は `{}` で 0 初期化し、1 つの文字列を変換している間は、同じ変数を渡し続けます。

UTF-32 の 1 文字は、マルチバイトでは最大 4 バイト（UTF-8）になります。

マルチバイト側の規則は、現在のロケールで決まります。Windows の MSVC では、UTF-8 ロケールにしていないと、日本語が正しく変換されません。文字列全体を扱う処理は、1 文字ずつこの関数を呼ぶのではなく、`MultiByteToWideChar` / `WideCharToMultiByte`（Windows）や、専用のライブラリを使うほうが簡単で確実です。

## 実際に動かしてみる

```cpp
#include <climits>
#include <cuchar>
#include <cstddef>
#include <print>

int main() {
  char buffer[MB_LEN_MAX];
  std::mbstate_t state{};
  const std::size_t n = std::c32rtomb(buffer, U'a', &state);
  std::println("書き込んだバイト数 = {}", n);
  std::println("結果は 'a': {}", buffer[0] == 'a');
}
```

```text title="実行結果"
書き込んだバイト数 = 1
結果は 'a': true
```

## ゲームでの使いどころ

標準だけで文字の符号化を変換したい、まれな場面で使います。ゲームでは、文字列全体を変換する処理を自作の関数にまとめて、内部で OS の API を呼ぶ形が一般的です。

## よくあるミス

??? failure "エラー値（`-1`）を確かめずに続ける"
    戻り値が `static_cast<std::size_t>(-1)` でないか確かめます。

??? failure "`ps` を毎回新しく初期化して、サロゲートペアが壊れる"
    1 つの文字列の間は、同じ `mbstate_t` を使い続けます。

??? failure "ロケールが UTF-8 でなくて、日本語が変換できない"
    ロケールを確かめるか、OS の API を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`mbstowcs`](../cstdlib/mbstowcs.md) | 文字列全体をワイド文字列に |
| [`mbtowc`](../cstdlib/mbtowc.md) | 1 文字をワイド文字に |

## コンパイラ対応

C++11 から使えます（`c8` 系は C++20）。`<cuchar>` で宣言されます。対応状況は標準ライブラリによって異なり、MSVC は UTF-8 のロケールが前提です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `c32rtomb` はUTF-32 をマルチバイト文字に
    - [x] 戻り値は読み書きしたバイト数。`-1` はエラー
    - [x] 文字列全体は OS の API やライブラリのほうが簡単

## 関連ページ

- [cpprefjp: std::c32rtomb](https://cpprefjp.github.io/reference/cuchar/c32rtomb.html)
- [cppreference: std::c32rtomb](https://en.cppreference.com/w/cpp/string/multibyte/c32rtomb)
