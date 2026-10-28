---
title: std::filesystem::is_symlink
summary: "パスがシンボリックリンクかを調べる。"
order: 900
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::is_symlink

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

パスが、別の場所への「近道」であるシンボリックリンクなのかどうかを知りたい。ファイルをコピーするときに、リンクをたどって実体をコピーするのか、リンクそのものをコピーするのかを、決めなくてはなりません。

`std::filesystem::is_symlink` は、<strong>パスがシンボリックリンクそのもの</strong>であるかを調べます。ここが他の `is_xxx` と違う点で、リンクをたどらず、リンクの種類を見ます。

!!! tip "ポイント"
    - `is_symlink(p)` は、`p` がシンボリックリンクなら `true`。他の `is_xxx` と違い、リンクをたどらない
    - 内部では [`symlink_status`](symlink_status.md) を使う
    - リンクの先が存在しなくても、リンク自体があれば `true`
    - Windows でも使えるが、リンクを作るには権限（開発者モードなど）が要る

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要と、[`path`](path.md) を先に読んでください。

## 関数の詳しい説明

### is_symlink {#is_symlink}

<span class="ver ver-17">C++17</span>

```cpp
bool is_symlink(const path& p);
bool is_symlink(const path& p, std::error_code& ec) noexcept;
bool is_symlink(file_status s) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | 調べるパス |
| `s` | `file_status` | `symlink_status` で取得した状態 |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

`symlink_status(p).type() == file_type::symlink` と同じです。他の `is_directory` や `is_regular_file` が `status`（リンクをたどる）を使うのに対し、`is_symlink` は `symlink_status`（リンクをたどらない）を使います。

`file_status` を受け取る版には注意が必要です。`status` で得た状態を渡しても、リンクはすでにたどられた後なので、`false` になります。リンクかどうかを調べたい `file_status` は、`symlink_status` で取得します。

指し先が存在しないリンク（ぶら下がったリンク）でも、`is_symlink` は `true` です。一方 `exists` は `false` になります。この組み合わせで、リンク切れを検出できます。

## 実際に動かしてみる

```cpp
#include <filesystem>
#include <fstream>
#include <print>

int main() {
  namespace fs = std::filesystem;
  std::ofstream("plain.txt") << "x";
  fs::create_directory("folder");

  std::println("通常のファイル: {}", fs::is_symlink("plain.txt"));
  std::println("フォルダー: {}", fs::is_symlink("folder"));
  std::println("存在しない: {}", fs::is_symlink("missing"));

  // リンク切れの検出: リンクだが、先が存在しない
  fs::path p = "plain.txt";
  bool broken = fs::is_symlink(p) && !fs::exists(p);
  std::println("リンク切れ: {}", broken);
}
```

```text title="実行結果"
通常のファイル: false
フォルダー: false
存在しない: false
リンク切れ: false
```

## ゲームでの使いどころ

アセットのコピーやパッケージ作成のツールで、リンクの扱いを決めるときに使います。リンクを実体としてコピーするなら `copy_options::copy_symlinks` を指定しない（既定）、リンクのまま複製するなら指定する、と選びますが、その前に、対象にリンクが含まれるかを `is_symlink` で数えて、ログに出す使い方があります。

リンク切れの検査にも使います。`is_symlink(p) && !exists(p)` が `true` なら、指し先が消えたリンクです。

## よくあるミス

??? failure "`status` で得た `file_status` を渡して、常に `false` になる"
    `status` はリンクをたどった後の状態です。`is_symlink(file_status)` に渡すなら、`symlink_status` で取得したものにします。

??? failure "リンク切れを `exists` だけで判定する"
    リンク切れは `exists` が `false` になるだけで、「存在しない」のか「リンクが切れている」のか区別できません。`is_symlink` と組み合わせます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`symlink_status`](symlink_status.md) | リンクをたどらずに状態を取る |
| [`read_symlink`](read_symlink.md) | リンクの指し先を読む |
| [`create_symlink`](create_symlink.md) | リンクを作る |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] シンボリックリンクそのものか
    - [x] リンクをたどらない
    - [x] リンク切れは `is_symlink` かつ `!exists`

## 関連ページ

- [cpprefjp: std::filesystem::is_symlink](https://cpprefjp.github.io/reference/filesystem/is_symlink.html)
- [cppreference: std::filesystem::is_symlink](https://en.cppreference.com/w/cpp/filesystem/is_symlink)
