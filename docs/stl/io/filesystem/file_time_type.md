---
title: std::filesystem::file_time_type
summary: "ファイルの更新時刻を表す型。"
order: 900
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::file_time_type

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

`fs::last_write_time(p)` が返す時刻の型です。`std::chrono::time_point` の仲間で、時計は `file_clock` です。現在時刻との比較や、`clock_cast` による `system_clock` への変換ができます。

!!! tip "ポイント"
    - `std::filesystem` の部品。
    - 例外を避けたいときは、`std::error_code` を渡す版を使う。
    - パスは `std::filesystem::path` で扱う。

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要と、[`path`](path.md) を先に読んでください。

## 関数の詳しい説明

### std::filesystem::file_time_type {#file_time_type}

```cpp
using file_time_type = std::chrono::time_point<std::chrono::file_clock>;
```

- 戻り値: `time_point`
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
  fs::file_time_type t = fs::last_write_time(p);
  std::println("{}", t <= fs::file_time_type::clock::now());
  fs::remove(p);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | ファイルが新しいかを比べる |

## よくあるミス

??? failure "`system_clock` と直接比べる"
    時計が違うので比べられません。`clock_cast` で変換します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`last_write_time`](last_write_time.md) | 取得・設定する関数 |
| [`file_clock`](../../utilities/chrono/file_clock.md) | ファイルの時計 |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ファイルの更新時刻を表す型
    - [x] `std::filesystem` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::filesystem::file_time_type](https://cpprefjp.github.io/reference/filesystem/file_time_type.html)
- [cppreference: std::filesystem::file_time_type](https://en.cppreference.com/w/cpp/filesystem/file_time_type)
