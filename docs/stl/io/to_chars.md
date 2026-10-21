---
title: std::to_chars
summary: "数値を文字列に変換する。速くて、例外を投げない。"
order: 84
tags:
  - 入出力・文字列
---

# std::to_chars

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-17">C++17</span>
`#include <charconv>`
</div>

`std::to_chars` は、**数値を文字列に変換して、用意したバッファに書き込む**関数です。`std::to_string` と違い、**メモリを確保せず、例外も投げません**。小数は「元に戻せる最短の表記」になります。

!!! tip "ポイント"
    - バッファは自分で用意する（数値の最大桁数を考えて、十分な大きさに）。
    - 戻り値の `ptr` が、書き終えた位置（終端の `\0` は付かない）。
    - ログ出力の高速化に使える。

## 関数の詳しい説明

### std::to_chars {#to_chars}

```cpp
std::to_chars_result to_chars(char* first, char* last, int value, int base = 10);
std::to_chars_result to_chars(char* first, char* last, double value);
std::to_chars_result to_chars(char* first, char* last, double value, std::chars_format fmt,
                              int precision);

struct to_chars_result {
  char* ptr;     // 書き終わった次の位置
  std::errc ec;  // バッファが足りなければ value_too_large
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `first`, `last` | `char*` | 書き込むバッファ |
| `value` | 数値 | 変換する値 |
| `base` | `int` | 進数（整数版） |
| `fmt` | `std::chars_format` | 浮動小数点の書き方 |
| `precision` | `int` | 桁数 |

- 末尾に `'\0'` は**付きません**。`ptr - first` が書いた文字数です
- 浮動小数点を精度指定なしで変換すると、「読み戻したときに同じ値になる最短の表記」になります

```cpp
#include <charconv>
#include <print>
#include <string_view>

int main() {
  char buf[32];
  auto r = std::to_chars(buf, buf + sizeof(buf), 0.1f);
  std::println("{}", std::string_view(buf, r.ptr));

  r = std::to_chars(buf, buf + sizeof(buf), 3.14159, std::chars_format::fixed, 2);
  std::println("{}", std::string_view(buf, r.ptr));

  r = std::to_chars(buf, buf + sizeof(buf), 255, 2);
  std::println("{}", std::string_view(buf, r.ptr));
}
```

```text title="実行結果"
0.1
3.14
11111111
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 毎フレームの数値表示（確保なし） | `std::to_chars(buf, buf + sizeof(buf), value)` |

## よくあるミス

??? failure "バッファが小さい"
    足りないと `ec == std::errc::value_too_large` です。`int` なら 12 バイト、`double` なら 32 バイト以上にします。

??? failure "終端に \0 があると思う"
    付きません。`std::string_view(buf, ptr - buf)` で扱います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::from_chars`](from_chars.md) | 文字列を数値に |
| `std::to_string` | 手軽だが確保する |
| [`std::format`](../utilities/format.md) | 書式つき |

## コンパイラ対応

C++17 の機能です。浮動小数点版は GCC 11 / MSVC 19.24 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 数値 → 文字列。確保なし・例外なし
    - [x] バッファは自分で用意
    - [x] 終端の `\0` は付かない

## 関連ページ

- [cpprefjp: std::to_chars](https://cpprefjp.github.io/reference/charconv/to_chars.html)
- [cppreference: std::to_chars](https://en.cppreference.com/w/cpp/utility/to_chars)
