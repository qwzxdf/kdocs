---
title: std::make_format_args
summary: "引数を、書式化用の引数リストにまとめる。"
order: 900
tags:
  - ユーティリティ
---

# std::make_format_args

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <format>`
</div>

`std::vformat(書式, 引数リスト)` に渡すための、引数のリストを作ります。書式文字列が実行時に決まるときなど、`format` ではなく `vformat` を使う場面で使います。引数は**左辺値の参照**で渡します。

!!! tip "ポイント"
    - `<format>` の部品。
    - ふつうは `std::format` / `std::println` を使えば足りる。
    - 自作の型に対応させるときに登場する。

!!! info "このページを読む前に"
    [`std::format`](format.md) を先に読んでください。

## 関数の詳しい説明

### std::make_format_args {#make_format_args}

```cpp
template <class Context = format_context, class... Args>
/* 実装定義 */ make_format_args(Args&... args);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `args...` | 左辺値 | 書式化する引数（右辺値は渡せない） |

- 戻り値: 引数リスト（`format_args`）
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <format>
#include <print>

int main() {
  int a = 1;
  int b = 2;
  auto args = std::make_format_args(a, b);
  std::println("{}", std::vformat("{}-{}", args));
}
```

```text title="実行結果"
1-2
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 実行時の書式文字列で書式化する |

## よくあるミス

??? failure "右辺値を渡す"
    一時オブジェクトを渡すとコンパイルエラーです。変数に入れてから渡します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`vformat`](vformat.md) | 引数リストで書式化する |
| [`make_wformat_args`](make_wformat_args.md) | wchar_t 版 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 引数を、書式化用の引数リストにまとめる
    - [x] `<format>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::make_format_args](https://cpprefjp.github.io/reference/format/make_format_args.html)
- [cppreference: std::make_format_args](https://en.cppreference.com/w/cpp/utility/format/make_format_args)
