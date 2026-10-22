---
title: std::formattable
summary: "型が `std::format` で書式化できることを要求するコンセプト。"
order: 900
tags:
  - ユーティリティ
---

# std::formattable

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <format>`
</div>

テンプレートの引数 `T` を `std::format` で出力できるかを、コンパイル時に調べます。自作のログ関数が、書式化できない型を受け取らないようにできます。

!!! tip "ポイント"
    - `<format>` の部品。
    - ふつうは `std::format` / `std::println` を使えば足りる。
    - 自作の型に対応させるときに登場する。

!!! info "このページを読む前に"
    [`std::format`](format.md) を先に読んでください。

## 関数の詳しい説明

### std::formattable {#formattable}

```cpp
template <class T, class CharT>
concept formattable = /* formatter<T, CharT> が使える */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べる型 |
| `CharT` | 型 | 文字の型（`char` など） |

- 戻り値: 書式化できれば `true`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <format>
#include <print>

struct S {};

int main() {
  std::println("{}", std::formattable<int, char>);
  std::println("{}", std::formattable<S, char>);
}
```

```text title="実行結果"
true
false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 書式化できない型を、コンパイル時に弾く |

## よくあるミス

??? failure "`<<` が使える型と混同する"
    `operator<<` があっても、`formatter` がなければ `false` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`formatter`](formatter.md) | 対応させる |
| [`format`](format.md) | 書式化 |

## コンパイラ対応

C++23 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 型が `std::format` で書式化できることを要求するコンセプト
    - [x] `<format>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::formattable](https://cpprefjp.github.io/reference/format/formattable.html)
- [cppreference: std::formattable](https://en.cppreference.com/w/cpp/utility/format/formattable)
