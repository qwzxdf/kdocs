---
title: std::fgets
summary: "C 由来の 1 行読み込み。"
order: 5
group: C の入出力（<cstdio>）
tags:
  - 入出力・文字列
---

# std::fgets

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <cstdio>`
</div>

`std::fgets` は、**ファイルから 1 行を読んで、バッファに入れる**C 由来の関数です。バッファの大きさを守って読むので、危険な `gets`（削除済み）と違って安全です。改行文字もバッファに入ります。C++ では [`std::getline`](../getline.md) が簡単です。

!!! tip "ポイント"
    - 改行文字（`\n`）も入る。
    - 読めなければ `nullptr`。
    - バッファより長い行は、途中までしか読まれない。

## 関数の詳しい説明

### std::fgets {#fgets}

```cpp
char* fgets(char* buffer, int size, FILE* stream);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `buffer` | `char*` | 読み込み先 |
| `size` | `int` | バッファの大きさ |
| `stream` | `FILE*` | 読み込み元 |

- 戻り値: バッファ（読めなければ `nullptr`）
- 計算量: O(入出力量)

```cpp
#include <cstdio>
#include <cstring>
#include <print>

int main() {
  std::FILE* f = std::tmpfile();
  std::fputs("hello\nworld\n", f);
  std::rewind(f);

  char buffer[16];
  std::fgets(buffer, sizeof(buffer), f);
  std::println("{}", std::strcmp(buffer, "hello\n") == 0);   // 改行も入っている
  std::fclose(f);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| C のAPI での 1 行読み込み | `while (std::fgets(buf, sizeof(buf), f))` |

## よくあるミス

??? failure "改行を取り除き忘れる"
    末尾に `\n` が付きます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::getline`](../getline.md) | C++ の 1 行読み込み |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 1 行を読む（C 由来）
    - [x] 改行も入る
    - [x] C++ では getline

## 関連ページ

- [cpprefjp: std::fgets](https://cpprefjp.github.io/reference/cstdio/fgets.html)
- [cppreference: std::fgets](https://en.cppreference.com/w/cpp/io/c/fgets)
