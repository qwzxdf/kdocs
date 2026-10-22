---
title: std::wformat_string
summary: "書式文字列を、コンパイル時に検査する型（wchar_t 版の別名）。"
order: 900
tags:
  - ユーティリティ
---

# std::wformat_string

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <format>`
</div>

`format_string` の `wchar_t` 版です。`std::wformat(L"{}", x)` の書式文字列を、コンパイル時に検査します。

!!! tip "ポイント"
    - `<format>` の部品。
    - ふつうは `std::format` / `std::println` を使えば足りる。
    - 自作の型に対応させるときに登場する。

!!! info "このページを読む前に"
    [`std::format`](format.md) を先に読んでください。

## 関数の詳しい説明

### std::wformat_string {#wformat_string}

```cpp
template <class... Args>
using wformat_string = basic_format_string<wchar_t, type_identity_t<Args>...>;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `Args...` | 型 | 書式に渡す引数の型 |

- 戻り値: 書式文字列の検査つきの引数型
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <format>
#include <print>

void LogW(std::wformat_string<int> fmt, int v) {
  std::println("{}", std::format(fmt, v).size());
}

int main() {
  LogW(L"{}", 42);
}
```

```text title="実行結果"
2
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | ワイド文字の自作のログ関数 |

## よくあるミス

??? failure "`format_string` と混ぜる"
    文字の型を合わせます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`format_string`](format_string.md) | char 版 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 書式文字列を、コンパイル時に検査する型（wchar_t 版の別名）
    - [x] `<format>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::wformat_string](https://cpprefjp.github.io/reference/format/wformat_string.html)
- [cppreference: std::wformat_string](https://en.cppreference.com/w/cpp/utility/format/wformat_string)
