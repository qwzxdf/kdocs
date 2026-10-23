---
title: std::from_chars
summary: "文字列を数値に変換する。速くて、例外を投げない。"
order: 83
tags:
  - 入出力・文字列
---

# std::from_chars

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-17">C++17</span>
`#include <charconv>`
</div>

`std::stoi` は、不正な文字列で例外を投げ、メモリを確保し、ロケールにも影響されます。大量のデータを読み込むゲームのローダーでは、これらが遅さと不安定さの原因になります。`std::from_chars` は、文字列を数値に変換する関数で、例外を投げず、メモリも確保せず、ロケールにも依存しません。結果は、戻り値のエラーコードで受け取ります。

!!! tip "ポイント"
    - `auto [ptr, ec] = std::from_chars(first, last, value);` と受ける。
    - `ec == std::errc{}` なら成功。`ptr` は読み終えた位置。
    - 先頭の空白や `+` は受け付けない。

!!! info "このページを読む前に"
    [`std::stoi`](../containers/stoi.md) との違いを知っておくと読みやすいです。`from_chars` は、その例外を使わない版です。

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
| `fmt` | `std::chars_format` | 浮動小数点の書き方（[フラグ](#flags)） |

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

## フラグ・オプション {#flags}

`std::chars_format` は、浮動小数点を文字列から読むときに、どの書き方を受け付けるかを決める列挙型です。整数を読む `from_chars` には関係しません。

### std::chars_format::general

`fixed` と `scientific` の両方を受け付けます。`"3.14"` も `"1e3"` も読めます。`fmt` を省略したときの既定がこれです。

### std::chars_format::fixed

`"3.14"` のような小数点の書き方だけを受け付けます。`"1e3"` は、`1` の部分だけを読んで、`e3` が残ります。

### std::chars_format::scientific

`"1e3"` のような指数の部分が**必須**です。`"3.14"` のように指数がないと、読み取りに失敗します（`errc::invalid_argument`）。

### std::chars_format::hex

16 進数として読みます。`"0x"` の接頭辞は付けません。`"ff"` や `"1.8p3"` のように、指数は `p` で書きます。

## ゲームでの使いどころ

設定ファイル、CSV、独自形式のデータなど、大量の数値を読み込む処理に使います。`auto [ptr, ec] = std::from_chars(first, last, value);` と受け、`ec == std::errc{}` なら成功です。`ptr` は読み終えた位置を指すので、続きの解析に使えます。

先頭の空白や `+` は、受け付けません。呼ぶ前に取り除きます。文字列は `string_view` で渡せるので、コピーなしで読めます。

小数の読み込みも使えます（C++17、対応は実装による）。ロケールに依存しないので、小数点が常に `.` で扱われ、国をまたぐデータで安全です。

## よくあるミス

??? failure "末尾に余計な文字があっても成功する"
    `from_chars` は読めるところまで読みます。全体が数値かは `ptr == last` で確かめます。

??? failure "先頭に空白や + がある"
    受け付けません。前処理で取り除きます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::to_chars`](to_chars.md) | 数値を文字列にする |
| `std::stoi` | 例外を投げる。遅い |
| [`std::istringstream`](istringstream.md) | 型安全だが遅い |

## コンパイラ対応

C++17 の機能です。浮動小数点版は GCC 11 / MSVC 19.24 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 文字列 → 数値。速く例外なし
    - [x] 成功は `ec == errc{}`
    - [x] 全体が数値か `ptr == last` で確認

## 関連ページ

- [cpprefjp: std::from_chars](https://cpprefjp.github.io/reference/charconv/from_chars.html)
- [cppreference: std::from_chars](https://en.cppreference.com/w/cpp/utility/from_chars)
