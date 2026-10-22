---
title: std::filesystem::symlink_status
summary: "シンボリックリンクをたどらずに、そのファイル自身の状態を返す。"
order: 900
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::symlink_status

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

`status` は、リンクをたどって先の状態を返します。`symlink_status` は、リンク自身の状態（種類が `symlink` か）を返します。

!!! tip "ポイント"
    - `std::filesystem` の部品。
    - 例外を避けたいときは、`std::error_code` を渡す版を使う。
    - パスは `std::filesystem::path` で扱う。

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要と、[`path`](path.md) を先に読んでください。

## 関数の詳しい説明

### std::filesystem::symlink_status {#symlink_status}

```cpp
file_status symlink_status(const path& p);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | path | 調べるパス |

- 戻り値: `file_status`
- 計算量: OS に依存


## 実際に動かしてみる

```cpp
#include <filesystem>
#include <fstream>
#include <print>

namespace fs = std::filesystem;

int main() {
  fs::path p = fs::temp_directory_path() / "kdocs_demo.txt";
  std::ofstream(p) << "x";
  std::println("{}", fs::symlink_status(p).type() == fs::file_type::regular);
  fs::remove(p);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | リンクかどうかを区別して処理する |

## よくあるミス

??? failure "`status` と取り違える"
    `status` はリンク先を見ます。リンク自身を見るなら `symlink_status` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`status`](status.md) | リンクをたどる |
| [`is_symlink`](is_symlink.md) | リンクか調べる |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] シンボリックリンクをたどらずに、そのファイル自身の状態を返す
    - [x] `std::filesystem` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::filesystem::symlink_status](https://cpprefjp.github.io/reference/filesystem/symlink_status.html)
- [cppreference: std::filesystem::symlink_status](https://en.cppreference.com/w/cpp/filesystem/symlink_status)
