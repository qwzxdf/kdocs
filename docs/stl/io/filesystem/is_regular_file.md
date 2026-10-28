---
title: std::filesystem::is_regular_file
summary: "普通のファイルか調べる。"
order: 11
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::is_regular_file

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

設定ファイルを読み込む前に、「そこにあるのは、ふつうのファイルか」を確かめたい。パスがフォルダーだったり、デバイスだったり、そもそも存在しなかったりすると、読み込みに失敗します。

`std::filesystem::is_regular_file` は、<strong>パスが通常のファイル</strong>（フォルダーでも、リンクでも、デバイスでもない）であるかを調べます。ファイルを開く前の検査として、いちばんよく使う判定です。

!!! tip "ポイント"
    - `is_regular_file(p)` は、`p` が通常のファイルなら `true`
    - 存在しないパスは `false`。例外にはならない
    - リンクは先をたどって判定する。リンクがファイルを指していれば `true`
    - ファイルを開く前の検査は、`exists` よりこちら。フォルダーも `exists` は `true` になる

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### is_regular_file {#is_regular_file}

<span class="ver ver-17">C++17</span>

```cpp
bool is_regular_file(const path& p);
bool is_regular_file(const path& p, std::error_code& ec) noexcept;
bool is_regular_file(file_status s) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | 調べるパス |
| `s` | `file_status` | すでに取得した状態 |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

`status(p).type() == file_type::regular` と同じです。存在しない、フォルダー、デバイス、ソケット、パイプのとき、`false` になります。

`exists` との違いに注意します。`exists("saves")` は、フォルダーでも `true` ですが、`is_regular_file("saves")` は `false` です。ファイルを開く前の検査は、`exists` では足りません。

ファイルの存在判定に、`std::ifstream` を開いて `is_open()` を見る方法もありますが、読み取り権限がなくて開けないだけのファイルと、存在しないファイルを区別できません。`is_regular_file` なら、存在だけを調べられます。

## 実際に動かしてみる

```cpp
#include <filesystem>
#include <fstream>
#include <print>

int main() {
  namespace fs = std::filesystem;
  std::ofstream("config.ini") << "x";
  fs::create_directory("saves");

  std::println("config.ini: {}", fs::is_regular_file("config.ini"));
  std::println("saves: {}", fs::is_regular_file("saves"));
  std::println("missing.ini: {}", fs::is_regular_file("missing.ini"));

  // exists との違い: フォルダーでも true になる
  std::println("exists(saves): {}", fs::exists("saves"));
}
```

```text title="実行結果"
config.ini: true
saves: false
missing.ini: false
exists(saves): true
```

## ゲームでの使いどころ

設定ファイルやセーブ データを読み込む前の検査に使います。`is_regular_file` が `true` のときだけ開き、`false` なら既定値で起動する、と書くと、パスがフォルダーだった場合も、まとめて安全に扱えます。

フォルダーを走査して、アセットを集めるときも、`entry.is_regular_file()` で通常のファイルだけを拾います。デバイスやパイプが混ざっても、読み込みが固まりません。

## よくあるミス

??? failure "`exists` で確かめて、フォルダーを開こうとして失敗する"
    `exists` はフォルダーでも `true` です。ファイルとして開くなら、`is_regular_file` で確かめます。

??? failure "確かめた直後に、ファイルが消えて失敗する"
    確認と使用の間に状態が変わることがあります（TOCTOU）。最終的には、開く処理の失敗を処理する必要があります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`exists`](exists.md) | 種類を問わず、存在するか |
| [`is_directory`](is_directory.md) | フォルダーか |
| [`is_other`](is_other.md) | 通常のファイルでもフォルダーでもない存在するものか |

## コンパイラ対応

C++17 の機能です。GCC 9 / Clang 9 / MSVC 19.14 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 通常のファイルか
    - [x] 存在しなければ `false`
    - [x] ファイルを開く前の検査に使う

## 関連ページ

- [cpprefjp: std::filesystem::is_regular_file](https://cpprefjp.github.io/reference/filesystem/is_regular_file.html)
- [cppreference: std::filesystem::is_regular_file](https://en.cppreference.com/w/cpp/filesystem/is_regular_file)
