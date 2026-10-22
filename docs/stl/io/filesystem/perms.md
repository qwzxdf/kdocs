---
title: std::filesystem::perms
summary: "ファイルの権限（読み・書き・実行）を表すビットマスク型。"
order: 900
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::perms

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

`owner_read`・`owner_write`・`owner_exec` のように、所有者・グループ・その他に対する権限を、ビットで表します。`|` でつなぎ、`&` で調べます。Windows では、読み取り専用かどうかだけが反映されます。

!!! tip "ポイント"
    - `std::filesystem` の部品。
    - 例外を避けたいときは、`std::error_code` を渡す版を使う。
    - パスは `std::filesystem::path` で扱う。

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要と、[`path`](path.md) を先に読んでください。

## 関数の詳しい説明

### std::filesystem::perms {#perms}

```cpp
enum class perms : unsigned {
  none = 0,
  owner_read = 0400, owner_write = 0200, owner_exec = 0100, owner_all = 0700,
  group_read = 040, others_read = 04, all = 0777, /* ... */
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
  auto perm = fs::status(p).permissions();
  std::println("{}", (perm & fs::perms::owner_read) != fs::perms::none);
  fs::remove(p);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | ファイルが読み取り専用かを調べる |

## よくあるミス

??? failure "`&` の結果を `bool` として使う"
    `enum class` なので `bool` に変換できません。`!= fs::perms::none` と比べます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`permissions`](permissions.md) | 権限を変更する |
| [`perm_options`](perm_options.md) | 変更の方法 |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ファイルの権限（読み・書き・実行）を表すビットマスク型
    - [x] `std::filesystem` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::filesystem::perms](https://cpprefjp.github.io/reference/filesystem/perms.html)
- [cppreference: std::filesystem::perms](https://en.cppreference.com/w/cpp/filesystem/perms)
