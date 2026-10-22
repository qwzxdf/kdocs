---
title: std::filesystem::file_type
summary: "ファイルの種類（通常ファイル・フォルダ・リンクなど）を表す列挙型。"
order: 900
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::file_type

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

`fs::status(p).type()` が返すのが、ファイルの種類を表す `file_type` です。通常のファイルか、フォルダか、シンボリックリンクか、存在しないかを区別できます。ふつうは `is_regular_file` や `is_directory` のほうが読みやすいです。

!!! tip "ポイント"
    - `regular`: 普通のファイル。
    - `directory`: フォルダ。
    - `not_found`: 存在しない（エラーではなく、この値）。

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::filesystem::file_type {#file_type}

```cpp
enum class file_type {
  none, not_found, regular, directory, symlink, block, character, fifo, socket, unknown
};
```

- 戻り値: 列挙型

| 値 | 意味 |
| --- | --- |
| `regular` | 普通のファイル |
| `directory` | フォルダ |
| `not_found` | 存在しない |
| `symlink` | シンボリックリンク |
| `block` / `character` / `fifo` / `socket` / `unknown` | 特殊なファイル（ゲームでは見ない） |
| `none` | 状態を取得できていない |


## 実際に動かしてみる

```cpp
#include <filesystem>
#include <print>

namespace fs = std::filesystem;

int main() {
  std::println("{}", fs::status(fs::current_path()).type() == fs::file_type::directory);
  std::println("{}", fs::status("no_such_file_kdocs").type() == fs::file_type::not_found);
}
```

```text title="実行結果"
true
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| パスの種類で処理を分ける | `switch (fs::status(p).type()) { ... }` |

## よくあるミス

??? failure "存在しないのを例外だと思う"
    存在しないパスの `status` は、例外にならず `not_found` を返します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`status`](status.md) | 種類を取得する |
| [`is_regular_file`](is_regular_file.md) | 通常ファイルか |
| [`is_directory`](is_directory.md) | フォルダか |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ファイルの種類を表す列挙型
    - [x] status(p).type() の値
    - [x] 存在しないのは not_found

## 関連ページ

- [cpprefjp: std::filesystem::file_type](https://cpprefjp.github.io/reference/filesystem/file_type.html)
- [cppreference: std::filesystem::file_type](https://en.cppreference.com/w/cpp/filesystem/file_type)
