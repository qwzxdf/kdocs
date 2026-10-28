---
title: std::fscanf
summary: "ファイルから、書式を指定して読み込む。"
order: 900
tags:
  - 入出力・文字列
---

# std::fscanf

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

テキスト形式のデータ ファイルから、数値や単語を、書式に沿って順に読み取りたい。ファイルに対する `sscanf` が、`std::fscanf` です。

!!! tip "ポイント"
    - `fscanf(ファイル, 書式, &変数...)`。戻り値は、読み取れた項目の数
    - 終わりに達して 1 つも読めなかったときは `EOF`
    - `%s` には幅を付ける。`%d` などには `&` を付けたアドレスを渡す
    - 書式に合わない文字が残ると、次の呼び出しも失敗し続ける

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::fscanf {#fscanf}

```cpp
int fscanf(std::FILE* stream, const char* format, ...);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | `FILE*` | 読み取るファイル |
| `format` | `const char*` | 書式文字列 |
| `...` | ポインター | 取り出した値を入れる変数のアドレス |

読み取る元がファイルであること以外は、[`sscanf`](sscanf.md) と同じです。空白は読み飛ばされるので、スペース区切りや改行区切りの数値の列を、続けて読むのに向いています。

戻り値は、読み取れた項目の数です。ループで `while (fscanf(f, "%d", &v) == 1)` と書くと、数値が読める限り続けて、書式に合わない文字か、ファイルの終わりで止まります。止まったあとで、`feof` と `ferror` を調べると、終わりなのか、不正な文字なのかが分かります。

行ごとに形式が決まっているデータは、`fgets` で 1 行読んでから `sscanf` で解釈するほうが、壊れた行に引きずられません。

## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  std::FILE* out = std::fopen("nums.txt", "w");
  std::fputs("10 20 30\n40 50\n", out);
  std::fclose(out);

  std::FILE* f = std::fopen("nums.txt", "r");
  int sum = 0, v = 0, count = 0;
  while (std::fscanf(f, "%d", &v) == 1) {   // 数値が読める限り続ける
    sum += v;
    ++count;
  }
  std::println("{} 個の合計: {}", count, sum);
  std::println("終わりまで読んだ: {}", std::feof(f) != 0);
  std::fclose(f);
}
```

```text title="実行結果"
5 個の合計: 150
終わりまで読んだ: true
```

## ゲームでの使いどころ

数値の列を並べただけの、簡単なデータ ファイル（座標のリスト、スコア表）を読むときに使います。形式が少しでも複雑になるなら、1 行ずつ `fgets` で読み、自分で分割するほうが、壊れたデータに強くなります。

JSON のような構造のあるデータには、専用のライブラリを使います。

## よくあるミス

??? failure "書式に合わない文字で止まって、無限ループになる"
    合わない文字は読まれずに残るので、同じ呼び出しが失敗し続けます。戻り値を見てループを抜けます。

??? failure "`%s` に幅を付けず、溢れる"
    幅を付けます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`sscanf`](sscanf.md) | 文字列から取り出す |
| [`fgets`](fgets.md) | 1 行を読む |
| `std::ifstream` の `>>` | C++ のストリームでの同等の読み取り |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ファイルから書式で読む
    - [x] 戻り値は読み取れた数
    - [x] 壊れたデータには行単位が強い

## 関連ページ

- [cpprefjp: std::fscanf](https://cpprefjp.github.io/reference/cstdio/fscanf.html)
- [cppreference: std::fscanf](https://en.cppreference.com/w/cpp/io/c/fscanf)
