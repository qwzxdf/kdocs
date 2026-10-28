---
title: std::feof
summary: "ファイルの終端に達したかを調べる。"
order: 900
tags:
  - 入出力・文字列
---

# std::feof

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

ファイルを読むループを書くとき、「ファイルの終わりまで繰り返す」と書きたくなります。`while (!feof(f))` と書くと、最後に 1 回余計に回ってしまう、という有名な落とし穴があります。`std::feof` が何を答える関数なのかを、正しく知っておくことが大事です。

<strong>「すでに、ファイルの終わりを読もうとして失敗した」</strong>かどうかを返します。「次が終わりか」を予告する関数ではありません。

!!! tip "ポイント"
    - `feof(f)` は、終わりを超えて読もうとしたあとで、初めて真になる
    - ループの条件には使わない。読み込み関数の戻り値で判定する
    - 読み込みが止まった理由を調べるために使う。終わりなのか、エラーなのかを見分ける
    - `rewind` や `clearerr` で、印を消せる

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::feof {#feof}

```cpp
int feof(std::FILE* stream);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | `FILE*` | 調べるファイル |

終わりの印は、読み込み関数が、ファイルの終わりを超えて読もうとしたときに立ちます。最後のデータをちょうど読み終えた時点では、まだ立っていません。次の読み込みで 0 バイトしか読めなかったときに、立ちます。

そのため、`while (!feof(f)) { fgets(...); 使う }` と書くと、最後の行を読んだあとも条件が真のままで、もう一度ループに入ります。この回の `fgets` は失敗するのに、バッファーには前の内容が残っているため、最後の行が 2 回処理されます。

正しい書き方は、読み込み関数の戻り値を条件にすることです。`while (fgets(buf, n, f))`、`while (fread(...) == n)` のように書きます。ループを抜けたあとで、`feof` と `ferror` を調べて、終わりなのかエラーなのかを見分けます。

## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  std::FILE* out = std::fopen("two.txt", "w");
  std::fputs("A\nB\n", out);
  std::fclose(out);

  std::FILE* f = std::fopen("two.txt", "r");
  char buf[16];

  // 正しい書き方: 読み込みの戻り値を条件にする
  int n = 0;
  while (std::fgets(buf, sizeof(buf), f)) ++n;
  std::println("読んだ行数: {}", n);
  std::println("終わりに達した: {}", std::feof(f) != 0);
  std::println("エラー: {}", std::ferror(f) != 0);
  std::fclose(f);

  // 悪い書き方: feof を先に調べると、1 回多く回る
  f = std::fopen("two.txt", "r");
  int bad = 0;
  while (!std::feof(f)) {
    std::fgets(buf, sizeof(buf), f);
    ++bad;
  }
  std::println("悪い書き方の回数: {}", bad);
  std::fclose(f);
}
```

```text title="実行結果"
読んだ行数: 2
終わりに達した: true
エラー: false
悪い書き方の回数: 3
```

## ゲームでの使いどころ

読み込みのループを抜けたあとで、理由を調べるために使います。`feof` が真なら、最後まで読み終えた正常な終了、`ferror` が真なら、読み込み中のエラーです。エラーのときは、途中までしか読めていないので、プレイヤーにファイルの破損を知らせます。

C++ の `std::ifstream` でも、`while (std::getline(in, line))` のように、読み込みの結果を条件にするのが定番で、`in.eof()` を条件にしないのは同じ理由です。

## よくあるミス

??? failure "`while (!feof(f))` で、最後の行が 2 回処理される"
    終わりの印は、読み込みが失敗してから立ちます。読み込み関数の戻り値を条件にします。

??? failure "`feof` が偽なら正常と考える"
    エラーで止まった場合も、`feof` は偽です。`ferror` も確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`ferror`](ferror.md) | 読み書きのエラーが起きたか |
| [`clearerr`](clearerr.md) | 終わりとエラーの印を消す |
| `std::ios::eof` | C++ のストリームでの同等の判定 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 終わりを超えて読んだ後で、真になる
    - [x] ループの条件に使わない
    - [x] ループの後で、理由を調べるのに使う

## 関連ページ

- [cpprefjp: std::feof](https://cpprefjp.github.io/reference/cstdio/feof.html)
- [cppreference: std::feof](https://en.cppreference.com/w/cpp/io/c/feof)
