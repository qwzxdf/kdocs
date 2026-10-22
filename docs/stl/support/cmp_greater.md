---
title: std::cmp_greater
summary: "符号付きと符号なしの整数を、安全に `>` で比べる。"
order: 900
group: 小さな便利機能（<utility>）
tags:
  - 型・言語サポート
---

# std::cmp_greater

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <utility>`
</div>

`int` と `unsigned` を `>` で比べると、符号付きの側が符号なしに変換されて、`-1 > 0u` がtrue（-1 が大きな符号なしの値に変換される）。数学的に正しい比較にしたいときに、`cmp_greater` を使います。

!!! tip "ポイント"
    - 整数型どうしだけで使える（`bool` や `char` は不可）。
    - 符号付きと符号なしを混ぜても、数学的に正しい結果になる。
    - 同系列: `cmp_equal`・`cmp_less` ほか。

!!! info "このページを読む前に"
    [小さな便利機能](utility-misc.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::cmp_greater {#cmp_greater}

```cpp
template <class T, class U>
constexpr bool cmp_greater(T a, U b) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `a, b` | 整数型 | 比べる 2 つの値 |

- 戻り値: `a > b` を数学的に評価した結果
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <print>
#include <utility>

int main() {
  std::println("{}", std::cmp_greater(-1, 0u));
}
```

```text title="実行結果"
false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| `vector::size()` と `int` の比較 | `std::cmp_greater(i, v.size())` |

## よくあるミス

??? failure "浮動小数点や char に使う"
    整数型（`bool`・`char` 型を除く）だけが対象です。それ以外はコンパイルエラーになります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`cmp_equal`](cmp_equal.md) | `==` |
| [`cmp_less`](cmp_less.md) | `<` |
| [`in_range`](in_range.md) | 値が型の範囲に入るか |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 符号を考慮した整数の比較
    - [x] int と unsigned を混ぜても安全
    - [x] 整数型だけ

## 関連ページ

- [cpprefjp: std::cmp_greater](https://cpprefjp.github.io/reference/utility/cmp_greater.html)
- [cppreference: std::cmp_greater](https://en.cppreference.com/w/cpp/utility/cmp_greater)
