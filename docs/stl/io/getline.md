---
title: std::getline
summary: "ストリームから 1 行を読んで、std::string に入れる。"
order: 73
tags:
  - 入出力・文字列
---

# std::getline

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-11">C++98〜</span>
`#include <string>`
</div>

`std::getline` は、**ストリームから 1 行（改行まで）を読んで、`std::string` に入れる**関数です。`std::cin`、ファイル（`ifstream`）、文字列ストリーム（`istringstream`）のどれにも使えます。ファイルを 1 行ずつ処理する `while (std::getline(in, line))` は定番の書き方です。

!!! tip "ポイント"
    - **`while (std::getline(in, line))`** で、全行を処理する。
    - 改行文字は `line` に含まれない。
    - 区切りを改行以外にしたいなら、第 3 引数で指定する（`getline(in, s, ',')`）。

## 関数の詳しい説明

### std::getline {#getline}

```cpp
std::istream& getline(std::istream& in, std::string& str, char delim = '\n');
```

- 空白を含めて 1 行読みます。名前の入力などに使います

## 実際に動かしてみる

```cpp
#include <iostream>
#include <print>
#include <sstream>
#include <string>

int main() {
  std::istringstream in("line1\nline2\n");
  std::string line;
  while (std::getline(in, line)) {
    std::println("[{}]", line);
  }
}
```

```text title="実行結果"
[line1]
[line2]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 設定ファイル・CSV を 1 行ずつ読む | `while (std::getline(file, line))` |
| カンマ区切りを分ける | `std::getline(ss, field, ',')` |

## よくあるミス

??? failure "Windows の改行（\r\n）で \r が残る"
    バイナリで開いたファイルでは、`\r` が行末に残ります。テキストモードで開くか、`line.back() == '\r'` を取り除きます。

??? failure ">> のあとに getline する"
    `>>` は改行を残すので、次の `getline` が空行を読みます。`ignore` を挟みます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ifstream`](ifstream.md) | 読み込み元のファイル |
| [`std::istringstream`](istringstream.md) | 文字列を読み込み元にする |
| [`std::cin`](cin.md) | 標準入力 |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 1 行を読む
    - [x] `while (getline(...))` で全行
    - [x] 区切りを変えられる

## 関連ページ

- [cpprefjp: std::getline](https://cpprefjp.github.io/reference/string/basic_string/getline.html)
- [cppreference: std::getline](https://en.cppreference.com/w/cpp/string/basic_string/getline)
