---
title: std::filesystem::file_status
summary: "ファイルの種類と権限を持つクラス。"
order: 900
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::file_status

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

`fs::status(p)` が返すのが `file_status` です。`type()` でファイルの種類（通常ファイル・フォルダなど）、`permissions()` で権限を取れます。

!!! tip "ポイント"
    - `std::filesystem` の部品。
    - 例外を避けたいときは、`std::error_code` を渡す版を使う。
    - パスは `std::filesystem::path` で扱う。

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要と、[`path`](path.md) を先に読んでください。

## 関数の詳しい説明

### std::filesystem::file_status {#file_status}

```cpp
class file_status {
 public:
  file_type type() const noexcept;
  perms permissions() const noexcept;
};
```

- 戻り値: `type()` と `permissions()`
- 計算量: OS に依存


## 実際に動かしてみる

```cpp
#include <filesystem>
#include <fstream>
#include <print>

namespace fs = std::filesystem;

int main() {
  fs::file_status st = fs::status(fs::current_path());
  std::println("{}", st.type() == fs::file_type::directory);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | ファイルの種類で処理を分ける |

## よくあるミス

??? failure "存在しないパスで `type()` を見る"
    存在しないと `file_type::not_found` になります。例外にはなりません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`status`](status.md) | 取得する関数 |
| [`perms`](perms.md) | 権限 |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ファイルの種類と権限を持つクラス
    - [x] `std::filesystem` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::filesystem::file_status](https://cpprefjp.github.io/reference/filesystem/file_status.html)
- [cppreference: std::filesystem::file_status](https://en.cppreference.com/w/cpp/filesystem/file_status)
