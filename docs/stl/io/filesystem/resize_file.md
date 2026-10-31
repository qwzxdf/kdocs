---
title: std::filesystem::resize_file
summary: "ファイルの大きさを変える（切り詰め・拡張）。"
order: 24
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::resize_file

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

ログ ファイルを一定の大きさで切り詰めたい。ダウンロード用に、最終的な大きさのファイルを先に確保しておきたい。ファイルを開いて、書き込んで、閉じる、という手順を踏まずに、<strong>ファイルの大きさだけを変えたい</strong>場面があります。

`std::filesystem::resize_file` は、指定した大きさにファイルを切り詰めるか、伸ばします。伸ばした部分は、0 で埋められます。

!!! tip "ポイント"
    - 縮めると、末尾が失われる。元に戻せない
    - 伸ばすと、増えた部分は 0 で埋められる
    - 存在しないファイルを渡すと、新しく作らずにエラーになる
    - ファイルを開いたままのストリームがあるときは、先に閉じる（環境によって失敗する）

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### resize_file {#resize_file}

<span class="ver ver-17">C++17</span>

```cpp
void resize_file(const path& p, std::uintmax_t new_size);
void resize_file(const path& p, std::uintmax_t new_size, std::error_code& ec) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | 大きさを変えるファイル。ふつうのファイルで、実在している必要がある |
| `new_size` | `std::uintmax_t` | 新しい大きさ（バイト） |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

`new_size` が今の大きさより小さければ、後ろが切り捨てられます。大きければ、足りない分が 0 バイトで埋められます。内容の中身を保ったまま大きさを変えるわけではなく、<strong>縮めた部分のデータは戻ってきません</strong>。

戻り値はありません。失敗すると、`filesystem_error` を投げます（`ec` の版では `ec` を見ます）。失敗の典型は、ファイルが存在しない、権限がない、書き込み禁止になっている、といったものです。

ファイルを開いている別のストリームがあると、OS によっては失敗します。Windows では、他のプロセスが開いているファイルの大きさを変えられないことがあります。

## 実際に動かしてみる

```cpp
#include <filesystem>
#include <fstream>
#include <iterator>
#include <print>
#include <string>

int main() {
  namespace fs = std::filesystem;
  {
    std::ofstream out("log.txt", std::ios::binary);
    out << "0123456789";   // 10 バイト
  }
  std::println("最初: {} バイト", fs::file_size("log.txt"));

  fs::resize_file("log.txt", 4);   // 末尾を切り詰める
  std::println("縮めた後: {} バイト", fs::file_size("log.txt"));

  fs::resize_file("log.txt", 8);   // 伸ばす。増えた部分は 0 で埋まる
  std::println("伸ばした後: {} バイト", fs::file_size("log.txt"));

  std::ifstream in("log.txt", std::ios::binary);
  std::string data((std::istreambuf_iterator<char>(in)), {});
  std::println("先頭 4 文字: {}", data.substr(0, 4));
  std::println("5 バイト目は 0: {}", data[4] == '\0');
}
```

```text title="実行結果"
最初: 10 バイト
縮めた後: 4 バイト
伸ばした後: 8 バイト
先頭 4 文字: 0123
5 バイト目は 0: true
```

## ゲームでの使いどころ

ログ ファイルが上限を超えたら、先頭を残して切り詰める、といった単純なローテーションに使えます（古い部分を捨てたいなら、別のファイルに書き出して置き換えるほうが普通です）。

大きなダウンロードでは、受信前に最終サイズでファイルを確保しておくと、途中でディスクが足りなくなる問題に早く気づけます。ただし、確保した部分は 0 で埋まるだけなので、「まだ書いていない」ことを別に管理します。

## よくあるミス

??? failure "ファイルがなくても、作ってくれると思う"
    `resize_file` は新しいファイルを作りません。存在しないと失敗するので、先に空のファイルを作ります。

??? failure "ストリームで開いたまま呼んで失敗する"
    `ofstream` を開いたままだと、環境によって失敗します。閉じてから呼びます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`file_size`](file_size.md) | ファイルの今の大きさを調べる |
| [`remove`](remove.md) | ファイルごと消す |

## コンパイラ対応

C++17 の機能です。GCC 9 / Clang 9 / MSVC 19.14 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ファイルの大きさだけを変える
    - [x] 縮めた部分は戻らない
    - [x] 伸ばした部分は 0 で埋まる

## 関連ページ

- [cpprefjp: std::filesystem::resize_file](https://cpprefjp.github.io/reference/filesystem/resize_file.html)
- [cppreference: std::filesystem::resize_file](https://en.cppreference.com/w/cpp/filesystem/resize_file)
