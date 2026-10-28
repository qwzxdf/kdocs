---
title: std::make_wformat_args
summary: "引数を、wchar_t 用の書式化引数リストにまとめる。"
order: 900
tags:
  - ユーティリティ
---

# std::make_wformat_args

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <format>`
</div>

`make_format_args` の `wchar_t` 版です。`std::vformat(L"...", 引数リスト)` に渡します。

!!! tip "ポイント"
    - `<format>` の部品。
    - ふつうは `std::format` / `std::println` を使えば足りる。
    - 自作の型に対応させるときに登場する。

!!! info "このページを読む前に"
    [`std::format`](format.md) を先に読んでください。

## 関数の詳しい説明

### std::make_wformat_args {#make_wformat_args}

```cpp
template <class... Args>
/* 実装定義 */ make_wformat_args(Args&... args);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `args...` | 左辺値 | 書式化する引数 |

- 戻り値: 引数リスト（`wformat_args`）
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <format>
#include <print>

int main() {
  int a = 42;
  std::println("{}", std::vformat(L"{}", std::make_wformat_args(a)).size());
}
```

```text title="実行結果"
2
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | ワイド文字で実行時の書式化をする |

## よくあるミス

??? failure "右辺値を渡す"
    変数に入れてから渡します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`make_format_args`](make_format_args.md) | char 版 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 引数を wchar_t 用の書式化引数リストにまとめる
    - [x] `<format>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::make_wformat_args](https://cpprefjp.github.io/reference/format/make_wformat_args.html)
- [cppreference: std::make_wformat_args](https://en.cppreference.com/w/cpp/utility/format/make_wformat_args)
