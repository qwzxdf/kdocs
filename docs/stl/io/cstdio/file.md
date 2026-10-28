---
title: FILE
summary: "ファイルを表す型。"
order: 900
tags:
  - 入出力・文字列
---

# FILE

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

ファイルを開くと、`FILE*` というポインターが返ってきます。その `FILE` は、ファイルの位置、バッファー、終わりやエラーの印など、入出力に必要な状態をまとめた型です。中身は処理系が決めていて、使う側は見えません。

!!! tip "ポイント"
    - `std::FILE` は、中身の見えない型。`FILE*` として、関数に渡すだけ
    - 自分で `FILE` を作ったり、コピーしたりしてはいけない。`fopen` が返したポインターだけを使う
    - ファイルを開いたら `fclose` で閉じる。`unique_ptr` と組み合わせると、閉じ忘れを防げる
    - 同じ `FILE*` を、複数のスレッドから同時に使うときは、排他が要る

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### FILE {#FILE}

```cpp
using FILE = /* 実装定義 */;
```

`FILE` の中には、ファイルを表す OS のハンドル、読み書きの位置、バッファーの先頭、終わりとエラーの印などが入っています。構造が処理系ごとに違うので、`sizeof(FILE)` に意味はなく、コピーもできません。

`FILE*` を例外安全に扱うには、`std::unique_ptr` に削除関数を渡します。

```cpp
std::unique_ptr<std::FILE, decltype(&std::fclose)> f(std::fopen("a.txt", "rb"), &std::fclose);
```

こう書くと、関数を抜けるときに、例外が起きても自動で `fclose` されます。`f.get()` で、C の関数に渡せます。

C の標準ライブラリの関数は、`FILE*` を受け取るので、C のライブラリ（zlib、libpng など）とつなぐ共通の形になっています。`FILE*` から C++ のストリームを作る標準の方法はなく、逆もありません。

## 実際に動かしてみる

```cpp
#include <cstdio>
#include <memory>
#include <print>

int main() {
  // 例外が起きても閉じ忘れない書き方
  std::unique_ptr<std::FILE, decltype(&std::fclose)> f(std::fopen("auto.txt", "w"), &std::fclose);
  if (!f) return 1;

  std::fputs("auto close", f.get());
  std::println("書いた");
}   // ここで fclose が呼ばれる
```

```text title="実行結果"
書いた
```

## ゲームでの使いどころ

C のライブラリとの連携で、`FILE*` を受け渡す場面で出てきます。C++ のコードでは、`std::ofstream` と `std::ifstream` を使うほうが自然ですが、`FILE*` を要求するライブラリには、`unique_ptr` で包んで渡します。

## よくあるミス

??? failure "`FILE` を値として宣言・コピーする"
    `FILE` は不完全な型として扱います。`FILE*` だけを使います。

??? failure "開いた `FILE*` を閉じ忘れる"
    `unique_ptr` で包み、閉じ忘れを防ぎます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fopen`](fopen.md) | `FILE*` を得る |
| [`fclose`](fclose.md) | `FILE*` を閉じる |
| `std::ofstream` | C++ のストリーム |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ファイルの状態をまとめた型
    - [x] `FILE*` として受け渡す
    - [x] `unique_ptr` で閉じ忘れを防ぐ

## 関連ページ

- [cpprefjp: FILE](https://cpprefjp.github.io/reference/cstdio/file.html)
- [cppreference: FILE](https://en.cppreference.com/w/cpp/io/c/FILE)
