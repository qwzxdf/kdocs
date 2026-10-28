---
title: std::filesystem::perm_options
summary: "permissions で権限をどう変更するか（置き換え・追加・削除）を指定する。"
order: 900
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::perm_options

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

`fs::permissions(p, 権限, オプション)` の第 3 引数です。`replace`（置き換える）・`add`（追加する）・`remove`（削除する）・`nofollow`（シンボリックリンクをたどらない）があります。

!!! tip "ポイント"
    - `std::filesystem` の部品。
    - 例外を避けたいときは、`std::error_code` を渡す版を使う。
    - パスは `std::filesystem::path` で扱う。

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要と、[`path`](path.md) を先に読んでください。

## 関数の詳しい説明

### std::filesystem::perm_options {#perm_options}

```cpp
enum class perm_options : unsigned {
  replace = 0x1,
  add = 0x2,
  remove = 0x4,
  nofollow = 0x8
};
```

- 戻り値: ビットマスク
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
  fs::permissions(p, fs::perms::owner_write | fs::perms::group_write | fs::perms::others_write, fs::perm_options::remove);
  std::println("{}", (fs::status(p).permissions() & fs::perms::owner_write) == fs::perms::none);
  fs::permissions(p, fs::perms::owner_write | fs::perms::group_write | fs::perms::others_write, fs::perm_options::add);
  fs::remove(p);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | ファイルを読み取り専用にする |

## よくあるミス

??? failure "`replace` を既定だと忘れる"
    オプションを省略すると `replace` で、他の権限が全部消えます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`permissions`](permissions.md) | 権限を変更する |
| [`perms`](perms.md) | 権限の値 |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] permissions で権限をどう変更するか（置き換え・追加・削除）を指定する
    - [x] `std::filesystem` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::filesystem::perm_options](https://cpprefjp.github.io/reference/filesystem/perm_options.html)
- [cppreference: std::filesystem::perm_options](https://en.cppreference.com/w/cpp/filesystem/perm_options)
