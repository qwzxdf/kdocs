---
title: std::strtod
summary: "文字列を double に変換する（読み終えた位置が分かる）。"
order: 900
tags:
  - 数値
---

# std::strtod

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdlib>`
</div>

"3.14" のような小数の文字列を `double` にしたい。`std::atof` でもできますが、失敗が分かりません。`std::strtod` は、読み終えた位置と範囲エラーを教えてくれる、より安全な版です。

!!! tip "ポイント"
    - `std::strtod("3.14abc", &end)` は 3.14 で、`end` は "abc" を指す
    - "1e3"（指数）、"inf"、"nan" も読める
    - 範囲を超えると `HUGE_VAL`、`errno` に `ERANGE`
    - 小数点はロケールに従う

!!! info "このページを読む前に"
    [STL](../../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::strtod {#strtod}

```cpp
double strtod(const char* str, char** str_end);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | `const char*` | 変換する文字列 |
| `str_end` | `char**` | 読み終えた位置の書き込み先。不要なら `nullptr` |

戻り値は変換した `double` です。先頭の空白を飛ばし、符号、数字、小数点、指数（`e` または `E`）を読みます。16 進の浮動小数点（`0x1.8p1`）、`inf`、`nan` も受け取ります。

`str_end` に、読めなかった最初の文字の位置が入ります。`*str_end == str` なら、何も読めず、0 を返しています。

小数点の記号は、現在のロケールで決まります。ロケールを変えていなければ "C" ロケールで `.` です。ロケールを日本語や欧州の設定にしているプログラムでは、`,` を小数点にする環境があり、ファイルの数値の読み込みが壊れることがあります。

`double` ではなく `float` で読みたいなら `strtof` です。新しいコードでは `std::from_chars`（浮動小数点も読める）が速く、ロケールの影響を受けません。

## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <print>

int main() {
  char* end = nullptr;
  const double a = std::strtod("3.14abc", &end);
  std::println("値 = {}, 残り = {}", a, end);

  std::println("1e3   = {}", std::strtod("1e3", nullptr));    // 指数表記
  std::println("-0.5  = {}", std::strtod("-0.5", nullptr));
}
```

```text title="実行結果"
値 = 3.14, 残り = abc
1e3   = 1000
-0.5  = -0.5
```

## ゲームでの使いどころ

設定ファイルやコンソールの入力から、小数の値を読むときに使います。

```cpp
char* end = nullptr;
const double speed = std::strtod(text.c_str(), &end);
if (end == text.c_str()) { /* 数値として読めなかった */ }
```

## よくあるミス

??? failure "ロケール設定で小数点が `,` になり、読み込みが壊れる"
    ロケールを変えない、または `std::from_chars` を使います。

??? failure "失敗を `0` の結果と区別できない"
    `end` の位置で、読めたかを確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`atof`](atof.md) | 失敗が分からない簡易版 |
| [`strtof`](strtof.md) | `float` を返す |
| [`from_chars`](../../io/from_chars.md) | ロケールに依存せず速い |

## コンパイラ対応

C++98 から使えます（C 言語由来）。`<cstdlib>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `strtod` は文字列を `double` に変換する
    - [x] `str_end` で読めた位置が分かる
    - [x] ロケールで小数点が変わる。新しいコードは `from_chars`

## 関連ページ

- [cpprefjp: std::strtod](https://cpprefjp.github.io/reference/cstdlib/strtod.html)
- [cppreference: std::strtod](https://en.cppreference.com/w/cpp/c/strtod)
