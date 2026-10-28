---
title: std::fwrite
summary: "C 由来のバイナリ書き込み。"
order: 4
group: C の入出力（<cstdio>）
tags:
  - 入出力・文字列
---

# std::fwrite

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <cstdio>`
</div>

セーブ データや、書き出したメッシュをバイナリで保存したい。1 バイトずつ書くと遅いので、<strong>メモリ上のまとまったデータを、一度にファイルへ書き出す</strong>のが `std::fwrite` です。

!!! tip "ポイント"
    - `fwrite(データ, 1 要素の大きさ, 要素数, ファイル)` の形。戻り値は、書けた要素の数
    - 戻り値が `count` より小さいときは、書き込みの失敗（ディスクが一杯など）
    - バイナリには `"wb"` で開く。`"w"` だと Windows で `\n` が `\r\n` に変わる
    - 書いた内容は、バッファーに残っていることがある。確実に書き出すには `fclose` か `fflush`

!!! info "このページを読む前に"
    - [STL](../../index.md)（STL 全体の地図（どこに何があるか））

## 関数の詳しい説明

### std::fwrite {#fwrite}

```cpp
std::size_t fwrite(const void* buffer, std::size_t size, std::size_t count, std::FILE* stream);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `buffer` | `const void*` | 書き出すデータの先頭 |
| `size` | `size_t` | 1 要素の大きさ（バイト） |
| `count` | `size_t` | 書き出す要素の数 |
| `stream` | `FILE*` | 書き出す先のファイル |

戻り値は、<strong>書けた要素の数</strong>です。`count` と同じなら成功です。小さいときは、ディスクが一杯、書き込み禁止、デバイスのエラーなどで、書ききれませんでした。

`fwrite` が `count` を返しても、データが実際にディスクに届いたとは限りません。C のライブラリは、いったん内部のバッファーに溜めて、まとめて書き出します。確実に届けたいときは、`fflush` を呼ぶか、`fclose` で閉じます。それでも OS のキャッシュに残る場合があり、電源が切れても残したいセーブでは、OS の機能（`FlushFileBuffers`、`fsync`）まで使います。

`void*` を受け取るので、型の安全性はありません。構造体をそのまま書くと、パディングの中のゴミまで保存され、同じデータでも毎回ファイルの内容が違うことがあります。

## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

struct Header {
  char magic[4];
  int version;
};

int main() {
  Header h = {{'S', 'A', 'V', 'E'}, 2};

  std::FILE* f = std::fopen("save.bin", "wb");
  std::size_t written = std::fwrite(&h, sizeof(h), 1, f);   // 構造体 1 個を書く
  std::println("書けた要素の数: {}", written);
  std::fclose(f);

  // 読み直して確かめる
  std::FILE* in = std::fopen("save.bin", "rb");
  Header back = {};
  std::fread(&back, sizeof(back), 1, in);
  std::fclose(in);
  std::println("magic: {}{}{}{}", back.magic[0], back.magic[1], back.magic[2], back.magic[3]);
  std::println("version: {}", back.version);
}
```

```text title="実行結果"
書けた要素の数: 1
magic: SAVE
version: 2
```

## ゲームでの使いどころ

独自形式のセーブ データ、頂点バッファーのキャッシュ、シェーダーのコンパイル結果の保存などに使います。ファイルの先頭に、識別用の文字列とバージョン番号を書くと、あとで形式を変えたときに、古いファイルを見分けられます。

セーブの失敗は、プレイヤーにとって大きな損失です。`fwrite` の戻り値と `fclose` の戻り値の両方を確かめ、失敗したら前のセーブ データを残す、一時ファイルに書いてから `rename` で置き換える、といった設計にします。

## よくあるミス

??? failure "戻り値を確かめず、書けなかったことに気づかない"
    ディスクが一杯のときも、プログラムは続きます。戻り値が `count` と等しいかを確かめます。

??? failure "構造体をそのまま書いて、別の環境で読めない"
    パディングとバイト順は環境しだいです。保存形式は、フィールドごとに大きさを決めて書き出します。

??? failure "書いた直後に別のプロセスで読んで、内容が足りない"
    バッファーに残っています。`fflush` か `fclose` の後に読みます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fread`](fread.md) | 対になる、読み込む関数 |
| [`fputs`](fputs.md) | 文字列を書き出す。テキスト向け |
| [`fflush`](fflush.md) | バッファーを書き出す |
| `std::ofstream::write` | C++ のストリームでの同等の関数 |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] バイト列を一度に書き出す
    - [x] 戻り値は書けた要素の数
    - [x] 確実に届けるには `fflush` か `fclose`

## 関連ページ

- [cpprefjp: std::fwrite](https://cpprefjp.github.io/reference/cstdio/fwrite.html)
- [cppreference: std::fwrite](https://en.cppreference.com/w/cpp/io/c/fwrite)
