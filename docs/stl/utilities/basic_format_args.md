---
title: std::basic_format_args
summary: "書式化の引数のリストを表す型。"
order: 900
tags:
  - ユーティリティ
---

# std::basic_format_args

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <format>`
</div>

`std::vformat` の第 2 引数の型です。`make_format_args` が返す値から作れ、`get(i)` で i 番目の引数を取り出せます。`std::format_args` は、`char` 版の別名です。

!!! tip "ポイント"
    - `<format>` の部品。
    - ふつうは `std::format` / `std::println` を使えば足りる。
    - 自作の型に対応させるときに登場する。

!!! info "このページを読む前に"
    [`std::format`](format.md) を先に読んでください。

## 関数の詳しい説明

### std::basic_format_args {#basic_format_args}

```cpp
template <class Context>
class basic_format_args {
 public:
  basic_format_arg<Context> get(size_t i) const noexcept;
};
```

- 戻り値: `get(i)` で i 番目の引数
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <format>
#include <print>

int main() {
  int a = 1;
  int b = 2;
  auto args = std::make_format_args(a, b);
  std::format_args fa = args;
  std::println("{}", static_cast<bool>(fa.get(1)));
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 自作のログ関数が、引数リストを受け取る |

## よくあるミス

??? failure "範囲外の番号を渡す"
    範囲外の `get` は空の引数を返します（`bool` は `false`）。

## 類似

| 名前 | 違い |
| --- | --- |
| [`make_format_args`](make_format_args.md) | 作る関数 |
| [`basic_format_arg`](basic_format_arg.md) | 1 つぶん |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 書式化の引数のリストを表す型
    - [x] `<format>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::basic_format_args](https://cpprefjp.github.io/reference/format/basic_format_args.html)
- [cppreference: std::basic_format_args](https://en.cppreference.com/w/cpp/utility/format/basic_format_args)
