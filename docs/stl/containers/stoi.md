---
title: std::stoi
summary: "文字列を int に変換する（失敗すると例外）。"
order: 61
group: 文字列と数値の変換
tags:
  - コンテナ
---

# std::stoi

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-11">C++11</span>
`#include <string>`
</div>

設定ファイルから読んだ「100」という文字列を `int` の値として使いたい。文字列と数値は別の型なので、変換が必要です。`std::stoi` は、文字列を `int` に変換する関数です。数字として読めなければ `std::invalid_argument`、範囲を超えていれば `std::out_of_range` の例外を投げます。仲間に `stol`、`stoll`、`stoul` などがあります。

!!! tip "ポイント"
    - 数字の前の空白は読み飛ばされ、数字の後ろの文字は無視される。
    - 変換できないと**例外**。
    - 失敗を例外にしたくないなら `from_chars`。

!!! info "このページを読む前に"
    例外の扱いが分かると読みやすいです。例外を使わない変換は、[`std::from_chars`](../io/from_chars.md) にまとめてあります。

## 関数の詳しい説明

### std::stoi {#stoi}

```cpp
int stoi(const std::string& str, std::size_t* pos = nullptr, int base = 10);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | `const std::string&` | 変換する文字列。先頭の空白は飛ばされる |
| `pos` | `std::size_t*` | 変換に使った文字数を受け取る（要らなければ省略） |
| `base` | `int` | 進数（2〜36）。`16` なら 16 進数、`0` なら `0x` などから自動判定 |

- 戻り値: 変換した `int`
- 例外: 数字で始まらなければ `std::invalid_argument`、int に入らなければ `std::out_of_range`

```cpp
#include <print>
#include <string>

int main() {
  std::println("{}", std::stoi("1500"));
  std::println("{}", std::stoi("ff", nullptr, 16));

  std::size_t used = 0;
  int value = std::stoi("42px", &used);
  std::println("{} ({} 文字使った)", value, used);
}
```

```text title="実行結果"
1500
255
42 (2 文字使った)
```

!!! note "実際は"
    例外を使わないなら `std::from_chars`（`<charconv>`）のほうが速く、失敗をエラーコードで返してくれます。

## ゲームでの使いどころ

設定ファイルの値やコマンドライン引数、コンソールに入力された数値を読み込むのが基本の使い方です。`std::stoi(args[1])` で、レベル番号を受け取ります。

外部から来る文字列は、不正かもしれないので、`try` と `catch` で囲みます。例外を使えない環境や、失敗が普通に起きる処理（大量のファイルを検査するなど）では、`std::from_chars` を使います。こちらは例外を投げず、速くもあります。

16 進数の文字列を読むときは、第 3 引数に基数を渡します。`std::stoi("ff", nullptr, 16)` は `255` です。

## よくあるミス

??? failure "前の空白と後ろの文字が許される"
    `std::stoi("  42abc")` は、前の空白を読み飛ばし、後ろの `abc` を無視して `42` を返します。文字列全体が数字かを確かめるには、第 2 引数で読んだ文字数を受け取り、文字列の長さと比べます。

??? failure "例外を捕まえずにゲームが落ちる"
    不正な文字列で `invalid_argument` が投げられ、`catch` していないと異常終了します。外部の入力は `try` で守ります。

??? failure "`int` に収まらない値"
    `std::stoi("99999999999")` は `out_of_range` です。大きい値が来うるなら `stoll` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::from_chars`](../io/from_chars.md) | 例外なし・高速 |
| [`stof`](stof.md) | float に変換 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 文字列 → int
    - [x] 失敗は例外
    - [x] 例外なしなら from_chars

## 関連ページ

- [cpprefjp: std::stoi](https://cpprefjp.github.io/reference/string/stoi.html)
- [cppreference: std::stoi](https://en.cppreference.com/w/cpp/string/basic_string/stoi)
