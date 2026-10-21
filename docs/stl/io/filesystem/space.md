---
title: std::filesystem::space
summary: "ディスクの空き容量を取得する。"
order: 23
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::space

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

`std::filesystem::space` は、**パスがあるドライブの容量・空き容量**を返す関数です。セーブの前に空きを確認する、といった使い方をします。

!!! tip "ポイント"
    - 戻り値は `capacity`（全体）、`free`（空き）、`available`（使える分）。
    - 単位はバイト。

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### space {#space}

```cpp
space_info space(const path& p);
```

- `capacity`（全体）、`free`（空き）、`available`（使える空き）をバイトで返します。セーブ前に容量を確かめるのに使えます

## 実際に動かしてみる

```cpp
#include <filesystem>
#include <print>

int main() {
  namespace fs = std::filesystem;
  std::println("{}", fs::space(".").capacity > 0);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| セーブ前に空き容量を確認する | `fs::space(dir).available` |

## よくあるミス

??? failure "単位を取り違える"
    バイトです。MB にするなら 1024 × 1024 で割ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`file_size`](file_size.md) | ファイルの大きさ |

## コンパイラ対応

C++17 の機能です。GCC 9 / Clang 9 / MSVC 19.14 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ドライブの容量と空き
    - [x] 単位はバイト
    - [x] セーブ前の確認に

## 関連ページ

- [cpprefjp: std::filesystem::space](https://cpprefjp.github.io/reference/filesystem/space.html)
- [cppreference: std::filesystem::space](https://en.cppreference.com/w/cpp/filesystem/space)
