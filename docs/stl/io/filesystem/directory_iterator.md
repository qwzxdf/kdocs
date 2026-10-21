---
title: std::filesystem::directory_iterator
summary: "フォルダの中身（直下のファイル）を順に回す。"
order: 5
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::directory_iterator

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

`std::filesystem::directory_iterator` は、**フォルダの直下にあるファイルやフォルダを順に回す**イテレータです。サブフォルダの中までは入りません（それは [`recursive_directory_iterator`](recursive_directory_iterator.md)）。順番は決まっていません。

!!! tip "ポイント"
    - 範囲 for で回せる: `for (const auto& entry : fs::directory_iterator(dir))`。
    - 順番は不定。必要なら集めて `sort`。
    - 要素は [`directory_entry`](directory_entry.md)。

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### directory_iterator {#directory_iterator}

```cpp
class directory_iterator;
explicit directory_iterator(const path& p);
directory_iterator(const path& p, directory_options options);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | 中身を見たいフォルダ |
| `options` | `directory_options` | 権限の無いフォルダを飛ばす、など（[フラグ](#フラグオプション)） |

- 範囲 for で回すと、`directory_entry` が 1 つずつ出てきます
- **順番は決まっていない**（名前順にしたいなら集めてから sort）
- `.` と `..` は出てこない

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <filesystem>
#include <fstream>
#include <print>
#include <string>
#include <vector>

int main() {
  namespace fs = std::filesystem;
  fs::create_directories("di_demo");
  std::ofstream("di_demo/b.txt") << "x";
  std::ofstream("di_demo/a.txt") << "x";

  std::vector<std::string> names;
  for (const auto& e : fs::directory_iterator("di_demo")) {
    names.push_back(e.path().filename().generic_string());
  }
  std::ranges::sort(names);  // 順番は不定なので、並べてから表示する
  std::println("{}", names);
  fs::remove_all("di_demo");
}
```

```text title="実行結果"
["a.txt", "b.txt"]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| アセットフォルダのファイル一覧 | `for (auto& e : fs::directory_iterator("assets"))` |

## よくあるミス

??? failure "順番に依存する"
    OS しだいです。一覧は `vector` に集めて並べ替えます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`recursive_directory_iterator`](recursive_directory_iterator.md) | サブフォルダの中まで |
| [`directory_entry`](directory_entry.md) | 要素の型 |

## コンパイラ対応

C++17 の機能です。GCC 9 / Clang 9 / MSVC 19.14 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] フォルダ直下を回す
    - [x] 順番は不定
    - [x] サブフォルダの中は recursive 版

## 関連ページ

- [cpprefjp: std::filesystem::directory_iterator](https://cpprefjp.github.io/reference/filesystem/directory_iterator.html)
- [cppreference: std::filesystem::directory_iterator](https://en.cppreference.com/w/cpp/filesystem/directory_iterator)
