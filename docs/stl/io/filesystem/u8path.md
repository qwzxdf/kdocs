---
title: std::filesystem::u8path
summary: "UTF-8 の文字列から path を作る（非推奨）。"
order: 900
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::u8path

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

UTF-8 の文字列から、`path` を作りたい。Windows では、`path` の内部は UTF-16 で、`const char*` の文字列は「そのときのコード ページ」で解釈されます。日本語のファイル名を UTF-8 の文字列から作ろうとすると、文字化けします。

`std::filesystem::u8path` は、<strong>UTF-8 の文字列を、文字コードを変換しながら `path` にする</strong>関数でした。ただし、C++20 から、`char8_t` の文字列を直接受け取る `path` のコンストラクターが加わり、この関数は非推奨になっています。

!!! tip "ポイント"
    - C++17 で追加され、C++20 で非推奨になった。新しいコードでは使わない
    - 代わりに、`std::u8string` や `char8_t` の文字列から `fs::path` を直接作る
    - UTF-8 の `char` 文字列を、そのコード ページ解釈のまま `path` に渡すと、Windows では文字化けする
    - ASCII だけの文字列なら、どの方法でも結果は同じ

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要と、[`path`](path.md) を先に読んでください。

## 関数の詳しい説明

### u8path {#u8path}

<span class="ver ver-17">C++17</span> <span class="ver ver-20">C++20 で非推奨</span>

```cpp
template <class Source>
path u8path(const Source& source);
template <class InputIt>
path u8path(InputIt first, InputIt last);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `source` | 文字列 | UTF-8 でエンコードされた `std::string` や `const char*` など |
| `first`, `last` | イテレータ | UTF-8 の文字の範囲 |

渡された UTF-8 の文字列を、その OS が `path` に使う形式（Windows は UTF-16、Linux は UTF-8 のまま）に変換して、`path` を返します。変換されるので、<strong>`path` を作ったあとに `.string()` で取り出すと、Windows では UTF-8 ではなく、コード ページの文字列になります</strong>。UTF-8 で取り出すには、`.u8string()` を使います。

C++20 では、`char8_t` が導入され、`path` のコンストラクターが `std::u8string` や `u8"..."` を受け取れるようになりました。これで十分なので、`u8path` は非推奨です。コンパイラが警告を出すことがあります。

## 実際に動かしてみる

```cpp
#include <filesystem>
#include <print>

int main() {
  namespace fs = std::filesystem;

  // 新しい書き方（C++20）: u8 の文字列から直接 path を作る
  fs::path p = u8"assets/hero.png";
  std::println("ファイル名: {}", p.filename().string());
  std::println("拡張子: {}", p.extension().string());

  // 日本語のファイル名も、u8 の文字列なら文字化けしない（内部では UTF-16 になる）
  fs::path jp = u8"assets/ボス.png";
  std::println("拡張子は .png: {}", jp.extension() == ".png");
}
```

```text title="実行結果"
ファイル名: hero.png
拡張子: .png
拡張子は .png: true
```

## ゲームでの使いどころ

UTF-8 でデータを持つゲーム（設定ファイルや JSON の中のアセット名を UTF-8 で書いている）が、日本語のパスを扱うときに必要になります。Windows でファイルを開く直前に、UTF-8 から `path` へ変換するのが、この関数の役割でした。

新しいコードでは、`u8"..."` のリテラルや `std::u8string` から `path` を作ります。`char` の UTF-8 文字列しか手元にない場合は、`reinterpret_cast` で `char8_t` に見せる、もしくは文字コード変換の関数を自分で用意します。文字コード全般は、[文字コード](../../../encoding/index.md)の章を参照してください。

## よくあるミス

??? failure "UTF-8 の `char` 文字列を、そのまま `path` に渡して化ける"
    `fs::path("ボス.png")` は、Windows では文字列を現在のコード ページ（日本語環境なら Shift_JIS）として解釈します。ソースを UTF-8 で保存していると、別の文字に変わります。`u8` のリテラルから作ります。

??? failure "`.string()` の結果が UTF-8 だと思い込む"
    Windows の `.string()` は、コード ページの文字列です。UTF-8 が欲しいなら `.u8string()` で取り出します。

## 類似

| 名前 | 違い |
| --- | --- |
| `path(std::u8string)` | C++20 以降の標準的な作り方 |
| [`path`](path.md) | パスの型。文字コードの扱いは、こちらも参照 |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] UTF-8 から `path` を作る関数
    - [x] C++20 では非推奨
    - [x] 新しいコードでは `u8` の文字列から直接作る

## 関連ページ

- [cpprefjp: std::filesystem::u8path](https://cpprefjp.github.io/reference/filesystem/u8path.html)
- [cppreference: std::filesystem::u8path](https://en.cppreference.com/w/cpp/filesystem/u8path)
