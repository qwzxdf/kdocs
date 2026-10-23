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

設定ファイルから読んだ「9.80665」のような文字列を、`double` の値として使いたい。精度が要る計算では、`float` では足りないことがあります。`std::stod` は、文字列を `double` に変換する関数です。[`stof`](stof.md) の `double` 版で、使い方はまったく同じです。読めない文字列には `std::invalid_argument`、範囲外には `std::out_of_range` を投げます。

!!! tip "ポイント"
    - 失敗は例外。
    - ロケールの影響を受ける。

!!! info "このページを読む前に"
    [`std::string`](string.md) を先に読んでください。

## 関数の詳しい説明

### std::stod {#stod}

```cpp
double stod(const std::string& str, std::size_t* pos = nullptr);
```

- `stof` の double 版です。

## 実際に動かしてみる

```cpp
#include <print>
#include <string>

int main() {
  double v = std::stod("3.25");
  std::println("{}", v);
}
```

```text title="実行結果"
3.25
```

## ゲームでの使いどころ

座標や時刻のように、`float` では桁が足りない値を読み込むときに使います。ワールドの座標が非常に大きいゲームでは、`double` で位置を持つことがあります。

ゲームの内部では `float` を使うことが多いので、`stof` のほうが出番は多めです。外部ファイルの値は不正かもしれないので、`try` で囲むか、`from_chars` を使います。

ロケールに影響されるのも、`stof` と同じです。小数点にカンマを使うロケールで、`"1.5"` が `1` と読まれる場合があります。

## よくあるミス

??? failure "例外を受けない"
    `try` / `catch` で受けます。

??? failure "不正な文字列で例外が飛ぶ"
    外部の入力が不正だと、`invalid_argument` が投げられます。`try` で守るか、例外を投げない `from_chars` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`stof`](stof.md) | float |
| [`std::from_chars`](../io/from_chars.md) | 例外なし |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 文字列 → double
    - [x] 失敗は例外
    - [x] stof の double 版

## 関連ページ

- [cpprefjp: std::stod](https://cpprefjp.github.io/reference/string/stod.html)
- [cppreference: std::stod](https://en.cppreference.com/w/cpp/string/basic_string/stod)
