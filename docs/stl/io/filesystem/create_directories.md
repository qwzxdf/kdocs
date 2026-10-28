---
title: std::filesystem::create_directories
summary: "途中のフォルダも含めて、フォルダを作る。"
order: 3
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::create_directories

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

`saves/slot1/` に保存したいのに、`saves` というフォルダがまだないと、ファイルを開くのに失敗します。フォルダを 1 階層ずつ作るコードを書くのは面倒です。`std::filesystem::create_directories` は、途中のフォルダも含めて、指定のパスまでを一度に作ってくれます。すでにあれば何もしません。

!!! tip "ポイント"
    - 途中のフォルダも含めて作る。`mkdir -p` と同じ。
    - すでにある場合は、エラーにならず `false` を返す。
    - 1 階層だけ作るなら `create_directory`。親が無いと失敗する。

!!! info "このページを読む前に"
    [`std::filesystem::path`](path.md) の書き方と、[`exists`](exists.md) を先に読んでください。

## 関数の詳しい説明

### create_directories {#create_directories}

```cpp
bool create_directories(const path& p);
bool create_directories(const path& p, std::error_code& ec);
```

`p` は作りたいフォルダのパスです。`logs/2026/10` なら、`logs`、`logs/2026`、`logs/2026/10` の 3 つを無ければ作ります。

戻り値は、新しく 1 つでもフォルダを作ったかです。`p` がすでにあったときは `false` です。`false` はエラーを意味しません。

`ec` を渡す版は、作成に失敗しても例外を投げずに `ec` へ結果を入れます。渡さない版は、権限がない、同じ名前のファイルがある、などの失敗で `filesystem_error` を投げます。

- `p` までのフォルダを途中のものも含めて全部作ります
- 戻り値: 新しく作ったら `true`、すでにあったら `false`（エラーではない）

```cpp
#include <filesystem>
#include <print>

int main() {
  namespace fs = std::filesystem;
  std::println("{}", fs::create_directories("logs/2026/10"));
  std::println("{}", fs::create_directories("logs/2026/10"));  // 2 回目は作らない
}
```

```text title="実行結果"
true
false
```

## ゲームでの使いどころ

ログやセーブデータの保存先を作るのに使います。ゲームの起動時に `fs::create_directories(save_dir)` を呼んでおけば、以降は保存先があるものとして書けます。

ユーザーごとのデータ置き場にも使います。Windows なら `%APPDATA%/ゲーム名/saves` のような深い場所です。毎回「あるか調べてから作る」と書く必要がなく、`create_directories` を呼ぶだけで済むのが利点です。

スクリーンショットの保存先を日付ごとのフォルダに分けるときにも、`screenshots/2026-10-22` を作るのに使えます。

## よくあるミス

??? failure "`create_directory` で複数階層を作ろうとする"
    `create_directory("a/b/c")` は、`a/b` が無いと失敗します。複数階層なら `create_directories` です。

??? failure "`false` をエラーと考える"
    `false` は、「新しく作ったものがなかった」という意味で、すでにあるときも返ります。失敗したかは、例外または `ec` で判断します。

??? failure "ファイルの名前までを含めたパスを渡す"
    `create_directories("saves/slot1/data.bin")` は、`data.bin` という名前のフォルダを作ってしまいます。ファイルの場所のフォルダを作るなら、`path.parent_path()` を渡します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`create_directory`](create_directory.md) | 1 階層だけ作る。親フォルダがなければ失敗する |
| [`exists`](exists.md) | あるか調べる。`create_directories` は内部で似た確認をするので、普通は不要 |
| [`remove_all`](remove_all.md) | フォルダの中身ごと消す |

## コンパイラ対応

C++17 の機能です。GCC 9 / Clang 9 / MSVC 19.14 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 途中のフォルダも含めて、パスまでを作る。
    - [x] すでにあっても失敗ではない（`false` が返るだけ）。
    - [x] ファイルのパスを渡さない。`parent_path()` を渡す。

## 関連ページ

- [cpprefjp: std::filesystem::create_directories](https://cpprefjp.github.io/reference/filesystem/create_directories.html)
- [cppreference: std::filesystem::create_directories](https://en.cppreference.com/w/cpp/filesystem/create_directories)
