---
title: std::filesystem::is_directory
summary: "フォルダか調べる。"
order: 12
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::is_directory

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

パスがフォルダかを調べたい。フォルダとファイルでは、扱いが違います。ファイルは開いて読めますが、フォルダは開いても読めません。`std::filesystem::is_directory` は、そのパスがフォルダかを調べる関数です。存在しなければ `false` を返します。

!!! tip "ポイント"
    - 存在しなければ `false`。
    - ファイルかは [`is_regular_file`](is_regular_file.md)。

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### is_directory {#is_directory}

```cpp
bool is_directory(const path& p);
```

- フォルダなら `true`

```cpp
#include <filesystem>
#include <fstream>
#include <print>

int main() {
  namespace fs = std::filesystem;
  fs::create_directories("music");
  std::ofstream("readme.txt");
  std::println("{} {}", fs::is_directory("music"), fs::is_regular_file("music"));
  std::println("{} {}", fs::is_directory("readme.txt"), fs::is_regular_file("readme.txt"));
}
```

```text title="実行結果"
true false
false true
```

## ゲームでの使いどころ

ドラッグ＆ドロップされたものが、ファイルかフォルダかで処理を分けます。ファイルなら 1 つ読み込み、フォルダなら中のファイルをすべて探索する、といった流れです。

フォルダを作る前に同名のものがすでにあるかを調べる用途もあります。名前が同じ「ファイル」があると、フォルダを作れません。`exists` だけでは、種類が分かりません。

通常のファイルかを調べるなら、`is_regular_file` です。存在しない場合も `false` なので、「存在しない」と「ファイルである」を区別したいときは、`exists` も併せて呼びます。

## よくあるミス

??? failure "シンボリックリンクの扱い"
    リンク先がフォルダなら `true` です。リンクそのものを調べるには `symlink_status` を使います。

??? failure "存在しないパスも `false` になる"
    `false` は、フォルダでない、または存在しない、の両方を意味します。区別したいときは `exists` も調べます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_regular_file`](is_regular_file.md) | ファイルか |

## コンパイラ対応

C++17 の機能です。GCC 9 / Clang 9 / MSVC 19.14 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] フォルダか
    - [x] 無ければ false
    - [x] リンク先で判定

## 関連ページ

- [cpprefjp: std::filesystem::is_directory](https://cpprefjp.github.io/reference/filesystem/is_directory.html)
- [cppreference: std::filesystem::is_directory](https://en.cppreference.com/w/cpp/filesystem/is_directory)
