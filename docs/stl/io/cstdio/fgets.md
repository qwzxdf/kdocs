---
title: std::fgets
summary: "C 由来の 1 行読み込み。"
order: 5
group: C の入出力（<cstdio>）
tags:
  - 入出力・文字列
---

# std::fgets

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <cstdio>`
</div>

設定ファイルを 1 行ずつ読んで解釈したい。`scanf` は空白で区切ってしまうので、スペースを含む行は読みにくい。<strong>1 行を、長さの上限つきで読み込む</strong>のが `std::fgets` です。上限があるので、バッファーを溢れさせる危険がありません。

!!! tip "ポイント"
    - `fgets(buf, 大きさ, ファイル)` で、改行までを `buf` に入れる。改行文字も含まれる
    - 戻り値は `buf`。ファイルの終わりかエラーなら `nullptr`
    - 1 行が `大きさ - 1` より長いと、途中で切れる。続きは次の呼び出しで読める
    - 末尾の `\n` を取り除きたいなら、`strcspn` などで自分で消す

!!! info "このページを読む前に"
    - [STL](../../index.md)（STL 全体の地図（どこに何があるか））

## 関数の詳しい説明

### std::fgets {#fgets}

```cpp
char* fgets(char* str, int count, std::FILE* stream);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | `char*` | 読み込んだ行を入れるバッファー |
| `count` | `int` | バッファーの大きさ（終端の `\0` を含む） |
| `stream` | `FILE*` | 読み込むファイル |

最大で `count - 1` 文字を読み、末尾に `\0` を付けます。改行に達したら、<strong>改行文字も含めて</strong>読み込んで止まります。そのため、行末の `\n` が文字列に残ります。比較するときは、これを取り除いてからにします。

1 行が長すぎてバッファーに入りきらないときは、入る分だけを返し、残りは次の `fgets` で読めます。行の最後に `\n` が無いことで、「途中で切れた」と見分けられます。

戻り値の `nullptr` は、ファイルの終わりで 1 文字も読めなかった場合と、エラーの場合です。ループの条件に `while (fgets(...))` と書く形が定番です。`gets` という似た関数は、大きさの上限が無く危険なため、C++14 で削除されました。

## 実際に動かしてみる

```cpp
#include <cstdio>
#include <cstring>
#include <print>

int main() {
  std::FILE* out = std::fopen("config.txt", "w");
  std::fputs("name=hero\nhp=100\n", out);
  std::fclose(out);

  std::FILE* in = std::fopen("config.txt", "r");
  char line[64];
  while (std::fgets(line, sizeof(line), in)) {
    line[std::strcspn(line, "\r\n")] = '\0';   // 末尾の改行を取り除く
    std::println("[{}]", line);
  }
  std::fclose(in);
}
```

```text title="実行結果"
[name=hero]
[hp=100]
```

## ゲームでの使いどころ

設定ファイルや、簡単なテキスト形式のデータを 1 行ずつ読んで、`key=value` に分解する処理に使います。バッファーの大きさが決まっているので、異常に長い行が入っていても、メモリを壊しません。

C++ では、`std::getline` が `std::string` に読めて、長さの制限もないので、通常はそちらが楽です。`fgets` は、`FILE*` を扱う C のライブラリとつなぐ部分や、一時的に確保するメモリを抑えたい場面で使います。

## よくあるミス

??? failure "行末の `\n` を取り除かずに比較して、一致しない"
    `fgets` は改行を含めて返します。比較の前に取り除きます。

??? failure "`sizeof(buf)` ではなく、ポインターに `sizeof` を使う"
    関数に渡した後の `char*` に `sizeof` を使うと、ポインターの大きさ（8）になります。配列の大きさを別に渡します。

??? failure "1 行が長いとき、切れた行を 1 行と思い込む"
    バッファーに入りきらない行は、複数回に分けて返ります。末尾に `\n` があるかで見分けます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fputs`](fputs.md) | 文字列を書き出す |
| [`fscanf`](fscanf.md) | 書式を指定して読む |
| `std::getline` | C++ のストリームで 1 行読む。長さの制限がない |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 1 行を上限つきで読む
    - [x] 改行文字も含まれる
    - [x] 終わりかエラーで `nullptr`

## 関連ページ

- [cpprefjp: std::fgets](https://cpprefjp.github.io/reference/cstdio/fgets.html)
- [cppreference: std::fgets](https://en.cppreference.com/w/cpp/io/c/fgets)
