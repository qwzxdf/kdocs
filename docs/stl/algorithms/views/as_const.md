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

範囲の要素を、読むだけにしたい。ビューを関数に渡すとき、中身を書き換えられては困る、という場面があります。`std::views::as_const` は、要素を `const` の参照として見せるビューを作ります。C++23 で追加されました。

!!! tip "ポイント"
    - 要素を `const` の参照として見せる
    - 元の範囲の要素は、書き換えられなくなる
    - すでに `const` な参照を返す範囲には、何もしない
    - `std::ranges::as_const_view` が実体

!!! info "このページを読む前に"
    [ビュー](../views.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::views::as_const {#as_const}

<span class="ver ver-23">C++23</span>

```cpp
inline constexpr /* 未規定 */ as_const = /* 未規定 */;
// v | std::views::as_const
```

`const std::vector<int>&` を渡せば読み取り専用になりますが、ビューは `const` なオブジェクトでも、要素を書き換えられることがあります（ビューの `const` は、浅い const です）。`as_const` は、要素の参照の型を `const` にすることで、この抜け道をふさぎます。

```cpp
for (auto& x : v | std::views::as_const) {
  // x は const int&。x = 1 はコンパイルできない
}
```

関数の引数に、`std::ranges::input_range` として範囲を渡すときの、読み取り専用の保証として使えます。

## 実際に動かしてみる

```cpp
#include <print>
#include <ranges>
#include <type_traits>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3};

  auto cv = v | std::views::as_const;
  using Ref = std::ranges::range_reference_t<decltype(cv)>;
  static_assert(std::is_const_v<std::remove_reference_t<Ref>>);

  int sum = 0;
  for (const int& x : cv) sum += x;
  std::println("合計: {}", sum);
  // cv[0] = 9;   // コンパイル エラー
}
```

```text title="実行結果"
合計: 6
```

## ゲームでの使いどころ

範囲を受け取る関数で、読み取り専用であることを、型で保証するときに使います。

## よくあるミス

??? failure "ビューが const なら書き換えられないと思う"
    浅い const です。`as_const` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`all`](all.md) | ビューへの変換 |
| [`ref_view`](ref_view.md) | 参照を持つビュー |
| `std::as_const` | 値を const 参照にする |

## コンパイラ対応

C++23 から使えます。

## 関連ページ

- [cpprefjp: std::ranges::as_const_view](https://cpprefjp.github.io/reference/ranges/as_const_view.html)
- [cppreference: std::ranges::as_const_view](https://en.cppreference.com/w/cpp/ranges/as_const_view)
