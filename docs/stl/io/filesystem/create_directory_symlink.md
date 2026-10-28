---
title: std::filesystem::create_directory_symlink
summary: "フォルダへのシンボリックリンクを作る。"
order: 900
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::create_directory_symlink

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

フォルダーを、別の場所にあるように見せたい。たとえば、巨大なアセット フォルダーをディスクの別の場所に置いて、ゲーム フォルダーの `assets` という名前から指したい。このとき使うのが、フォルダーへのシンボリックリンクです。

`std::filesystem::create_directory_symlink` は、<strong>フォルダーを指すシンボリックリンク</strong>を作ります。[`create_symlink`](create_symlink.md) と同じ働きですが、Windows ではファイル用とフォルダー用が別の種類なので、フォルダーを指すときは、こちらを使います。

!!! tip "ポイント"
    - フォルダーを指すリンクを作る専用の関数。POSIX では `create_symlink` と同じ動き
    - Windows ではフォルダー用のリンクとファイル用のリンクが区別され、種類を間違えるとリンクが機能しない
    - Windows では、リンクを作る権限（開発者モードなど）が必要
    - 引数の順番は、「指し先、リンクの名前」

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要と、[`path`](path.md) を先に読んでください。

## 関数の詳しい説明

### create_directory_symlink {#create_directory_symlink}

<span class="ver ver-17">C++17</span>

```cpp
void create_directory_symlink(const path& target, const path& link);
void create_directory_symlink(const path& target, const path& link, std::error_code& ec) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `target` | `const path&` | 指し先のフォルダー |
| `link` | `const path&` | 作るリンクの名前。すでに存在するとエラー |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

Windows の NTFS では、シンボリックリンクにファイル用とフォルダー用の 2 種類があります。指し先がフォルダーなのにファイル用のリンクを作ると、`cd` や、フォルダーとして開く操作が失敗します。そのため、フォルダーを指すときは、`create_symlink` ではなく、この関数を使います。

`target` は、書いたとおりの文字列がリンクに保存されます。相対パスなら、リンクのあるフォルダーから見た位置として解釈されます。実在しなくても作れます。

Windows 10 以降は、「開発者モード」を有効にするか、管理者として実行しているときに、作れます。権限がないと失敗するので、`error_code` 版で調べるか、例外を処理します。

## 実際に動かしてみる

```cpp
#include <filesystem>
#include <print>
#include <system_error>

int main() {
  namespace fs = std::filesystem;
  fs::create_directory("real_assets");

  std::error_code ec;
  fs::create_directory_symlink("real_assets", "assets", ec);

  // 作れたか、権限がなくて作れなかったか。どちらの環境でも、結果は整合している
  std::println("結果が整合している: {}", static_cast<bool>(ec) == !fs::is_symlink("assets"));
}
```

```text title="実行結果"
結果が整合している: true
```

## ゲームでの使いどころ

ゲームの開発環境で、巨大なアセット フォルダーを別のドライブに置き、プロジェクトからは同じ名前で見せる、という構成に使います。ビルド システムが、プロジェクト フォルダーにリンクを作る処理を持つことがあります。

製品版の配布物に、シンボリックリンクを含めることは、あまりしません。権限の問題があり、Windows では ZIP の展開などでリンクが壊れることがあるためです。

## よくあるミス

??? failure "フォルダーを指すのに `create_symlink` を使い、Windows で開けないリンクになる"
    フォルダーへのリンクには、この関数を使います。

??? failure "権限がなくて失敗する"
    Windows では、開発者モードを有効にするか、管理者権限が必要です。`error_code` 版を使い、失敗したらコピーで代用する、といった逃げ道を用意します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`create_symlink`](create_symlink.md) | ファイルを指すシンボリックリンク |
| [`create_hard_link`](create_hard_link.md) | ファイルの実体を共有する別名 |
| [`read_symlink`](read_symlink.md) | リンクの指し先を読む |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] フォルダーを指すシンボリックリンクを作る
    - [x] Windows ではファイル用と区別される
    - [x] 権限が必要なことがある

## 関連ページ

- [cpprefjp: std::filesystem::create_directory_symlink](https://cpprefjp.github.io/reference/filesystem/create_directory_symlink.html)
- [cppreference: std::filesystem::create_directory_symlink](https://en.cppreference.com/w/cpp/filesystem/create_directory_symlink)
