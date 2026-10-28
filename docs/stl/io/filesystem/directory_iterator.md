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

フォルダに入っているファイルを全部調べたい。ファイルの一覧を取る関数は OS ごとに違い、Windows の `FindFirstFile` や Linux の `readdir` を使い分けるのは面倒です。`std::filesystem::directory_iterator` は、フォルダの直下にあるファイルやフォルダを順に回す標準のイテレーターで、OS の違いを吸収してくれます。サブフォルダの中までは入りません。

!!! tip "ポイント"
    - 範囲 for で回せる: `for (const auto& entry : fs::directory_iterator(dir))`。
    - 順番は不定。必要なら集めて `sort`。
    - 要素は [`directory_entry`](directory_entry.md)。

!!! info "このページを読む前に"
    [`std::filesystem::path`](path.md) の書き方と、[`directory_entry`](directory_entry.md) を先に読んでください。

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
| `options` | `directory_options` | 権限の無いフォルダを飛ばす、など（[フラグ](#flags)） |

- 範囲 for で回すと、`directory_entry` が 1 つずつ出てきます
- **順番は決まっていない**（名前順にしたいなら集めてから sort）
- `.` と `..` は出てこない

## しくみ

`directory_iterator(dir)` を作ると、`dir` の直下にある項目を指します。範囲 for で回すと、各項目が [`directory_entry`](directory_entry.md) として得られます。`.` と `..` は含まれません。

順番は決まっていません。OS やファイルシステムによって、作成順だったり、名前順だったり、バラバラだったりします。順番が必要なら、いったん `vector` に集めて `sort` します。

`directory_options` を第 2 引数に渡すと、動きを変えられます。`skip_permission_denied` は、権限のないフォルダを無視して、例外を出さずに進みます。`follow_directory_symlink` は、シンボリックリンクの先まで入ります。

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

## フラグ・オプション {#flags}

`std::filesystem::directory_options` は、フォルダの中身を列挙するときの動きを決めます。

### directory_options::none

既定です。権限のないフォルダを開こうとするとエラーになります。

### directory_options::skip_permission_denied

権限のないフォルダは、エラーにせず飛ばします。ユーザーのドキュメントなど、中身が分からないフォルダを調べるときに付けます。

### directory_options::follow_directory_symlink

シンボリック リンクのフォルダも、中へ入ります。`recursive_directory_iterator` で効きます。リンクが輪になっていると、同じ場所を何度も巡るので注意します。

## ゲームでの使いどころ

ゲームの起動時にアセットフォルダやセーブデータのフォルダを調べるのに使います。

```cpp
std::vector<fs::path> saves;
for (const auto& entry : fs::directory_iterator("saves")) {
  if (entry.path().extension() == ".sav") {
    saves.push_back(entry.path());
  }
}
std::ranges::sort(saves);  // 順番は不定なので、並べる
```

セーブデータ選択の画面で、スロットを一覧にするときに使います。MOD やプラグインのフォルダを調べて、読み込むファイルを見つける用途にも使えます。

サブフォルダの中まで調べたいときは、`recursive_directory_iterator` に替えます。

## よくあるミス

??? failure "順番が決まっていると思う"
    OS やファイルシステムによって、順番が変わります。画面に一覧を出すなら、必ず `sort` します。

??? failure "フォルダが存在しないのに回して、例外で落ちる"
    存在しないフォルダを渡すと、`filesystem_error` を投げます。先に `exists` と `is_directory` で確かめるか、`std::error_code` を渡す版を使います。

??? failure "回している最中にフォルダの中身を変更する"
    ファイルの追加や削除を回している最中に行うと、イテレーターの挙動が不定になります。いったん結果を集めてから、あとで操作します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`recursive_directory_iterator`](recursive_directory_iterator.md) | サブフォルダの中まで回す |
| [`directory_entry`](directory_entry.md) | 回して得られる 1 つの項目 |
| [`exists`](exists.md) | 回す前にフォルダがあるかを確かめる |

## コンパイラ対応

C++17 の機能です。GCC 9 / Clang 9 / MSVC 19.14 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] フォルダの直下を順に回す。サブフォルダの中には入らない。
    - [x] 順番は不定。必要なら集めて `sort`。
    - [x] 存在しないフォルダは例外になる。先に確かめる。

## 関連ページ

- [cpprefjp: std::filesystem::directory_iterator](https://cpprefjp.github.io/reference/filesystem/directory_iterator.html)
- [cppreference: std::filesystem::directory_iterator](https://en.cppreference.com/w/cpp/filesystem/directory_iterator)
