---
title: std::minus
summary: "`a - b` を表す関数オブジェクト。"
order: 900
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::minus

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <functional>`
</div>

アルゴリズムに「足し算をする」「大きい順に並べる」といった演算を渡したいとき、ラムダ `[](int a, int b) { return a - b; }` を毎回書くのは冗長です。`std::minus` は、<strong>演算子 `-`（引き算）を関数オブジェクトにしたもの</strong>で、そのままアルゴリズムに渡せます。

!!! tip "ポイント"
    - `std::minus<>{}(2 つの値)` は演算子 `-` と同じ結果
    - 型を省略した `std::minus<>` が推奨。型を自動で推論する
    - `std::accumulate` や `std::sort` などの引数として渡せる
    - 関数オブジェクトなので、インライン化されやすく、速い

!!! info "このページを読む前に"
    [`<functional>`](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::minus {#minus}

```cpp
template <class T = void>
struct minus {
  constexpr auto operator()(const T& x, const T& y) const;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 値 | 1 つ目の値 |
| `y` | 値 | 2 つ目の値 |

`std::minus<>{}(a, b)` は `a - b` と同じ結果を返します。足し算と違い、引数の順序で結果が変わります。1 つ目の引数から 2 つ目の引数を引きます。`std::adjacent_difference` の既定の演算が、この引き算です。

## 実際に動かしてみる

```cpp
#include <functional>
#include <print>

int main() {
  std::println("std::minus<>{{}}(5, 3) = {}", std::minus<>{}(5, 3));
}
```

```text title="実行結果"
std::minus<>{}(5, 3) = 2
```

## ゲームでの使いどころ

隣り合う座標の差（移動量）を求めます。

```cpp
std::vector<int> pos = {0, 3, 7, 12};
std::vector<int> delta(pos.size());
std::adjacent_difference(pos.begin(), pos.end(), delta.begin(), std::minus<>{});   // 0, 3, 4, 5
```

## よくあるミス

??? failure "引数の順序を取り違える"
    `minus<>{}(a, b)` は `a - b` です。`b - a` ではありません。`transform` に渡すときは、第 1 範囲が引かれる側になります。

??? failure "符号なし整数で負になる計算をする"
    `unsigned` の `3 - 5` は負にならず、巨大な値になります。差が負になりうるなら、符号つきの型を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`plus`](plus.md) | 足し算 |
| [`negate`](negate.md) | 符号を反転する（単項のマイナス） |
| [`adjacent_difference`](../../algorithms/adjacent_difference.md) | 隣との差を求めるアルゴリズム |

## コンパイラ対応

C++98 から使えます（`<>` の型省略形は C++14 から）。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::minus<>` は演算子 `-`（引き算）の関数オブジェクト
    - [x] 型を省略した `<>` の形が標準
    - [x] アルゴリズムの引数に渡せる

## 関連ページ

- [cpprefjp: std::minus](https://cpprefjp.github.io/reference/functional/minus.html)
- [cppreference: std::minus](https://en.cppreference.com/w/cpp/utility/functional/minus)
