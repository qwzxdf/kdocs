---
title: std::filesystem::hard_link_count
summary: "ファイルのハードリンクの数を返す。"
order: 900
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::hard_link_count

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

同じ実体を指す名前（ハードリンク）がいくつあるかを返します。通常のファイルは 1 です。

!!! tip "ポイント"
    - `std::filesystem` の部品。
    - 例外を避けたいときは、`std::error_code` を渡す版を使う。
    - パスは `std::filesystem::path` で扱う。

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要と、[`path`](path.md) を先に読んでください。

## 関数の詳しい説明

### std::filesystem::hard_link_count {#hard_link_count}

```cpp
std::uintmax_t hard_link_count(const path& p);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | path | 調べるファイル |

- 戻り値: ハードリンクの数
- 計算量: OS に依存


## 実際に動かしてみる

```cpp
#include <filesystem>
#include <fstream>
#include <print>

namespace fs = std::filesystem;

int main() {
  fs::path a = fs::temp_directory_path() / "kdocs_a.txt";
  fs::path b = fs::temp_directory_path() / "kdocs_b.txt";
  std::ofstream(a) << "x";
  fs::create_hard_link(a, b);
  std::println("{}", fs::hard_link_count(a));
  fs::remove(a);
  fs::remove(b);
}
```

```text title="実行結果"
2
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 重複して保存されていないかを調べる |

## よくあるミス

??? failure "フォルダに使う"
    フォルダでは、環境によって意味が違います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`create_hard_link`](create_hard_link.md) | ハードリンクを作る |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ファイルのハードリンクの数を返す
    - [x] `std::filesystem` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::filesystem::hard_link_count](https://cpprefjp.github.io/reference/filesystem/hard_link_count.html)
- [cppreference: std::filesystem::hard_link_count](https://en.cppreference.com/w/cpp/filesystem/hard_link_count)
