---
title: std::filesystem::path
summary: "ファイルやフォルダの場所（パス）を表す型。"
order: 1
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::path

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

`std::filesystem::path` は、**ファイルやフォルダの場所（パス）を表す型**です。文字列ではなく `path` で持つと、`/` でつなげたり、ファイル名・拡張子を取り出したりできます。Windows と Linux の区切り文字の違いも吸収してくれます。

!!! tip "ポイント"
    - パスは `path` で持ち、`/` でつなぐ（`dir / "save.dat"`）。
    - `filename()` `extension()` `stem()` `parent_path()` で分解できる。
    - Windows で日本語のパスは、`u8string()` などを経由して扱う。

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### path {#path}

```cpp
class path;
```

パスを表す型です。文字列から作れて、`/` でつなげられます。区切り文字（`/` と `\`）の違いを吸収してくれます。

| メンバ | 重要度 | 何をする | `"assets/img/player.png"` の例 |
| --- | --- | --- | --- |
| `operator/` | <span class="rank rank-must">必須</span> | パスをつなげる | `fs::path("assets") / "img"` |
| `filename()` | <span class="rank rank-must">必須</span> | ファイル名 | `player.png` |
| `extension()` | <span class="rank rank-must">必須</span> | 拡張子（`.` 付き） | `.png` |
| `stem()` | <span class="rank rank-often">よく使う</span> | 拡張子なしのファイル名 | `player` |
| `parent_path()` | <span class="rank rank-often">よく使う</span> | 親フォルダ | `assets/img` |
| `string()` | <span class="rank rank-often">よく使う</span> | `std::string` に変換（OS の区切り文字） | Windows なら `\` になることも |
| `generic_string()` | <span class="rank rank-often">よく使う</span> | `/` 区切りの `std::string` | `assets/img/player.png` |
| `replace_extension(".jpg")` | <span class="rank rank-sometimes">たまに</span> | 拡張子を変える | `assets/img/player.jpg` |
| `has_extension()` など `has_*` | <span class="rank rank-sometimes">たまに</span> | その部分があるか | `true` |
| `is_absolute()` / `is_relative()` | <span class="rank rank-sometimes">たまに</span> | 絶対パスか | `false` / `true` |
| `operator+=` | <span class="rank rank-sometimes">たまに</span> | 区切りを入れずに後ろに足す | `p += ".tmp"` |
| `lexically_normal()` | <span class="rank rank-rare">知ってるだけ</span> | `a/./b/../c` を `a/c` に整える | |
| `begin()` / `end()` | <span class="rank rank-rare">知ってるだけ</span> | 区切りごとに回す | `assets`, `img`, `player.png` |
| `u8string()` | <span class="rank rank-rare">知ってるだけ</span> | UTF-8 の文字列（`std::u8string`） | |
| `native()` | <span class="rank rank-rare">知ってるだけ</span> | OS 固有の文字列（Windows は `std::wstring`） | |

```cpp
#include <filesystem>
#include <print>

int main() {
  std::filesystem::path p = "saves";
  p /= "slot1";               // saves/slot1
  p += ".dat";                // saves/slot1.dat（区切りなしで足す）
  auto backup = p;
  backup.replace_extension(".bak");
  std::println("{} {}", p.generic_string(), backup.generic_string());
  std::println("{}", std::filesystem::path("a/./b/../c").lexically_normal().generic_string());
}
```

```text title="実行結果"
saves/slot1.dat saves/slot1.bak
a/c
```

!!! warning "Windows で日本語のパス"
    Windows では、日本語を含むパスを `string()` で取り出すと文字化けや例外になることがあります。表示用には `generic_u8string()` や、Visual Studio の `/utf-8` オプションを使います。ファイルを開くときは `path` をそのまま `std::ifstream` に渡せば問題ありません。

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| アセットのパスの組み立てと分解 | `root / "textures" / name` |

## よくあるミス

??? failure "パスを文字列でつなぐ"
    `"dir" + "/" + name` は区切りを間違えがちです。`path` の `/` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::string`](../../containers/string.md) | パスは `path` で持つ |

## コンパイラ対応

C++17 の機能です。GCC 9 / Clang 9 / MSVC 19.14 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] パスは `path` で持つ
    - [x] `/` でつなぐ
    - [x] Windows の日本語に注意

## 関連ページ

- [cpprefjp: std::filesystem::path](https://cpprefjp.github.io/reference/filesystem/path.html)
- [cppreference: std::filesystem::path](https://en.cppreference.com/w/cpp/filesystem/path)
