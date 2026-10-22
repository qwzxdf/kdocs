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

`copy` や `copy_file` は、リンクをたどって、リンク先の中身をコピーします。`copy_symlink` は、リンクそのもの（向き先）をコピーします。

!!! tip "ポイント"
    - `std::filesystem` の部品。
    - 例外を避けたいときは、`std::error_code` を渡す版を使う。
    - パスは `std::filesystem::path` で扱う。

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要と、[`path`](path.md) を先に読んでください。

## 関数の詳しい説明

### std::filesystem::copy_symlink {#copy_symlink}

```cpp
void copy_symlink(const path& from, const path& to);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `from` | path | コピー元のリンク |
| `to` | path | コピー先のリンク名 |

- 戻り値: なし
- 計算量: OS に依存


## 実際に動かしてみる

```cpp
#include <filesystem>
#include <fstream>
#include <print>

namespace fs = std::filesystem;

int main() {
  // リンクを作る権限が必要な環境があります
  std::error_code ec;
  fs::copy_symlink("link", "link_copy", ec);
}
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | リンクの構造ごと複製する |

## よくあるミス

??? failure "リンクでないものを渡す"
    元がシンボリックリンクでないとエラーです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`copy`](copy.md) | リンクをたどってコピー |
| [`read_symlink`](read_symlink.md) | リンク先を読む |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] シンボリックリンクを、リンクのままコピーする
    - [x] `std::filesystem` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::filesystem::copy_symlink](https://cpprefjp.github.io/reference/filesystem/copy_symlink.html)
- [cppreference: std::filesystem::copy_symlink](https://en.cppreference.com/w/cpp/filesystem/copy_symlink)
