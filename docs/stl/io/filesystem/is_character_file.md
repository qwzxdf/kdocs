---
title: std::filesystem::is_character_file
summary: "パスがキャラクタデバイスかを調べる。"
order: 900
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::is_character_file

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

Unix 系の OS では、キーボード、端末、乱数の発生源（`/dev/urandom`）なども、ファイルの名前で扱います。これらは、ディスクと違って、バイトが 1 つずつ流れてくる「文字デバイス」です。

`std::filesystem::is_character_file` は、<strong>パスが文字デバイスか</strong>を調べます。

!!! tip "ポイント"
    - `is_character_file(p)` は、`p` が文字デバイスなら `true`
    - `/dev/null`、`/dev/urandom`、`/dev/tty` などが該当する
    - Windows では、`NUL` や `CON` といった特別な名前があるが、ふつう `false` になる
    - 存在しないパスは `false`。リンクは先をたどって判定する

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要と、[`path`](path.md) を先に読んでください。

## 関数の詳しい説明

### is_character_file {#is_character_file}

<span class="ver ver-17">C++17</span>

```cpp
bool is_character_file(const path& p);
bool is_character_file(const path& p, std::error_code& ec) noexcept;
bool is_character_file(file_status s) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | 調べるパス |
| `s` | `file_status` | すでに取得した状態 |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

`status(p).type() == file_type::character` と同じ判定です。文字デバイスは、サイズの概念がなく、読み込みが終わらないこともあります。`/dev/urandom` は、永遠にデータが出てきます。

そのため、ファイルを丸ごと読み込む処理（`ifstream` で最後まで読む）を、文字デバイスに行うと、終わらなくなります。ユーザーの指定したパスを読み込む前に、この種類を除外します。

## 実際に動かしてみる

```cpp
#include <filesystem>
#include <fstream>
#include <print>

int main() {
  namespace fs = std::filesystem;
  std::ofstream("plain.txt") << "x";

  std::println("通常のファイル: {}", fs::is_character_file("plain.txt"));
  std::println("カレント ディレクトリ: {}", fs::is_character_file("."));
}
```

```text title="実行結果"
通常のファイル: false
カレント ディレクトリ: false
```

## ゲームでの使いどころ

設定ファイルや MOD のファイルを読み込む前の検査で使います。ユーザーが `/dev/zero` のようなパスを指定すると、全部を読み込もうとして終わらなくなるので、`is_regular_file` が `true` のものだけを対象にします。その除外に、この関数は直接は要らず、`is_regular_file` で足ります。

文字デバイスと分かった上で、読み込み方を変えたい特殊なツール（端末の入力を扱うものなど）だけが、直接使います。

## よくあるミス

??? failure "文字デバイスを丸ごと読み込もうとして、終わらなくなる"
    `/dev/urandom` や `/dev/zero` は、読み続けても終わりません。サイズが不明なファイルは、読み込む量の上限を決めます。

??? failure "Windows の `NUL` や `CON` で `true` を期待する"
    これらは Win32 の特別な名前で、`std::filesystem` からは通常のファイルとして見える、または存在しないように見えるなど、環境で変わります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_block_file`](is_block_file.md) | ブロック デバイスか |
| [`is_regular_file`](is_regular_file.md) | 通常のファイルか |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 文字デバイスか
    - [x] 読み込みが終わらないことがある
    - [x] ユーザーの入力したパスは `is_regular_file` で絞る

## 関連ページ

- [cpprefjp: std::filesystem::is_character_file](https://cpprefjp.github.io/reference/filesystem/is_character_file.html)
- [cppreference: std::filesystem::is_character_file](https://en.cppreference.com/w/cpp/filesystem/is_character_file)
