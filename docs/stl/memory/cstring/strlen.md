---
title: strlen
summary: "C 文字列（終端が \\0）の長さを調べる。"
order: 5
group: C の文字列・メモリ関数（<cstring>）
tags:
  - メモリ
---

# strlen

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <cstring>`
</div>

`strlen` は、**終端が `\0` の C 文字列の長さ（バイト数）を返す**関数です。終端の `\0` は数えません。先頭から順に探すので、長さに比例して時間がかかります（O(n)）。

!!! tip "ポイント"
    - `std::string` なら `size()` が O(1)。
    - 終端が無い文字列に使うと、範囲外を読む。
    - 何度も呼ぶなら、結果を変数に保存する。

!!! info "このページを読む前に"
    [ポインタ](../../../basics/pointer.md) が分かると読みやすいです。

## 関数の詳しい説明

### strlen {#strlen}

```cpp
std::size_t strlen(const char* str);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | `const char*` | `'\0'` で終わる文字列 |

- 戻り値: 終端の `'\0'` を**数えない**文字数（バイト数）
- 計算量: O(n)。文字列を最後まで数えるので、ループの条件の中で毎回呼ぶと遅くなります
- 終端の `'\0'` がない配列に使うと、範囲外を読み続けます（未定義動作）
- UTF-8 の日本語は 1 文字が 3 バイトなので、`strlen("あ")` は 3 です。**文字数ではなくバイト数**です

## 実際に動かしてみる

```cpp
#include <cstring>
#include <print>

int main() {
  std::println("{}", std::strlen("hello"));
}
```

```text title="実行結果"
5
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| C のライブラリが返した文字列を `std::string` にする | `std::string(s, strlen(s))` |

## よくあるミス

??? failure "ループの条件に strlen を使う"
    `for (i < strlen(s))` は、毎回 O(n) です。

## 類似

| 名前 | 違い |
| --- | --- |
| `std::string::size` | O(1) |
| [`std::char_traits::length`](../../containers/char_traits.md) | C++ の同等品 |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 終端までの長さ
    - [x] O(n)
    - [x] 終端 `\0` が必須

## 関連ページ

- [cpprefjp: strlen](https://cpprefjp.github.io/reference/cstring/strlen.html)
- [cppreference: strlen](https://en.cppreference.com/w/cpp/string/byte/strlen)
