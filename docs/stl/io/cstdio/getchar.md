---
title: std::getchar
summary: "標準入力から 1 文字を読む。"
order: 900
tags:
  - 入出力・文字列
---

# std::getchar

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

コンソール ゲームや、ツールの対話で、キー入力を 1 文字ずつ受け取りたい。`getchar` は、<strong>標準入力から 1 文字読む</strong>関数です。`fgetc(stdin)` と同じ意味です。

!!! tip "ポイント"
    - `getchar()` は `fgetc(stdin)` と同じ。戻り値は `int`
    - 端末では、Enter を押すまで入力が確定しない（行バッファリング）
    - リダイレクトした入力（`< file.txt`）や、パイプからも読める
    - ファイルの終わり（Ctrl+Z / Ctrl+D）で `EOF`

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::getchar {#getchar}

```cpp
int getchar();
```

標準入力から次の 1 文字を読んで、`int` で返します。終わりかエラーで `EOF` を返します。引数はありません。

端末から読むとき、多くの環境では<strong>行単位</strong>で入力が渡されます。1 文字打っただけでは `getchar` は戻らず、Enter を押して初めて、その行の文字が順に読めます。「キーを押した瞬間に反応する」ゲームの入力には、`getchar` は向きません。Windows なら `_getch`（`<conio.h>`）などの、コンソール専用の関数を使います。

入力を Enter まで読み捨てたいときの定番は、`while ((c = getchar()) != '\n' && c != EOF) {}` です。`fflush(stdin)` は標準では未定義動作なので、使いません。

## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  // 標準入力から 1 文字読む。入力がなければ EOF
  int c = std::getchar();
  if (c == EOF) {
    std::println("入力なし");
  } else {
    std::println("読んだ文字: {}", static_cast<char>(c));
  }
}
```

```text title="実行結果"
入力なし
```

## ゲームでの使いどころ

入力を待つだけの「Press Enter to continue」のような処理に使います。`getchar()` を 1 回呼べば、Enter が押されるまで待ちます。

ツールの対話や、パイプで流し込まれたテキストを 1 文字ずつ処理するフィルターなどでも使います。ゲーム本体のキー入力には、別の仕組み（ウィンドウ メッセージ、Raw Input、ゲームパッド API）を使います。

## よくあるミス

??? failure "リアルタイムのキー入力に使おうとして、Enter まで反応しない"
    行バッファリングのためです。ゲームの入力は、ウィンドウ メッセージや Raw Input で受けます。

??? failure "戻り値を `char` で受ける"
    `EOF` と区別できなくなります。`int` で受けます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fgetc`](fgetc.md) | 任意のファイルから 1 文字 |
| [`scanf`](scanf.md) | 書式つきで読む |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 標準入力から 1 文字
    - [x] `fgetc(stdin)` と同じ
    - [x] 端末では Enter まで確定しない

## 関連ページ

- [cpprefjp: std::getchar](https://cpprefjp.github.io/reference/cstdio/getchar.html)
- [cppreference: std::getchar](https://en.cppreference.com/w/cpp/io/c/getchar)
