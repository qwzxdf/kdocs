---
title: std::inner_product
summary: "2 つの範囲の内積（要素ごとの積の合計）を求める。"
order: 27
tags:
  - アルゴリズム
---

# std::inner_product

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <numeric>`
</div>

`std::inner_product` は、**2 つの範囲の内積**（要素ごとに掛けて、合計したもの）を求める関数です。ベクトルの内積が `vector` 同士で簡単に計算できます。C++17 以降は、並列化できる [`transform_reduce`](transform_reduce.md) が後継です。

!!! tip "ポイント"
    - 結果の型は、初期値の型で決まる。`float` なら `0.0f` を渡す。
    - 2 つ目の範囲は、1 つ目と同じ長さ以上であること。
    - 足し算・掛け算を別の演算に置き換えることもできる。

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。ヘッダーは `<numeric>` です。

## 関数の詳しい説明

### std::inner_product {#inner_product}

```cpp
template <class It1, class It2, class T>
T inner_product(It1 first1, It1 last1, It2 first2, T init);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `first1`, `last1` | イテレータ | 1 つ目の範囲 |
| `first2` | イテレータ | 2 つ目の範囲の先頭 |
| `init` | T | 合計の初期値（結果の型） |

- 戻り値: 内積
- 計算量: O(n)

```cpp
#include <numeric>
#include <print>
#include <vector>

int main() {
  std::vector<float> a = {1.0f, 0.0f, 0.0f};  // X 軸
  std::vector<float> b = {0.5f, 0.5f, 0.0f};

  float dot = std::inner_product(a.begin(), a.end(), b.begin(), 0.0f);
  std::println("内積 {}", dot);
}
```

```text title="実行結果"
内積 0.5
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 3D ベクトルの内積（配列で持っている場合） | `inner_product(a, b, 0.0f)` |

## よくあるミス

??? failure "初期値に 0 を渡す"
    `float` の内積に `0`（int）を渡すと、結果が `int` になって小数が切り捨てられます。`0.0f` を渡します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::transform_reduce`](transform_reduce.md) | 並列化できる後継 |
| SimpleMath の `Vector3::Dot` | ゲームでは、ベクトル型の `Dot` を使うのが普通 |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 2 つの範囲の内積
    - [x] 初期値の型が結果の型
    - [x] 後継は `transform_reduce`

## 関連ページ

- [cpprefjp: std::inner_product](https://cpprefjp.github.io/reference/numeric/inner_product.html)
- [cppreference: std::inner_product](https://en.cppreference.com/w/cpp/algorithm/inner_product)
