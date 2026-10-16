---
title: std::from_chars / std::to_chars
tags:
  - 入出力
  - 文字列
---

# std::from_chars / std::to_chars

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="perf perf-4">◎ 速い</span>
<span class="ver ver-17">C++17</span>
`#include <charconv>`
</div>

`std::from_chars` は**文字列から数値への変換**、`std::to_chars` は**数値から文字列への変換**を行う関数です。[`std::stoi`](../containers/string.md#stoi) や `std::to_string` と違って、**メモリ確保をせず、例外も投げず、ロケール（国の設定）にも影響されない**ので、とても速くて安全です。設定ファイルやセーブデータを大量に読み込むパーサーで使います。

!!! tip "結論"
    - 文字列 → 数値は `std::from_chars(先頭, 末尾, 結果)`。成功したか `ec == std::errc{}` で確かめる。
    - 数値 → 文字列は `std::to_chars(バッファ先頭, バッファ末尾, 値)`。
    - 例外を使わないゲームのコードに向いている。
    - 少し書くのが面倒なので、ちょっとした変換なら `std::stoi` / `std::format` で十分。

## 関数一覧

| 関数 | 重要度 | 何をする |
| --- | --- | --- |
| [`std::from_chars`](#from_chars) | <span class="rank rank-sometimes">たまに</span> | 文字列から数値へ |
| [`std::to_chars`](#to_chars) | <span class="rank rank-sometimes">たまに</span> | 数値から文字列へ |

## よくある使い方

```cpp
#include <charconv>
#include <optional>
#include <print>
#include <string_view>

// 失敗したら nullopt を返す、例外を使わない変換
std::optional<int> ParseInt(std::string_view s) {
  int value = 0;
  auto [ptr, ec] = std::from_chars(s.data(), s.data() + s.size(), value);
  if (ec != std::errc{} || ptr != s.data() + s.size()) {  // 失敗、または後ろにゴミがある
    return std::nullopt;
  }
  return value;
}

int main() {
  for (std::string_view s : {"1500", "-42", "12abc", "", "99999999999"}) {
    if (auto v = ParseInt(s)) {
      std::println("[{}] → {}", s, *v);
    } else {
      std::println("[{}] → 失敗", s);
    }
  }
}
```

```text title="実行結果"
[1500] → 1500
[-42] → -42
[12abc] → 失敗
[] → 失敗
[99999999999] → 失敗
```

## 関数の詳しい説明

### std::from_chars {#from_chars}

```cpp
std::from_chars_result from_chars(const char* first, const char* last, int& value, int base = 10);
std::from_chars_result from_chars(const char* first, const char* last, double& value,
                                  std::chars_format fmt = std::chars_format::general);
// 整数・浮動小数点の型ごとにある

struct from_chars_result {
  const char* ptr;  // 読み終わった次の位置
  std::errc ec;     // エラー（成功なら std::errc{}）
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `first`, `last` | `const char*` | 読む範囲 |
| `value` | 数値の参照 | 結果が入る（失敗したら変わらない） |
| `base` | `int` | 進数（2〜36）。整数版のみ |
| `fmt` | `std::chars_format` | 浮動小数点の書き方（[フラグ](#フラグオプション)） |

- 先頭の空白や `+` は**受け付けません**（`"+5"` や `" 5"` は失敗）
- エラーの種類: `std::errc::invalid_argument`（数字で始まらない）、`std::errc::result_out_of_range`（型に入らない）

```cpp
#include <charconv>
#include <print>
#include <string_view>

int main() {
  std::string_view s = "ff 3.25";
  int color = 0;
  auto r1 = std::from_chars(s.data(), s.data() + 2, color, 16);
  double scale = 0;
  auto r2 = std::from_chars(s.data() + 3, s.data() + s.size(), scale);
  std::println("{} {} / ok? {} {}", color, scale, r1.ec == std::errc{}, r2.ec == std::errc{});
}
```

```text title="実行結果"
255 3.25 / ok? true true
```

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

## フラグ・オプション

`std::chars_format`（浮動小数点の書き方）です。

| 値 | 重要度 | 意味 | 例 |
| --- | --- | --- | --- |
| `general`（省略時） | <span class="rank rank-sometimes">たまに</span> | fixed と scientific の短いほう | `1234.5` |
| `fixed` | <span class="rank rank-sometimes">たまに</span> | 固定小数点 | `1234.500` |
| `scientific` | <span class="rank rank-rare">知ってるだけ</span> | 指数表記 | `1.2345e+03` |
| `hex` | <span class="rank rank-rare">知ってるだけ</span> | 16 進数の浮動小数点 | `1.34ap+10` |

## 古い書き方と今の書き方

=== "古い書き方"

    ```cpp
    int v = atoi(text);           // 失敗が分からない（0 になる）
    int v2 = std::stoi(text);     // 失敗すると例外
    ```

=== "今の書き方（C++17）"

    ```cpp
    int v = 0;
    auto [ptr, ec] = std::from_chars(text.data(), text.data() + text.size(), v);
    if (ec == std::errc{}) {
    }
    ```

## ゲームでの使いどころ

| 場面 | 例 |
| --- | --- |
| 設定ファイル・CSV の大量読み込み | 1 行ずつ `from_chars` |
| セーブデータのテキスト形式 | 数値と文字列の高速な変換 |
| デバッグ表示 | 確保なしで数値を文字にする（`to_chars`） |

## よくあるミス

??? failure "成功したか確かめない"
    失敗しても `value` は変わらないだけなので、初期値のまま使ってしまいます。

??? failure "\"+5\" や前の空白が読めない"
    `from_chars` は `+` も空白も受け付けません。必要なら先に取り除きます。

## 理解度チェック

!!! question "Q1. `from_chars` で `\"42px\"` を int に読むと、結果と ptr は？"
    <div class="spoiler" markdown>

    **答え:** 値は 42、`ec` は成功、`ptr` は `p` を指します（数字の後ろで止まる）。全部が数字か確かめるには `ptr == 末尾` を見ます。

    </div>

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::stoi` / `std::stof`](../containers/string.md#stoi) | 失敗すると例外。手軽 |
| [`std::to_string`](../containers/string.md#to_string) | 確保あり。小数は 6 桁固定 |
| [`std::format`](../utilities/format.md) | 書式を細かく指定できる |

## コンパイラ対応

C++17 の機能です。整数版は主要なコンパイラすべてで使えます。浮動小数点版は GCC 11 / Clang（libc++）17 / MSVC VS 2019 16.4 以降が目安です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 速くて例外なしの変換は from_chars / to_chars
    - [x] `ec == std::errc{}` で成功を確認
    - [x] to_chars は `'\0'` を付けない

## 関連ページ

- [cpprefjp: <charconv>](https://cpprefjp.github.io/reference/charconv.html)
- [cppreference: std::from_chars](https://en.cppreference.com/w/cpp/utility/from_chars)
