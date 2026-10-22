---
title: std::slice
summary: "valarray から、開始位置・個数・間隔で要素を選ぶ。"
order: 900
tags:
  - コンテナ
---

# std::slice

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <valarray>`
</div>

`valarray` の中から、1 つおき、あるいは行列の列のように、一定の間隔の要素を選びたいことがあります。`slice(start, size, stride)` で選び方を指定して、`v[slice]` と書きます。

!!! tip "ポイント"
    - `valarray` の部分選択に使う。
    - `v[選び方]` の形で書く。
    - ゲームではほとんど使わない（`span` や `mdspan` のほうが一般的）。

!!! info "このページを読む前に"
    [`std::valarray`](valarray.md) を先に読んでください。

## 関数の詳しい説明

### std::slice {#slice}

```cpp
class slice {
 public:
  slice(std::size_t start, std::size_t size, std::size_t stride);
};
```

- 戻り値: 選んだ要素
- 計算量: 選んだ要素の数に比例


## 実際に動かしてみる

```cpp
#include <print>
#include <valarray>

int main() {
  std::valarray<int> v = {1, 2, 3, 4, 5, 6};
  std::valarray<int> s = v[std::slice(1, 3, 2)];
  std::println("{} {} {}", s[0], s[1], s[2]);
}
```

```text title="実行結果"
2 4 6
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 配列の一部を一括で書き換える | `v[std::slice(...)] = x;` |

## よくあるミス

??? failure "結果が元を指すと思う"
    `v[slice]` を `valarray` に代入すると、コピーされます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`valarray`](valarray.md) | 数値計算用の配列 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] valarray から、開始位置・個数・間隔で要素を選ぶ
    - [x] `v[...]` の形で使う
    - [x] valarray 専用

## 関連ページ

- [cpprefjp: std::slice](https://cpprefjp.github.io/reference/valarray/slice.html)
- [cppreference: std::slice](https://en.cppreference.com/w/cpp/numeric/valarray/slice)
