---
title: std::strtoul
summary: "文字列を unsigned long に変換する（進数を指定でき、読み終えた位置が分かる）。"
order: 900
tags:
  - 数値
---

# std::strtoul

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdlib>`
</div>

文字列を数値に直すとき、「どこまで読めたか」と「範囲を超えなかったか」を知りたいことがあります。`std::strtoul` は、文字列を`unsigned long`に変換し、読み終えた位置を教えてくれます。`std::strtol` の、戻り値の型違いの仲間です。

!!! tip "ポイント"
    - 戻り値は `unsigned long`
    - 読み終えた位置が `str_end` に入る。`nullptr` なら不要
    - 基数（2〜36）を指定できる。0 なら接頭辞で自動判定
    - 範囲を超えると上限（または下限）を返し、`errno` に `ERANGE`

!!! info "このページを読む前に"
    [STL](../../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::strtoul {#strtoul}

```cpp
unsigned long strtoul(const char* str, char** str_end, int base);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | `const char*` | 変換する文字列 |
| `str_end` | `char**` | 読み終えた位置の書き込み先。不要なら `nullptr` |
| `base` | `int` | 基数。0 または 2〜36 |

戻り値は変換した値で、型は unsigned long です。先頭の空白を飛ばし、符号と数字を読みます。`base` が 16 なら `0x` を許し、0 なら `0x` で 16 進数、`0` で 8 進数、それ以外は 10 進数と判断します。

`str_end` には、数字として読めなかった最初の文字の位置が入ります。`*str_end == str` なら、1 文字も読めずに失敗です。`*str_end` が `'\0'` なら、文字列全体が数字でした。

範囲を超えた場合は、型の最大値か最小値を返し、`errno` に `ERANGE` を設定します。呼ぶ前に `errno = 0` とし、呼んだあとで確かめます。負の数を渡すと、符号なしに折り返された大きな値になります（エラーになりません）。

新しいコードでは、`std::from_chars` のほうが速く、ロケールの影響を受けません。

## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <print>

int main() {
  char* end = nullptr;
  const unsigned long a = std::strtoul("255 rest", &end, 10);
  std::println("値 = {}, 残り = {}", a, end);

  const unsigned long b = std::strtoul("ff", nullptr, 16);
  std::println("ff = {}", b);
}
```

```text title="実行結果"
値 = 255, 残り =  rest
ff = 255
```

## ゲームでの使いどころ

ファイルの数値を、失敗を検出しながら読むときに使います。大きな値（`unsigned long`）を扱う場合に、`strtol` では足りないときの選択肢です。

```cpp
errno = 0;
char* end = nullptr;
const unsigned long v = std::strtoul(text.c_str(), &end, 10);
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
| [`strtol`](strtol.md) | `long` を返す |
| [`atoi`](atoi.md) | 失敗が分からない簡易版 |
| [`from_chars`](../../io/from_chars.md) | ロケール非依存で速い |

## コンパイラ対応

C++98 から使えます（C 言語由来）。`<cstdlib>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `strtoul` は文字列を`unsigned long`に変換する
    - [x] `str_end` で読み終えた位置、`errno` で範囲外が分かる
    - [x] 新しいコードは `from_chars`

## 関連ページ

- [cpprefjp: std::strtoul](https://cpprefjp.github.io/reference/cstdlib/strtoul.html)
- [cppreference: std::strtoul](https://en.cppreference.com/w/cpp/c/strtoul)
