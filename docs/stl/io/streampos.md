---
title: std::streampos
summary: "ストリーム上の位置を表す型。"
order: 900
tags:
  - 入出力・文字列
---

# std::streampos

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <ios>`
</div>

ファイルを途中まで読んで、「ここまで読んだ」と覚えておき、あとで戻ってやり直したい。その「位置」を持つための型が `std::streampos` です。`tellg()` が返し、`seekg()` に渡すと、その位置に戻れます。

!!! tip "ポイント"
    - ストリーム上の位置を覚えておくための型。`tellg()` / `tellp()` の戻り値
    - `seekg(pos)` に渡して、覚えた位置に戻る
    - 位置どうしを引き算すると、`streamoff`（位置のずれ）になる
    - 中身は実装定義。数値として扱いたいときは、`streamoff` に変換する

!!! info "このページを読む前に"
    [`std::ios_base`](ios_base.md) を先に読んでください。

## 関数の詳しい説明

### std::streampos {#streampos}

```cpp
using streampos = std::fpos<std::mbstate_t>;
```

`<ios>` で定義される、`std::fpos<std::mbstate_t>` の別名です。`fpos` は、位置の数値（`streamoff`）と、マルチバイト文字の変換の途中状態（`mbstate_t`）をまとめて持つクラスです。

状態も持つのは、文字コードの変換が必要なストリームで、位置だけでは元の状態に戻れないことがあるからです。そのため、`tellg()` が返した値は、そのまま `seekg()` に渡すのが原則で、勝手に数値を作って渡すと、正しく戻れないことがあります。

## 実際に動かしてみる

```cpp
#include <ios>
#include <print>
#include <sstream>
#include <string>

int main() {
  std::istringstream in("0123456789\nabc\n");

  // 位置を覚えて、あとで戻る
  in.seekg(4);
  std::streampos here = in.tellg();
  std::string line;
  std::getline(in, line);
  std::println("読んだ行: {}", line);

  in.seekg(here);
  std::getline(in, line);
  std::println("戻って読み直し: {}", line);
}
```

```text title="実行結果"
読んだ行: 456789
戻って読み直し: 456789
```

`tellg()` で覚えた位置 `here` に `seekg(here)` で戻ると、同じ行を読み直せます。

## ゲームでの使いどころ

パーサーで、先を少し読んでみて、合わなければ戻る（先読みとやり直し）ときです。設定ファイルの行が、数値で始まるのか、文字列で始まるのかを見分けるために、位置を覚えて、読んでから戻る、といった使い方です。

ファイル全体を扱うときは、位置を数値で持つ必要はありません。`streampos` のまま、`tellg()` と `seekg()` だけで足ります。

## よくあるミス

??? failure "覚えた位置に戻っても、続きが読めない"
    `eofbit` や `failbit` が立っています。`seekg` の前に `in.clear()` で状態をクリアします（C++11 以降の `seekg` は `eofbit` を自動で消しますが、`failbit` が立っていれば効きません）。

??? failure "`tellg()` が `-1` を返した"
    ストリームが失敗状態です。位置を取る前に、ストリームの状態を確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`streamoff`](streamoff.md) | 位置のずれ。2 つの `streampos` の差 |
| [`streamsize`](streamsize.md) | 読み書きする文字数 |
| [`fpos`](fpos.md) | `streampos` の元になっているクラス テンプレート |

## コンパイラ対応

C++98 から使えます。手元の MSVC（Visual Studio 2026）で動作を確かめました。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `streampos` は、ストリーム上の位置を覚えるための型
    - [x] `tellg()` で覚えて、`seekg()` で戻る
    - [x] 数値として使いたいときは `streamoff` に変換する。勝手に数値から作らない

## 関連ページ

- [cpprefjp: std::streampos](https://cpprefjp.github.io/reference/ios/streampos.html)
- [cppreference: std::streampos](https://en.cppreference.com/w/cpp/io/streampos)
