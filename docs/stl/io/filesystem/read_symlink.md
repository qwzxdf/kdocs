---
title: std::filesystem::read_symlink
summary: "シンボリックリンクが指すパスを返す。"
order: 900
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::read_symlink

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

シンボリックリンクは、別のパスを指すだけの小さなファイルです。`status` や `canonical` はリンクの先まで追いかけますが、「リンクが、どこを指すように書かれているか」を知りたいことがあります。

`std::filesystem::read_symlink` は、<strong>シンボリックリンクに書かれている指し先のパス</strong>を、そのまま返します。先を追いかけず、存在するかも調べません。

!!! tip "ポイント"
    - リンクが指す先のパスを、書かれているとおりに返す（相対パスなら相対のまま）
    - 引数がシンボリックリンクでないとエラーになる
    - 指し先が存在していなくても、取り出せる
    - Windows では、シンボリックリンクを作る権限（開発者モードなど）が要る

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要と、[`path`](path.md) を先に読んでください。

## 関数の詳しい説明

### read_symlink {#read_symlink}

<span class="ver ver-17">C++17</span>

```cpp
path read_symlink(const path& p);
path read_symlink(const path& p, std::error_code& ec);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | シンボリックリンクのパス |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

戻り値は、リンクの中身（ターゲット）のパスです。作成時に相対パスを指定していれば、相対パスのまま返ります。実際に開くときは、リンクのあるフォルダーを基準に解決されるので、必要なら `canonical` を組み合わせます。

引数がシンボリックリンクでないとき（通常のファイル、フォルダー、存在しないパス）は、エラーです。リンクかどうかを先に調べるなら、[`is_symlink`](is_symlink.md) を使います。

[`canonical`](canonical.md) は、最終的な本当の場所を返しますが、`read_symlink` は、リンク 1 段分の内容を返すだけです。リンクが別のリンクを指していても、1 段しかたどりません。

## 実際に動かしてみる

```cpp
#include <filesystem>
#include <fstream>
#include <print>
#include <system_error>

int main() {
  namespace fs = std::filesystem;
  std::ofstream("plain.txt") << "x";

  // シンボリックリンクではないものに使うと、エラーになる
  std::error_code ec;
  fs::path target = fs::read_symlink("plain.txt", ec);
  std::println("結果が空: {}", target.empty());
  std::println("エラー: {}", static_cast<bool>(ec));
  std::println("リンクか: {}", fs::is_symlink("plain.txt"));
}
```

```text title="実行結果"
結果が空: true
エラー: true
リンクか: false
```

## ゲームでの使いどころ

リンクの張り直しや、ツールでのリンク切れの検査に使います。リンクが指している先の文字列を取り出して、その先が存在するかを調べる、という流れです。

ゲームの実行中に使うことはほとんどありません。Linux や macOS 向けのビルドで、共有ライブラリのバージョン リンク（`libfoo.so` → `libfoo.so.1.2`）を調べるツールを書くときなどに現れます。

## よくあるミス

??? failure "リンクではないパスに使ってエラーになる"
    通常のファイルやフォルダーでは失敗します。`is_symlink` で確かめてから呼びます。

??? failure "戻り値を、そのまま開けると思う"
    相対パスで作られたリンクは、戻り値が相対パスのままです。現在のフォルダーからではなく、リンクのあるフォルダーを基準に解釈します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`create_symlink`](create_symlink.md) | シンボリックリンクを作る |
| [`is_symlink`](is_symlink.md) | リンクかどうかを調べる |
| [`canonical`](canonical.md) | 最終的な実体の絶対パスを返す |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] リンクが指す先を返す
    - [x] リンクでないとエラー
    - [x] 1 段分だけ読む

## 関連ページ

- [cpprefjp: std::filesystem::read_symlink](https://cpprefjp.github.io/reference/filesystem/read_symlink.html)
- [cppreference: std::filesystem::read_symlink](https://en.cppreference.com/w/cpp/filesystem/read_symlink)
