---
title: std::filesystem::relative
summary: "基準のフォルダからの、相対パスにする。"
order: 19
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::relative

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

ログに出すパスが `C:\Users\kan\Documents\MyGame\Assets\Textures\hero.png` のように長いと、読みづらい。ゲームのフォルダーからの相対パス `Assets/Textures/hero.png` なら、すぐ分かります。パックファイルに、ルートからの相対パスで名前を記録したい場面もあります。

`std::filesystem::relative` は、`p` を<strong>`base` から見た相対パス</strong>に直します。

!!! tip "ポイント"
    - `relative(p, base)` は、`base` から `p` へ行くための相対パスを返す
    - 内部で `weakly_canonical` を使う。`p` や `base` が存在しなくてもよい
    - 2 つのパスのルートが違うと（別のドライブなど）、相対パスが作れず、空のパスを返す
    - `base` を省略すると、カレント ディレクトリが基準になる

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### relative {#relative}

<span class="ver ver-17">C++17</span>

```cpp
path relative(const path& p, const path& base = current_path());
path relative(const path& p, std::error_code& ec);
path relative(const path& p, const path& base, std::error_code& ec);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | 相対パスにしたいパス |
| `base` | `const path&` | 基準になるフォルダー。省略するとカレント ディレクトリ |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

先に `p` と `base` を `weakly_canonical` で正規化し、共通の先頭部分を取り除いて、足りない分を `..` で補います。`relative("/a/b/c", "/a/d")` は `../b/c` です。

2 つのパスが同じ場所なら、`.` を返します。ルートが違って、相対パスにできないとき（Windows で `C:` と `D:`）は、<strong>空のパスを返します</strong>。この空の結果を、そのままファイルの操作に渡さないよう、`empty()` で確かめます。

ファイルシステムに問い合わせる処理を含むので、文字列の上だけで済ませたいなら、`path::lexically_relative` を使います。

## 実際に動かしてみる

```cpp
#include <filesystem>
#include <print>

int main() {
  namespace fs = std::filesystem;
  fs::path root = "/game";

  // 基準より下にあるパス
  std::println("{}", fs::relative("/game/assets/hero.png", root).generic_string());

  // 基準と別の枝にあるパス: .. で戻る
  std::println("{}", fs::relative("/game/assets/hero.png", "/game/saves").generic_string());

  // 同じ場所なら "."
  std::println("{}", fs::relative(root, root).generic_string());
}
```

```text title="実行結果"
assets/hero.png
../assets/hero.png
.
```

## ゲームでの使いどころ

ログや UI に、ゲーム フォルダーからの相対パスを出すために使います。絶対パスは長く、ユーザー名のような個人情報も含むので、画面やレポートには相対パスのほうが向いています。

パックファイル（アセットをまとめたファイル）を作るツールで、ルートからの相対パスを名前として記録するときにも使います。区切りは `generic_string()` で `/` にそろえておくと、OS が違っても同じ名前になります。

## よくあるミス

??? failure "別のドライブのパスで、空の結果を使ってしまう"
    `C:` と `D:` のように、ルートが違うと相対パスは作れず、空のパスが返ります。`empty()` を確かめるか、絶対パスのまま使う [`proximate`](proximate.md) を使います。

??? failure "`base` にファイルのパスを渡す"
    `base` はフォルダーとして扱われます。ファイルの場所を渡すと、`..` が 1 つ多い結果になります。`parent_path()` を渡します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`proximate`](proximate.md) | 相対パスにできないときは `p` をそのまま返す版 |
| `path::lexically_relative` | 文字列の上だけで処理する。ファイルシステムに問い合わせない |
| [`absolute`](absolute.md) | 逆に、絶対パスにする |

## コンパイラ対応

C++17 の機能です。GCC 9 / Clang 9 / MSVC 19.14 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `base` から見た相対パスにする
    - [x] ルートが違うと空のパスが返る
    - [x] ログや pack の名前に使う

## 関連ページ

- [cpprefjp: std::filesystem::relative](https://cpprefjp.github.io/reference/filesystem/relative.html)
- [cppreference: std::filesystem::relative](https://en.cppreference.com/w/cpp/filesystem/relative)
