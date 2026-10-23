---
title: std::strtoumax
summary: "文字列を `uintmax_t` に変換する。"
order: 900
tags:
  - 数値
---

# std::strtoumax

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cinttypes>`
</div>

文字列を数値に直すとき、「どこまで読めたか」と「範囲を超えなかったか」を知りたいことがあります。`std::strtoumax` は、文字列を`std::uintmax_t`（最大幅の符号なし整数）に変換し、読み終えた位置を教えてくれます。`std::strtol` の、戻り値の型違いの仲間です。

!!! tip "ポイント"
    - 戻り値は `std::uintmax_t`（最大幅の符号なし整数）
    - 読み終えた位置が `str_end` に入る。`nullptr` なら不要
    - 基数（2〜36）を指定できる。0 なら接頭辞で自動判定
    - 範囲を超えると上限（または下限）を返し、`errno` に `ERANGE`

!!! info "このページを読む前に"
    [STL](../../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::strtoumax {#strtoumax}

```cpp
std::uintmax_t strtoumax(const char* str, char** str_end, int base);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | `const char*` | 変換する文字列 |
| `str_end` | `char**` | 読み終えた位置の書き込み先。不要なら `nullptr` |
| `base` | `int` | 基数。0 または 2〜36 |

戻り値は変換した値で、型は std::uintmax_t です。先頭の空白を飛ばし、符号と数字を読みます。`base` が 16 なら `0x` を許し、0 なら `0x` で 16 進数、`0` で 8 進数、それ以外は 10 進数と判断します。

`str_end` には、数字として読めなかった最初の文字の位置が入ります。`*str_end == str` なら、1 文字も読めずに失敗です。`*str_end` が `'\0'` なら、文字列全体が数字でした。

範囲を超えた場合は、型の最大値か最小値を返し、`errno` に `ERANGE` を設定します。呼ぶ前に `errno = 0` とし、呼んだあとで確かめます。負の数を渡すと、符号なしに折り返された大きな値になります（エラーになりません）。

新しいコードでは、`std::from_chars` のほうが速く、ロケールの影響を受けません。

## 実際に動かしてみる

```cpp
#include <cinttypes>
#include <print>

int main() {
  char* end = nullptr;
  const std::uintmax_t a = std::strtoumax("123abc", &end, 10);
  std::println("値 = {}, 残り = {}", a, end);

  const std::uintmax_t b = std::strtoumax("77", nullptr, 10);
  std::println("77 = {}", b);
}
```

```text title="実行結果"
値 = 123, 残り = abc
77 = 77
```

## ゲームでの使いどころ

ファイルの数値を、失敗を検出しながら読むときに使います。大きな値（`std::uintmax_t`（最大幅の符号なし整数））を扱う場合に、`strtol` では足りないときの選択肢です。

```cpp
errno = 0;
char* end = nullptr;
const std::uintmax_t v = std::strtoumax(text.c_str(), &end, 10);
if (errno == ERANGE || end == text.c_str()) { /* 失敗 */ }
```

## よくあるミス

??? failure "範囲外の検査を忘れる"
    呼ぶ前に `errno = 0`、呼んだ後に `errno == ERANGE` を確かめます。

??? failure "文字列全体が数字かを確かめない"
    `*end == '\0'` で確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`strtol`](../cstdlib/strtol.md) | `long` を返す |
| [`atoi`](../cstdlib/atoi.md) | 失敗が分からない簡易版 |
| [`from_chars`](../../io/from_chars.md) | ロケール非依存で速い |

## コンパイラ対応

C++11 から使えます。`<cinttypes>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `strtoumax` は文字列を`std::uintmax_t`（最大幅の符号なし整数）に変換する
    - [x] `str_end` で読み終えた位置、`errno` で範囲外が分かる
    - [x] 新しいコードは `from_chars`

## 関連ページ

- [cpprefjp: std::strtoumax](https://cpprefjp.github.io/reference/cinttypes/strtoumax.html)
- [cppreference: std::strtoumax](https://en.cppreference.com/w/cpp/c/strtoumax)
