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

`std::valarray` の、飛び飛びの位置の要素を、まとめて書き換えたい。`v[valarray<size_t>{0, 2, 5}]` のように、添字の列を渡すと、その位置の要素だけを選べます。その結果が `std::indirect_array` です。

!!! tip "ポイント"
    - `v[添字の valarray<size_t>]` で、指定した位置の要素を選ぶ
    - 代入すると、選ばれた位置だけが更新される
    - 添字は重複しないこと（重複すると、代入の結果が不定）
    - 範囲外の添字は未定義動作

!!! info "このページを読む前に"
    [`std::valarray`](valarray.md) を先に読んでください。

## 関数の詳しい説明

### std::indirect_array {#indirect_array}

```cpp
template <class T> class indirect_array;
```

直接作らず、`valarray<T>::operator[](const valarray<std::size_t>&)` の戻り値として得ます。

`mask_array` が「条件」で選ぶのに対し、こちらは「位置」で選びます。位置のリストを、別の計算で作って渡す場面に向きます。

選んだ要素を取り出すと、新しい `valarray` になります。

## 実際に動かしてみる

```cpp
#include <iterator>
#include <print>
#include <valarray>
#include <vector>

int main() {
  std::valarray<int> v = {10, 20, 30, 40, 50, 60};

  // 添字 0, 2, 5 の要素を選んで書き換える
  const std::valarray<std::size_t> idx = {0, 2, 5};
  v[idx] = 0;
  std::println("{}", std::vector<int>(std::begin(v), std::end(v)));

  // 取り出すと、新しい valarray になる
  const std::valarray<int> w = {1, 2, 3, 4};
  const std::valarray<int> picked(w[std::valarray<std::size_t>{3, 1}]);
  std::println("{}", std::vector<int>(std::begin(picked), std::end(picked)));
}
```

```text title="実行結果"
[0, 20, 0, 40, 50, 0]
[4, 2]
```

## ゲームでの使いどころ

位置のリストを別に持つ数値計算で使います。

## よくあるミス

??? failure "添字を重複させる"
    代入の結果が不定になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`mask_array`](mask_array.md) | 条件で選ぶ |
| [`slice`](slice.md) | 等間隔で選ぶ |
| [`valarray`](valarray.md) | 対象 |

## コンパイラ対応

C++98 から使えます。

## 関連ページ

- [cpprefjp: std::indirect_array](https://cpprefjp.github.io/reference/valarray/indirect_array.html)
- [cppreference: std::indirect_array](https://en.cppreference.com/w/cpp/numeric/valarray/indirect_array)
