---
title: std::partial_ordering
summary: "「比べられない」場合がある比較結果（NaN を含む小数）。"
order: 4
group: 比較（<compare>）
tags:
  - 型・言語サポート
---

# std::partial_ordering

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <compare>`
</div>

`std::partial_ordering` は、**「大小が決められない（`unordered`）」場合がある比較結果**です。小数の比較がこの型で、NaN とは大小を比べられません。値は `less`、`equivalent`、`greater`、`unordered` の 4 つです。小数のメンバを含むクラスの `<=>` は、この型になります。

!!! tip "ポイント"
    - `unordered` のとき、`<`、`>`、`==` はすべて `false`。
    - 小数を含むクラスの `<=> = default` は、自動で `partial_ordering` になる。
    - `sort` に使うときは、NaN を含まないことが前提。

## 関数の詳しい説明

### std::partial_ordering {#partial_ordering}

```cpp
struct partial_ordering {
  static const partial_ordering less, equivalent, greater, unordered;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `r` | `partial_ordering` | 比較結果 |

- 戻り値: `less` / `equivalent` / `greater` / `unordered`
- 計算量: O(1)

```cpp
#include <cmath>
#include <compare>
#include <print>

int main() {
  double nan = std::nan("");
  std::partial_ordering r = (nan <=> 1.0);
  std::println("{} {}", r == std::partial_ordering::unordered, r < 0);
}
```

```text title="実行結果"
true false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 座標・速度を含む構造体の比較 | `float` のメンバがあると `partial_ordering` |

## よくあるミス

??? failure "NaN を含むデータを sort する"
    大小が決められないので、`sort` の結果が不定になります。NaN を取り除いてから並べ替えます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`strong_ordering`](strong_ordering.md) | 常に比べられる |
| [`isnan`](../numeric/cmath/isnan.md) | NaN を調べる |

## コンパイラ対応

C++20 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 比べられない場合がある
    - [x] 小数の比較結果
    - [x] unordered は全部 false

## 関連ページ

- [cpprefjp: std::partial_ordering](https://cpprefjp.github.io/reference/compare/partial_ordering.html)
- [cppreference: std::partial_ordering](https://en.cppreference.com/w/cpp/utility/compare/partial_ordering)
