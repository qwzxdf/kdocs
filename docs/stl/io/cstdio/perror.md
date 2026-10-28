---
title: std::perror
summary: "`errno` の内容を、説明つきで標準エラー出力に出す。"
order: 900
tags:
  - 入出力・文字列
---

# std::perror

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

ファイルが開けなかったとき、「失敗しました」だけでは、原因が分かりません。ファイルがないのか、権限がないのか、ディスクが一杯なのか。C の関数は、失敗の理由を `errno` という変数に入れていますが、数字のままでは読めません。

`std::perror` は、<strong>`errno` の意味を、人が読める文章で標準エラー出力に出す</strong>関数です。

!!! tip "ポイント"
    - `perror("接頭辞")` は、「接頭辞: エラーの説明」の形で、標準エラー出力に出す
    - 直前に失敗した関数の `errno` を使うので、失敗の直後に呼ぶ
    - 説明の文面は、環境（OS、ロケール）によって違う
    - 成功したときに `errno` が 0 になるとは限らない。失敗が確実なときだけ呼ぶ

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::perror {#perror}

```cpp
void perror(const char* s);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `s` | `const char*` | エラーの説明の前に付ける文字列。`nullptr` や空文字列なら付けない |

`s` が空でなければ、「`s: `」を出してから、`errno` に対応する説明と改行を出します。出力先は標準エラー出力（`stderr`）です。

`errno` は、関数が失敗したときに値が設定される変数ですが、成功したときに 0 に戻るとは限りません。`perror` を呼ぶのは、`fopen` が `nullptr` を返した、といった失敗が確かめられた直後に限ります。その間に別の関数（`printf` など）を呼ぶと、`errno` が上書きされることがあります。

説明の文面は、環境ごとに違います。プログラムの中で文面を比較して分岐してはいけません。分岐は `errno` の値（`ENOENT` など）で行います。

## 実際に動かしてみる

```cpp
#include <cerrno>
#include <cstdio>
#include <print>

int main() {
  std::FILE* f = std::fopen("not_found.txt", "r");
  if (!f) {
    // perror は stderr に出す。実行結果には現れないので、errno を確かめる
    std::println("存在しない: {}", errno == ENOENT);
    std::perror("not_found.txt を開けません");   // 標準エラー出力に説明が出る
  }
}
```

```text title="実行結果"
存在しない: true
```

## ゲームでの使いどころ

ファイルが開けない、読めない、といった失敗の原因を、簡単に知りたいときに使います。デバッグ中の確認や、小さなツールのエラー表示に便利です。

ゲームの製品では、`std::filesystem` の `error_code`（`ec.message()`）や、自前のログに残すほうが、文面を整えられます。`perror` は標準エラー出力にしか出せないので、ログ ファイルには使えません。

## よくあるミス

??? failure "失敗の確認なしに呼んで、意味のない説明が出る"
    成功した直後でも、前の失敗の `errno` が残っていることがあります。失敗を確かめてから呼びます。

??? failure "文面で分岐して、環境が変わると動かない"
    分岐は `errno` の値で行います。

## 類似

| 名前 | 違い |
| --- | --- |
| `std::strerror` | `errno` の説明を、文字列として受け取る |
| [`fopen`](fopen.md) | 失敗で `errno` を設定する代表的な関数 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `errno` の意味を標準エラーに出す
    - [x] 失敗の直後に呼ぶ
    - [x] 文面は環境による

## 関連ページ

- [cpprefjp: std::perror](https://cpprefjp.github.io/reference/cstdio/perror.html)
- [cppreference: std::perror](https://en.cppreference.com/w/cpp/io/c/perror)
