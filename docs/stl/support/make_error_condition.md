---
title: std::make_error_condition
summary: "errc などの列挙値から、error_condition を作る。"
order: 900
group: エラーコード（<system_error>）
tags:
  - 型・言語サポート
---

# std::make_error_condition

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <system_error>`
</div>

`std::errc` の値から、`std::error_condition`（エラーの種類）を作る関数が `std::make_error_condition` です。`error_code` と比べるための右辺を、明示的に作りたいときに使います。

!!! tip "ポイント"
    - `std::make_error_condition(std::errc::...)` で `error_condition` を作る
    - `std::errc` から暗黙にも作れるので、直接呼ぶ機会は少ない
    - 自作の列挙型でも、この関数を用意すると `error_condition` に変換できる
    - `std::is_error_condition_enum` を特殊化して有効にする

!!! info "このページを読む前に"
    [STL](../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::make_error_condition {#make_error_condition}

<span class="ver ver-11">C++11</span>

```cpp
std::error_condition make_error_condition(std::errc e) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `e` | `errc` | エラーの種類 |

列挙子から、番号とカテゴリーの組を作って返します。`std::errc` の値は、暗黙に `error_condition` に変換できるので、`ec == std::errc::...` のように書けば、この関数を直接呼ぶ必要はありません。

自作の列挙型で、エラーの「種類」を表現したいときに、同じ名前空間に定義して使います。

## 実際に動かしてみる

```cpp
#include <print>
#include <system_error>

int main() {
  const std::error_condition cond = std::make_error_condition(std::errc::permission_denied);
  std::println("カテゴリーは generic: {}", cond.category() == std::generic_category());
}
```

```text title="実行結果"
カテゴリーは generic: true
```

## ゲームでの使いどころ

自作の列挙型を `error_condition` として使えるようにします。通常は `std::errc` のまま `==` で比べれば足ります。

## よくあるミス

??? failure "`error_code` と取り違える"
    種類を表すのは `error_condition` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`make_error_code`](make_error_code.md) | 具体的なエラーを作る |
| [`error_condition`](error_condition.md) | エラーの種類 |

## コンパイラ対応

C++11 から使えます。`<system_error>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `make_error_condition(e)` は列挙子から `error_condition` を作る
    - [x] 通常は暗黙の変換で足りる
    - [x] 自作の列挙型に用意できる

## 関連ページ

- [cpprefjp: std::make_error_condition](https://cpprefjp.github.io/reference/exception/make_error_condition.html)
- [cppreference: std::make_error_condition](https://en.cppreference.com/w/cpp/error/make_error_condition)
