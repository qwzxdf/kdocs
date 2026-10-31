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

画面に出す名前や、ファイルのパスの長さを知りたい。C の文字列は長さを持たず、終端の `'\0'` までを数えるしかありません。`std::strlen(s)` は、先頭から `'\0'` までの文字数（終端は含まない）を返します。

!!! tip "ポイント"
    - 先頭から終端まで数えるので、計算量は文字列の長さに比例する
    - 終端を含まない。配列に収めるには `strlen + 1` 要素が要る
    - 終端のない配列に使うと、配列の外まで読む
    - ループの条件に毎回書くと遅い。先に変数へ取る

!!! info "このページを読む前に"
    [`<cstring>`](../cstring.md) の概要を先に読んでください。C の文字列は、終端が `'\0'` の `char` の配列です。

## 関数の詳しい説明

### std::strlen {#strlen}

```cpp
std::size_t strlen(const char* str);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | `const char*` | 終端が `'\0'` の文字列 |

戻り値は、終端の手前までの `char` の個数です。バイト数であって、文字数ではありません。UTF-8 の「あ」は 3 を返します。

`nullptr` や、終端のない配列を渡すと、未定義動作です。`char name[4] = {'H','e','r','o'};` のように、終端がない配列は、`strlen` が配列の外を読み続けます。

C++ の `std::string` なら `size()` が定数時間で長さを返すので、`strlen` を繰り返し呼ぶ必要がありません。

## 実際に動かしてみる

```cpp
#include <cstring>
#include <print>

int main() {
  std::println("{}", std::strlen("hello"));
  std::println("{}", std::strlen(""));
  std::println("UTF-8 の「あ」: {}", std::strlen("あ"));  // バイト数

  char buf[16] = "abc";
  std::println("配列の大きさ {} 文字列の長さ {}", sizeof(buf), std::strlen(buf));
}
```

```text title="実行結果"
5
0
UTF-8 の「あ」: 3
配列の大きさ 16 文字列の長さ 3
```

## ゲームでの使いどころ

C の API が返した `const char*` の長さを知りたいときに使います。ループの外で 1 回だけ呼び、結果を変数に取っておきます。

## よくあるミス

??? failure "sizeof と混同する"
    配列に `sizeof` を使うと、配列全体の大きさです。文字列の長さは `strlen` です。

??? failure "終端のない配列に使う"
    配列の外を読み、クラッシュや、ゴミの長さになります。

## 類似

| 名前 | 違い |
| --- | --- |
| `std::string::size()` | 定数時間。普段はこちら |
| [`strncpy`](strncpy.md) | 長さを指定してコピーする |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## 関連ページ

- [cpprefjp: strlen](https://cpprefjp.github.io/reference/cstring/strlen.html)
- [cppreference: strlen](https://en.cppreference.com/w/cpp/string/byte/strlen)
