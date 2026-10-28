---
title: std::filesystem::create_symlink
summary: "シンボリックリンク（別の場所を指す印）を作る。"
order: 30
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::create_symlink

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

`std::filesystem::create_symlink` は、**別のファイルやフォルダを指す「シンボリックリンク」を作る**関数です。アセットフォルダを複数の場所から共有する、といった開発用の仕組みで使います。**Windows では管理者権限か開発者モードが必要**なことがあります。

!!! tip "ポイント"
    - `create_symlink(指す先, リンクの場所)` の順。
    - フォルダを指すときは `create_directory_symlink`。
    - Windows では権限が要る。ゲームの実行時には使わず、ビルドツール向け。

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::filesystem::create_symlink {#create_symlink}

```cpp
void create_symlink(const path& target, const path& link);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `target` | `const path&` | リンクが指す先 |
| `link` | `const path&` | 作るリンクの場所 |

- 戻り値: なし（失敗は例外）
- 計算量: O(1)

```cpp
#include <filesystem>
#include <print>
#include <system_error>

int main() {
  namespace fs = std::filesystem;
  std::error_code ec;   // 権限が無い環境でも、例外を出さずに結果を調べる
  fs::create_symlink("assets", "assets_link", ec);
  std::println("{}", ec ? "作れなかった（権限がない）" : "作れた");   // 権限が無い環境では前者
  fs::remove("assets_link", ec);
}
```

```text title="実行結果（開発者モードが有効な Windows など、権限があるとき）"
作れた
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 開発用にアセットフォルダを共有する | `create_directory_symlink` |

## よくあるミス

??? failure "権限が無くて例外"
    `error_code` 版で結果を確認します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`copy`](copy.md) | リンクでなくコピー |
| [`status`](status.md) | `symlink_status` でリンクそのものを調べる |

## コンパイラ対応

C++17 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 別の場所を指すリンクを作る
    - [x] Windows は権限が要る
    - [x] 開発ツール向け

## 関連ページ

- [cpprefjp: std::filesystem::create_symlink](https://cpprefjp.github.io/reference/filesystem/create_symlink.html)
- [cppreference: std::filesystem::create_symlink](https://en.cppreference.com/w/cpp/filesystem/create_symlink)
