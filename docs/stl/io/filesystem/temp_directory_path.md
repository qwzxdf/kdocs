---
title: std::filesystem::temp_directory_path
summary: "一時ファイル用のフォルダの場所を返す。"
order: 20
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::temp_directory_path

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

`std::filesystem::temp_directory_path` は、**OS が用意する一時ファイル用のフォルダ**を返す関数です。ダウンロード中のファイルや、一時的な作業ファイルの置き場所に使います。

!!! tip "ポイント"
    - Windows では `%TEMP%`、Linux では `/tmp`。
    - ファイル名は他と重ならないものにする。

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### temp_directory_path {#temp_directory_path}

```cpp
path temp_directory_path();
```

- OS の一時フォルダの場所を返します

## 実際に動かしてみる

```cpp
#include <filesystem>
#include <print>

int main() {
  namespace fs = std::filesystem;
  std::println("{}", fs::exists(fs::temp_directory_path()));
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ダウンロードの途中経過を置く | `fs::temp_directory_path() / "dl.tmp"` |

## よくあるミス

??? failure "固定のファイル名を使う"
    複数起動で衝突します。プロセス ID や乱数を混ぜます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`create_directories`](create_directories.md) | 作業フォルダを作る |

## コンパイラ対応

C++17 の機能です。GCC 9 / Clang 9 / MSVC 19.14 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 一時ファイルのフォルダ
    - [x] OS 任せ
    - [x] 名前は衝突させない

## 関連ページ

- [cpprefjp: std::filesystem::temp_directory_path](https://cpprefjp.github.io/reference/filesystem/temp_directory_path.html)
- [cppreference: std::filesystem::temp_directory_path](https://en.cppreference.com/w/cpp/filesystem/temp_directory_path)
