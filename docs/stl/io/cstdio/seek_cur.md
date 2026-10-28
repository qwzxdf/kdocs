---
title: SEEK_CUR
summary: "`fseek` の基準：現在位置。"
order: 900
tags:
  - 入出力・文字列
---

# SEEK_CUR

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

`fseek` の基準のうち、<strong>今の位置</strong>から数えるのが `SEEK_CUR` です。「今の場所から 4 バイト飛ばしたい」「1 バイト戻りたい」といった、相対的な移動に使います。

!!! tip "ポイント"
    - `fseek(f, n, SEEK_CUR)` で、今の位置から `n` バイト動く。負の値で戻る
    - `fseek(f, 0, SEEK_CUR)` は、位置を変えずに、読み書きの切り替えをするときに使う
    - テキスト モードでは、`offset` は 0 のときだけ使える
    - 値そのものは環境定義。名前で使う

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### SEEK_CUR {#SEEK_CUR}

```cpp
#define SEEK_CUR /* 整数定数 */
```

位置の基準を「今の位置」にします。`offset` が正なら先へ、負なら手前へ動きます。

構造のあるバイナリ ファイルを順に読むとき、不要な部分を読み飛ばす用途で使います。たとえば、サイズ 16 バイトのヘッダーの後ろに、使わない 8 バイトのパディングがあるなら、`fseek(f, 8, SEEK_CUR)` で飛ばします。

読み書き兼用で開いたファイルで、書き込みから読み込みに切り替える間には、`fseek` を挟む決まりがあります。位置を変えたくないときは、`fseek(f, 0, SEEK_CUR)` が、その役割を果たします。

## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  std::FILE* out = std::fopen("abc.txt", "w");
  std::fputs("ABCDEF", out);
  std::fclose(out);

  std::FILE* f = std::fopen("abc.txt", "rb");
  std::fgetc(f);                    // A を読む
  std::fseek(f, 2, SEEK_CUR);       // B, C を飛ばす
  std::println("{}", static_cast<char>(std::fgetc(f)));   // D
  std::fseek(f, -2, SEEK_CUR);      // 2 つ戻る（C へ）
  std::println("{}", static_cast<char>(std::fgetc(f)));   // C
  std::fclose(f);
}
```

```text title="実行結果"
D
C
```

## ゲームでの使いどころ

バイナリ形式の読み込みで、不要な領域を読み飛ばすときに使います。読んだ量に関係なく、「ここから N バイト」と相対的に指定できるので、レコードの長さが変わる形式の解析で重宝します。

## よくあるミス

??? failure "テキスト モードで 0 以外の `offset` を使う"
    テキスト モードでは、`\r\n` の変換のため、バイト数の計算が合いません。バイナリ モードで使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`SEEK_SET`](seek_set.md) | 先頭を基準にする |
| [`SEEK_END`](seek_end.md) | 末尾を基準にする |
| [`fseek`](fseek.md) | これらを受け取る関数 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 今の位置を基準にする
    - [x] 負の値で戻れる
    - [x] テキスト モードでは 0 だけ

## 関連ページ

- [cpprefjp: SEEK_CUR](https://cpprefjp.github.io/reference/cstdio/seek_cur.html)
- [cppreference: SEEK_CUR](https://en.cppreference.com/w/cpp/io/c/SEEK_CUR)
