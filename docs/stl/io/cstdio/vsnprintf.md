---
title: std::vsnprintf
summary: "可変引数のリスト（va_list）を使って、大きさを指定して文字配列に書き込む。"
order: 900
tags:
  - 入出力・文字列
---

# std::vsnprintf

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdarg>`
</div>

自作のログ関数で、書式つきの文字列を、固定の配列に安全に作りたい。出力が長すぎたときも、メモリを壊さずに切り詰めたい。それをやる、いちばん安全な書式出力の関数が `std::vsnprintf` です。

<strong>バッファーの大きさを受け取り、溢れないように切り詰め、本来の長さを返します</strong>。

!!! tip "ポイント"
    - `vsnprintf(バッファー, 大きさ, 書式, va_list)`。必ず `\0` で終わらせる（大きさが 1 以上なら）
    - 戻り値は、切り詰めがなければ書けたはずの文字数。`大きさ` 以上なら切れている
    - `nullptr` と大きさ 0 を渡すと、必要な長さだけが分かる
    - 動的に確保した配列に、ちょうどの大きさで書く 2 段階の手順に使える

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::vsnprintf {#vsnprintf}

```cpp
int vsnprintf(char* buffer, std::size_t buf_size, const char* format, std::va_list vlist);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `buffer` | `char*` | 結果を入れる配列。`nullptr` も可（`buf_size` が 0 のとき） |
| `buf_size` | `size_t` | 配列の大きさ（終端の `\0` を含む） |
| `format` | `const char*` | 書式文字列 |
| `vlist` | `va_list` | 書式に対応する値の並び |

書き込みは、最大で `buf_size - 1` 文字までで、必ず `\0` を付けます。戻り値は、<strong>バッファーが無限に大きかったら書けたはずの文字数</strong>（`\0` を除く）です。そのため、戻り値が `buf_size` 以上なら、切り詰められています。失敗時は負の値を返します。

この戻り値を使うと、ちょうどの大きさで確保し直せます。1 回目は `nullptr` と 0 を渡して長さだけを調べ、2 回目で、その長さ + 1 の配列に書きます。`va_list` は 1 回使うと壊れるため、`va_copy` で複製してから、1 回目の呼び出しに使います。

自作のロガーで、固定長の配列に溜めてから出力する、というときの標準的な道具です。C++20 以降なら `std::format_to_n` や `std::vformat` も選べます。

## 実際に動かしてみる

```cpp
#include <cstdarg>
#include <cstdio>
#include <print>
#include <string>

std::string Format(const char* fmt, ...) {
  std::va_list args;
  va_start(args, fmt);

  std::va_list copy;
  va_copy(copy, args);
  int len = std::vsnprintf(nullptr, 0, fmt, copy);   // 必要な長さだけを調べる
  va_end(copy);

  std::string result(static_cast<std::size_t>(len), '\0');
  std::vsnprintf(result.data(), result.size() + 1, fmt, args);   // ちょうどの大きさに書く
  va_end(args);
  return result;
}

int main() {
  std::println("{}", Format("HP: %d / %d (%s)", 85, 120, "ok"));
}
```

```text title="実行結果"
HP: 85 / 120 (ok)
```

## ゲームでの使いどころ

自作のログ関数や、書式つきの文字列を `std::string` で返すヘルパーを作るときに使います。長さを 2 回に分けて調べる手順は、定番のイディオムです。

C++20 の `std::format` が使える環境では、型安全なので、そちらを選びます。`vsnprintf` は、C のライブラリの書式（`%d` など）に合わせる必要がある場面や、`va_list` を受け渡す境界で使います。

## よくあるミス

??? failure "戻り値が `buf_size` 以上なのを確かめず、切れたまま使う"
    戻り値と `buf_size` を比べて、切り詰めを検出します。

??? failure "`va_list` を 2 回使って、2 回目が壊れる"
    `va_copy` で複製します。

??? failure "終端の `\0` の分を、大きさに入れ忘れる"
    `std::string` に書くなら、`size() + 1` を渡します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`vsprintf`](vsprintf.md) | 大きさを指定できない危険な版 |
| [`sprintf`](sprintf.md) | 可変個引数のまま受け取る |
| `std::format` | C++20 の型安全な組み立て |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 大きさを指定して `va_list` から書く
    - [x] 戻り値は書けたはずの長さ
    - [x] 長さを調べて 2 段階で書ける

## 関連ページ

- [cpprefjp: std::vsnprintf](https://cpprefjp.github.io/reference/cstdio/vsnprintf.html)
- [cppreference: std::vsnprintf](https://en.cppreference.com/w/cpp/io/c/vsnprintf)
