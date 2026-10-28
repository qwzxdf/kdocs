---
title: std::error_category
summary: "エラーコードの種類（分類）を表す基底クラス。"
order: 900
group: エラーコード（<system_error>）
tags:
  - 型・言語サポート
---

# std::error_category

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <system_error>`
</div>

エラー番号の意味は、エラーの出どころ（OS、標準ライブラリ、ネットワーク、自作のライブラリ）で違います。同じ番号 2 でも、出どころによって別のエラーです。`std::error_category` は、<strong>エラー番号の「出どころ」を表す基底クラス</strong>で、番号を意味のある文字列にする役割を持ちます。

!!! tip "ポイント"
    - `std::error_category` は、エラー番号の出どころを表す基底クラス
    - `name()` で出どころの名前、`message(n)` で番号の説明文を返す
    - 標準では `generic_category()`、`system_category()`、`iostream_category()` が用意されている
    - 自作のライブラリは、これを継承して自前のカテゴリーを作れる

!!! info "このページを読む前に"
    [STL](../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::error_category {#error_category}

<span class="ver ver-11">C++11</span>

```cpp
class error_category {
 public:
  virtual const char* name() const noexcept = 0;
  virtual std::string message(int ev) const = 0;
};
```

`std::error_code` は「番号 + カテゴリー」の組です。カテゴリーが違えば、番号が同じでも別のエラーとして扱われます。

自作のライブラリのエラーを `std::error_code` で表したいときは、`std::error_category` を継承した型を作り、`name()` と `message()` を実装します。カテゴリーのオブジェクトは、プログラムに 1 つだけ存在するシングルトンにします。

標準が用意する 3 つのカテゴリーのうち、`generic_category` は移植性のある `errc`、`system_category` は OS 固有のエラー、`iostream_category` は入出力のエラーです。

## 実際に動かしてみる

```cpp
#include <print>
#include <system_error>

int main() {
  std::println("generic  : {}", std::generic_category().name());
  std::println("system   : {}", std::system_category().name());
  std::println("iostream : {}", std::iostream_category().name());
}
```

```text title="実行結果"
generic  : generic
system   : system
iostream : iostream
```

## ゲームでの使いどころ

自作のライブラリのエラーを、標準の枠組みに載せます。

```cpp
struct GameErrorCategory : std::error_category {
  const char* name() const noexcept override { return "game"; }
  std::string message(int ev) const override { return ev == 1 ? "セーブデータが壊れている" : "不明"; }
};
```

## よくあるミス

??? failure "カテゴリーのオブジェクトを複数作る"
    1 つだけ作って共有します。比較はアドレスで行われるためです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`error_code`](error_code.md) | 番号とカテゴリーの組 |
| [`generic_category`](generic_category.md) | 移植性のあるカテゴリー |

## コンパイラ対応

C++11 から使えます。`<system_error>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `error_category` はエラー番号の出どころを表す
    - [x] `name()` と `message()` を持つ
    - [x] 自作のカテゴリーはシングルトンにする

## 関連ページ

- [cpprefjp: std::error_category](https://cpprefjp.github.io/reference/exception/error_category.html)
- [cppreference: std::error_category](https://en.cppreference.com/w/cpp/error/error_category)
