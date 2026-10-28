---
title: std::system_category
summary: "OS 固有のエラー（Windows の `GetLastError`、POSIX の `errno`）の分類を表す error_category を返す。"
order: 900
group: エラーコード（<system_error>）
tags:
  - 型・言語サポート
---

# std::system_category

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <system_error>`
</div>

エラー番号は、出どころ（カテゴリー）とセットで意味を持ちます。`std::system_category()` は、<strong>OS 固有のエラーのカテゴリー</strong>を返す関数です。

!!! tip "ポイント"
    - `std::system_category()` はOS 固有のエラーのカテゴリーを表す `error_category` への参照を返す
    - `name()` は "system" を返す
    - 返ったオブジェクトは、プログラムに 1 つだけ存在する
    - `error_code` のカテゴリーの比較に使う

!!! info "このページを読む前に"
    [STL](../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::system_category {#system_category}

<span class="ver ver-11">C++11</span>

```cpp
const std::error_category& system_category() noexcept;
```

Windows では `GetLastError()` が返す値、POSIX では `errno` の値を表すカテゴリーです。`std::filesystem` や `std::thread` の失敗などで、OS が報告したエラーが、このカテゴリーで返ります。

返る参照は、常に同じオブジェクトを指します。`error_code::category()` との比較で、出どころを確かめられます。

## 実際に動かしてみる

```cpp
#include <print>
#include <system_error>

int main() {
  std::println("name() = {}", std::system_category().name());
  std::println("同じオブジェクト: {}", &std::system_category() == &std::system_category());
}
```

```text title="実行結果"
name() = system
同じオブジェクト: true
```

## ゲームでの使いどころ

エラーコードの出どころを調べます。

```cpp
if (ec.category() == std::system_category()) { /* OS 固有のエラーのカテゴリー */ }
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
    - [x] `system_category()` はOS 固有のエラーのカテゴリーを返す
    - [x] `name()` は "system"
    - [x] 常に同じオブジェクトを返す

## 関連ページ

- [cpprefjp: std::system_category](https://cpprefjp.github.io/reference/exception/system_category.html)
- [cppreference: std::system_category](https://en.cppreference.com/w/cpp/error/system_category)
