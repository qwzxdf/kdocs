---
title: std::filesystem::exists
summary: "ファイルやフォルダがあるか調べる。"
order: 2
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::exists

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

`std::filesystem::exists` は、**そのパスにファイルかフォルダがあるか**を調べる関数です。設定ファイルがなければデフォルトを使う、といった分岐に使います。

!!! tip "ポイント"
    - 例外を避けたいときは `std::error_code` を渡す版。
    - ファイルかフォルダかは区別しない（区別は `is_regular_file` / `is_directory`）。

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### exists {#exists}

```cpp
bool exists(const path& p);
bool exists(const path& p, std::error_code& ec) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | 調べるパス |
| `ec` | `std::error_code&` | 失敗したときにエラーが入る（例外を投げない版） |

- 戻り値: ファイルかフォルダがあれば `true`

```cpp
#include <filesystem>
#include <print>

int main() {
  namespace fs = std::filesystem;
  if (!fs::exists("config.json")) {
    std::println("設定ファイルが無いのでデフォルトを使う");
  }
}
```

```text title="実行結果"
設定ファイルが無いのでデフォルトを使う
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 設定ファイルの有無で分岐 | `if (!fs::exists(path))` |

## よくあるミス

??? failure "調べた直後に消される"
    調べてから使うまでの間に、別のプロセスが消すことがあります。開く処理の成功で確かめるのが確実です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_regular_file`](is_regular_file.md) | ファイルか |
| [`is_directory`](is_directory.md) | フォルダか |

## コンパイラ対応

C++17 の機能です。GCC 9 / Clang 9 / MSVC 19.14 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] あるかを調べる
    - [x] ファイルかフォルダかは区別しない
    - [x] error_code 版は例外なし

## 関連ページ

- [cpprefjp: std::filesystem::exists](https://cpprefjp.github.io/reference/filesystem/exists.html)
- [cppreference: std::filesystem::exists](https://en.cppreference.com/w/cpp/filesystem/exists)
