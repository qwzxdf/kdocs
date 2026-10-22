---
title: std::filesystem::is_fifo
summary: "パスが名前つきパイプ（FIFO）かを調べる。"
order: 900
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::is_fifo

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

パスが名前つきパイプかを調べます。ゲームでは通常、通常のファイルとフォルダだけを扱うので、あまり使いません。リンクをたどらずに調べる場合は `symlink_status` を使います。

!!! tip "ポイント"
    - `std::filesystem` の部品。
    - 例外を避けたいときは、`std::error_code` を渡す版を使う。
    - パスは `std::filesystem::path` で扱う。

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要と、[`path`](path.md) を先に読んでください。

## 関数の詳しい説明

### std::filesystem::is_fifo {#is_fifo}

```cpp
bool is_fifo(const path& p);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | path | 調べるパス |

- 戻り値: 名前つきパイプ（FIFO）かなら `true`
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
  std::println("{}", fs::is_fifo(p));
  fs::remove(p);
}
```

```text title="実行結果"
false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 特殊なファイルを除外して処理する |

## よくあるミス

??? failure "通常のファイルで `true` を期待する"
    通常のファイルは `is_regular_file` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`status`](status.md) | 状態を取得する |
| [`is_regular_file`](is_regular_file.md) | 通常のファイルか |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] パスが名前つきパイプ（FIFO）かを調べる
    - [x] `std::filesystem` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::filesystem::is_fifo](https://cpprefjp.github.io/reference/filesystem/is_fifo.html)
- [cppreference: std::filesystem::is_fifo](https://en.cppreference.com/w/cpp/filesystem/is_fifo)
