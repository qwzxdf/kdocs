---
title: std::stdin
summary: "標準入力を表す FILE*。"
order: 900
tags:
  - 入出力・文字列
---

# std::stdin

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

キーボードから入力を受け取る関数 `scanf` や `getchar` は、どこから読んでいるのでしょう。その読み込み元が、`stdin`（標準入力）です。プログラムの開始時に、自動で開かれています。

!!! tip "ポイント"
    - `scanf(...)` は `fscanf(stdin, ...)` と、`getchar()` は `fgetc(stdin)` と同じ
    - 端末では、キー入力が行単位でバッファーされる。Enter まで確定しない
    - リダイレクト（`< input.txt`）やパイプで、ファイルや他のプログラムの出力を入力にできる
    - `fflush(stdin)` で入力を捨てるのは、標準では未定義

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### stdin {#stdin}

```cpp
extern std::FILE* stdin;   // 実際はマクロの場合もある
```

`stdin` は、`scanf`、`gets` 系、`getchar` の読み込み元です。`fgets(buf, n, stdin)` は、標準入力から 1 行を読む、定番の書き方です。

シェルで `game.exe < input.txt` とすると、`stdin` がファイルになります。自動テストで、入力をファイルから流し込む、ツール同士をパイプでつなぐ、といった使い方ができます。入力が尽きると、`fgets` などは `EOF` / `nullptr` を返します。

端末から読むときは、1 行入力されるまで待ちます。キーを押した瞬間に反応するゲームの操作には、向きません。Windows なら `_getch`、ゲーム全体では、ウィンドウ メッセージやゲームパッド API を使います。

入力の読み残しを消す目的で `fflush(stdin)` を書く例がありますが、標準では未定義動作です。読み捨てるなら、`getchar` を改行まで繰り返します。

## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  char line[64];
  // 入力が空だと nullptr が返る
  if (std::fgets(line, sizeof(line), stdin)) {
    std::print("入力: {}", line);
  } else {
    std::println("入力なし");
  }
}
```

```text title="実行結果"
入力なし
```

## ゲームでの使いどころ

コンソールの簡単なツールや、パイプでつなぐフィルターで使います。ゲーム本編の入力は、ここを使いません。

ツール同士を組み合わせる開発環境（ビルド スクリプト、アセット変換）では、`stdin` から読んで `stdout` に出す、というフィルター型のプログラムが便利です。

## よくあるミス

??? failure "リアルタイム入力に使って、Enter まで反応しない"
    行バッファリングのためです。ゲームの入力は別の仕組みで受けます。

??? failure "`fflush(stdin)` で入力を捨てる"
    標準では未定義です。`getchar` で読み捨てます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`stdout`](stdout.md) | 標準出力 |
| [`getchar`](getchar.md) | `stdin` から 1 文字 |
| `std::cin` | C++ のストリームでの標準入力 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 標準入力の `FILE*`
    - [x] `scanf` や `getchar` の読み込み元
    - [x] `fflush(stdin)` は使わない

## 関連ページ

- [cpprefjp: std::stdin](https://cpprefjp.github.io/reference/cstdio/stdin.html)
- [cppreference: std::stdin](https://en.cppreference.com/w/cpp/io/c/stdin)
