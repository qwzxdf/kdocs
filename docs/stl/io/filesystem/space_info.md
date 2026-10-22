---
title: std::filesystem::space_info
summary: "ディスクの容量と空き容量を持つ構造体。"
order: 900
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::space_info

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

`fs::space(p)` が返す構造体です。`capacity`（全体の容量）・`free`（空き容量）・`available`（このプロセスが使える空き容量）をバイト数でもちます。セーブ前に空き容量を確認するときに使います。

!!! tip "ポイント"
    - `std::filesystem` の部品。
    - 例外を避けたいときは、`std::error_code` を渡す版を使う。
    - パスは `std::filesystem::path` で扱う。

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要と、[`path`](path.md) を先に読んでください。

## 関数の詳しい説明

### std::filesystem::space_info {#space_info}

```cpp
struct space_info {
  std::uintmax_t capacity;
  std::uintmax_t free;
  std::uintmax_t available;
};
```

- 戻り値: `capacity`・`free`・`available`
- 計算量: OS に依存


## 実際に動かしてみる

```cpp
#include <filesystem>
#include <fstream>
#include <print>

namespace fs = std::filesystem;

int main() {
  fs::space_info si = fs::space(fs::current_path());
  std::println("{}", si.capacity >= si.available);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | セーブの前に、空き容量を確かめる |

## よくあるミス

??? failure "`free` を使える量と思う"
    このプロセスが使えるのは `available` です。`free` は権限の制限を含みません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`space`](space.md) | 取得する関数 |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ディスクの容量と空き容量を持つ構造体
    - [x] `std::filesystem` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::filesystem::space_info](https://cpprefjp.github.io/reference/filesystem/space_info.html)
- [cppreference: std::filesystem::space_info](https://en.cppreference.com/w/cpp/filesystem/space_info)
