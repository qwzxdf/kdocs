---
title: std::default_accessor
summary: "mdspan の要素への標準のアクセス方法（ふつうのポインタ）。"
order: 900
tags:
  - コンテナ
---

# std::default_accessor

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <mdspan>`
</div>

`std::mdspan` は、データへのアクセスの方法（添字から実際の要素を取り出す処理）を、アクセサーという部品に任せています。普通は、ポインターの添字参照でよく、それを行う標準の部品が `std::default_accessor<T>` です。自作のアクセサーを書くと、読み取り時に変換する、といったことができます。

!!! tip "ポイント"
    - `mdspan` の 4 番目のテンプレート引数の既定値
    - `access(p, i)` は `p[i]` を返す
    - `offset(p, i)` は `p + i` を返す
    - 自作のアクセサーで、型の変換や範囲の検査を挟める

!!! info "このページを読む前に"
    [`std::mdspan`](mdspan.md) を先に読んでください。

## 関数の詳しい説明

### std::default_accessor {#default_accessor}

<span class="ver ver-23">C++23</span>

```cpp
template <class ElementType>
struct default_accessor {
  using offset_policy = default_accessor;
  using element_type = ElementType;
  using reference = ElementType&;
  using data_handle_type = ElementType*;

  constexpr reference access(data_handle_type p, std::size_t i) const noexcept;
  constexpr data_handle_type offset(data_handle_type p, std::size_t i) const noexcept;
};
```

`mdspan` は、レイアウト（添字から 1 次元の位置を求める）と、アクセサー（その位置の要素を得る）を分けています。レイアウトが並び方、アクセサーが取り出し方です。

自作のアクセサーの例には、`float` を内部では 16 ビット（`half`）で持ち、読むときに `float` に変換する、といったものがあります。`reference` が実際の参照でなく、変換結果の値を返すプロキシでもよいのです。

## 実際に動かしてみる

```cpp
#include <array>
#include <mdspan>
#include <print>

int main() {
  std::array<int, 4> data = {10, 20, 30, 40};

  std::default_accessor<int> acc;
  std::println("access(2) = {}", acc.access(data.data(), 2));
  std::println("offset の差 = {}", acc.offset(data.data(), 3) - data.data());

  // mdspan は、これを既定のアクセサーとして使う
  std::mdspan<int, std::extents<std::size_t, 2, 2>> m(data.data());
  std::println("m[1, 0] = {}", m[1, 0]);
}
```

```text title="実行結果"
access(2) = 30
offset の差 = 3
m[1, 0] = 30
```

## ゲームでの使いどころ

普段は触りません。データの保存形式を変えたい（半精度の浮動小数点数など）ときに、自作します。

## よくあるミス

??? failure "レイアウトとアクセサーを取り違える"
    レイアウトは位置の計算、アクセサーは取り出しです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`layout_left`](layout_left.md) | レイアウトの例 |
| [`aligned_accessor`](aligned_accessor.md) | アライメントを保証するアクセサー |
| [`mdspan`](mdspan.md) | 使う側 |

## コンパイラ対応

C++23 から使えます。

## 関連ページ

- [cpprefjp: std::default_accessor](https://cpprefjp.github.io/reference/mdspan/default_accessor.html)
- [cppreference: std::default_accessor](https://en.cppreference.com/w/cpp/container/mdspan/default_accessor)
