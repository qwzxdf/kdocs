---
title: std::mbtowc
summary: "マルチバイト文字 1 文字を wchar_t に変換する。"
order: 900
tags:
  - 数値
---

# std::mbtowc

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdlib>`
</div>

マルチバイト文字列（UTF-8 など）の先頭の 1 文字をワイド文字（`wchar_t`）に変換するのが `std::mbtowc` です。Windows の API に渡す前の変換などで使われました。

!!! tip "ポイント"
    - `std::mbtowc(&wc, s, n)` は先頭の 1 文字を `wchar_t` に変換する
    - 戻り値は、読んだバイト数。null 文字は 0、不正なら −1
    - ロケールに依存し、内部状態を持つ
    - 文字列全体なら `mbstowcs`

!!! info "このページを読む前に"
    [STL](../../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::mbtowc {#mbtowc}

```cpp
int mbtowc(wchar_t* pwc, const char* s, std::size_t n);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `pwc` | `wchar_t*` | 変換結果の書き込み先。`nullptr` ならバイト数だけ調べる |
| `s` | `const char*` | 変換する文字列 |
| `n` | `size_t` | 調べてよい最大のバイト数 |

`s` の先頭の 1 文字を変換して `*pwc` に書き込み、その文字が占めていたバイト数を返します。null 文字なら 0、不正なら −1 です。

`mblen` と同様にロケールに依存し、内部に状態を持つため、スレッドセーフではありません。スレッドセーフな `mbrtowc` を使うのが、現在の推奨です。

Windows の `wchar_t` は UTF-16 で 16 ビットなので、サロゲートペアになる文字は 1 つの `wchar_t` に入りきりません。Windows では、`MultiByteToWideChar` で UTF-8 から UTF-16 に変換するほうが確実です。

## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <print>

int main() {
  wchar_t wc = 0;
  const int bytes = std::mbtowc(&wc, "a", 1);
  std::println("読んだバイト数 = {}", bytes);
  std::println("変換結果は L'a': {}", wc == L'a');
}
```

```text title="実行結果"
読んだバイト数 = 1
変換結果は L'a': true
```

## ゲームでの使いどころ

昔の C のコードで見かけます。現在は、Windows なら `MultiByteToWideChar`、標準ならスレッドセーフな `mbrtowc` を使います。

## よくあるミス

??? failure "複数のスレッドから呼ぶ"
    `mbrtowc` を使います。

??? failure "Windows で UTF-8 を変換する"
    `MultiByteToWideChar` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`mblen`](mblen.md) | バイト数だけ調べる |
| [`mbstowcs`](mbstowcs.md) | 文字列全体を変換 |
| [`wctomb`](wctomb.md) | 逆の変換 |

## コンパイラ対応

C++98 から使えます（C 言語由来）。`<cstdlib>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `mbtowc` は 1 文字を `wchar_t` に変換する
    - [x] ロケール依存でスレッドセーフでない
    - [x] Windows の UTF-8 は `MultiByteToWideChar`

## 関連ページ

- [cpprefjp: std::mbtowc](https://cpprefjp.github.io/reference/cstdlib/mbtowc.html)
- [cppreference: std::mbtowc](https://en.cppreference.com/w/cpp/c/mbtowc)
