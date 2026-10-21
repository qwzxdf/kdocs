---
title: std::views::as_const
summary: "要素を読み取り専用にして見る。"
order: 25
group: ビュー（std::views）
tags:
  - アルゴリズム
---

# std::views::as_const

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <ranges>`
</div>

`std::views::as_const` は、**範囲の要素を `const`（読み取り専用）として見せる**ビューです。「この関数の中では、中身を書き換えさせない」と、型で保証したいときに使います。

!!! tip "ポイント"
    - 書き換えようとすると**コンパイルエラー**になる。
    - 範囲を値渡し・コピーせずに、読み取り専用にできる。
    - C++23 の機能。

!!! info "このページを読む前に"
    [ranges とビュー](../../../basics/ranges.md)、[ラムダ式](../../../basics/lambda.md) を先に読むと分かりやすいです。

## 関数の詳しい説明

### views::as_const {#as_const}

```cpp
r | std::views::as_const
std::views::as_const(r)
```

- 戻り値: 読み取り専用のビュー
- 計算量: O(1)

```cpp
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3};

  auto cv = v | std::views::as_const;
  // cv[0] = 10;  // コンパイルエラー: 読み取り専用
  int sum = 0;
  for (int x : cv) sum += x;
  std::println("合計 {}", sum);
}
```

```text title="実行結果"
合計 6
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 描画関数に、データを読み取り専用で渡す | `draw(enemies | as_const)` |

## よくあるミス

??? failure "古い環境で使えない"
    C++23 の機能です。`const std::vector<int>&` で受け取る従来の書き方でも、同じ保証が得られます。

## 類似

| 名前 | 違い |
| --- | --- |
| `const std::vector<T>&` | 従来の読み取り専用の渡し方 |
| [`std::span<const T>`](../../containers/span.md) | 連続メモリの読み取り専用の窓 |

## コンパイラ対応

C++23 の機能です。GCC 13 / MSVC 19.34（VS 2022 17.4）以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 要素を読み取り専用にする
    - [x] 書き換えるとコンパイルエラー
    - [x] C++23

## 関連ページ

- [cpprefjp: std::ranges::as_const_view](https://cpprefjp.github.io/reference/ranges/as_const_view.html)
- [cppreference: std::ranges::as_const_view](https://en.cppreference.com/w/cpp/ranges/as_const_view)
