---
title: std::formatted_size
summary: "書式化した結果が何文字になるかだけを返す（文字列は作らない）。"
order: 900
tags:
  - ユーティリティ
---

# std::formatted_size

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <format>`
</div>

整形した結果を、ちょうど入る大きさのバッファに書きたい。そのためには、結果の長さを先に知る必要があります。`std::formatted_size(fmt, args...)` は、実際には文字列を作らずに、整形した結果の長さだけを返します。`std::format_to_n` の `size` と同じ値ですが、書き込みなしで求められます。

!!! tip "ポイント"
    - 整形後の文字数を返す。文字列は作らない
    - 返した長さのバッファを用意して、`format_to` で書き込む、という使い方
    - 長さは文字数（バイト数）で、終端の `\0` は含まない
    - 計算に整形と同じ手間がかかる

!!! info "このページを読む前に"
    [`std::format_to`](format_to.md) を先に読んでください。

## 関数の詳しい説明

### std::formatted_size {#formatted_size}

<span class="ver ver-20">C++20</span>

```cpp
template <class... Args>
std::size_t formatted_size(std::format_string<Args...> fmt, Args&&... args);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `fmt` | `std::format_string` | 書式文字列 |
| `args` | 任意 | 書式の引数 |

整形と同じ処理を行いますが、結果を捨てて、文字数だけを数えます。幅の指定（`{:>10}`）があれば、その幅も含めた長さです。

`std::string` に整形するだけなら、`std::format` で足ります。バッファを、あらかじめ確保したいとき（固定長の領域、メモリ プール）に、ちょうどの大きさを知るのに使います。

文字数の数え方は、バイト数です。UTF-8 の日本語は、1 文字が 3 バイトとして数えられます。

## 実際に動かしてみる

```cpp
#include <format>
#include <print>
#include <string>

int main() {
  std::println("{}", std::formatted_size("{}", 12345));       // 5
  std::println("{}", std::formatted_size("{:>10}", 42));      // 幅 10
  std::println("{}", std::formatted_size("{:.2f}", 3.14159)); // "3.14"

  // ちょうどの大きさのバッファに書く
  const std::size_t n = std::formatted_size("HP {}/{}", 30, 100);
  std::string buf(n, '\0');
  std::format_to(buf.begin(), "HP {}/{}", 30, 100);
  std::println("{} ({} 文字)", buf, n);
}
```

```text title="実行結果"
5
10
4
HP 30/100 (9 文字)
```

## ゲームでの使いどころ

メモリ プールから文字列の領域を確保するとき、必要な大きさを先に求めます。

## よくあるミス

??? failure "終端の分を数え忘れる"
    返る値に `\0` は含まれません。C の文字列として使うなら、1 を足します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`format_to_n`](format_to_n.md) | 長さを制限して書き込む |
| [`format`](format.md) | 文字列を作って返す |
| `std::snprintf(nullptr, 0, ...)` | C の同様の方法 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::formatted_size](https://cpprefjp.github.io/reference/format/formatted_size.html)
- [cppreference: std::formatted_size](https://en.cppreference.com/w/cpp/utility/format/formatted_size)
