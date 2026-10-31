---
title: std::wint_t
summary: "ワイド文字と WEOF を入れられる整数型。"
order: 900
tags:
  - 入出力・文字列
---

# std::wint_t

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cwchar>`
</div>

`fgetwc` は、ファイルからワイド文字を 1 文字読み、終わりに達すると `WEOF` を返します。この戻り値を受ける変数に `wchar_t` を使うと、正しい文字と終端の値を区別できなくなります。`wchar_t` で表せる全部の値に、終端を表す特別な値をもう 1 つ足す必要があるからです。そのための、一回り広い整数型が `std::wint_t` です。

!!! tip "ポイント"
    - `fgetwc`、`btowc`、`WEOF` など、「文字か終端か」を返す関数の型
    - `wchar_t` で受けると `WEOF` と区別できない場合がある。`wint_t` で受ける
    - `wchar_t` に入れるのは、`WEOF` でないと確かめたあと
    - Windows では 16 ビット、Linux では 32 ビットの符号なし整数が多い

!!! info "このページを読む前に"
    [`<cwchar>`](../cwchar.md) の概要と [`WEOF`](weof.md) を先に読んでください。

## 関数の詳しい説明

### std::wint_t {#wint_t}

```cpp
using wint_t = /* 整数型 */;
```

`char` を返す `fgetc` が、戻り値を `int` にしているのと同じ事情です。`fgetc` は、0 から 255 の文字と、`EOF`（-1）を区別するために、`int` で返します。`char` で受けると、文字コード 255 が `-1`（`EOF`）と同じになってしまう環境があります。ワイド文字版の `wint_t` は、これと同じ役割を持っています。

型の大きさは、`wchar_t` と同じか、それ以上です。MSVC では `unsigned short` で、`WEOF` は `0xFFFF` です。つまり、`wchar_t` の値としての `0xFFFF` は、文字としても存在しうるので、区別が要る場面があるのです。

`wint_t` で受けて、`WEOF` でないことを確かめてから、`wchar_t` に直します。

```cpp
std::wint_t ch;
while ((ch = std::fgetwc(file)) != WEOF) {
  const wchar_t wc = static_cast<wchar_t>(ch);
  // wc を使う
}
```

## 実際に動かしてみる

```cpp
#include <cwchar>
#include <print>
#include <type_traits>

int main() {
  static_assert(std::is_integral_v<std::wint_t>);

  // btowc は wint_t を返す。ASCII の 'A' なら、そのままの値
  const std::wint_t ch = std::btowc('A');
  std::println("{}", ch == L'A');
  std::println("{}", std::btowc(EOF) == WEOF);  // 終端は WEOF になる
}
```

```text title="実行結果"
true
true
```

## ゲームでの使いどころ

自分で `wint_t` の変数を書く場面は、`fgetwc` で 1 文字ずつ読むような、低水準のコードくらいです。普段は `std::wstring` と `std::wifstream` で、文字ごとの終端判定を意識しなくて済みます。

## よくあるミス

??? failure "fgetwc の戻り値を wchar_t で受ける"
    `wchar_t c = fgetwc(f);` と書くと、`WEOF` が文字の値と同じになる環境で、ループが終わらなくなります。`wint_t` で受けて、`WEOF` を検査します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`WEOF`](weof.md) | 終端を表す `wint_t` の値 |
| `int`（`fgetc` の戻り値） | `char` 版の同じ役割 |
| `wchar_t` | ワイド文字そのものの型。終端は入れられない |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `wint_t` は、ワイド文字と `WEOF` の両方を入れられる整数型
    - [x] `fgetwc` の戻り値は `wint_t` で受ける
    - [x] `WEOF` でないと確かめてから、`wchar_t` に直す

## 関連ページ

- [cpprefjp: wint_t](https://cpprefjp.github.io/reference/cwchar/wint_t.html)
- [cppreference: wint_t](https://en.cppreference.com/w/cpp/string/wide)
