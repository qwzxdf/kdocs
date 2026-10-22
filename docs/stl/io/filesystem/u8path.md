---
title: std::filesystem::u8path
summary: "UTF-8 の文字列から path を作る（非推奨）。"
order: 900
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::u8path

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

UTF-8 の文字列を、`path` に変換します。C++20 以降は、`char8_t` の文字列を `path` のコンストラクタに直接渡せるので、`u8path` は非推奨になりました。

!!! tip "ポイント"
    - `std::filesystem` の部品。
    - 例外を避けたいときは、`std::error_code` を渡す版を使う。
    - パスは `std::filesystem::path` で扱う。

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要と、[`path`](path.md) を先に読んでください。

## 関数の詳しい説明

### std::filesystem::u8path {#u8path}

```cpp
path u8path(const std::string& source);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `source` | string | UTF-8 の文字列 |

- 戻り値: `path`
- 計算量: OS に依存


## 実際に動かしてみる

```cpp
#include <filesystem>
#include <print>

namespace fs = std::filesystem;

int main() {
  std::println("{}", fs::u8path("dir/file.txt").filename().generic_string());
}
```

```text title="実行結果"
file.txt
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | UTF-8 の文字列からパスを作る（古いコード） |

## よくあるミス

??? failure "新しいコードで使う"
    C++20 以降は `fs::path(u8"...")` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`path`](path.md) | パスの型 |
| [文字コード](../../../encoding/index.md) | UTF-8 の扱い |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] UTF-8 の文字列から path を作る（非推奨）
    - [x] `std::filesystem` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::filesystem::u8path](https://cpprefjp.github.io/reference/filesystem/u8path.html)
- [cppreference: std::filesystem::u8path](https://en.cppreference.com/w/cpp/filesystem/u8path)
