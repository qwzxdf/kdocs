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

`std::filesystem::create_directories` は、**途中のフォルダもまとめて作る**関数です。`saves/slot1/` のように深い場所へ保存する前に呼びます。すでにあれば何もしません。

!!! tip "ポイント"
    - すでにあってもエラーにならない（`false` を返すだけ）。
    - 1 階層だけなら [`create_directory`](create_directory.md)。

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### create_directories {#create_directories}

```cpp
bool create_directories(const path& p);
bool create_directories(const path& p, std::error_code& ec);
```

- `p` までのフォルダを、途中のものも含めて全部作ります
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

| 場面 | 書き方 |
| --- | --- |
| セーブ用のフォルダを用意する | `fs::create_directories("saves/slot1")` |

## よくあるミス

??? failure "ofstream でフォルダが作られると思う"
    `ofstream` はフォルダを作りません。先にこの関数で用意します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`create_directory`](create_directory.md) | 1 階層だけ |

## コンパイラ対応

C++17 の機能です。GCC 9 / Clang 9 / MSVC 19.14 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 途中のフォルダもまとめて作る
    - [x] すでにあってもエラーでない
    - [x] ofstream の前に呼ぶ

## 関連ページ

- [cpprefjp: std::filesystem::create_directories](https://cpprefjp.github.io/reference/filesystem/create_directories.html)
- [cppreference: std::filesystem::create_directories](https://en.cppreference.com/w/cpp/filesystem/create_directories)
