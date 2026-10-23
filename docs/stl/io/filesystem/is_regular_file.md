---
title: std::filesystem::is_regular_file
summary: "普通のファイルか調べる。"
order: 11
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::is_regular_file

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

パスが普通のファイルかを調べたい。フォルダや特殊なファイルを開こうとすると、失敗します。`std::filesystem::is_regular_file` は、そのパスが普通のファイルかを調べる関数です。フォルダや特殊なファイルは `false` を返します。存在しなくても `false` です。

!!! tip "ポイント"
    - 存在しなければ `false`。
    - フォルダかは [`is_directory`](is_directory.md)。

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### is_regular_file {#is_regular_file}

```cpp
bool is_regular_file(const path& p);
```

- 普通のファイルなら `true`（フォルダやリンクは `false`）

## 実際に動かしてみる

```cpp
#include <filesystem>
#include <fstream>
#include <print>

int main() {
  namespace fs = std::filesystem;
  std::ofstream("irf_demo.txt") << "x";
  std::println("{} {}", fs::is_regular_file("irf_demo.txt"), fs::is_regular_file("."));
  fs::remove("irf_demo.txt");
}
```

```text title="実行結果"
true false
```

## ゲームでの使いどころ

フォルダの中を回しながら、ファイルだけを読み込むときに使います。`directory_iterator` で得た項目のうち、`is_regular_file` が真のものだけを対象にします。

読み込む前に、念のために確かめる用途もあります。ただし、確かめたあとに消される可能性があるので、開く操作の戻り値で最終的に確認します。

フォルダかを調べるなら `is_directory` です。存在するかだけなら `exists` です。

## よくあるミス

??? failure "存在しないパスで例外を期待する"
    `false` を返すだけで、例外にはなりません。

??? failure "フォルダや存在しないパスを区別せずに `false` を扱う"
    `false` は、ファイルでない理由が複数あります。区別したいなら、`exists` と `is_directory` も使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_directory`](is_directory.md) | フォルダか |

## コンパイラ対応

C++17 の機能です。GCC 9 / Clang 9 / MSVC 19.14 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 普通のファイルか
    - [x] 無ければ false
    - [x] フォルダは is_directory

## 関連ページ

- [cpprefjp: std::filesystem::is_regular_file](https://cpprefjp.github.io/reference/filesystem/is_regular_file.html)
- [cppreference: std::filesystem::is_regular_file](https://en.cppreference.com/w/cpp/filesystem/is_regular_file)
