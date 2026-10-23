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

アセットフォルダの中の画像を、サブフォルダの中も含めて全部探したい。`directory_iterator` はフォルダの直下しか見ないので、サブフォルダに入るたびに、自分で再帰の関数を書くことになります。`std::filesystem::recursive_directory_iterator` は、フォルダの中身を、サブフォルダの奥まで全部たどって回します。再帰の関数を書かなくて済みます。

!!! tip "ポイント"
    - 範囲 for で回せる。
    - 拡張子で絞るなら `entry.path().extension()`。
    - 回しながらフォルダを変更するのは危険。

!!! info "このページを読む前に"
    [`directory_iterator`](directory_iterator.md) を先に読んでください。`recursive_directory_iterator` は、その再帰版です。

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

## しくみ

`recursive_directory_iterator(dir)` は、深さ優先でフォルダをたどります。サブフォルダを見つけたら、その中を先に全部回してから、次の項目へ進みます。各項目は [`directory_entry`](directory_entry.md) として返ります。

フォルダも項目の 1 つとして返るので、ファイルだけが欲しいなら、`entry.is_regular_file()` で絞ります。

イテレーターの `depth()` で現在の深さが取れ、`disable_recursion_pending()` を呼ぶと、いま見ているフォルダの中には入らず、次へ進めます。特定のフォルダ（`.git` など）を飛ばしたいときに使います。

## ゲームでの使いどころ

アセットの一括読み込みに使います。

```cpp
for (const auto& entry : fs::recursive_directory_iterator("assets")) {
  if (entry.is_regular_file() && entry.path().extension() == ".png") {
    LoadTexture(entry.path());
  }
}
```

ホットリロードの対象を探すときも同じです。ファイルの更新時刻を調べて、変わったものだけを読み直します。

フォルダの数が多いと、全部をたどるのに時間がかかります。起動のたびに全部を調べると遅くなるので、一覧をキャッシュするか、ゲームの本番ではパッケージ（1 つのファイルにまとめたアセット）を使います。

## よくあるミス

??? failure "フォルダも項目に含まれることを忘れる"
    フォルダ自体も項目として返ります。ファイルだけを処理するなら、`entry.is_regular_file()` で絞ります。

??? failure "回しながらフォルダの中身を変更する"
    ファイルの追加や削除を、回している最中に行うと、挙動が不定になります。いったん集めてから操作します。

??? failure "巨大なフォルダを毎回たどって遅くなる"
    `.git` や `node_modules` のような大きなフォルダに入ると、非常に時間がかかります。`disable_recursion_pending()` で飛ばすか、対象のフォルダを絞ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`directory_iterator`](directory_iterator.md) | フォルダの直下だけを回す |
| [`directory_entry`](directory_entry.md) | 回して得られる 1 つの項目 |
| [`path`](path.md) | 拡張子の取り出し（`extension()`）などに使う |

## コンパイラ対応

C++17 の機能です。GCC 9 / Clang 9 / MSVC 19.14 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] サブフォルダの中まで全部たどって回す。
    - [x] フォルダも項目に含まれる。ファイルだけなら `is_regular_file()` で絞る。
    - [x] 巨大なフォルダに入らないよう、対象を絞る。

## 関連ページ

- [cpprefjp: std::filesystem::recursive_directory_iterator](https://cpprefjp.github.io/reference/filesystem/recursive_directory_iterator.html)
- [cppreference: std::filesystem::recursive_directory_iterator](https://en.cppreference.com/w/cpp/filesystem/recursive_directory_iterator)
