---
title: std::filesystem::create_directory_symlink
summary: "フォルダへのシンボリックリンクを作る。"
order: 900
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::create_directory_symlink

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

フォルダへの「ショートカット」のようなリンクを作ります。Windows では、ファイルへのリンクとフォルダへのリンクが別の種類なので、この関数を使い分ける必要があります。作成には権限が必要な環境があります。

!!! tip "ポイント"
    - `std::filesystem` の部品。
    - 例外を避けたいときは、`std::error_code` を渡す版を使う。
    - パスは `std::filesystem::path` で扱う。

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要と、[`path`](path.md) を先に読んでください。

## 関数の詳しい説明

### std::filesystem::create_directory_symlink {#create_directory_symlink}

```cpp
void create_directory_symlink(const path& target, const path& link);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `target` | path | リンク先のフォルダ |
| `link` | path | 作るリンクの名前 |

- 戻り値: なし
- 計算量: OS に依存


## 実際に動かしてみる

```cpp
#include <filesystem>
#include <fstream>
#include <print>

namespace fs = std::filesystem;

int main() {
  fs::path dir = fs::temp_directory_path() / "kdocs_dir";
  fs::path link = fs::temp_directory_path() / "kdocs_link";
  fs::create_directory(dir);
  std::error_code ec;
  fs::create_directory_symlink(dir, link, ec);
  std::println("{}", !ec || ec);
  fs::remove(link, ec);
  fs::remove(dir);
}
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | フォルダを別の場所にも見せる |

## よくあるミス

??? failure "Windows で権限がない"
    シンボリックリンクの作成に管理者権限（または開発者モード）が必要です。`error_code` で受けると安全です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`create_symlink`](create_symlink.md) | ファイルへのリンク |
| [`read_symlink`](read_symlink.md) | リンク先を読む |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] フォルダへのシンボリックリンクを作る
    - [x] `std::filesystem` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::filesystem::create_directory_symlink](https://cpprefjp.github.io/reference/filesystem/create_directory_symlink.html)
- [cppreference: std::filesystem::create_directory_symlink](https://en.cppreference.com/w/cpp/filesystem/create_directory_symlink)
