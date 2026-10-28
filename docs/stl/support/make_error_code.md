---
title: std::make_error_code
summary: "errc などの列挙値から、error_code を作る。"
order: 900
group: エラーコード（<system_error>）
tags:
  - 型・言語サポート
---

# std::make_error_code

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <system_error>`
</div>

`std::errc` の値（列挙子）から、`std::error_code` を作りたい。`std::make_error_code(e)` は、<strong>列挙型の値から対応するエラーコードを作ります</strong>。

!!! tip "ポイント"
    - `std::make_error_code(std::errc::...)` で `error_code` を作る
    - `std::errc` は `generic_category` のコードになる
    - 自作の列挙型でも、この関数を用意すると `error_code` に変換できる
    - `std::error_code ec = std::errc::...;` と書けないので、この関数を使う

!!! info "このページを読む前に"
    [STL](../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::make_error_code {#make_error_code}

<span class="ver ver-11">C++11</span>

```cpp
std::error_code make_error_code(std::errc e) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `e` | `errc` | エラーの種類 |

列挙子から、番号とカテゴリーの組を作って返します。`std::errc` の場合は、`generic_category()` に属する `error_code` になります。

自作の列挙型（ゲームのエラーの種類）を `error_code` として扱いたいときは、`std::is_error_code_enum` を特殊化して `true` にし、同じ名前空間に `make_error_code(MyError)` を定義します。そうすると `std::error_code ec = MyError::kCorrupt;` のように書けるようになります。

## 実際に動かしてみる

```cpp
#include <print>
#include <system_error>

int main() {
  const std::error_code ec = std::make_error_code(std::errc::no_such_file_or_directory);
  std::println("カテゴリーは generic: {}", ec.category() == std::generic_category());
  std::println("値は 0 以外      : {}", ec.value() != 0);
}
```

```text title="実行結果"
カテゴリーは generic: true
値は 0 以外      : true
```

## ゲームでの使いどころ

関数の失敗を、`error_code` で返します。

```cpp
std::error_code Load(const char* path) {
  if (!Exists(path)) return std::make_error_code(std::errc::no_such_file_or_directory);
  return {};   // 成功
}
```

## よくあるミス

??? failure "名前空間が違って、自作の列挙型で見つからない"
    列挙型と同じ名前空間に定義します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`make_error_condition`](make_error_condition.md) | 種類を作る |
| [`errc`](errc.md) | 列挙型 |

## コンパイラ対応

C++11 から使えます。`<system_error>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `make_error_code(e)` は列挙子から `error_code` を作る
    - [x] `errc` は `generic_category` に属する
    - [x] 自作の列挙型にも用意できる

## 関連ページ

- [cpprefjp: std::make_error_code](https://cpprefjp.github.io/reference/exception/make_error_code.html)
- [cppreference: std::make_error_code](https://en.cppreference.com/w/cpp/error/make_error_code)
