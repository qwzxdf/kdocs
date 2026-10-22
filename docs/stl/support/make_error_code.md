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

`std::errc::no_such_file_or_directory` のような、読みやすい名前の列挙値から、`error_code` を作ります。自作のエラー列挙型にも、同じ名前の関数を定義すると、`error_code` に暗黙に変換できるようになります。

!!! tip "ポイント"
    - 例外の関連の部品。
    - `try` / `catch` と組み合わせて使う。
    - ゲームでは、ファイルや外部入力のエラーの扱いに登場する。

!!! info "このページを読む前に"
    [`std::error_code`](error_code.md) を先に読んでください。

## 関数の詳しい説明

### std::make_error_code {#make_error_code}

```cpp
std::error_code make_error_code(std::errc e) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `e` | errc | 標準のエラーの列挙値 |

- 戻り値: 対応する `error_code`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cerrno>
#include <print>
#include <system_error>

int main() {
  std::error_code ec = std::make_error_code(std::errc::no_such_file_or_directory);
  std::println("{}", ec.value() == ENOENT);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | ファイル操作の失敗を、標準のエラーとして返す |

## よくあるミス

??? failure "`value()` を直接比べる"
    OS によって `value()` の数値は違います。`ec == std::errc::...` で比べます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`make_error_condition`](make_error_condition.md) | 移植性のある条件を作る |
| [`is_error_code_enum`](is_error_code_enum.md) | 自作の列挙型を対応させる |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] errc などの列挙値から、error_code を作る
    - [x] 例外の関連の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::make_error_code](https://cpprefjp.github.io/reference/exception/make_error_code.html)
- [cppreference: std::make_error_code](https://en.cppreference.com/w/cpp/error/make_error_code)
