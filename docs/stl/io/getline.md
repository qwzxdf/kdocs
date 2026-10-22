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

ファイルから設定を読むときも、ユーザーが入力した名前を受け取るときも、1 行ずつ読んで処理したい場面は多いです。`std::cin >> s` は空白で区切るので、「Taro Yamada」のような空白入りの名前が `Taro` と `Yamada` に分かれてしまいます。`std::getline` は、改行までを 1 行まとめて読むので、空白入りの文字列をそのまま受け取れます。

!!! tip "ポイント"
    - ファイルを全行処理するときは、`while (std::getline(in, line))` と書く。
    - 改行文字は読み捨てられ、`line` には含まれない。
    - 第 3 引数で区切りを変えられる。CSV なら `getline(in, field, ',')`。

!!! info "このページを読む前に"
    [`ifstream`](ifstream.md) や [`stringstream`](stringstream.md) で、ストリームから読む基本を先に読んでください。

## 関数の詳しい説明

### std::getline {#getline}

```cpp
std::istream& getline(std::istream& in, std::string& str, char delim = '\n');
```

`in` は読み取り元のストリームです。`std::cin`、`std::ifstream`、`std::istringstream` のどれでも渡せます。

`str` は読んだ結果を入れる文字列です。呼ぶたびに中身が上書きされ、前回の内容は消えます。大きな行を何度も読むときは、同じ `std::string` を使い回すと、メモリの確保が減ります。

`delim` は区切り文字です。既定は `'\n'` で、指定した文字までを読んで、区切りは捨てます。`getline(in, s, ',')` を繰り返せば、CSV の 1 項目ずつを取り出せます。ただし、引用符の中のカンマは扱えません。本格的な CSV は専用のライブラリを使います。

戻り値は `in` 自身で、`bool` として評価できます。1 文字も読めなかったとき（ファイルの終わり）は `false` になるので、`while` の条件に書けます。

- 空白を含めて 1 行読みます。名前の入力などに使います

## しくみ

`getline` が `while` の条件に書けるのは、戻り値のストリームが `bool` に変換できるからです。読み取りに失敗すると、ストリームに `failbit` が立ち、`bool` にすると `false` になります。ファイルの終わりでは `eofbit` と `failbit` が立ちます。

`std::cin >> n` のあとに `std::getline(std::cin, line)` を呼ぶと、空の行が読めてしまうことがあります。`>> n` は数字の後ろの改行を読まずに残すので、`getline` は、その残った改行だけを読んで、空の行として返すからです。`std::cin >> n >> std::ws;` と書いて、残った空白を読み飛ばしてから `getline` を呼びます。

Windows のテキストファイルは、行末が `\r\n` です。バイナリモードで開くと、`\r` が行の末尾に残ります。テキストモード（既定）で開けば、`\r\n` が `\n` に変換されます。

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

設定ファイルやセーブデータを行ごとに読むのが、基本の使い方です。`key=value` の形式なら、1 行読んで `=` で分けます。

```cpp
std::ifstream in("config.txt");
std::string line;
while (std::getline(in, line)) {
  if (line.empty() || line[0] == '#') {
    continue;  // 空行とコメントを飛ばす
  }
  // line を処理する
}
```

台詞やシナリオのテキストを 1 行ずつ読む場面でも使います。エンジンの開発中は、コンソールからのコマンド入力を `getline(std::cin, cmd)` で 1 行ずつ受け取って、デバッグコマンドにすることもあります。

## よくあるミス

??? failure "`>>` のあとに `getline` を呼んで空行を読む"
    `std::cin >> n; std::getline(std::cin, line);` は、`line` が空になります。`n` を読んだあと、改行が入力に残っているからです。間に `std::cin >> std::ws;` を入れて、空白を読み飛ばします。

??? failure "`eof()` でループを回す"
    `while (!in.eof()) { getline(in, line); ... }` と書くと、最後の行を読んだあとにもう一度ループが回り、空の行を処理してしまいます。`while (std::getline(in, line))` と書けば、読めたときだけ中が実行されます。

??? failure "Windows の `\r` が行の末尾に残る"
    Linux で作ったファイルを Windows で読む、またはその逆では、行末の違いで `\r` が残ることがあります。`line.pop_back()` で取り除くか、読み込み後に `\r` を削る処理を入れます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::cin`](cin.md) の `>>` | 空白で区切って 1 語ずつ読む。空白入りの文字列は読めない |
| `istream::get` | 1 文字だけ読む。バイナリや細かい制御向け |
| [`std::ws`](ws.md) | 先頭の空白を読み飛ばす。`>>` のあとに使う |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 全行処理は `while (std::getline(in, line))`。
    - [x] `>>` のあとで使うときは、`std::ws` で改行を読み飛ばす。
    - [x] 区切りは第 3 引数で変えられる。

## 関連ページ

- [cpprefjp: std::getline](https://cpprefjp.github.io/reference/string/basic_string/getline.html)
- [cppreference: std::getline](https://en.cppreference.com/w/cpp/string/basic_string/getline)
