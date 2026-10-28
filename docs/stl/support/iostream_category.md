---
title: std::iostream_category
summary: "入出力ストリームのエラー（`io_errc`）の分類を表す error_category を返す。"
order: 900
group: エラーコード（<system_error>）
tags:
  - 型・言語サポート
---

# std::iostream_category

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <system_error>`
</div>

エラー番号は、出どころ（カテゴリー）とセットで意味を持ちます。`std::iostream_category()` は、<strong>入出力ストリームのエラーのカテゴリー</strong>を返す関数です。

!!! tip "ポイント"
    - `std::iostream_category()` は入出力ストリームのエラーのカテゴリーを表す `error_category` への参照を返す
    - `name()` は "iostream" を返す
    - 返ったオブジェクトは、プログラムに 1 つだけ存在する
    - `error_code` のカテゴリーの比較に使う

!!! info "このページを読む前に"
    [STL](../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::iostream_category {#iostream_category}

<span class="ver ver-11">C++11</span>

```cpp
const std::error_category& iostream_category() noexcept;
```

`std::io_errc::stream` などの、`<iostream>` が報告するエラーを表します。`std::ios_base::failure` 例外の `code()` が返す `error_code` が、このカテゴリーに属します。

返る参照は、常に同じオブジェクトを指します。`error_code::category()` との比較で、出どころを確かめられます。

## 実際に動かしてみる

```cpp
#include <print>
#include <system_error>

int main() {
  std::println("name() = {}", std::iostream_category().name());
  std::println("同じオブジェクト: {}", &std::iostream_category() == &std::iostream_category());
}
```

```text title="実行結果"
name() = iostream
同じオブジェクト: true
```

## ゲームでの使いどころ

エラーコードの出どころを調べます。

```cpp
if (ec.category() == std::iostream_category()) { /* 入出力ストリームのエラーのカテゴリー */ }
```

## よくあるミス

??? failure "カテゴリーを無視して番号だけを比べる"
    番号とカテゴリーの両方で判断します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`error_category`](error_category.md) | 基底クラス |
| [`error_code`](error_code.md) | 番号とカテゴリーの組 |

## コンパイラ対応

C++11 から使えます。`<system_error>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `iostream_category()` は入出力ストリームのエラーのカテゴリーを返す
    - [x] `name()` は "iostream"
    - [x] 常に同じオブジェクトを返す

## 関連ページ

- [cpprefjp: std::iostream_category](https://cpprefjp.github.io/reference/exception/iostream_category.html)
- [cppreference: std::iostream_category](https://en.cppreference.com/w/cpp/error/iostream_category)
