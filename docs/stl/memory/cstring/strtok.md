---
title: std::strtok
summary: "文字列を、区切り文字で分割して 1 つずつ取り出す。"
order: 900
tags:
  - メモリ
---

# std::strtok

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstring>`
</div>

「a,b,c」のような文字列を分割して順番に取り出したいとき、`strtok` が使えます。ただし元の文字列を**書き換え**（区切りを `'\0'` にする）、内部の状態を使うので、同時に複数の分割はできません。

!!! tip "ポイント"
    - 元の文字列を書き換える。
    - 2 回目以降は第 1 引数に `nullptr` を渡す。
    - 新しいコードでは `views::split` のほうが安全。

!!! info "このページを読む前に"
    [`<cstring>`](../cstring.md) の概要と [ポインタ](../../../basics/pointer.md) を先に読んでください。

## 関数の詳しい説明

### std::strtok {#strtok}

```cpp
char* strtok(char* str, const char* delim);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | char* | 最初の呼び出しでは分割する文字列。続きでは `nullptr` |
| `delim` | const char* | 区切り文字の集まり |

- 戻り値: 次のトークンのポインタ。なければ `nullptr`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cstring>
#include <print>

int main() {
  char s[] = "a,b,c";
  for (char* t = std::strtok(s, ","); t != nullptr; t = std::strtok(nullptr, ",")) {
    std::println("{}", t);
  }
}
```

```text title="実行結果"
a
b
c
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 古い C のコードの文字列の分割 |

## よくあるミス

??? failure "文字列リテラルに使う"
    リテラルは書き換えられません。`char s[] = ...` のコピーに使います。内部状態があるので、スレッドや入れ子では使えません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::views::split`](../../algorithms/views/split.md) | 新しい書き方 |
| [`std::getline`](../../io/getline.md) | 区切り文字で読む |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 文字列を区切り文字で分割して 1 つずつ取り出す
    - [x] 元の文字列を書き換える
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::strtok](https://cpprefjp.github.io/reference/cstring/strtok.html)
- [cppreference: std::strtok](https://en.cppreference.com/w/cpp/string/byte/strtok)
