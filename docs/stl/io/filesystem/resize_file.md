---
title: std::filesystem::resize_file
summary: "ファイルの大きさを変える（切り詰め・拡張）。"
order: 24
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::resize_file

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

`std::filesystem::resize_file` は、**ファイルの大きさを指定したバイト数にする**関数です。短くすると切り詰め、長くすると 0 で埋めます。

!!! tip "ポイント"
    - 長くした部分は 0 で埋まる。
    - 開いているファイルには使わない。

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### resize_file {#resize_file}

```cpp
void resize_file(const path& p, std::uintmax_t new_size);
```

- ファイルの大きさを変えます（足りない分は 0 で埋まる）

## 実際に動かしてみる

```cpp
#include <filesystem>
#include <fstream>
#include <print>

int main() {
  namespace fs = std::filesystem;
  std::ofstream("rs_demo.bin") << "0123456789";
  fs::resize_file("rs_demo.bin", 4);
  std::println("{}", fs::file_size("rs_demo.bin"));
  fs::remove("rs_demo.bin");
}
```

```text title="実行結果"
4
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ログファイルを一定の大きさに切り詰める | `fs::resize_file(path, limit)` |

## よくあるミス

??? failure "開いたまま呼ぶ"
    環境によって失敗します。閉じてから呼びます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`file_size`](file_size.md) | 今の大きさ |

## コンパイラ対応

C++17 の機能です。GCC 9 / Clang 9 / MSVC 19.14 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ファイルの大きさを変える
    - [x] 長くすると 0 で埋まる
    - [x] 閉じてから呼ぶ

## 関連ページ

- [cpprefjp: std::filesystem::resize_file](https://cpprefjp.github.io/reference/filesystem/resize_file.html)
- [cppreference: std::filesystem::resize_file](https://en.cppreference.com/w/cpp/filesystem/resize_file)
