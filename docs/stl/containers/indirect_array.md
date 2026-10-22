---
title: std::indirect_array
summary: "valarray から、添字の配列で選んだ要素への参照。"
order: 900
tags:
  - コンテナ
---

# std::indirect_array

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <valarray>`
</div>

`v[indices]`（`indices` は `valarray<size_t>`）と書くと、指定した添字の要素を選べます。その結果の型が `indirect_array` です。代入すると、元の `valarray` の対応する要素が書き換わります。

!!! tip "ポイント"
    - `valarray` の部分選択に使う。
    - `v[選び方]` の形で書く。
    - ゲームではほとんど使わない（`span` や `mdspan` のほうが一般的）。

!!! info "このページを読む前に"
    [`std::valarray`](valarray.md) を先に読んでください。

## 関数の詳しい説明

### std::indirect_array {#indirect_array}

```cpp
template <class T>
class indirect_array;  // v[indices] が返す型
```

- 戻り値: 選んだ要素
- 計算量: 選んだ要素の数に比例


## 実際に動かしてみる

```cpp
#include <print>
#include <valarray>

int main() {
  std::valarray<int> v = {1, 2, 3, 4};
  std::valarray<std::size_t> idx = {3, 0};
  v[idx] = 9;
  std::println("{} {} {} {}", v[0], v[1], v[2], v[3]);
}
```

```text title="実行結果"
9 2 3 9
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 配列の一部を一括で書き換える | `v[std::indirect_array(...)] = x;` |

## よくあるミス

??? failure "範囲外の添字"
    範囲外の添字は未定義動作です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`valarray`](valarray.md) | 数値計算用の配列 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] valarray から、添字の配列で選んだ要素への参照
    - [x] `v[...]` の形で使う
    - [x] valarray 専用

## 関連ページ

- [cpprefjp: std::indirect_array](https://cpprefjp.github.io/reference/valarray/indirect_array.html)
- [cppreference: std::indirect_array](https://en.cppreference.com/w/cpp/numeric/valarray/indirect_array)
