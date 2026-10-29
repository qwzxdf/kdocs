---
title: std::ends
summary: "文字列の終端（`'\\0'`）を出力する。"
order: 900
tags:
  - 入出力・文字列
---

# std::ends

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <ostream>`
</div>

`ostringstream` に書いた文字列は、`str()` で取り出せば `std::string` になります。ところが、固定長の `char` 配列に直接書き込むストリーム（C++23 の `ospanstream` や、古い `ostrstream`）では、書き終わった文字列の後ろに終端文字が付きません。C の関数に渡す前に閉じておく必要があります。`std::ends` は、その `'\0'` を 1 文字書き込む操作子です。

!!! tip "ポイント"
    - 書き込むのは、文字型の既定値（`char` なら `'\0'`）1 文字だけ。改行も、フラッシュもしない
    - `ostringstream` に使うと、`str()` の長さが 1 増える。ふつうは要らない
    - 固定長の `char` 配列に書く `ospanstream` で、C の文字列として閉じるために使う
    - 名前は「end of string」の意味。`endl`（end of line）と取り違えやすい

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::ends {#ends}

```cpp
template <class CharT, class Traits>
std::basic_ostream<CharT, Traits>& ends(std::basic_ostream<CharT, Traits>& os);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `os` | `basic_ostream&` | 書き込み先のストリーム |

`os.put(CharT())` を呼ぶのと同じです。`char` のストリームなら `'\0'`、`wchar_t` のストリームなら `L'\0'` を 1 文字書き込みます。戻り値は、渡したストリームへの参照です。

`os << std::ends` と書けるのは、`ostream` が「ストリームを受け取って返す関数」を `<<` で受け付ける仕組みを持っているからです。`endl` や `flush` と同じ形で、`std::ends` の後ろに続けて `<<` をつなげます。

## 実際に動かしてみる

`ostringstream` に使うと、文字列の長さが 1 増えます。

```cpp
#include <iostream>
#include <print>
#include <sstream>
#include <cstring>

int main() {
  std::ostringstream a;
  a << "ab";
  std::ostringstream b;
  b << "ab" << std::ends;
  std::println("ends なし: {}", a.str().size());
  std::println("ends あり: {}", b.str().size());
  // c_str() は終端が 1 つあるので、strlen では見えない
  std::println("strlen: {}", std::strlen(b.str().c_str()));
}
```

```text title="実行結果"
ends なし: 2
ends あり: 3
strlen: 2
```

`str()` の長さは 3 ですが、`'\0'` が文字列の中に入っているだけで、`c_str()` を C の関数に渡すと 2 文字として読まれます。`std::string` として扱う限り、この余分な 1 文字は邪魔になるだけです。

本来の使い道は、固定長の配列に書くときです。C++23 の `ospanstream` は、渡した配列の中に直接書き込み、終端文字を勝手には足しません。

```cpp
#include <print>
#include <spanstream>
#include <cstring>

int main() {
  char buf[16] = "xxxxxxxxxxxxxxx";
  std::ospanstream os{std::span<char>(buf)};
  os << "ab";
  std::println("ends なし: {}", std::strlen(buf) > 2);     // 後ろの x が残る
  std::ospanstream os2{std::span<char>(buf)};
  os2 << "ab" << std::ends;
  std::println("ends あり: [{}]", buf);                      // 'ab' で終わる
}
```

```text title="実行結果"
ends なし: true
ends あり: [ab]
```

1 回目は、配列が `x` で埋まっていたので、`ab` の後ろに `x` が続いたまま `strlen` が 2 より大きくなります。2 回目は `ends` で `'\0'` を書いたので、`ab` で止まります。

## ゲームでの使いどころ

スタック上の固定長バッファに、書式付きで文字列を組み立てて、`const char*` を要求する C の API（ウィンドウのタイトル、外部ライブラリのログ関数など）へ渡す場面で使います。ヒープを使わずに済むので、毎フレーム呼ばれる場所では向いています。

ただし、現代の C++ では `std::format_to_n(buf, sizeof(buf) - 1, ...)` で、書式付きの文字列を固定長バッファに書けます。終端も自分で書けて、書き込み先が溢れる心配も少ないので、新しく書くコードはそちらのほうが素直です。`ends` は、`ospanstream` や、古いコードの `ostrstream` を読むときに出会う操作子と考えてください。

## よくあるミス

??? failure "`ostringstream` に `ends` を付けたら、文字列の比較が合わない"
    `str()` の末尾に `'\0'` が入っています。`str() == "ab"` は `false` になります。`ostringstream` では、`ends` は付けません。

??? failure "`ospanstream` に書いた配列を、`ends` なしで C の関数に渡した"
    配列に前の内容が残っていると、書いた文字列の後ろに、ごみが続いて見えます。`ends` で閉じるか、`char buf[16]{}` のように、最初から 0 で埋めておきます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`endl`](endl.md) | 改行を書いて、フラッシュする |
| [`flush`](flush.md) | 何も書かず、バッファの中身を送り出す |
| [`ospanstream`](ospanstream.md) | 固定長の配列に直接書くストリーム。`ends` の使い道 |

## コンパイラ対応

`ends` は C++98 から使えます。`ospanstream` を使う例は C++23 で、手元の MSVC（Visual Studio 2026）で動作を確かめました。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `ends` は `'\0'` を 1 文字書き込む
    - [x] `ostringstream` には使わない（`str()` の長さが 1 増える）
    - [x] 固定長の配列に書く `ospanstream` で、C の文字列として閉じるときに使う

## 関連ページ

- [cpprefjp: std::ends](https://cpprefjp.github.io/reference/ios/ends.html)
- [cppreference: std::ends](https://en.cppreference.com/w/cpp/io/manip/ends)
