---
title: std::filesystem::copy_symlink
summary: "シンボリックリンクを、リンクのままコピーする。"
order: 900
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::copy_symlink

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

フォルダーのコピーなどで、シンボリックリンクに出会ったとき、リンクの指し先の実体をコピーするのか、リンクそのものを新しい場所に作るのか、選ぶ必要があります。後者のために用意された関数が、`std::filesystem::copy_symlink` です。

<strong>リンクそのもの</strong>を、新しい場所へコピーします。新しいリンクは、元と同じ指し先を指します。

!!! tip "ポイント"
    - コピーするのは、リンクの中身（指し先のパス）。指し先の実体ではない
    - 引数が両方とも、パス。コピー元がシンボリックリンクでないとエラー
    - 新しいリンクの指し先は、元と同じ文字列。相対パスなら、新しい場所から見て別の場所を指すことがある
    - Windows では、リンクを作る権限が要る

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要と、[`path`](path.md) を先に読んでください。

## 関数の詳しい説明

### copy_symlink {#copy_symlink}

<span class="ver ver-17">C++17</span>

```cpp
void copy_symlink(const path& existing_symlink, const path& new_symlink);
void copy_symlink(const path& existing_symlink, const path& new_symlink, std::error_code& ec) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `existing_symlink` | `const path&` | コピー元。シンボリックリンクである必要がある |
| `new_symlink` | `const path&` | 作る新しいリンクのパス。すでに存在するとエラー |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

`read_symlink(existing)` で指し先を読んで、同じ指し先の新しいリンクを作る、という処理と同じです。指し先がファイルかフォルダーかで、`create_symlink` と `create_directory_symlink` を使い分けます。

注意するのは、<strong>相対パスのリンクをコピーすると、意味が変わりうる</strong>ことです。`../data` を指すリンクを別のフォルダーにコピーすると、新しい場所から見た `../data` を指します。元と同じ実体を指したいなら、リンクを絶対パスで作っておきます。

`copy` 関数で `copy_options::copy_symlinks` を指定すると、フォルダーの再帰コピーの中でリンクに出会ったとき、内部でこの処理が行われます。

## 実際に動かしてみる

```cpp
#include <filesystem>
#include <fstream>
#include <print>
#include <system_error>

int main() {
  namespace fs = std::filesystem;
  std::ofstream("plain.txt") << "x";

  // コピー元がリンクでないと、エラーになる
  std::error_code ec;
  fs::copy_symlink("plain.txt", "copy_link", ec);
  std::println("エラー: {}", static_cast<bool>(ec));
  std::println("コピー先が作られた: {}", fs::exists("copy_link"));
}
```

```text title="実行結果"
エラー: true
コピー先が作られた: false
```

## ゲームでの使いどころ

ゲームのインストーラーや、アセットのパッケージ作成ツールで、フォルダー構造を複製するときに使います。リンクを実体にして展開するか、リンクのまま保つかは、ツールの方針です。通常は `copy` に `copy_options::copy_symlinks` を渡して任せ、この関数を直接呼ぶのは、リンクだけを特別扱いしたいときです。

ゲームの実行中に使うことは、ほとんどありません。

## よくあるミス

??? failure "リンクではないものを渡して、エラーになる"
    コピー元がリンクでないと失敗します。通常のファイルは `copy_file` を使います。

??? failure "相対リンクをコピーして、リンク切れになる"
    指し先の文字列だけがコピーされるので、新しい場所から見た相対パスが、存在しない場所を指すことがあります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`copy`](copy.md) | ファイルやフォルダーをまとめてコピー。`copy_symlinks` オプションで内部的にこの処理を使う |
| [`create_symlink`](create_symlink.md) | 指し先を指定して、新しいリンクを作る |
| [`read_symlink`](read_symlink.md) | リンクの指し先を読む |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] リンクそのものをコピーする
    - [x] コピー元はリンクである必要がある
    - [x] 相対リンクは意味が変わりうる

## 関連ページ

- [cpprefjp: std::filesystem::copy_symlink](https://cpprefjp.github.io/reference/filesystem/copy_symlink.html)
- [cppreference: std::filesystem::copy_symlink](https://en.cppreference.com/w/cpp/filesystem/copy_symlink)
