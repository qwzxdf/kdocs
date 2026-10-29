---
title: std::quoted
summary: "文字列を、引用符で囲んで出力・入力する。"
order: 900
tags:
  - 入出力・文字列
---

# std::quoted

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-14">C++14</span>
`#include <iomanip>`
</div>

`"Boss Slime"` のように、空白を含む名前をテキストで保存すると、読み込むときに `Boss` と `Slime` に分かれてしまいます。`>>` が空白で区切るからです。名前を引用符で囲んで書き出し、読み込むときに引用符を外してくれるのが、C++14 の `std::quoted` です。

!!! tip "ポイント"
    - 出力すると、文字列が `"` で囲まれ、中の `"` は `\"` になる
    - 入力すると、囲みを外して、中身を 1 つの文字列として読む。空白を含んでいても分かれない
    - 区切り文字と、エスケープ文字は、変えられる（既定は `"` と `\`）
    - 書き出しと読み込みの両方に同じ `quoted` を使うと、元に戻る

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::quoted {#quoted}

```cpp
template <class CharT, class Traits, class Alloc>
/* 未規定 */ quoted(const std::basic_string<CharT, Traits, Alloc>& s,
                    CharT delim = CharT('"'), CharT escape = CharT('\\'));

template <class CharT, class Traits, class Alloc>
/* 未規定 */ quoted(std::basic_string<CharT, Traits, Alloc>& s,
                    CharT delim = CharT('"'), CharT escape = CharT('\\'));
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `s` | 文字列 | 書き出す（const）か、読み込み先（非 const）の文字列。`const CharT*` や `string_view` も渡せる |
| `delim` | 文字 | 文字列を囲む文字。既定は `"` |
| `escape` | 文字 | 中にある `delim` と `escape` の前に付ける文字。既定は `\` |

出力のときは、`delim` で囲み、中に `delim` か `escape` があれば、その前に `escape` を付けます。入力のときは、先頭の `delim` を確かめてから、次の `delim` まで読み、`escape` に続く文字は、そのまま取り込みます。先頭が `delim` でないときは、`>>` と同じように空白までを読みます。

この関数が返す値は、戻り値の型が未規定の、ストリームに渡すためだけの小さな入れ物です。変数に保存しないで、`<<` や `>>` の右側にそのまま書きます。

## 実際に動かしてみる

```cpp
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>

int main() {
  std::string name = "Boss Slime";
  std::cout << std::quoted(name) << '\n';

  std::string tricky = R"(He said "hi")";
  std::cout << std::quoted(tricky) << '\n';

  // 書いたものを、空白ごと読み戻せる
  std::stringstream ss;
  ss << std::quoted(name) << ' ' << 7;
  std::string back;
  int level = 0;
  ss >> std::quoted(back) >> level;
  std::cout << '[' << back << "] " << level << '\n';

  // quoted なしだと、空白で切れる
  std::stringstream ss2;
  ss2 << name;
  std::string w;
  ss2 >> w;
  std::cout << '[' << w << "]\n";
}
```

```text title="実行結果"
"Boss Slime"
"He said \"hi\""
[Boss Slime] 7
[Boss]
```

2 行目は、中にある `"` が `\"` になって、全体が囲まれています。3 行目は、書き出した `"Boss Slime" 7` から、名前を空白ごと読み戻し、続けて数も読めています。4 行目は、`quoted` なしの場合で、空白で `Boss` と `Slime` に分かれ、`Boss` だけが読まれています。

## ゲームでの使いどころ

名前やメッセージのような、空白を含む文字列を、簡単なテキスト形式で保存するときです。セーブ データを 1 行 1 項目の `名前 レベル HP` の形で書くと、名前に空白があった瞬間に壊れます。`quoted` で名前を囲めば、区切りの空白と、名前の中の空白を区別できます。

その代わり、`quoted` が扱うのは、引用符とバックスラッシュだけです。改行を含む文字列を 1 行に収めたいときは、別に変換が要ります。JSON のような本格的な形式を使えるなら、ライブラリに任せたほうが安全です。

## よくあるミス

??? failure "書き出しには `quoted` を付けたが、読み込みに付け忘れた"
    読み込みは、囲みを外す処理が働かないので、`"Boss` のように、引用符が付いたまま読まれます。両方に `quoted` を付けます。

??? failure "`const char*` を読み込み先にした"
    読み込み先は、書き換えられる `std::string` でなければなりません。`const` の文字列や、`const char*` は、書き出しにしか使えません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`getline`](getline.md) | 区切りまでを読む。囲みやエスケープは扱わない |
| [`put_money`](put_money.md) | 金額を書式付きで出力する |

## コンパイラ対応

C++14 から使えます。手元の MSVC（Visual Studio 2026）で動作を確かめました。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `quoted` は、文字列を `"` で囲んで出力し、読むときは囲みを外す
    - [x] 中の `"` は `\"` と書き出されるので、空白や引用符を含む文字列も元に戻る
    - [x] 書き出しと読み込みの、両方に付ける

## 関連ページ

- [cpprefjp: std::quoted](https://cpprefjp.github.io/reference/ios/quoted.html)
- [cppreference: std::quoted](https://en.cppreference.com/w/cpp/io/manip/quoted)
