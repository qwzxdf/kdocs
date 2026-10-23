---
title: std::strtol
summary: "文字列を整数に変換する（進数の指定・終了位置・エラーの検出ができる）。"
order: 3
group: <cstdlib> の関数
tags:
  - 数値
---

# std::strtol

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <cstdlib>`
</div>

文字列を整数に変換するとき、「どこまで読めたか」と「失敗したか」を知りたい場面があります。16 進数 "ff" を読みたい、"123abc" の abc の位置から続きを読みたい。`std::atoi` では分からないこれらを、`std::strtol` は教えてくれます。

!!! tip "ポイント"
    - `std::strtol("123abc", &end, 10)` は 123 で、`end` は "abc" を指す
    - 基数（2〜36）を指定できる。0 を渡すと接頭辞（`0x`、`0`）で自動判定
    - 範囲を超えると `LONG_MAX` / `LONG_MIN` を返し、`errno` に `ERANGE`
    - Windows の `long` は 32 ビット。64 ビットなら `strtoll`

!!! info "このページを読む前に"
    [STL](../../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::strtol {#strtol}

```cpp
long strtol(const char* str, char** str_end, int base);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | `const char*` | 変換する文字列 |
| `str_end` | `char**` | 読み終えた位置の書き込み先。不要なら `nullptr` |
| `base` | `int` | 基数。0 または 2〜36 |

戻り値は変換した整数です。先頭の空白は飛ばされ、符号と数字が読まれます。`base` が 16 なら `0x` の接頭辞を許し、0 なら `0x` で 16 進数、`0` で 8 進数、それ以外は 10 進数と判断します。

`str_end` に、数字として読めなかった最初の文字の位置が入ります。`*str_end == str` なら、1 文字も読めずに失敗です。`*str_end` が `'\0'` なら、文字列全体が数字でした。入力を検査するのに便利です。

範囲を超えたときは、`LONG_MAX` または `LONG_MIN` を返し、`errno` に `ERANGE` を設定します。変換前に `errno = 0` としておき、変換後に確かめます。

落とし穴は、`long` の幅です。Windows では 32 ビットで、64 ビット整数を読むなら `std::strtoll` です。

## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <print>

int main() {
  char* end = nullptr;
  const long a = std::strtol("123abc", &end, 10);
  std::println("値 = {}, 残り = {}", a, end);             // 残りは "abc"

  const long b = std::strtol("ff", nullptr, 16);           // 16 進数
  std::println("0xff = {}", b);

  const long c = std::strtol("0x1F", nullptr, 0);          // 接頭辞で自動判定
  std::println("0x1F = {}", c);
}
```

```text title="実行結果"
値 = 123, 残り = abc
0xff = 255
0x1F = 31
```

## ゲームでの使いどころ

色コード "#ff8800" の 16 進数を読むような場面で使います。

```cpp
// "ff8800" の最初の 2 文字 "ff" を読む
const long red = std::strtol(std::string(hex.substr(0, 2)).c_str(), nullptr, 16);
```

最近のコードでは、`std::from_chars(first, last, value, 16)` のほうが簡潔で速いです。

## よくあるミス

??? failure "範囲外の検査を忘れる"
    呼ぶ前に `errno = 0`、呼んだ後に `errno == ERANGE` を確かめます。

??? failure "全体が数字かを確かめない"
    `*end == '\0'` で、文字列全体を読めたか確認します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`atoi`](atoi.md) | 失敗が分からない簡易版 |
| [`strtoll`](strtoll.md) | `long long` を返す |
| [`strtoul`](strtoul.md) | 符号なし |

## コンパイラ対応

C++98 から使えます（C 言語由来）。`<cstdlib>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `strtol` は基数を指定して整数に変換する
    - [x] `str_end` で読み終えた位置が分かる
    - [x] Windows の `long` は 32 ビット。64 ビットは `strtoll`

## 関連ページ

- [cpprefjp: std::strtol](https://cpprefjp.github.io/reference/cstdlib/strtol.html)
- [cppreference: std::strtol](https://en.cppreference.com/w/cpp/numeric/math/strtol)
