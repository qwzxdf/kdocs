---
title: std::fclose
summary: "ファイルを閉じる。"
order: 900
tags:
  - 入出力・文字列
---

# std::fclose

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

ファイルを開いたら、使い終わったときに閉じなければなりません。閉じないと、書いたつもりのデータが、まだバッファーの中にあって、ディスクに届いていないことがあります。開けるファイルの数にも、OS ごとに上限があります。

`std::fclose` は、<strong>バッファーに残ったデータを書き出してから、ファイルを閉じて</strong>、`FILE*` を使えなくします。

!!! tip "ポイント"
    - 戻り値は、成功なら 0、失敗なら `EOF`。書き込みのエラーは、ここで初めて分かることがある
    - 閉じた後の `FILE*` を使ってはいけない。`nullptr` を入れておくと安全
    - プログラムが終了すれば自動で閉じられるが、途中で閉じておくのが基本
    - `nullptr` を渡すと未定義動作。開けたことを確かめてから呼ぶ

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::fclose {#fclose}

```cpp
int fclose(std::FILE* stream);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | `FILE*` | 閉じるファイル。`fopen` などで得たもの |

閉じる前に、書き込み用のバッファーに残っているデータを、ファイルへ書き出します（`fflush` と同じ処理）。このとき、ディスクが一杯だったなどの理由で書き出しに失敗すると、`fclose` が `EOF` を返します。<strong>書き込みの成否を確かめるなら、`fclose` の戻り値まで見る</strong>必要があります。`fputs` が成功していても、書き出しはここで初めて行われることがあるからです。

閉じた後の `FILE*` は、解放されたメモリを指すのと同じです。もう一度 `fclose` したり、`fgets` に渡したりすると、未定義動作です。閉じたら `f = nullptr;` としておくと、誤用に気づきやすくなります。

`stdin`、`stdout`、`stderr` は閉じません。プログラムが開始と終了に自動で扱います。

## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  std::FILE* f = std::fopen("log.txt", "w");
  std::fputs("start\n", f);

  int r = std::fclose(f);   // バッファーの内容を書き出して閉じる
  f = nullptr;              // 閉じた FILE* を使わないように
  std::println("fclose の戻り値: {}", r);

  // 閉じた後なので、内容が読める
  std::FILE* in = std::fopen("log.txt", "r");
  char buf[16];
  std::fgets(buf, sizeof(buf), in);
  std::println("中身: {}", buf);
  std::fclose(in);
}
```

```text title="実行結果"
fclose の戻り値: 0
中身: start
```

## ゲームでの使いどころ

セーブ データの書き込みでは、`fclose` の戻り値を確かめます。ディスクの空きが足りなかった場合、`fputs` が成功を返しても、`fclose` で初めて失敗が分かります。失敗したら、書きかけのファイルを消し、前のセーブ データを残します。

C++ では、`unique_ptr` に削除関数として `fclose` を渡すと、例外が起きても閉じ忘れません。ただし、戻り値を確かめる場面（セーブ）では、明示的に `fclose` を呼びます。

## よくあるミス

??? failure "閉じ忘れて、データが書き出されない"
    プログラムが異常終了すると、バッファーが書き出されません。書き終わったらすぐ閉じます。

??? failure "閉じた後の `FILE*` を使う"
    閉じたあとは使えません。`nullptr` を代入する習慣をつけます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fopen`](fopen.md) | ファイルを開く |
| [`fflush`](fflush.md) | 閉じずにバッファーだけを書き出す |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] バッファーを書き出して閉じる
    - [x] 戻り値で書き込みの失敗が分かる
    - [x] 閉じたら使わない

## 関連ページ

- [cpprefjp: std::fclose](https://cpprefjp.github.io/reference/cstdio/fclose.html)
- [cppreference: std::fclose](https://en.cppreference.com/w/cpp/io/c/fclose)
