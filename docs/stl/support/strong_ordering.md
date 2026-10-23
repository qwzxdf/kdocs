---
title: std::strong_ordering
summary: "「等しいものは区別できない」比較結果（整数など）。less / equal / greater の 3 値。"
order: 2
group: 比較（<compare>）
tags:
  - 型・言語サポート
---

# std::strong_ordering

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <compare>`
</div>

`std::strong_ordering` は、**三方比較（`<=>`）の結果の型のうち、最も強いもの**で、`less`（小さい）、`equal`（等しい）、`greater`（大きい）の 3 つの値を持ちます。`equal` のものは**区別がつかない**（どちらを使っても同じ）ことを表します。整数や文字列の比較結果がこの型です。

!!! tip "ポイント"
    - `(a <=> b) < 0` のように 0 と比べて判定する。
    - `std::is_lt(r)`、`is_eq(r)`、`is_gt(r)` で読みやすく書ける。
    - 小数は NaN があるので `partial_ordering`。

!!! info "このページを読む前に"
    - [STL](../index.md)（STL 全体の地図（どこに何があるか））
    - [テンプレート](../../basics/template.md)（テンプレートの基礎）

## 関数の詳しい説明

### std::strong_ordering {#strong_ordering}

```cpp
struct strong_ordering {
  static const strong_ordering less, equal, greater;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `r` | `strong_ordering` | 比較結果 |

- 戻り値: `less` / `equal` / `greater`
- 計算量: O(1)

```cpp
#include <compare>
#include <print>

int main() {
  std::strong_ordering r = (3 <=> 5);
  std::println("{} {} {}", r < 0, std::is_lt(r), (2 <=> 2) == 0);
}
```

```text title="実行結果"
true true true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 自作の比較関数の戻り値 | `std::strong_ordering Compare(const Item& a, const Item& b)` |

## よくあるミス

??? failure "0 以外のリテラルと比べる"
    `r < 1` のように 0 以外と比べるのはエラーです。`< 0`、`== 0`、`> 0` の形だけが使えます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`weak_ordering`](weak_ordering.md) | 等しくても区別できるかもしれない |
| [`partial_ordering`](partial_ordering.md) | 比べられない場合がある |

## コンパイラ対応

C++20 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 3 値の比較結果
    - [x] 0 と比べて判定
    - [x] 整数・文字列の結果

## 関連ページ

- [cpprefjp: std::strong_ordering](https://cpprefjp.github.io/reference/compare/strong_ordering.html)
- [cppreference: std::strong_ordering](https://en.cppreference.com/w/cpp/utility/compare/strong_ordering)
