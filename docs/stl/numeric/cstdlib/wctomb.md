---
title: std::wctomb
summary: "wchar_t 1 文字をマルチバイト文字に変換する。"
order: 900
tags:
  - 数値
---

# std::wctomb

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdlib>`
</div>

ワイド文字（`wchar_t`）1 文字を、マルチバイトの文字（UTF-8 など）に戻すのが `std::wctomb` です。`std::mbtowc` の逆の変換です。

!!! tip "ポイント"
    - `std::wctomb(s, wc)` は `wc` を `s` に書き込む
    - 戻り値は書き込んだバイト数。変換できなければ −1
    - `s` には `MB_CUR_MAX` バイト以上の領域が要る
    - ロケールに依存し、内部状態を持つ

!!! info "このページを読む前に"
    [STL](../../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::wctomb {#wctomb}

```cpp
int wctomb(char* s, wchar_t wc);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `s` | `char*` | 書き込み先。`MB_CUR_MAX` バイト以上 |
| `wc` | `wchar_t` | 変換するワイド文字 |

`wc` を現在のロケールのマルチバイト表現に変換して `s` に書き込み、書き込んだバイト数を返します。変換できない文字なら −1 です。

`s` は、1 文字の最大長（`MB_CUR_MAX`）以上の大きさが必要です。足りないと書き込みがあふれます。

ロケールに依存し、内部に状態を持つので、スレッドセーフではありません。MSVC は安全版の `wctomb_s` を勧めています。

## 実際に動かしてみる

```cpp
#include <climits>
#include <cstdlib>
#include <print>

int main() {
  char buffer[MB_LEN_MAX];
  const int bytes = std::wctomb(buffer, L'a');
  std::println("書き込んだバイト数 = {}", bytes);
  std::println("結果は 'a': {}", buffer[0] == 'a');
}
```

```text title="実行結果"
書き込んだバイト数 = 1
結果は 'a': true
```

## ゲームでの使いどころ

昔の C のコードで見かけます。現在は、Windows なら `WideCharToMultiByte`、標準ならスレッドセーフな `wcrtomb` を使います。

## よくあるミス

??? failure "バッファが小さくてあふれる"
    `MB_LEN_MAX` バイト以上を確保します。

??? failure "複数のスレッドから呼ぶ"
    `wcrtomb` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`mbtowc`](mbtowc.md) | 逆の変換 |
| [`wcstombs`](wcstombs.md) | 文字列全体を変換 |

## コンパイラ対応

C++98 から使えます（C 言語由来）。`<cstdlib>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `wctomb` は `wchar_t` 1 文字をマルチバイトに変換する
    - [x] `MB_LEN_MAX` バイトの領域が要る
    - [x] Windows では `WideCharToMultiByte`

## 関連ページ

- [cpprefjp: std::wctomb](https://cpprefjp.github.io/reference/cstdlib/wctomb.html)
- [cppreference: std::wctomb](https://en.cppreference.com/w/cpp/c/wctomb)
