---
title: std::fopen
summary: "C 由来のファイルを開く関数。"
order: 2
group: C の入出力（<cstdio>）
tags:
  - 入出力・文字列
---

# std::fopen

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <cstdio>`
</div>

セーブ データを書き出したい。設定ファイルを読み込みたい。C++ では `std::ofstream` や `std::ifstream` を使うのがふつうですが、C のライブラリ（zlib、SQLite、各種ミドルウェア）は、`FILE*` を受け取る関数で動いています。それらとつなぐとき、最初に出会うのが `std::fopen` です。

<strong>ファイル名とモードを渡すと、ファイルを開いて `FILE*` を返す</strong>関数です。使い終わったら `fclose` で閉じます。

!!! tip "ポイント"
    - 戻り値は `FILE*`。開けなかったときは `nullptr`。使う前に必ず確かめる
    - モードは `"r"`（読む）、`"w"`（書く。中身を消す）、`"a"`（末尾に追記）が基本
    - バイナリを扱うなら `"rb"`、`"wb"`。Windows のテキスト モードは、改行を変換するため
    - 開いたら、必ず `fclose` する。C++ なら `unique_ptr` と組み合わせて自動化できる

!!! info "このページを読む前に"
    - [STL](../../index.md)（STL 全体の地図（どこに何があるか））

## 関数の詳しい説明

### std::fopen {#fopen}

```cpp
std::FILE* fopen(const char* filename, const char* mode);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `filename` | `const char*` | 開くファイルのパス |
| `mode` | `const char*` | 開き方を表す文字列 |

モードの意味は、次のとおりです。

`"r"` は読み込みです。ファイルが存在しないと失敗します。`"w"` は書き込みで、ファイルがなければ作り、あれば<strong>中身を空にして</strong>から書き始めます。うっかり使うと、既存のセーブ データが消えます。`"a"` は追記で、ファイルの末尾から書き足します。

後ろに `+` を付けると、読み書きの両方ができます（`"r+"`、`"w+"`、`"a+"`）。`b` を付けるとバイナリ モードです。`"rb"` のように書きます。

`b` が要るのは Windows です。テキスト モードでは、書くときに `\n` が `\r\n` に、読むときに `\r\n` が `\n` に変換され、バイナリ データが壊れることがあります。セーブ データ、画像、圧縮ファイルなどには、必ず `b` を付けます。

戻り値の `nullptr` は、ファイルがない、権限がない、ディスクが一杯、パスが不正、などを表します。原因は `errno` や `perror` で調べます。確かめずに使うと、`nullptr` を `fread` などに渡して落ちます。

MSVC は、`fopen` を安全でないとして警告（C4996）を出します。`fopen_s` を使うか、警告を無効にするか、`std::ofstream` を使います。

## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  // 書く。ファイルがなければ作り、あれば中身を消して書き始める
  std::FILE* out = std::fopen("save.txt", "w");
  if (!out) {
    std::println("開けなかった");
    return 1;
  }
  std::fputs("HP=100\n", out);
  std::fclose(out);

  // 読む
  std::FILE* in = std::fopen("save.txt", "r");
  char line[64];
  std::fgets(line, sizeof(line), in);
  std::println("読んだ: {}", line);
  std::fclose(in);

  // 存在しないファイルを読むと nullptr
  std::FILE* none = std::fopen("missing.txt", "r");
  std::println("存在しない: {}", none == nullptr);
}
```

```text title="実行結果"
読んだ: HP=100

存在しない: true
```

## ゲームでの使いどころ

C のライブラリにファイルを渡す場面で使います。zlib の `gzdopen`、`stb_image` の `stbi_load_from_file`、SQLite などは、`FILE*` を受け取ります。自分のコードは `std::ofstream` で書き、C のライブラリとつなぐ部分だけ `fopen` を使う、と使い分けます。

`FILE*` を例外安全に扱うには、`std::unique_ptr<std::FILE, decltype(&std::fclose)> f(std::fopen(path, "rb"), &std::fclose);` と書くと、スコープを抜けるときに自動で閉じます。

## よくあるミス

??? failure "`nullptr` を確かめずに使って落ちる"
    ファイルがないだけで `nullptr` が返ります。`if (!f)` で必ず確かめます。

??? failure "`"w"` で既存のファイルを消してしまう"
    `"w"` は開いた時点で中身が空になります。追記したいなら `"a"`、上書きしたくないなら `"wx"`（C11。すでにあれば失敗する）を使います。

??? failure "バイナリのデータをテキスト モードで読み書きして壊れる"
    Windows では、`\r\n` の変換が入ります。バイナリは `"rb"`、`"wb"` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fclose`](fclose.md) | ファイルを閉じる |
| [`freopen`](freopen.md) | 開き直す |
| `std::ofstream` / `std::ifstream` | C++ のストリーム。通常はこちらを使う |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ファイルを開いて `FILE*` を返す
    - [x] `nullptr` を必ず確かめる
    - [x] バイナリは `"rb"` / `"wb"`

## 関連ページ

- [cpprefjp: std::fopen](https://cpprefjp.github.io/reference/cstdio/fopen.html)
- [cppreference: std::fopen](https://en.cppreference.com/w/cpp/io/c/fopen)
