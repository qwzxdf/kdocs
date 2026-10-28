---
title: std::printf
summary: "書式に従って画面に出す（C 由来・型の安全がない）。"
order: 1
group: C の入出力（<cstdio>）
tags:
  - 入出力・文字列
---

# std::printf

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-11">C++98〜</span>
`#include <cstdio>`
</div>

C から来たコードや、C のライブラリを使うと、`printf` に出会います。`std::printf` は、書式に従って画面に出す C 由来の関数で、`%d`（整数）、`%f`（小数）、`%s`（文字列）などの指定で出します。書式と引数の型が合わなくても、コンパイルが通って、未定義動作になります。新しいコードでは、`std::println` を使います。

!!! tip "ポイント"
    - `%d` に `float` を渡すと未定義動作。
    - C のライブラリや古いコードでよく見かける。
    - 新しいコードでは `std::println`。

!!! info "このページを読む前に"
    [`std::println`](../../utilities/print.md) を先に読んでください。`printf` を読む前にいまの書き方を知っておくと、違いが分かります。

## 関数の詳しい説明

### std::printf {#printf}

```cpp
int printf(const char* format, ...);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `format` | `const char*` | 書式文字列（`%d` など） |
| `...` | 可変個 | 書式に対応する値 |

- 戻り値: 出力した文字数
- 計算量: O(入出力量)

```cpp
#include <cstdio>

int main() {
  std::printf("HP %d/%d (%.1f%%)\n", 45, 120, 37.5);
}
```

```text title="実行結果"
HP 45/120 (37.5%)
```

## ゲームでの使いどころ

C のライブラリのログ出力や、古いコードの中で見かけます。読むときは、`%d` が整数、`%f` が小数、`%s` が文字列、`%x` が 16 進数、と対応を押さえておきます。

`%d` に `float` を渡すと、未定義動作です。書式文字列と引数の型を人間が一致させる責任があります。コンパイラーの警告を有効にすると、一部の間違いは見つかります。

Windows のデバッグ出力（`OutputDebugString`）に書式付きの文字列を出したいときも、`snprintf` で作った文字列を渡す、という形で現れます。新しいコードでは、`std::format` で文字列を作ります。

## よくあるミス

??? failure "書式と型が合わない"
    `%d` に `size_t` を渡すなど、未定義動作になります。`println` なら型が安全です。

??? failure "書式と引数の型が合わない"
    `%d` に `float`、`%s` に `int` を渡すと、未定義動作です。コンパイラーの警告で見つかることもありますが、確実ではありません。`std::println` なら、型が合わなければコンパイルエラーです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::println`](../../utilities/print.md) | 型安全な代わり |
| [`snprintf`](../../memory/cstring/snprintf.md) | バッファへの書式出力 |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] C 由来の書式つき出力
    - [x] 型の安全がない
    - [x] 新しいコードは println

## 関連ページ

- [cpprefjp: std::printf](https://cpprefjp.github.io/reference/cstdio/printf.html)
- [cppreference: std::printf](https://en.cppreference.com/w/cpp/io/c/printf)
