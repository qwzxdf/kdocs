---
title: std::filesystem::recursive_directory_iterator
summary: "フォルダの中身を、サブフォルダの中まで全部回す。"
order: 6
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::recursive_directory_iterator

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

`std::filesystem::recursive_directory_iterator` は、**フォルダの中身を、サブフォルダの中まで全部たどって回す**イテレータです。アセットフォルダのファイルを全部探す、といった処理に使います。

!!! tip "ポイント"
    - 範囲 for で回せる。
    - 拡張子で絞るなら `entry.path().extension()`。
    - 回しながらフォルダを変更するのは危険。

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### recursive_directory_iterator {#recursive_directory_iterator}

```cpp
class recursive_directory_iterator;
```

- サブフォルダの中まで全部たどります。`depth()` で今の深さ、`disable_recursion_pending()` で「このフォルダには入らない」ができます

```cpp
#include <algorithm>
#include <filesystem>
#include <fstream>
#include <print>
#include <string>
#include <vector>

namespace fs = std::filesystem;

int main() {
  fs::create_directories("data/stages");
  std::ofstream("data/items.json");
  std::ofstream("data/stages/1.json");

  std::vector<std::string> files;
  for (const auto& entry : fs::recursive_directory_iterator("data")) {
    if (entry.is_regular_file()) {
      files.push_back(entry.path().generic_string());
    }
  }
  std::ranges::sort(files);
  std::println("{}", files);
}
```

```text title="実行結果"
["data/items.json", "data/stages/1.json"]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| アセットフォルダの画像を全部探す | `for (auto& e : fs::recursive_directory_iterator(root))` |

## よくあるミス

??? failure "回しながらファイルを消す・作る"
    回している最中にフォルダを変更すると、結果が不定になります。先に集めてから処理します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`directory_iterator`](directory_iterator.md) | 直下だけ |

## コンパイラ対応

C++17 の機能です。GCC 9 / Clang 9 / MSVC 19.14 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] サブフォルダの中まで全部回す
    - [x] 順番は不定
    - [x] 回しながら変更しない

## 関連ページ

- [cpprefjp: std::filesystem::recursive_directory_iterator](https://cpprefjp.github.io/reference/filesystem/recursive_directory_iterator.html)
- [cppreference: std::filesystem::recursive_directory_iterator](https://en.cppreference.com/w/cpp/filesystem/recursive_directory_iterator)
