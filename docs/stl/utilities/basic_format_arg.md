---
title: std::basic_format_arg
summary: "書式化の引数 1 つぶんを表す型。"
order: 900
tags:
  - ユーティリティ
---

# std::basic_format_arg

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <format>`
</div>

`std::make_format_args` が作る引数リストの 1 つの要素です。整数・文字列・小数など、さまざまな型の値を、型を消した形で持ちます。中身を調べるには `visit_format_arg` を使います。

!!! tip "ポイント"
    - `<format>` の部品。
    - ふつうは `std::format` / `std::println` を使えば足りる。
    - 自作の型に対応させるときに登場する。

!!! info "このページを読む前に"
    [`std::format`](format.md) を先に読んでください。

## 関数の詳しい説明

### std::basic_format_arg {#basic_format_arg}

```cpp
template <class Context>
class basic_format_arg {
 public:
  explicit operator bool() const noexcept;
};
```

- 戻り値: 値を持っていれば `true`（`operator bool`）
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <format>
#include <print>

int main() {
  int v = 42;
  auto args = std::make_format_args(v);
  std::format_args fa = args;
  std::println("{}", static_cast<bool>(fa.get(0)));
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 自作のフォーマッタで、他の引数を参照する |

## よくあるミス

??? failure "直接中身を取り出そうとする"
    型が消えているので、`visit_format_arg` で取り出します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`visit_format_arg`](visit_format_arg.md) | 中身を取り出す |
| [`basic_format_args`](basic_format_args.md) | 引数のリスト |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 書式化の引数 1 つぶんを表す型
    - [x] `<format>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::basic_format_arg](https://cpprefjp.github.io/reference/format/basic_format_arg.html)
- [cppreference: std::basic_format_arg](https://en.cppreference.com/w/cpp/utility/format/basic_format_arg)
