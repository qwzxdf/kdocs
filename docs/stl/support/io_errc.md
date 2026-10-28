---
title: std::io_errc
summary: "入出力ストリームのエラーを表す列挙型。"
order: 900
group: エラーコード（<system_error>）
tags:
  - 型・言語サポート
---

# std::io_errc

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <system_error>`
</div>

入出力ストリームのエラーを、標準のエラーコードの枠組みで表すための列挙型が `std::io_errc` です。値は `stream` の 1 つだけです。

!!! tip "ポイント"
    - `std::io_errc::stream` の 1 つだけの値を持つ列挙型
    - `std::ios_base::failure` 例外の `code()` が返すコードに使われる
    - `iostream_category()` に属する
    - `std::is_error_code_enum` が `true`

!!! info "このページを読む前に"
    [STL](../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::io_errc {#io_errc}

<span class="ver ver-11">C++11</span>

```cpp
enum class io_errc {
  stream = 1
};
```

入出力ストリームの操作が失敗して、`exceptions()` で例外を有効にしているとき、投げられる `std::ios_base::failure` の `code()` は、`std::make_error_code(std::io_errc::stream)` と同じです。

ゲームでこの値を直接使う機会はほとんどありません。ファイル読み込みの失敗は、`std::ifstream` の状態（`fail()`）か、`std::filesystem` のエラーコードで調べます。

## 実際に動かしてみる

```cpp
#include <print>
#include <system_error>

int main() {
  const std::error_code ec = std::make_error_code(std::io_errc::stream);
  std::println("カテゴリーは iostream: {}", ec.category() == std::iostream_category());
}
```

```text title="実行結果"
カテゴリーは iostream: true
```

## ゲームでの使いどころ

入出力例外の原因を調べるときに登場します。通常は意識しません。

## よくあるミス

??? failure "ファイルの存在エラーを調べるのに使う"
    ファイル システムのエラーは `std::errc` で調べます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`iostream_category`](iostream_category.md) | カテゴリー |
| [`error_code`](error_code.md) | エラーコード |

## コンパイラ対応

C++11 から使えます。`<system_error>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `io_errc::stream` は入出力ストリームのエラー
    - [x] `iostream_category` に属する
    - [x] 直接使う機会はほとんどない

## 関連ページ

- [cpprefjp: std::io_errc](https://cpprefjp.github.io/reference/exception/io_errc.html)
- [cppreference: std::io_errc](https://en.cppreference.com/w/cpp/error/io_errc)
