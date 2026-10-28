---
title: std::generic_category
summary: "OS に依存しない標準のエラー（`errc`）の分類を表す error_category を返す。"
order: 900
group: エラーコード（<system_error>）
tags:
  - 型・言語サポート
---

# std::generic_category

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <system_error>`
</div>

エラー番号は、出どころ（カテゴリー）とセットで意味を持ちます。`std::generic_category()` は、<strong>移植性のあるエラー（`std::errc`）のカテゴリー</strong>を返す関数です。

!!! tip "ポイント"
    - `std::generic_category()` は移植性のあるエラー（`std::errc`）のカテゴリーを表す `error_category` への参照を返す
    - `name()` は "generic" を返す
    - 返ったオブジェクトは、プログラムに 1 つだけ存在する
    - `error_code` のカテゴリーの比較に使う

!!! info "このページを読む前に"
    [STL](../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::generic_category {#generic_category}

<span class="ver ver-11">C++11</span>

```cpp
const std::error_category& generic_category() noexcept;
```

`std::errc` の値は、このカテゴリーに属します。`std::make_error_code(std::errc::...)` が作る `error_code` は、このカテゴリーを持ちます。OS が違っても、同じ意味のエラー番号になるのが利点です。

返る参照は、常に同じオブジェクトを指します。`error_code::category()` との比較で、出どころを確かめられます。

## 実際に動かしてみる

```cpp
#include <print>
#include <system_error>

int main() {
  std::println("name() = {}", std::generic_category().name());
  std::println("同じオブジェクト: {}", &std::generic_category() == &std::generic_category());
}
```

```text title="実行結果"
name() = generic
同じオブジェクト: true
```

## ゲームでの使いどころ

エラーコードの出どころを調べます。

```cpp
if (ec.category() == std::generic_category()) { /* 移植性のあるエラー（`std::errc`）のカテゴリー */ }
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
    - [x] `generic_category()` は移植性のあるエラー（`std::errc`）のカテゴリーを返す
    - [x] `name()` は "generic"
    - [x] 常に同じオブジェクトを返す

## 関連ページ

- [cpprefjp: std::generic_category](https://cpprefjp.github.io/reference/exception/generic_category.html)
- [cppreference: std::generic_category](https://en.cppreference.com/w/cpp/error/generic_category)
