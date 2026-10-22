---
title: std::filesystem::status_known
summary: "ファイルの状態を取得できたかを調べる。"
order: 900
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::status_known

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

`fs::status(p)` が返す `file_status` が、「状態を取得できた」ものかを調べます。`type() == file_type::none` なら取得できていません。

!!! tip "ポイント"
    - `std::filesystem` の部品。
    - 例外を避けたいときは、`std::error_code` を渡す版を使う。
    - パスは `std::filesystem::path` で扱う。

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要と、[`path`](path.md) を先に読んでください。

## 関数の詳しい説明

### std::filesystem::status_known {#status_known}

```cpp
bool status_known(file_status s) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `s` | file_status | 調べる状態 |

- 戻り値: 取得できていれば `true`
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
  std::println("{}", fs::status_known(fs::status(p)));
  fs::remove(p);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 状態の取得の失敗を検出する |

## よくあるミス

??? failure "存在しないことを「不明」と思う"
    存在しないのは `not_found` という確定した状態で、`status_known` は `true` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`status`](status.md) | 状態を取得する |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ファイルの状態を取得できたかを調べる
    - [x] `std::filesystem` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::filesystem::status_known](https://cpprefjp.github.io/reference/filesystem/status_known.html)
- [cppreference: std::filesystem::status_known](https://en.cppreference.com/w/cpp/filesystem/status_known)
