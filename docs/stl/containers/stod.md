---
title: std::stod
summary: "文字列を double に変換する（失敗すると例外）。"
order: 63
group: 文字列と数値の変換
tags:
  - コンテナ
---

# std::stod

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-11">C++11</span>
`#include <string>`
</div>

`std::stod(str)` は、文字列を `double` に変換します。`"3.14"` も `"1e3"` も、`"-0.5"` も読めます。ロケールの影響を受け、小数点が `,` のロケールでは、`"3.14"` が `3` まで読まれることがあります。

!!! tip "ポイント"
    - `double` に変換する
    - 指数表記（`1e3`）や、`inf`、`nan` も読める
    - ロケールで小数点が変わる環境がある
    - 失敗は例外（`invalid_argument` / `out_of_range`）

!!! info "このページを読む前に"
    [`std::string`](string.md) を先に読んでください。

## 関数の詳しい説明

### std::stod {#stod}

<span class="ver ver-11">C++11</span>

```cpp
double stod(const std::string& str, std::size_t* pos = nullptr);
```

`strtod` の仕様に従います。先頭の空白を飛ばし、符号、数字、小数点、指数を読みます。`"1.5abc"` は 1.5 を返し、`pos` が 3 になります。

ロケールの影響を受けるため、`setlocale` で、小数点が `,` の国のロケールに設定されていると、`"3.14"` が `3` と読まれます。ゲームの設定ファイルのように、環境に依存してはいけないデータには、ロケールに依存しない `std::from_chars` が適しています。

値が `double` の範囲を超えると `out_of_range` です。

## 実際に動かしてみる

```cpp
#include <print>
#include <string>

int main() {
  std::println("{}", std::stod("3.14"));
  std::println("{}", std::stod("1e3"));
  std::println("{}", std::stod("-0.5"));

  std::size_t pos = 0;
  std::println("{} 位置 {}", std::stod("1.5abc", &pos), pos);
}
```

```text title="実行結果"
3.14
1000
-0.5
1.5 位置 3
```

## ゲームでの使いどころ

設定ファイルの小数の読み込みに使いますが、ロケールの影響を避けるなら `from_chars` です。

## よくあるミス

??? failure "ロケールに依存することを知らない"
    小数点が `,` のロケールで読み違えます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`stold`](stold.md) | `long double` |
| [`stol`](stol.md) | 整数 |
| `std::from_chars` | ロケールに依存しない |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::stod](https://cpprefjp.github.io/reference/string/stod.html)
- [cppreference: std::stod](https://en.cppreference.com/w/cpp/string/basic_string/stod)
