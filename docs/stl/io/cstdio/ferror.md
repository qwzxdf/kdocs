---
title: std::ferror
summary: "ファイルの読み書きでエラーが起きたかを調べる。"
order: 900
tags:
  - 入出力・文字列
---

# std::ferror

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

ファイルから読んだデータが、途中で止まっている。読み込み関数が `nullptr` や 0 を返したが、それが、ファイルの終わりに達したからなのか、ディスクの故障のようなエラーなのか、見分けられない。

`std::ferror` は、<strong>そのファイルで、読み書きのエラーが起きたか</strong>を返します。終わりに達しただけなら、真にはなりません。

!!! tip "ポイント"
    - エラーが起きていれば 0 以外、そうでなければ 0
    - 一度起きたエラーの印は、`clearerr` か `rewind` で消すまで残る
    - 読み込みが止まった後に、`feof` と組み合わせて、終わりかエラーかを見分ける
    - 詳しい原因は `errno` と `perror` で調べる

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::ferror {#ferror}

```cpp
int ferror(std::FILE* stream);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | `FILE*` | 調べるファイル |

読み書きで失敗したとき、`FILE` の内部にエラーの印が立ち、`ferror` が 0 以外を返します。印は、`clearerr` や `rewind` を呼ぶまで残り続けます。

読み込みが期待より早く止まったときは、2 つの可能性があります。終わりに達した場合（`feof` が真）と、エラーが起きた場合（`ferror` が真）です。2 つは別の印なので、同時に真になることもありません。ループの後に、次のように書き分けます。

```cpp
if (std::ferror(f)) { /* 読み込みの失敗。ファイルが壊れている可能性 */ }
else { /* 正常に最後まで読んだ */ }
```

ファイルが開けなかったとき（`fopen` が `nullptr`）は、`FILE*` がないので `ferror` は使えません。`fopen` の失敗は、`errno` で調べます。

## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  // 読み取り専用で開いたファイルに書こうとして、エラーを起こす
  std::FILE* out = std::fopen("ro.txt", "w");
  std::fputs("x", out);
  std::fclose(out);

  std::FILE* f = std::fopen("ro.txt", "r");
  std::println("最初のエラー: {}", std::ferror(f) != 0);

  int r = std::fputc('Y', f);   // 読み込み用に開いたので、書けない
  std::println("fputc の戻り値が EOF: {}", r == EOF);
  std::println("その後のエラー: {}", std::ferror(f) != 0);

  std::clearerr(f);             // 印を消す
  std::println("clearerr の後: {}", std::ferror(f) != 0);
  std::fclose(f);
}
```

```text title="実行結果"
最初のエラー: false
fputc の戻り値が EOF: true
その後のエラー: true
clearerr の後: false
```

## ゲームでの使いどころ

セーブ データの読み込みで、読み込みが途中で止まったときの原因を分けます。終わりに達しただけなら、データが足りない（ファイルが短い）という形式の問題、エラーなら、ディスクやネットワーク ドライブの問題、と案内を変えられます。

書き込みでも、`fwrite` を何回も呼んだあと、最後に `ferror` を 1 回だけ調べて、どこかで失敗したかをまとめて確かめる使い方があります。

## よくあるミス

??? failure "`ferror` が偽だから、ファイルは正しいと考える"
    ファイルの内容の正しさとは別の話です。読み書きのエラーが無かったことしか分かりません。

??? failure "エラーの印が残ったまま、続きの処理をして失敗が続く"
    印は自動では消えません。`clearerr` で消してから、やり直します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`feof`](feof.md) | ファイルの終わりに達したか |
| [`clearerr`](clearerr.md) | 印を消す |
| [`perror`](perror.md) | `errno` の意味を表示する |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 読み書きのエラーが起きたか
    - [x] 終わりに達しただけでは真にならない
    - [x] `clearerr` で消すまで残る

## 関連ページ

- [cpprefjp: std::ferror](https://cpprefjp.github.io/reference/cstdio/ferror.html)
- [cppreference: std::ferror](https://en.cppreference.com/w/cpp/io/c/ferror)
