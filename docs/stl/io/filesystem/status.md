---
title: std::filesystem::status
summary: "ファイルの種類と権限を取得する（file_status）。"
order: 25
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::status

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

パスがファイルなのかフォルダーなのか、読み取り専用なのか、それとも存在しないのか。ファイルを開く前に知りたい情報は、いくつもあります。`exists` や `is_directory` を順に呼ぶと、そのたびにファイルシステムへ問い合わせます。

`std::filesystem::status` は、<strong>1 回の問い合わせで、種類（`type`）と権限（`permissions`）をまとめて</strong>取り出して、[`file_status`](file_status.md) として返します。`exists` や `is_regular_file` も、中身はこの関数です。

!!! tip "ポイント"
    - 戻り値の `file_status` から `type()` と `permissions()` を読む
    - パスがシンボリックリンクなら、指し先の情報を返す。リンク自体を調べるなら `symlink_status`
    - パスが存在しなくても、例外にはならない。`type()` が `not_found` になる
    - 判定をいくつも書くより、`status` を 1 回呼んで使い回すほうが、問い合わせが減る

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### status {#status}

<span class="ver ver-17">C++17</span>

```cpp
file_status status(const path& p);
file_status status(const path& p, std::error_code& ec) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | 調べるパス |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

戻り値は [`file_status`](file_status.md) です。`type()` で `regular`（ふつうのファイル）、`directory`、`symlink` などの種類が、`permissions()` で読み書きの権限が分かります。

パスが存在しないときの扱いが、他の関数と違います。<strong>存在しないこと自体はエラーではなく</strong>、`type()` が `file_type::not_found` の `file_status` が返ります。例外を投げるのは、権限がなくて調べられない、パスの形式が不正、といった本当の失敗のときだけです。このため、「存在するかどうか」を例外なしで判定できます。

シンボリックリンクは、たどった先の情報を返します。リンク自体の情報が欲しいときは、[`symlink_status`](symlink_status.md) を使います。

`exists(p)`、`is_directory(p)` などは、`status(p)` の結果を調べる補助関数です。複数の種類を続けて調べるなら、`status` を一度だけ呼んで、その結果に `fs::is_directory(st)` のように渡すほうが、問い合わせの回数が減ります。

## 実際に動かしてみる

```cpp
#include <filesystem>
#include <fstream>
#include <print>

int main() {
  namespace fs = std::filesystem;
  std::ofstream("save.dat") << "data";
  fs::create_directory("saves");

  // 1 回だけ status を呼んで、結果を使い回す
  fs::file_status st = fs::status("save.dat");
  std::println("save.dat は通常のファイル: {}", fs::is_regular_file(st));
  std::println("save.dat はフォルダー: {}", fs::is_directory(st));

  std::println("saves はフォルダー: {}", fs::is_directory(fs::status("saves")));

  // 存在しなくても例外にならない
  fs::file_status none = fs::status("missing.dat");
  std::println("missing.dat は not_found: {}", none.type() == fs::file_type::not_found);
  std::println("missing.dat は存在する: {}", fs::exists(none));
}
```

```text title="実行結果"
save.dat は通常のファイル: true
save.dat はフォルダー: false
saves はフォルダー: true
missing.dat は not_found: true
missing.dat は存在する: false
```

## ゲームでの使いどころ

ファイルの読み込み前の検査に使います。設定ファイルが「ふつうのファイルとして存在するか」を確かめてから開き、なければ既定の設定を使う、という流れです。ファイルのつもりでフォルダーを開こうとして失敗する、という事故も、種類を見れば防げます。

フォルダーを走査するときは、[`directory_entry`](directory_entry.md) が情報をキャッシュしているので、毎回 `status` を呼ぶより、そちらを使うほうが軽くなります。

## よくあるミス

??? failure "リンクの指し先ではなく、リンクそのものを調べたかった"
    `status` はリンクをたどります。リンク自体の種類（`symlink`）を知りたいときは、`symlink_status` を使います。

??? failure "存在しないパスで、例外が出ると思って try を書く"
    存在しないだけなら例外は出ません。`type()` が `not_found` になるので、`exists` で判定できます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`symlink_status`](symlink_status.md) | リンクをたどらずに、リンク自体を調べる |
| [`exists`](exists.md) | `status` の結果が not_found でないかの補助関数 |
| [`file_status`](file_status.md) | この関数が返す型 |

## コンパイラ対応

C++17 の機能です。GCC 9 / Clang 9 / MSVC 19.14 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 種類と権限をまとめて取る
    - [x] 存在しなくても例外にならない
    - [x] リンクはたどる（`symlink_status` はたどらない）

## 関連ページ

- [cpprefjp: std::filesystem::status](https://cpprefjp.github.io/reference/filesystem/status.html)
- [cppreference: std::filesystem::status](https://en.cppreference.com/w/cpp/filesystem/status)
