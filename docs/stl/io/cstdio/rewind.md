---
title: std::rewind
summary: "ファイルの読み書き位置を、先頭に戻す。"
order: 900
tags:
  - 入出力・文字列
---

# std::rewind

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

ファイルを最後まで読んだあと、もう一度、先頭から読み直したい。1 回目で行数を数え、2 回目で中身を読む、という 2 パスの処理では、いったん閉じて開き直さずに、先頭へ戻れると便利です。

`std::rewind` は、<strong>読み書きの位置を先頭に戻し、エラーとファイルの終わりの印も消す</strong>関数です。

!!! tip "ポイント"
    - `rewind(f)` は、`fseek(f, 0, SEEK_SET)` と、`clearerr(f)` を合わせたもの
    - ファイルの終わりに達していても、`rewind` の後は、また読める
    - 戻り値はない。失敗しても分からないので、確実さが要る場面は `fseek` を使う
    - ストリーム全体で「最初に戻る」だけなら、これで十分

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::rewind {#rewind}

```cpp
void rewind(std::FILE* stream);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | `FILE*` | 先頭に戻すファイル |

`fseek(stream, 0L, SEEK_SET)` を呼び、さらに、ファイルの終わりの印とエラーの印を消します（`clearerr`）。`fseek` だけでは、終わりの印は消えますが、エラーの印は残ることがある、という違いがあります。

戻り値が `void` なので、位置を戻せたかが分かりません。失敗を確かめたいときは、`fseek` を直接呼んで戻り値を見ます。

読み書き兼用で開いたファイル（`"w+"`、`"r+"`）では、書いた直後に読むために位置を戻す、という使い方もします。このとき、書き込みと読み込みの切り替えの間には、`fseek` か `rewind`、`fflush` のどれかを挟む決まりがあり、`rewind` がその役割も果たします。

## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  std::FILE* f = std::fopen("lines.txt", "w+");   // 読み書き兼用
  std::fputs("A\nB\nC\n", f);

  std::rewind(f);                                 // 書いた後、先頭に戻って読む

  int count = 0;
  char buf[16];
  while (std::fgets(buf, sizeof(buf), f)) ++count;
  std::println("1 回目: {} 行", count);
  std::println("終わりに達した: {}", std::feof(f) != 0);

  std::rewind(f);                                 // もう一度、先頭から
  std::println("rewind 後の終わり: {}", std::feof(f) != 0);
  std::fgets(buf, sizeof(buf), f);
  std::println("先頭の行: {}", buf[0]);
  std::fclose(f);
}
```

```text title="実行結果"
1 回目: 3 行
終わりに達した: true
rewind 後の終わり: false
先頭の行: A
```

## ゲームでの使いどころ

2 パスの処理で使います。1 回目でデータの個数を数えて、配列を確保し、`rewind` で先頭に戻って、2 回目で中身を読み込みます。ファイルを閉じて開き直すより簡単です。

一時ファイルに書き込んで、すぐ読み戻す場面にも向いています。`tmpfile()` で作ったファイルは、読み書き兼用なので、書いた後に `rewind` するだけで、中身を確かめられます。

## よくあるミス

??? failure "終わりに達したまま読み続けようとして、何も読めない"
    `fgets` が `nullptr` を返した後は、`feof` が真のままです。再び読むなら、`rewind` や `clearerr` で印を消します。

??? failure "書いた直後にそのまま読んで、不定の結果になる"
    読み書き兼用のファイルでは、書き込みと読み込みの間に、`rewind`、`fseek`、`fflush` のどれかが要ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fseek`](fseek.md) | 好きな位置に動かす。戻り値で成否が分かる |
| [`clearerr`](clearerr.md) | 終わりとエラーの印だけを消す |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 先頭に戻り、印も消す
    - [x] 戻り値がないので成否は分からない
    - [x] 2 パスの処理に便利

## 関連ページ

- [cpprefjp: std::rewind](https://cpprefjp.github.io/reference/cstdio/rewind.html)
- [cppreference: std::rewind](https://en.cppreference.com/w/cpp/io/c/rewind)
