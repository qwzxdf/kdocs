---
title: std::filesystem::permissions
summary: "ファイルの権限（読み書きの許可）を取得・変更する。"
order: 26
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::permissions

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

`std::filesystem::permissions` は、**ファイルの権限（所有者や他人の読み・書き・実行）を変更する**関数です。Windows では、読み取り専用かだけが反映されます。

!!! tip "ポイント"
    - `perms::owner_write` などを組み合わせる。
    - Windows では限定的。

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### permissions {#permissions}

```cpp
void permissions(const path& p, perms prms, perm_options opts = perm_options::replace);
```

- 読み書き・実行の権限を変えます。ゲームではほぼ使いません

## 実際に動かしてみる

```cpp
#include <filesystem>
#include <fstream>
#include <print>

int main() {
  namespace fs = std::filesystem;
  std::ofstream("perm_demo.txt") << "x";
  fs::permissions("perm_demo.txt", fs::perms::owner_write, fs::perm_options::remove);
  std::println("{}", (fs::status("perm_demo.txt").permissions() & fs::perms::owner_write) == fs::perms::none);
  fs::permissions("perm_demo.txt", fs::perms::owner_write, fs::perm_options::add);  // 消せるように戻す
  fs::remove("perm_demo.txt");
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| セーブデータを読み取り専用にする | `fs::permissions(p, fs::perms::owner_write, fs::perm_options::remove)` |

## よくあるミス

??? failure "Windows で細かい権限を期待する"
    読み取り専用の有無しか反映されません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`status`](status.md) | 権限を取得する |

## コンパイラ対応

C++17 の機能です。GCC 9 / Clang 9 / MSVC 19.14 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 権限を変更する
    - [x] Windows では限定的
    - [x] perms を組み合わせる

## 関連ページ

- [cpprefjp: std::filesystem::permissions](https://cpprefjp.github.io/reference/filesystem/permissions.html)
- [cppreference: std::filesystem::permissions](https://en.cppreference.com/w/cpp/filesystem/permissions)
