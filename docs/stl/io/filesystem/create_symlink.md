---
title: std::filesystem::create_symlink
summary: "シンボリックリンク（別の場所を指す印）を作る。"
order: 30
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::create_symlink

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

別の場所にあるファイルを、ゲーム フォルダーの中にあるように見せたい。コピーするとディスクを使い、元との差も出ます。シンボリックリンクなら、「あのファイルの場所」という参照だけを、小さなファイルとして置けます。

`std::filesystem::create_symlink` は、<strong>ファイルを指すシンボリックリンク</strong>を作ります。

!!! tip "ポイント"
    - `create_symlink(指し先, リンクの名前)`。引数の順は、「指し先」が先
    - 指し先が存在しなくても作れる（ぶら下がったリンク）
    - フォルダーを指すリンクは、`create_directory_symlink` を使う（Windows で必要）
    - Windows では、開発者モードか管理者権限が要る

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### create_symlink {#create_symlink}

<span class="ver ver-17">C++17</span>

```cpp
void create_symlink(const path& target, const path& link);
void create_symlink(const path& target, const path& link, std::error_code& ec) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `target` | `const path&` | リンクが指す先。書いたとおりの文字列が保存される |
| `link` | `const path&` | 作るリンクの名前。すでに存在するとエラー |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

`target` が相対パスのとき、リンクを開く時点で、<strong>リンクのあるフォルダーを基準に</strong>解釈されます。作成時のカレント ディレクトリではないので、`create_symlink("data/a.txt", "link")` は、`link` の隣にある `data/a.txt` を指します。意図と違う場所にならないよう、絶対パスで作るか、リンクの位置から見た相対パスで書きます。

[`create_hard_link`](create_hard_link.md) とは違い、リンクは「名前を覚えているだけ」です。指し先を消したり、動かしたりすると、リンクは壊れます（リンク切れ）。

Windows では、シンボリックリンクを作る権限が要ります。権限がないと失敗するので、`error_code` 版を使うか、例外を処理します。

## 実際に動かしてみる

```cpp
#include <filesystem>
#include <fstream>
#include <print>
#include <system_error>

int main() {
  namespace fs = std::filesystem;
  std::ofstream("real.txt") << "x";

  std::error_code ec;
  fs::create_symlink("real.txt", "link.txt", ec);

  // 作れたか、権限がなくて作れなかったか。どちらの環境でも、結果は整合している
  std::println("結果が整合している: {}", static_cast<bool>(ec) == !fs::is_symlink("link.txt"));
}
```

```text title="実行結果"
結果が整合している: true
```

## ゲームでの使いどころ

開発環境で、共通のアセットを複数のプロジェクトから参照するときに使います。ツールが作る生成物を、ゲームから見える場所にリンクする、という構成です。

製品版の配布物には含めません。権限の問題と、ZIP などの展開でリンクが壊れる問題があるためです。

## よくあるミス

??? failure "相対パスのリンクが、意図と違う場所を指す"
    リンクのあるフォルダーを基準に解釈されます。絶対パスにするか、基準に合わせて書きます。

??? failure "フォルダーを指すのに `create_symlink` を使う"
    Windows では、フォルダー用は `create_directory_symlink` です。

??? failure "権限がなく失敗する"
    開発者モードを有効にするか、`error_code` 版で失敗を処理して、コピーで代用します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`create_directory_symlink`](create_directory_symlink.md) | フォルダーを指すリンク |
| [`create_hard_link`](create_hard_link.md) | 実体を共有する別名 |
| [`read_symlink`](read_symlink.md) | リンクの指し先を読む |

## コンパイラ対応

C++17 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ファイルを指すシンボリックリンクを作る
    - [x] 相対パスはリンクの位置が基準
    - [x] Windows は権限が必要

## 関連ページ

- [cpprefjp: std::filesystem::create_symlink](https://cpprefjp.github.io/reference/filesystem/create_symlink.html)
- [cppreference: std::filesystem::create_symlink](https://en.cppreference.com/w/cpp/filesystem/create_symlink)
