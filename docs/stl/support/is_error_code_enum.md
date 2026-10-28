---
title: std::is_error_code_enum
summary: "自作の列挙型を、error_code に暗黙変換できるようにする特性。"
order: 900
group: エラーコード（<system_error>）
tags:
  - 型・言語サポート
---

# std::is_error_code_enum

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <system_error>`
</div>

自作のエラーの列挙型を、`std::error_code` に暗黙に変換できるようにしたい。そのためには、この列挙型を `std::error_code` の対象だと標準に教える必要があります。`std::is_error_code_enum<E>` は、<strong>その目印</strong>で、特殊化して `true` にします。

!!! tip "ポイント"
    - `std::is_error_code_enum<E>::value` が `true` なら、`E` は `error_code` に暗黙に変換できる
    - 自作の列挙型では、特殊化して `std::true_type` を継承する
    - 同じ名前空間に `make_error_code(E)` が必要
    - `std::errc` は対象外（`error_condition` の対象）

!!! info "このページを読む前に"
    [STL](../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_error_code_enum {#is_error_code_enum}

<span class="ver ver-11">C++11</span>

```cpp
template <class E>
struct is_error_code_enum : std::false_type {};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `E` | 型 | 調べる列挙型 |

既定では `false` です。自作の列挙型 `GameError` で `std::error_code ec = GameError::kCorrupt;` と書けるようにするには、次の 2 つが必要です。

1. `template <> struct std::is_error_code_enum<GameError> : std::true_type {};` と特殊化する
2. `GameError` と同じ名前空間に `std::error_code make_error_code(GameError)` を定義する

この仕組みを使うと、ゲーム独自のエラーを、標準のエラー報告の枠組みの中で扱えます。

## 実際に動かしてみる

```cpp
#include <print>
#include <system_error>
#include <type_traits>

int main() {
  std::println("io_errc は error_code の対象: {}", std::is_error_code_enum_v<std::io_errc>);
  std::println("int は対象           : {}", std::is_error_code_enum_v<int>);
}
```

```text title="実行結果"
io_errc は error_code の対象: true
int は対象           : false
```

## ゲームでの使いどころ

自作のエラーの列挙型を、標準のエラーコードの仕組みに載せます。

## よくあるミス

??? failure "特殊化だけして、`make_error_code` を定義し忘れる"
    同じ名前空間に定義します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_error_condition_enum`](is_error_condition_enum.md) | `error_condition` の対象 |
| [`make_error_code`](make_error_code.md) | コードを作る |

## コンパイラ対応

C++11 から使えます。`<system_error>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `is_error_code_enum<E>` は E が `error_code` の対象かの目印
    - [x] 自作の列挙型は特殊化で `true` にする
    - [x] 同じ名前空間に `make_error_code` が必要

## 関連ページ

- [cpprefjp: std::is_error_code_enum](https://cpprefjp.github.io/reference/exception/is_error_code_enum.html)
- [cppreference: std::is_error_code_enum](https://en.cppreference.com/w/cpp/error/is_error_code_enum)
