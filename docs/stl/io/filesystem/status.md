---
title: std::filesystem::status
summary: "ファイルの種類と権限を取得する（file_status）。"
order: 25
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::status

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

`std::filesystem::status` は、**ファイルの種類と権限をまとめた `file_status` を返す**関数です。`type()` で種類（通常ファイル、フォルダ、リンクなど）を調べます。

!!! tip "ポイント"
    - `status(p).type()` が `file_type`。
    - リンクそのものを調べるのは `symlink_status`。

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### status {#status}

```cpp
file_status status(const path& p);
```

- 種類（`type()`）と権限（`permissions()`）をまとめて取得します

## 実際に動かしてみる

```cpp
#include <filesystem>
#include <print>

int main() {
  namespace fs = std::filesystem;
  std::println("{}", fs::status(".").type() == fs::file_type::directory);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ファイルの種類で処理を分ける | `switch (fs::status(p).type())` |

## よくあるミス

??? failure "種類の値を忘れる"
    `file_type::not_found`、`regular`、`directory`、`symlink` などがあります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_regular_file`](is_regular_file.md) | 種類を bool で |

## コンパイラ対応

C++17 の機能です。GCC 9 / Clang 9 / MSVC 19.14 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 種類と権限を取る
    - [x] `type()` で種類
    - [x] リンクは symlink_status

## 関連ページ

- [cpprefjp: std::filesystem::status](https://cpprefjp.github.io/reference/filesystem/status.html)
- [cppreference: std::filesystem::status](https://en.cppreference.com/w/cpp/filesystem/status)
