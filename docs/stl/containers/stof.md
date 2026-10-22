---
title: std::stof
summary: "文字列を float に変換する（失敗すると例外）。"
order: 62
group: 文字列と数値の変換
tags:
  - コンテナ
---

# std::stof

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-11">C++11</span>
`#include <string>`
</div>

設定ファイルから読んだ「0.25」という文字列を、`float` の値として使いたい。文字列と数値は別の型なので、変換が必要です。`std::stof` は、文字列を `float` に変換する関数で、[`stoi`](stoi.md) の小数版です。読めない文字列を渡すと、例外を投げます。`double` に変換するなら `stod` です。

!!! tip "ポイント"
    - `"0.25"` や `"1e3"` のような形式も読める。
    - 失敗は例外。
    - ロケールの影響を受ける（地域によって小数点が違う）。

!!! info "このページを読む前に"
    [`std::stoi`](stoi.md) の変換の仕組みと例外の扱いは、`stof` でも同じです。先にそちらを読んでください。

## 関数の詳しい説明

### std::stof {#stof}

```cpp
float stof(const std::string& str, std::size_t* pos = nullptr);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | `const std::string&` | 変換する文字列 |
| `pos` | `std::size_t*` | 変換に使った文字数を受け取る |

- 例外: `stoi` と同じ

```cpp
#include <print>
#include <string>

int main() {
  float gravity = std::stof("9.8");
  std::println("{}", gravity * 2.0f);
}
```

```text title="実行結果"
19.6
```

## ゲームでの使いどころ

設定ファイルやセーブデータから、小数の値を読み込むときに使います。`"gravity=9.8"` のように、`=` で分けた右側を `std::stof` で `float` にします。

ユーザーが入力した値や、外部のファイルの内容は、不正な文字列かもしれません。例外が投げられても落ちないように、`try` と `catch` で囲みます。例外を使いたくない場面では、`std::from_chars` を使います。こちらは例外を投げず、ロケールにも依存しません。

## よくあるミス

??? failure "不正な文字列で例外が飛んで、ゲームが落ちる"
    `std::stof("abc")` は `std::invalid_argument` を投げます。`catch` していないと、ゲームが終了します。外部から来る文字列は、`try` で囲むか、`from_chars` を使います。

??? failure "後ろの余計な文字が無視される"
    `std::stof("1.5abc")` は、エラーにならず `1.5` を返します。変換できた長さは第 2 引数の `size_t*` で受け取れるので、文字列全体が数値かを確かめたいときは、それを使います。

??? failure "ロケールで小数点が違う"
    `stof` は現在のロケールに従います。小数点をカンマで書くロケールでは、`"1.5"` が `1` として読まれることがあります。設定ファイルの読み込みには、ロケールに依存しない `from_chars` が確実です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::from_chars`](../io/from_chars.md) | ロケールに依存しない |
| [`stod`](stod.md) | double |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 文字列 → float
    - [x] 失敗は例外
    - [x] ロケールに依存する

## 関連ページ

- [cpprefjp: std::stof](https://cpprefjp.github.io/reference/string/stof.html)
- [cppreference: std::stof](https://en.cppreference.com/w/cpp/string/basic_string/stof)
