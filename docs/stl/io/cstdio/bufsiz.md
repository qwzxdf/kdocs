---
title: BUFSIZ
summary: "標準のバッファの大きさ（バイト）。"
order: 900
tags:
  - 入出力・文字列
---

# BUFSIZ

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

標準ライブラリがファイルの入出力で使う、バッファーの大きさ。その既定の大きさを表すのが `BUFSIZ` です。自分でバッファーを用意して渡す `setbuf` では、この大きさ以上の配列が必要になります。

!!! tip "ポイント"
    - `BUFSIZ` は整数定数のマクロ。環境ごとに値が違う（MSVC は 512、glibc は 8192 など）
    - `setbuf(ファイル, 配列)` に渡す配列は、`BUFSIZ` 以上の大きさにする
    - `setvbuf` では大きさを自由に指定できるので、`BUFSIZ` に縛られない
    - 最低でも 256 以上であることが、規格で決まっている

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### BUFSIZ {#BUFSIZ}

```cpp
#define BUFSIZ /* 実装定義の整数定数式 */
```

標準ライブラリが、入出力のバッファーに使う標準の大きさです。規格が保証するのは、256 以上であることだけで、実際の値は実装しだいです。

`setbuf` は大きさを引数に取らず、`BUFSIZ` の大きさの配列を渡す決まりです。`char buf[BUFSIZ];` と宣言して渡します。

実際のバッファーの大きさとして、`BUFSIZ` が最適とは限りません。大量のデータを読み書きするなら、64 KB のような大きなバッファーを `setvbuf` で渡すと、システム呼び出しの回数が減って速くなることがあります。

「読み書きを 1 回の呼び出しで処理する単位」として使うこともできます。一時的な読み込みのバッファーに `char buf[BUFSIZ]` と書くのは、C の定番の書き方です。

## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  std::println("256 以上: {}", BUFSIZ >= 256);

  // setbuf に渡す配列は BUFSIZ 以上の大きさ
  static char buffer[BUFSIZ];
  std::FILE* f = std::fopen("buf.txt", "w");
  std::setbuf(f, buffer);
  std::fputs("hello", f);
  std::fclose(f);               // 閉じる前に buffer を破棄しない
  std::println("書けた");
}
```

```text title="実行結果"
256 以上: true
書けた
```

## ゲームでの使いどころ

`setbuf` と組み合わせるほか、ファイルを一定の単位で読み書きするときの、バッファーの大きさの目安に使います。ゲームでは、読み込みの速度が重要なら、`BUFSIZ` ではなく、数十 KB から数 MB の単位を自分で決めます。

## よくあるミス

??? failure "`BUFSIZ` が固定の値だと思って、他の場所に書き込む"
    環境によって違います。名前で使います。

??? failure "ファイルを閉じる前に、渡した配列を破棄する"
    バッファーは閉じるまで使われます。`static` にするなど、寿命を長くします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`setbuf`](setbuf.md) | この大きさのバッファーを渡す |
| [`setvbuf`](setvbuf.md) | 大きさを自由に決められる |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 既定のバッファーの大きさ
    - [x] 環境ごとに値が違う
    - [x] `setbuf` の配列は `BUFSIZ` 以上

## 関連ページ

- [cpprefjp: BUFSIZ](https://cpprefjp.github.io/reference/cstdio/bufsiz.html)
- [cppreference: BUFSIZ](https://en.cppreference.com/w/cpp/io/c/BUFSIZ)
