---
title: std::views::values
summary: "map などから、値だけが見える範囲を作る。"
order: 14
group: ビュー（std::views）
tags:
  - アルゴリズム
---

# std::views::values

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

`std::views::values` は、**`map` のような「(キー, 値) の組」の範囲から、値だけが見える範囲**を作るビューです。`elements<1>` の別名です。値の合計や最大を調べるときに便利です。

!!! tip "ポイント"
    - 値の合計: `std::ranges::fold_left(m | values, 0, std::plus{})`。
    - 値を書き換えることもできる（`map` の値は書き換え可能）。
    - キーだけなら [`keys`](keys.md)。

!!! info "このページを読む前に"
    [ranges とビュー](../../../basics/ranges.md)、[ラムダ式](../../../basics/lambda.md) を先に読むと分かりやすいです。

## 関数の詳しい説明

### views::values {#values}

```cpp
m | std::views::values
std::views::values(m)
```

- 戻り値: 値だけのビュー
- 計算量: O(1)

```cpp
#include <algorithm>
#include <functional>
#include <map>
#include <print>
#include <ranges>
#include <string>

int main() {
  std::map<std::string, int> price = {{"potion", 50}, {"sword", 300}};

  int total = std::ranges::fold_left(price | std::views::values, 0, std::plus{});
  std::println("合計 {}", total);

  for (int& p : price | std::views::values) {
    p *= 2;  // 値は書き換えられる
  }
  std::println("{}", price["potion"]);
}
```

```text title="実行結果"
合計 350
100
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 所持金（値）の合計を求める | `fold_left(wallet | values, 0, plus)` |
| 全アイテムの値段を一括で変更する | `for (auto& p : prices | values) p *= 2;` |

## よくあるミス

??? failure "キーまで書き換えようとする"
    `map` のキーは `const` なので、書き換えられません。値だけが書き換え可能です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::views::keys`](keys.md) | キーだけを見る |
| [`std::views::elements`](elements.md) | 任意の番号を取る |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `map` の値だけを見る
    - [x] `elements<1>` の別名
    - [x] 値は書き換えられる

## 関連ページ

- [cpprefjp: std::ranges::values_view](https://cpprefjp.github.io/reference/ranges/values_view.html)
- [cppreference: std::ranges::values_view](https://en.cppreference.com/w/cpp/ranges/values_view)
