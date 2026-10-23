---
title: std::filesystem::create_directory
summary: "フォルダを 1 階層だけ作る。"
order: 4
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::create_directory

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

保存用のフォルダを 1 つ作りたい。`std::filesystem::create_directory` は、フォルダを 1 つだけ作る関数です。親のフォルダがなければ失敗します。すでにあれば何もせず、`false` を返します。深い階層をまとめて作るなら、`create_directories` を使います。

!!! tip "ポイント"
    - 親がないと失敗する。
    - すでにあれば何もしない。

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### create_directory {#create_directory}

```cpp
bool create_directory(const path& p);
```

- フォルダを 1 つだけ作ります。親フォルダが無いと失敗するので、普通は `create_directories` を使います

## 実際に動かしてみる

```cpp
#include <filesystem>
#include <print>

int main() {
  namespace fs = std::filesystem;
  std::println("{}", fs::create_directory("dir_demo"));   // 作った
  std::println("{}", fs::create_directory("dir_demo"));   // すでにある
  fs::remove("dir_demo");
}
```

```text title="実行結果"
true
false
```

## ゲームでの使いどころ

親のフォルダが必ずあると分かっているときに、1 階層だけ作ります。たとえば、保存先の `saves` がすでにあって、その中に `slot1` を作る場合です。

実際には、親があるかどうか分からないことが多いので、`create_directories` のほうが使いやすく、迷ったらそちらを選びます。

戻り値の `false` は、すでにあったことを示し、エラーではありません。失敗は例外か、`error_code` で受け取ります。

## よくあるミス

??? failure "深い階層を作ろうとして失敗"
    親が無いと失敗します。`create_directories` を使います。

??? failure "親がなくて失敗する"
    `create_directory("a/b/c")` は、`a/b` が無いと失敗します。深い階層は `create_directories` で作ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`create_directories`](create_directories.md) | まとめて作る |

## コンパイラ対応

C++17 の機能です。GCC 9 / Clang 9 / MSVC 19.14 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] フォルダを 1 つ作る
    - [x] 親が必要
    - [x] 深い階層は create_directories

## 関連ページ

- [cpprefjp: std::filesystem::create_directory](https://cpprefjp.github.io/reference/filesystem/create_directory.html)
- [cppreference: std::filesystem::create_directory](https://en.cppreference.com/w/cpp/filesystem/create_directory)
