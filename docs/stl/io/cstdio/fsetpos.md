---
title: std::fsetpos
summary: "`fgetpos` で保存した位置に、読み書き位置を戻す。"
order: 900
tags:
  - 入出力・文字列
---

# std::fsetpos

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

`fgetpos` で保存しておいた位置に、ファイルの読み書きの位置を戻します。数値として扱えない `fpos_t` を、そのまま受け取って、同じ状態から再開できる関数が `std::fsetpos` です。

!!! tip "ポイント"
    - `fsetpos(ファイル, &pos)`。`fgetpos` で得た `pos` を渡す
    - 戻り値は、成功なら 0、失敗なら 0 以外
    - 終わりとエラーの印も消える
    - 別のファイルで得た `pos` を渡してはいけない

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::fsetpos {#fsetpos}

```cpp
int fsetpos(std::FILE* stream, const std::fpos_t* pos);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | `FILE*` | 位置を戻すファイル |
| `pos` | `const fpos_t*` | `fgetpos` で保存した位置 |

保存した時点の位置と、ファイルの解析状態に戻ります。ファイルの終わりの印は消え、`ungetc` で戻した文字も捨てられます。

位置が `long` に収まるなら、`fseek(f, pos, SEEK_SET)` でも戻れます。`fsetpos` が必要なのは、`long` に収まらない巨大なファイルや、`fpos_t` でしか表せない状態を持つ、特殊な場合です。

## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  std::FILE* out = std::fopen("seq.txt", "w");
  std::fputs("ABCDE", out);
  std::fclose(out);

  std::FILE* f = std::fopen("seq.txt", "r");
  std::fpos_t start;
  std::fgetpos(f, &start);              // 先頭を記録する

  while (std::fgetc(f) != EOF) {}       // 最後まで読む
  std::println("読み終えた: {}", std::feof(f) != 0);

  int r = std::fsetpos(f, &start);      // 先頭に戻る。印も消える
  std::println("戻れた: {}  終わりの印: {}", r == 0, std::feof(f) != 0);
  std::println("先頭の文字: {}", static_cast<char>(std::fgetc(f)));
  std::fclose(f);
}
```

```text title="実行結果"
読み終えた: true
戻れた: true  終わりの印: false
先頭の文字: A
```

## ゲームでの使いどころ

`fgetpos` と組み合わせて、バックトラックに使います。`rewind` との違いは、先頭以外の、記録した任意の位置へ戻れる点です。

## よくあるミス

??? failure "別のファイルの `fpos_t` を渡す"
    取得したファイルのものだけが有効です。

??? failure "戻り値を確かめない"
    失敗すると、位置は変わりません。続きの処理が、意図と違う場所で動きます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fgetpos`](fgetpos.md) | 位置を保存する |
| [`fseek`](fseek.md) | 数値で位置を動かす |
| [`rewind`](rewind.md) | 先頭へ戻る |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 保存した位置に戻る
    - [x] 終わりの印も消える
    - [x] 戻り値で成否を確かめる

## 関連ページ

- [cpprefjp: std::fsetpos](https://cpprefjp.github.io/reference/cstdio/fsetpos.html)
- [cppreference: std::fsetpos](https://en.cppreference.com/w/cpp/io/c/fsetpos)
