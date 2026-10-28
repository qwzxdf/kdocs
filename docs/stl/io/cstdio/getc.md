---
title: std::getc
summary: "ファイルから 1 文字を読む（`fgetc` と同じ）。"
order: 900
tags:
  - 入出力・文字列
---

# std::getc

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

`fgetc` と同じように、ファイルから 1 文字を読みます。違いは、C の規格が「`getc` はマクロとして実装してもよい」と許している点です。昔は、関数呼び出しの手間を省くために、マクロ版が速いことがありました。

!!! tip "ポイント"
    - `getc(f)` は `fgetc(f)` と同じ結果を返す。戻り値は `int`
    - マクロとして実装されうるので、引数を 2 回評価されても困らないようにする
    - 現在のコンパイラでは、`fgetc` との速さの差はほとんどない
    - 迷ったら `fgetc` を使う

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::getc {#getc}

```cpp
int getc(std::FILE* stream);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | `FILE*` | 読み込むファイル |

動作は [`fgetc`](fgetc.md) と同じです。次の 1 文字を `unsigned char` として読み、`int` で返し、終わりかエラーなら `EOF` を返します。

規格上、`getc` はマクロでもよいことになっています。マクロの場合、引数の式が複数回評価されることがあります。`getc(*files++)` のように、副作用のある式を渡すと、位置が二重に進むかもしれません。副作用のない式（変数名）を渡します。

C++ の標準ライブラリ（`<cstdio>`）では、`std::getc` は関数として使えます。現代のコンパイラは、`fgetc` と同じ速さで動くので、違いを気にする必要はありません。

## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  std::FILE* out = std::fopen("ab.txt", "w");
  std::fputs("AB", out);
  std::fclose(out);

  std::FILE* f = std::fopen("ab.txt", "r");
  int a = std::getc(f);
  int b = std::getc(f);
  int c = std::getc(f);   // もう無い
  std::println("{} {}", static_cast<char>(a), static_cast<char>(b));
  std::println("3 回目は EOF: {}", c == EOF);
  std::fclose(f);
}
```

```text title="実行結果"
A B
3 回目は EOF: true
```

## ゲームでの使いどころ

`fgetc` と同じ場面で使えます。既存の C のコードを読むと `getc` がよく出てきますが、新しく書くなら、`fgetc` で足ります。

## よくあるミス

??? failure "副作用のある式を引数に渡す"
    マクロ展開で複数回評価されると、意図しない位置の文字を読みます。変数に入れてから渡します。

??? failure "戻り値を `char` で受ける"
    `fgetc` と同じ落とし穴です。`int` で受けます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fgetc`](fgetc.md) | 関数として必ず存在する版 |
| [`getchar`](getchar.md) | 標準入力専用 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `fgetc` と同じ
    - [x] マクロかもしれない
    - [x] 迷ったら `fgetc`

## 関連ページ

- [cpprefjp: std::getc](https://cpprefjp.github.io/reference/cstdio/getc.html)
- [cppreference: std::getc](https://en.cppreference.com/w/cpp/io/c/getc)
