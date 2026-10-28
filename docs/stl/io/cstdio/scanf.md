---
title: std::scanf
summary: "標準入力から、書式を指定して読み込む。"
order: 900
tags:
  - 入出力・文字列
---

# std::scanf

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

コンソールで、プレイヤーの名前や数値を入力してもらいたい。標準入力から、書式に沿って値を読み取るのが `std::scanf` です。ゲームの本編より、ツールや練習用のプログラムで使う場面が多い関数です。

!!! tip "ポイント"
    - `scanf(書式, &変数...)`。戻り値は、読み取れた項目の数
    - 値を入れる変数には、アドレス（`&x`）を渡す。忘れると、クラッシュする
    - `%s` は幅の指定がないと、バッファーを溢れさせる
    - 入力が書式に合わなかったとき、残った文字が入力に残る。次の読み込みに影響する

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::scanf {#scanf}

```cpp
int scanf(const char* format, ...);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `format` | `const char*` | 書式文字列 |
| `...` | ポインター | 取り出した値を入れる変数のアドレス |

動作は [`sscanf`](sscanf.md) と同じで、読み取る元が標準入力です。戻り値は、読み取れた項目の数で、入力が終わったら `EOF` です。

`scanf` の扱いにくい点は、<strong>書式に合わなかった文字が、入力に残る</strong>ことです。たとえば、`%d` で数値を読もうとして、`abc` と入力されると、0 が返り、`abc` はそのまま残ります。ループの中で同じ `scanf` を繰り返すと、同じ `abc` を何度も読もうとして、無限ループになります。入力を一行ずつ `fgets` で読み、`sscanf` で解釈するほうが、失敗の扱いが楽です。

`%s` の幅の指定や、`double` に `%lf` を使う決まりは、`sscanf` と同じです。MSVC は `scanf` を安全でないと警告し、`scanf_s` を勧めますが、標準ではないので、移植性を考えるなら、`fgets` と `sscanf` の組み合わせにします。

## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  int hp = -1;
  // 標準入力が空のとき、読み取りは失敗して EOF が返る
  int n = std::scanf("%d", &hp);
  std::println("読み取り結果: {}", n == EOF ? "EOF" : "読めた");
  std::println("hp は変わらない: {}", hp == -1);
}
```

```text title="実行結果"
読み取り結果: EOF
hp は変わらない: true
```

## ゲームでの使いどころ

コンソールの簡単なツールや、アルゴリズムの練習で使います。ゲームの製品では、入力はウィンドウ メッセージやゲームパッドから受けるので、`scanf` を使う場面はほとんどありません。

コンソールで入力を受けるなら、`fgets` で 1 行読んでから、`sscanf` や `std::from_chars` で解釈する形が、失敗に強い書き方です。

## よくあるミス

??? failure "書式に合わない入力で、無限ループになる"
    合わなかった文字が残ります。`fgets` で行ごとに読んで、解釈に失敗したら、その行を捨てます。

??? failure "変数のアドレスを渡し忘れて、クラッシュする"
    `scanf("%d", x)` ではなく、`&x` です。

??? failure "`%s` に幅を付けず、溢れる"
    `%31s` のように幅を付けます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`sscanf`](sscanf.md) | 文字列から取り出す |
| [`fscanf`](fscanf.md) | ファイルから取り出す |
| [`fgets`](fgets.md) | 1 行を読む。解釈は別にする |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 標準入力から書式で読む
    - [x] 戻り値は読み取れた数
    - [x] 行ごとに `fgets` で読む方が安全

## 関連ページ

- [cpprefjp: std::scanf](https://cpprefjp.github.io/reference/cstdio/scanf.html)
- [cppreference: std::scanf](https://en.cppreference.com/w/cpp/io/c/scanf)
