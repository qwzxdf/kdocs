---
title: std::fread
summary: "C 由来のバイナリ読み込み。"
order: 3
group: C の入出力（<cstdio>）
tags:
  - 入出力・文字列
---

# std::fread

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <cstdio>`
</div>

セーブ データがバイナリで保存されている。画像やモデルのファイルを、そのままメモリに読み込みたい。1 文字ずつ読んでいては遅いので、<strong>まとまったバイト列を、一度にメモリへ読み込む</strong>のが `std::fread` です。

!!! tip "ポイント"
    - `fread(buf, 1 要素の大きさ, 要素数, ファイル)` の形。戻り値は、読めた要素の数
    - 戻り値が要求より少ないのは、ファイルの終わりか、エラー。`feof` と `ferror` で見分ける
    - バイナリ データには `"rb"` で開いたファイルを使う
    - 構造体をそのまま読み込めるのは、パディングや型の大きさがそろう同じ環境のときだけ

!!! info "このページを読む前に"
    - [STL](../../index.md)（STL 全体の地図（どこに何があるか））

## 関数の詳しい説明

### std::fread {#fread}

```cpp
std::size_t fread(void* buffer, std::size_t size, std::size_t count, std::FILE* stream);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `buffer` | `void*` | 読み込んだデータを入れる場所。`size * count` バイト以上の領域が必要 |
| `size` | `size_t` | 1 要素の大きさ（バイト） |
| `count` | `size_t` | 読み込む要素の数 |
| `stream` | `FILE*` | 読み込むファイル |

戻り値は、<strong>実際に読めた要素の数</strong>（バイト数ではありません）です。`size` を 1 にして `count` をバイト数にすると、戻り値がそのままバイト数になるので、扱いやすくなります。

戻り値が `count` より小さいときは、2 つの場合があります。ファイルの終わりに達した場合と、読み込みエラーが起きた場合です。`feof(stream)` が真なら終わり、`ferror(stream)` が真ならエラーです。ファイルの大きさが分からないときは、少なめの `count` で呼び、戻り値が `count` より小さくなった時点で終わり、とする使い方ができます。

`buffer` が小さいと、メモリを破壊します。`size * count` が確保した領域に収まっているかを、呼ぶ前に確かめます。

## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  // 4 バイトのデータを書き出す
  std::FILE* out = std::fopen("data.bin", "wb");
  const unsigned char src[4] = {10, 20, 30, 40};
  std::fwrite(src, 1, 4, out);
  std::fclose(out);

  // 8 バイト読もうとするが、ファイルには 4 バイトしかない
  std::FILE* in = std::fopen("data.bin", "rb");
  unsigned char buf[8] = {};
  std::size_t n = std::fread(buf, 1, 8, in);
  std::println("読めたバイト数: {}", n);
  std::println("ファイルの終わり: {}", std::feof(in) != 0);
  std::println("先頭の値: {}", buf[0]);
  std::fclose(in);
}
```

```text title="実行結果"
読めたバイト数: 4
ファイルの終わり: true
先頭の値: 10
```

## ゲームでの使いどころ

アセットや、独自形式のバイナリ ファイルを読み込むときに使います。ファイルの先頭にあるヘッダー（マジック ナンバーとバージョン）を `fread` で読み、形式が正しいと確かめてから、続きを読み進めます。

構造体を丸ごと読み込むのは手軽ですが、コンパイラや設定が変わるとパディングが変わり、読めなくなります。保存する形式は、1 フィールドずつ、大きさとバイト順を決めて書き出すほうが、長持ちします。

## よくあるミス

??? failure "戻り値を確かめずに、読めたと仮定する"
    ファイルが短いと、読み残しがあります。バッファーの残りは、初期化していなければ、ゴミのままです。戻り値を確かめます。

??? failure "テキスト モードで開いて、バイナリが壊れる"
    Windows のテキスト モードは、`\r\n` を変換し、`0x1A` を終端と見なすことがあります。`"rb"` で開きます。

??? failure "`size` と `count` の積がバッファーを超える"
    メモリを破壊します。`sizeof(buf)` で確かめて、`count` を決めます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fwrite`](fwrite.md) | 対になる、書き出す関数 |
| [`fgets`](fgets.md) | 1 行ずつ読む。テキスト向け |
| `std::ifstream::read` | C++ のストリームでの同等の関数 |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] バイト列を一度に読み込む
    - [x] 戻り値は読めた要素の数
    - [x] 短いときは `feof` と `ferror` で見分ける

## 関連ページ

- [cpprefjp: std::fread](https://cpprefjp.github.io/reference/cstdio/fread.html)
- [cppreference: std::fread](https://en.cppreference.com/w/cpp/io/c/fread)
