---
title: std::is_error_condition_enum
summary: "自作の列挙型を、error_condition に暗黙変換できるようにする特性。"
order: 900
group: エラーコード（<system_error>）
tags:
  - 型・言語サポート
---

# std::is_error_condition_enum

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <system_error>`
</div>

`std::errc` は `std::error_condition` に暗黙に変換できます。自作のエラーの種類の列挙型も、同じ扱いにしたい。`std::is_error_condition_enum<E>` は、<strong>その目印</strong>で、特殊化して `true` にします。

!!! tip "ポイント"
    - `std::is_error_condition_enum<E>::value` が `true` なら、`E` は `error_condition` に暗黙に変換できる
    - `std::errc` は `true`
    - 自作の列挙型では、特殊化して `std::true_type` を継承する
    - 同じ名前空間に `make_error_condition(E)` が必要

!!! info "このページを読む前に"
    [STL](../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_error_condition_enum {#is_error_condition_enum}

<span class="ver ver-11">C++11</span>

```cpp
template <class E>
struct is_error_condition_enum : std::false_type {};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `E` | 型 | 調べる列挙型 |

既定では `false` ですが、`std::errc` に対しては標準が `true` にしています。自作の列挙型を、エラーの「種類」として使いたいときは、`is_error_code_enum` と同じ手順で、特殊化と `make_error_condition` の定義を行います。

## 実際に動かしてみる

```cpp
#include <print>
#include <system_error>
#include <type_traits>

int main() {
  std::println("errc は error_condition の対象: {}", std::is_error_condition_enum_v<std::errc>);
  std::println("int は対象でない           : {}", std::is_error_condition_enum_v<int>);
}
```

```text title="実行結果"
errc は error_condition の対象: true
int は対象でない           : true
```

## ゲームでの使いどころ

自作のエラーの種類の列挙型を、標準の枠組みに載せます。

## よくあるミス

??? failure "`is_error_code_enum` と取り違える"
    種類は `condition`、具体的なエラーは `code` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_error_code_enum`](is_error_code_enum.md) | `error_code` の対象 |
| [`make_error_condition`](make_error_condition.md) | 種類を作る |

## コンパイラ対応

C++11 から使えます。`<system_error>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `is_error_condition_enum<E>` は E が `error_condition` の対象かの目印
    - [x] `errc` は `true`
    - [x] 自作の列挙型は特殊化で `true` にする

## 関連ページ

- [cpprefjp: std::is_error_condition_enum](https://cpprefjp.github.io/reference/exception/is_error_condition_enum.html)
- [cppreference: std::is_error_condition_enum](https://en.cppreference.com/w/cpp/error/is_error_condition_enum)
