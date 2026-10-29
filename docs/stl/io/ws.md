---
title: std::ws
summary: "入力で、空白（スペース・改行・タブ）を読み飛ばす。"
order: 900
tags:
  - 入出力・文字列
---

# std::ws

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <istream>`
</div>

`std::cin >> n;` で数を読んだあと、続けて `std::getline` で 1 行読もうとすると、空の文字列が返ってきて、入力を読み損ねたように見えます。数字の直後の改行が、入力に残っているからです。`std::ws` は、入力の先頭にある空白（スペース、タブ、改行）をまとめて読み捨てる操作子で、この問題を片付けます。

!!! tip "ポイント"
    - 空白でない文字に当たるまで、入力を読み捨てる。その文字は読まずに残す
    - `>>` で数を読んだあとに `getline` をつなげるときに、挟んで使う
    - 入力が空白のまま終わったときは、`eofbit` が立つ（読み損ねの `failbit` ではない）
    - `skipws` と違い、設定ではなく、その場で 1 回読み捨てる操作

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::ws {#ws}

```cpp
template <class CharT, class Traits>
std::basic_istream<CharT, Traits>& ws(std::basic_istream<CharT, Traits>& is);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `is` | `basic_istream&` | 読み込み元のストリーム |

`is` から空白文字を読み捨てます。空白かどうかは、ストリームのロケールの `isspace` で判定します。空白以外の文字に当たったら、その文字は読み込まずに残して止まります。戻り値は、渡したストリームへの参照です。

`>>` による整形入力は、既定で先頭の空白を読み飛ばす設定（`skipws`）になっているので、`in >> a >> b` のように続ける場合に、`ws` を挟む必要はありません。必要になるのは、`getline` や `get` のような、空白を読み飛ばさない関数に切り替えるときです。

## 実際に動かしてみる

```cpp
#include <iostream>
#include <print>
#include <sstream>
#include <string>

int main() {
  std::istringstream in("42\nhello world\n");
  int n = 0;
  in >> n;

  std::string line;
  std::getline(in, line);
  std::println("ws なし: [{}]", line);   // 数字の直後の改行を読んでしまう

  std::istringstream in2("42\nhello world\n");
  in2 >> n >> std::ws;
  std::getline(in2, line);
  std::println("ws あり: [{}]", line);
}
```

```text title="実行結果"
ws なし: []
ws あり: [hello world]
```

`in >> n` が読むのは `42` までで、直後の `'\n'` は入力に残ります。そのまま `getline` を呼ぶと、その `'\n'` までの 0 文字を 1 行として返すので、空の文字列になります。`>> std::ws` を挟むと、`'\n'` が読み捨てられ、`getline` は `hello world` の行頭から始まります。

## ゲームでの使いどころ

コンソールのデバッグ コマンドや、設定ファイルの読み込みで使います。たとえば `spawn 5` の `5` を `>>` で読んだあと、続く行に自由な文字列（敵の名前など）を書く書式にしたいときです。数と行が混ざる入力では、`>> n >> std::ws` と書いておくのが定番です。

同じことは、`in.ignore()` や `in.ignore(std::numeric_limits<std::streamsize>::max(), '\n')` でもできます。ただし、`ignore()` は、空白かどうかに関係なく 1 文字か 1 行を捨てるので、行末に余計な空白があると失敗します。`ws` は、空白だけを捨てるので、行頭の字下げも一緒に消えて、意図に合いやすい書き方です。

## よくあるミス

??? failure "`ws` を挟んだのに、行頭の字下げまで消えてしまう"
    `ws` は、空白をすべて読み捨てます。字下げを残したい行は、`ws` ではなく、`ignore(1)` で改行 1 文字だけを捨てます。

??? failure "`cin >> n;` の直後の `getline` が空になる"
    直後の改行が残っています。`cin >> n >> std::ws;` のように、`ws` を挟みます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`skipws`](skipws.md) | 設定。`>>` が先頭の空白を読み飛ばすかを決める |
| [`istream::ignore`](basic_istream.md) | 空白かどうかに関係なく、指定した数や区切りまで捨てる |
| [`getline`](getline.md) | 区切りまでを読み込む。空白は読み飛ばさない |

## コンパイラ対応

C++98 から使えます。手元の MSVC（Visual Studio 2026）で動作を確かめました。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `ws` は、入力の先頭の空白をまとめて読み捨てる
    - [x] `>>` のあとで `getline` を使うとき、`>> std::ws` を挟むと、残った改行が消える
    - [x] 設定の `skipws` とは別物で、その場で 1 回だけ読み捨てる

## 関連ページ

- [cpprefjp: std::ws](https://cpprefjp.github.io/reference/ios/ws.html)
- [cppreference: std::ws](https://en.cppreference.com/w/cpp/io/manip/ws)
