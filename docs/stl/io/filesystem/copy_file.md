---
title: std::filesystem::copy_file
summary: "ファイルを 1 つコピーする。"
order: 14
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::copy_file

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

`std::filesystem::copy_file` は、**ファイルを 1 つコピーする**関数です。すでに同名のファイルがあるときの動作は、`copy_options` で決めます。

!!! tip "ポイント"
    - 既定では、コピー先があると**エラー**。`copy_options::overwrite_existing` で上書き。
    - フォルダのコピーには [`copy`](copy.md)。

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### copy_file {#copy_file}

```cpp
bool copy_file(const path& from, const path& to);
bool copy_file(const path& from, const path& to, copy_options options);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `from` | `const path&` | コピー元 |
| `to` | `const path&` | コピー先 |
| `options` | `copy_options` | すでにあるときどうするか（[フラグ](#flags)） |

- 何も指定しないと、`to` がすでにあるとき**例外**になります

```cpp
#include <filesystem>
#include <fstream>
#include <print>

int main() {
  namespace fs = std::filesystem;
  std::ofstream("save.dat") << "data";
  fs::copy_file("save.dat", "save_backup.dat", fs::copy_options::overwrite_existing);
  std::println("{}", fs::file_size("save_backup.dat"));
}
```

```text title="実行結果"
4
```

## フラグ・オプション {#flags}

`std::filesystem::copy_options` は、コピー先にすでに同名のものがあるときの動きを決めます。`copy_file` が見るのは、次の 3 つだけです。残りは [`copy`](copy.md) で使います。

### copy_options::none

既定です。コピー先がすでにあると、エラーにします。`ec` を渡さない版では `filesystem_error` を投げます。

### copy_options::skip_existing

コピー先がすでにあるときは、何もしないで戻ります。戻り値は `false` です。

### copy_options::overwrite_existing

コピー先がすでにあるときは、上書きします。セーブ データのバックアップのように、新しい内容で置き換えたいときに使います。

### copy_options::update_existing

コピー先がすでにあるときは、コピー元のほうが新しい場合だけ上書きします。更新日時で見分けます。

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| セーブデータのバックアップ | `fs::copy_file(src, bak, fs::copy_options::overwrite_existing)` |

## よくあるミス

??? failure "上書きの指定を忘れる"
    既存のファイルがあるとエラー（例外）になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`copy`](copy.md) | フォルダも含めてコピー |

## コンパイラ対応

C++17 の機能です。GCC 9 / Clang 9 / MSVC 19.14 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ファイルをコピーする
    - [x] 上書きは copy_options で
    - [x] フォルダは copy

## 関連ページ

- [cpprefjp: std::filesystem::copy_file](https://cpprefjp.github.io/reference/filesystem/copy_file.html)
- [cppreference: std::filesystem::copy_file](https://en.cppreference.com/w/cpp/filesystem/copy_file)
