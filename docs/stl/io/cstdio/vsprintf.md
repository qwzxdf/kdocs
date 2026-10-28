---
title: std::vsprintf
summary: "可変引数のリスト（va_list）を使って、文字配列に書き込む。"
order: 900
tags:
  - 入出力・文字列
---

# std::vsprintf

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdarg>`
</div>

自作の関数で、書式つきの文字列を作って返したい。`sprintf` の可変個引数版が `std::vsprintf` ですが、`sprintf` と同じく、<strong>書き込み先の大きさを確かめない</strong>ため、バッファーを溢れさせる危険があります。

!!! tip "ポイント"
    - `vsprintf(バッファー, 書式, va_list)`。大きさを指定できない
    - 溢れると、メモリを破壊する。新しいコードでは使わない
    - 代わりに `vsnprintf` を使う
    - 戻り値は、書いた文字数（終端を除く）

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::vsprintf {#vsprintf}

```cpp
int vsprintf(char* buffer, const char* format, std::va_list vlist);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `buffer` | `char*` | 結果を入れる配列 |
| `format` | `const char*` | 書式文字列 |
| `vlist` | `va_list` | 書式に対応する値の並び |

[`sprintf`](sprintf.md) の可変個引数を `va_list` にした版で、同じ危険があります。出力の長さは、書式と値によって実行時に決まるので、固定の大きさの配列では、足りなくなる可能性があります。

[`vsnprintf`](vsnprintf.md) なら、バッファーの大きさを渡せて、溢れが起きません。さらに、戻り値が「書けたはずの長さ」なので、足りなかったときに、必要な大きさが分かります。

MSVC は警告 C4996 を出します。警告を無効にするのではなく、`vsnprintf` に置き換えます。

## 実際に動かしてみる

```cpp
#include <cstdarg>
#include <cstdio>
#include <print>

void Format(char* out, std::size_t size, const char* fmt, ...) {
  std::va_list args;
  va_start(args, fmt);
  std::vsnprintf(out, size, fmt, args);   // 安全な版を使う
  va_end(args);
}

int main() {
  char buf[32];
  Format(buf, sizeof(buf), "Player_%02d.png", 7);
  std::println("{}", buf);
}
```

```text title="実行結果"
Player_07.png
```

## ゲームでの使いどころ

新しいコードでは使いません。古い C のコードを移植するときに出てきたら、`vsnprintf` に置き換えます。

## よくあるミス

??? failure "バッファーが足りず、メモリを壊す"
    `vsnprintf` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`vsnprintf`](vsnprintf.md) | 大きさを指定する安全な版 |
| [`sprintf`](sprintf.md) | 可変個引数のまま受け取る |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `va_list` を受け取る `sprintf`
    - [x] 大きさを指定できず危険
    - [x] `vsnprintf` を使う

## 関連ページ

- [cpprefjp: std::vsprintf](https://cpprefjp.github.io/reference/cstdio/vsprintf.html)
- [cppreference: std::vsprintf](https://en.cppreference.com/w/cpp/io/c/vsprintf)
