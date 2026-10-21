---
title: std::filesystem::copy
summary: "ファイルやフォルダを（中身ごと）コピーする。"
order: 15
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::copy

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

`std::filesystem::copy` は、**ファイルやフォルダをコピーする**関数です。`copy_options::recursive` を付けると、フォルダを中身ごとコピーします。

!!! tip "ポイント"
    - フォルダの中身ごとなら `copy_options::recursive`。
    - 上書きは `overwrite_existing`、すでにあれば飛ばすのは `skip_existing`。

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### copy {#copy}

```cpp
void copy(const path& from, const path& to, copy_options options = copy_options::none);
```

- ファイルでもフォルダでもコピーします。フォルダの中身まで全部なら `copy_options::recursive`

## 実際に動かしてみる

```cpp
#include <filesystem>
#include <print>

int main() {
  namespace fs = std::filesystem;
  fs::create_directories("cp_src/sub");
  fs::copy("cp_src", "cp_dst", fs::copy_options::recursive);
  std::println("{}", fs::exists("cp_dst/sub"));
  fs::remove_all("cp_src");
  fs::remove_all("cp_dst");
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| アセットフォルダを丸ごとコピーする | `fs::copy(src, dst, fs::copy_options::recursive)` |

## よくあるミス

??? failure "recursive を付け忘れる"
    付けないと、フォルダの直下のファイルだけがコピーされます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`copy_file`](copy_file.md) | ファイル 1 つ |

## コンパイラ対応

C++17 の機能です。GCC 9 / Clang 9 / MSVC 19.14 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ファイル・フォルダをコピーする
    - [x] フォルダ丸ごとは `recursive`
    - [x] copy_options で動作を選ぶ

## 関連ページ

- [cpprefjp: std::filesystem::copy](https://cpprefjp.github.io/reference/filesystem/copy.html)
- [cppreference: std::filesystem::copy](https://en.cppreference.com/w/cpp/filesystem/copy)
