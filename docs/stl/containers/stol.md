---
title: std::stol
summary: "文字列を long に変換する（失敗すると例外）。"
order: 900
tags:
  - コンテナ
---

# std::stol

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <string>`
</div>

文字列 `"123"` を整数に直したい。`std::stol(str)` は、`std::string` を `long` に変換します。先頭の空白を読み飛ばし、数字として読める所まで変換して、残りは無視します。変換できなければ、例外を投げます。

!!! tip "ポイント"
    - 先頭の空白を飛ばし、符号と数字を読む
    - 数字でない文字に当たったら、そこで止まる（残りは無視）
    - 全く変換できなければ `std::invalid_argument`、範囲外なら `std::out_of_range`
    - 第 2 引数で、読み終えた位置を受け取れる

!!! info "このページを読む前に"
    [`std::string`](string.md) を先に読んでください。

## 関数の詳しい説明

### std::stol {#stol}

<span class="ver ver-11">C++11</span>

```cpp
long stol(const std::string& str, std::size_t* pos = nullptr, int base = 10);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | `const std::string&` | 変換する文字列 |
| `pos` | `std::size_t*` | 読み終えた位置の受け取り先。不要なら `nullptr` |
| `base` | `int` | 進数。2〜36、または 0（自動判定） |

`base` が 0 のとき、`0x` で始まれば 16 進、`0` で始まれば 8 進、それ以外は 10 進です。

`"12abc"` は、12 を返し、`pos` に 2 を入れます。余計な文字が続いていることを検出したいなら、`pos` が文字列の長さに等しいかを確かめます。

例外を使うので、ユーザーの入力のように、失敗がありうる変換では、`try` で囲むか、例外を投げない `std::from_chars` を使います。Windows では `long` が 32 ビットです。64 ビットが必要なら `stoll` です。

## 実際に動かしてみる

```cpp
#include <print>
#include <stdexcept>
#include <string>

int main() {
  std::println("{}", std::stol("123"));
  std::println("{}", std::stol("  -42"));  // 先頭の空白は読み飛ばす

  std::size_t pos = 0;
  std::println("{} 読み終えた位置 {}", std::stol("12abc", &pos), pos);

  std::println("16 進: {}", std::stol("ff", nullptr, 16));

  try {
    std::stol("abc");
  } catch (const std::invalid_argument&) {
    std::println("変換できない: invalid_argument");
  }
}
```

```text title="実行結果"
123
-42
12 読み終えた位置 2
16 進: 255
変換できない: invalid_argument
```

## ゲームでの使いどころ

設定ファイルの数値の読み込みに使います。入力が信頼できないなら、`from_chars` で例外なしに検査します。

## よくあるミス

??? failure "余計な文字を見逃す"
    `"12abc"` が 12 になります。`pos` で確かめます。

??? failure "例外を考えない"
    変換できないと例外で止まります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`stoul`](stoul.md) | 符号なし |
| [`stoll`](stoll.md) | `long long` |
| `std::from_chars` | 例外なしで速い |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::stol](https://cpprefjp.github.io/reference/string/stol.html)
- [cppreference: std::stol](https://en.cppreference.com/w/cpp/string/basic_string/stol)
