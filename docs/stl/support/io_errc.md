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

`ios_base::failure` の `code()` は、`io_errc::stream` を返します。ストリームのエラーを標準の `error_code` の仕組みで扱うための列挙型です。

!!! tip "ポイント"
    - 例外の関連の部品。
    - `try` / `catch` と組み合わせて使う。
    - ゲームでは、ファイルや外部入力のエラーの扱いに登場する。

!!! info "このページを読む前に"
    [`std::error_code`](error_code.md) を先に読んでください。

## 関数の詳しい説明

### std::io_errc {#io_errc}

```cpp
enum class io_errc { stream = 1 };
const error_category& iostream_category() noexcept;
```

- 戻り値: `io_errc::stream` だけがある
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <ios>
#include <print>
#include <system_error>

int main() {
  std::error_code ec = std::make_error_code(std::io_errc::stream);
  std::println("{}", ec.category().name());
}
```

```text title="実行結果"
iostream
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | ストリームの例外を `error_code` として扱う |

## よくあるミス

??? failure "`failbit` と取り違える"
    `io_errc` は例外のコード、`failbit` はストリームの状態のフラグです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`iostream_category`](iostream_category.md) | 分類 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 入出力ストリームのエラーを表す列挙型
    - [x] 例外の関連の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::io_errc](https://cpprefjp.github.io/reference/exception/io_errc.html)
- [cppreference: std::io_errc](https://en.cppreference.com/w/cpp/error/io_errc)
