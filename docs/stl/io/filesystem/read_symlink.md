---
title: std::filesystem::read_symlink
summary: "シンボリックリンクが指すパスを返す。"
order: 900
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::read_symlink

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

リンクの**中身**（どこを指しているか）を読みます。リンク先のファイルの内容ではありません。

!!! tip "ポイント"
    - `std::filesystem` の部品。
    - 例外を避けたいときは、`std::error_code` を渡す版を使う。
    - パスは `std::filesystem::path` で扱う。

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要と、[`path`](path.md) を先に読んでください。

## 関数の詳しい説明

### std::filesystem::read_symlink {#read_symlink}

```cpp
path read_symlink(const path& p);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | path | シンボリックリンク |

- 戻り値: リンク先のパス
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
  fs::path target = fs::read_symlink("link", ec);
}
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | リンクの向き先を調べる |

## よくあるミス

??? failure "リンクでないパスに使う"
    シンボリックリンクでないと、エラー（例外）になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`create_symlink`](create_symlink.md) | リンクを作る |
| [`is_symlink`](is_symlink.md) | リンクか調べる |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] シンボリックリンクが指すパスを返す
    - [x] `std::filesystem` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::filesystem::read_symlink](https://cpprefjp.github.io/reference/filesystem/read_symlink.html)
- [cppreference: std::filesystem::read_symlink](https://en.cppreference.com/w/cpp/filesystem/read_symlink)
