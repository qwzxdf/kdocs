---
title: std::sprintf
summary: "書式を指定して、文字配列に書き込む。"
order: 900
tags:
  - 入出力・文字列
---

# std::sprintf

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

書式を使って作った文字列を、ファイルではなく、メモリ上の配列に入れたい。たとえば、「Player_01.png」のようなファイル名を作る。それをやるのが `std::sprintf` ですが、<strong>書き込む先の大きさを確かめない</strong>ため、バッファーを溢れさせる危険があります。

!!! tip "ポイント"
    - `sprintf(バッファー, 書式, 値...)`。戻り値は、書いた文字数（終端の `\0` を除く）
    - バッファーの大きさを指定できない。溢れると、メモリを破壊する
    - 代わりに `snprintf`（大きさを指定する版）を使う
    - C++ では `std::format`（C++20）や `std::to_string` のほうが安全で楽

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::sprintf {#sprintf}

```cpp
int sprintf(char* buffer, const char* format, ...);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `buffer` | `char*` | 結果を入れる配列 |
| `format` | `const char*` | 書式文字列 |
| `...` | 可変個引数 | 書式に対応する値 |

結果の文字数に、終端の `\0` を足した分の領域が `buffer` に必要です。`%d` で出る数字の桁数や、`%s` に渡す文字列の長さは、実行時に決まるので、固定の大きさの配列では、足りなくなることがあります。溢れると、周りのメモリを書き潰して、クラッシュや脆弱性の原因になります。

そのため、`sprintf` は避け、<strong>`snprintf(buffer, size, format, ...)` を使う</strong>のが原則です。`snprintf` は、書き込みを `size - 1` 文字までで止めて、必ず `\0` を付けます。

MSVC は、`sprintf` を使うと、警告（C4996）を出します。警告を黙らせるのではなく、`snprintf` に置き換えるのが正しい対処です。

## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  char name[32];
  int n = std::sprintf(name, "Player_%02d.png", 7);   // 余裕のある大きさの配列に
  std::println("{} ({} 文字)", name, n);

  // 安全な版: 大きさを渡す
  char small[8];
  int m = std::snprintf(small, sizeof(small), "Player_%02d.png", 7);
  std::println("切り詰め: {}", small);
  std::println("本来の長さ: {}", m);
}
```

```text title="実行結果"
Player_07.png (13 文字)
切り詰め: Player_
本来の長さ: 13
```

## ゲームでの使いどころ

既存の C のコードで見かけます。新しく書くなら、`snprintf` か、C++20 の `std::format`、`std::format_to_n` を使います。ファイル名の組み立てのような、文字列が短い場面でも、後で書式や元の文字列が変わって溢れることがあるので、大きさを指定できる版にしておきます。

## よくあるミス

??? failure "バッファーが足りず、メモリを壊す"
    桁数や文字列の長さが読めないものは、`snprintf` にします。

??? failure "`snprintf` の戻り値が、書いた文字数だと思う"
    戻り値は、切り詰めがなければ書けたはずの長さです。`size` 以上なら切れています。

## 類似

| 名前 | 違い |
| --- | --- |
| [`vsnprintf`](vsnprintf.md) | 可変個引数を `va_list` で受ける版 |
| [`fprintf`](fprintf.md) | ファイルに書く |
| `std::format` | C++20 の型安全な文字列組み立て |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 書式つきで文字配列に書く
    - [x] 大きさを指定できず危険
    - [x] `snprintf` を使う

## 関連ページ

- [cpprefjp: std::sprintf](https://cpprefjp.github.io/reference/cstdio/sprintf.html)
- [cppreference: std::sprintf](https://en.cppreference.com/w/cpp/io/c/sprintf)
