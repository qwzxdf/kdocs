---
title: std::filesystem::copy
summary: "ファイルやフォルダを（中身ごと）コピーする。"
order: 15
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::copy

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

ゲームのインストールや、セーブ データのバックアップで、フォルダーをまるごとコピーしたい。ファイル 1 つなら `copy_file` ですが、フォルダーの中身や、リンクの扱いまで考えると、選ぶことが多くなります。

`std::filesystem::copy` は、<strong>ファイルでもフォルダーでも、`copy_options` の指定に従ってコピー</strong>する、いちばん汎用的な関数です。

!!! tip "ポイント"
    - コピー元がファイルなら `copy_file` と同じ。フォルダーなら、既定では直下のファイルだけ
    - フォルダーの中身まで全部なら `copy_options::recursive`
    - 既存のファイルがあると、既定ではエラー。`overwrite_existing` などで動きを選ぶ
    - オプションなしでサブフォルダーを含むフォルダーをコピーすると、サブフォルダーは作られない

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### copy {#copy}

<span class="ver ver-17">C++17</span>

```cpp
void copy(const path& from, const path& to);
void copy(const path& from, const path& to, copy_options options);
void copy(const path& from, const path& to, std::error_code& ec);
void copy(const path& from, const path& to, copy_options options, std::error_code& ec);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `from` | `const path&` | コピー元のファイルまたはフォルダー |
| `to` | `const path&` | コピー先。フォルダーを指していれば、その中に入る |
| `options` | [`copy_options`](copy_options.md) | 動き方。省略すると `none` |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

`from` がふつうのファイルで、`to` がフォルダーなら、`to` の中に同じ名前でコピーされます。`to` がファイルの名前なら、その名前でコピーされます。

`from` がフォルダーのときの動きが、いちばん間違えやすい所です。<strong>オプションなしでは、そのフォルダーの直下にあるファイルだけがコピーされ、サブフォルダーは無視されます</strong>。サブフォルダーの中身まで、全部をコピーするには、`copy_options::recursive` を付けます。`directories_only` を付けると、フォルダー構造だけが作られ、ファイルはコピーされません。

コピー先に同名のファイルがあるとき、オプションなしではエラーになります。`skip_existing` なら飛ばし、`overwrite_existing` なら上書き、`update_existing` なら、コピー元のほうが新しいときだけ上書きします。この 3 つは同時に指定できません。

シンボリックリンクの扱いも、オプションで決まります。`copy_symlinks` はリンクとしてコピーし、`skip_symlinks` は無視し、どちらも付けないと、リンクの指し先をコピーします。

## 実際に動かしてみる

```cpp
#include <filesystem>
#include <fstream>
#include <print>

int main() {
  namespace fs = std::filesystem;
  fs::create_directories("src/sub");
  std::ofstream("src/a.txt") << "a";
  std::ofstream("src/sub/b.txt") << "b";

  // オプションなし: 直下のファイルだけ
  fs::copy("src", "dst1");
  std::println("dst1/a.txt: {}", fs::exists("dst1/a.txt"));
  std::println("dst1/sub: {}", fs::exists("dst1/sub"));

  // recursive: サブフォルダーの中まで
  fs::copy("src", "dst2", fs::copy_options::recursive);
  std::println("dst2/sub/b.txt: {}", fs::exists("dst2/sub/b.txt"));

  // ファイルをフォルダーの中へ
  fs::copy("src/a.txt", "dst1/sub_copy");   // 名前が新規なので、そのままの名前でコピーされる
  std::println("dst1/sub_copy: {}", fs::is_regular_file("dst1/sub_copy"));
}
```

```text title="実行結果"
dst1/a.txt: true
dst1/sub: false
dst2/sub/b.txt: true
dst1/sub_copy: true
```

## ゲームでの使いどころ

ゲームのインストーラーや、セーブ データのバックアップで、フォルダー全体をコピーするときに使います。`recursive | update_existing` を指定すると、新しくなったファイルだけを上書きする、簡易な差分更新になります。

MOD や、ユーザーのカスタム データを取り込むときは、`skip_existing` を付けて、既存のファイルを守る使い方もあります。

## よくあるミス

??? failure "フォルダーをコピーしたのに、サブフォルダーが無い"
    オプションなしでは、直下のファイルしかコピーされません。`copy_options::recursive` を付けます。

??? failure "同名のファイルがあって、エラーになる"
    既定では上書きしません。`overwrite_existing`、`skip_existing`、`update_existing` から選びます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`copy_file`](copy_file.md) | ファイル 1 つだけをコピーする。動きが単純 |
| [`copy_options`](copy_options.md) | この関数の動きを決めるフラグ |
| [`copy_symlink`](copy_symlink.md) | シンボリックリンクだけをコピーする |

## コンパイラ対応

C++17 の機能です。GCC 9 / Clang 9 / MSVC 19.14 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ファイルもフォルダーもコピーする
    - [x] フォルダーの中身まで全部なら `recursive`
    - [x] 既存のファイルの扱いは `copy_options` で決める

## 関連ページ

- [cpprefjp: std::filesystem::copy](https://cpprefjp.github.io/reference/filesystem/copy.html)
- [cppreference: std::filesystem::copy](https://en.cppreference.com/w/cpp/filesystem/copy)
