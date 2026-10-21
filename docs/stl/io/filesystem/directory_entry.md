---
title: std::filesystem::directory_entry
summary: "フォルダを回して得られる、1 つの項目（パスと情報）。"
order: 7
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::directory_entry

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

`std::filesystem::directory_entry` は、**フォルダを回したときの 1 つの項目**です。パスのほか、ファイルかフォルダか、サイズなどを（キャッシュして）持っています。`entry.path()` でパスが取れます。

!!! tip "ポイント"
    - `path()` でパス、`is_regular_file()` `is_directory()` で種類、`file_size()` でサイズ。
    - 情報はキャッシュされるので、別途 `fs::file_size` を呼ぶより速いことがある。

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### directory_entry {#directory_entry}

```cpp
class directory_entry;
```

| メンバ | 何をする |
| --- | --- |
| `path()` | パス |
| `is_regular_file()` / `is_directory()` | 種類 |
| `file_size()` | 大きさ |
| `last_write_time()` | 更新日時 |
| `exists()` | まだあるか |

- フォルダを回したときに取れる情報をまとめて持っているので、`fs::file_size(entry.path())` より `entry.file_size()` のほうが速いことがあります

## 実際に動かしてみる

```cpp
#include <filesystem>
#include <fstream>
#include <print>

int main() {
  namespace fs = std::filesystem;
  fs::create_directories("de_demo");
  std::ofstream("de_demo/a.txt") << "x";
  for (const auto& e : fs::directory_iterator("de_demo")) {
    std::println("{} {}", e.path().filename().generic_string(), e.is_regular_file());
  }
  fs::remove_all("de_demo");
}
```

```text title="実行結果"
a.txt true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 一覧の各ファイルの種類とサイズ | `entry.is_regular_file()` |

## よくあるミス

??? failure "キャッシュが古い"
    回している間にファイルが変わっても、キャッシュは更新されません。`refresh()` で更新できます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`directory_iterator`](directory_iterator.md) | 回す側 |

## コンパイラ対応

C++17 の機能です。GCC 9 / Clang 9 / MSVC 19.14 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] フォルダ内の 1 項目
    - [x] `path()` でパス
    - [x] 情報はキャッシュされる

## 関連ページ

- [cpprefjp: std::filesystem::directory_entry](https://cpprefjp.github.io/reference/filesystem/directory_entry.html)
- [cppreference: std::filesystem::directory_entry](https://en.cppreference.com/w/cpp/filesystem/directory_entry)
