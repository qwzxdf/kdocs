---
title: std::gslice
summary: "valarray から、多次元の添字（開始位置・各次元の個数・各次元の間隔）で要素を選ぶ。"
order: 900
tags:
  - コンテナ
---

# std::gslice

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <valarray>`
</div>

`slice` は 1 次元の選び方です。行列の一部の矩形のように、多次元の選び方は `gslice(start, sizes, strides)` で指定します。

!!! tip "ポイント"
    - `valarray` の部分選択に使う。
    - `v[選び方]` の形で書く。
    - ゲームではほとんど使わない（`span` や `mdspan` のほうが一般的）。

!!! info "このページを読む前に"
    [`std::valarray`](valarray.md) を先に読んでください。

## 関数の詳しい説明

### std::gslice {#gslice}

```cpp
class gslice {
 public:
  gslice(std::size_t start, const std::valarray<std::size_t>& sizes, const std::valarray<std::size_t>& strides);
};
```

- 戻り値: 選んだ要素
- 計算量: 選んだ要素の数に比例


## 実際に動かしてみる

```cpp
#include <print>
#include <valarray>

int main() {
  std::valarray<int> v(16);
  for (int i = 0; i < 16; ++i) v[i] = i;
  std::valarray<std::size_t> sizes = {2, 2};
  std::valarray<std::size_t> strides = {4, 1};
  std::valarray<int> s = v[std::gslice(0, sizes, strides)];
  std::println("{} {} {} {}", s[0], s[1], s[2], s[3]);
}
```

```text title="実行結果"
0 1 4 5
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 配列の一部を一括で書き換える | `v[std::gslice(...)] = x;` |

## よくあるミス

??? failure "次元の数が合わない"
    `sizes` と `strides` は、同じ長さ（次元の数）にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`valarray`](valarray.md) | 数値計算用の配列 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] valarray から、多次元の添字（開始位置・各次元の個数・各次元の間隔）で要素を選ぶ
    - [x] `v[...]` の形で使う
    - [x] valarray 専用

## 関連ページ

- [cpprefjp: std::gslice](https://cpprefjp.github.io/reference/valarray/gslice.html)
- [cppreference: std::gslice](https://en.cppreference.com/w/cpp/numeric/valarray/gslice)
