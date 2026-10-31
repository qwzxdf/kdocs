---
title: std::multiplies
summary: "掛け算をする関数オブジェクト（`*` の代わり）。"
order: 5
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::multiplies

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <functional>`
</div>

アルゴリズムに「足し算をする」「大きい順に並べる」といった演算を渡したいとき、ラムダ `[](int a, int b) { return a * b; }` を毎回書くのは冗長です。`std::multiplies` は、<strong>演算子 `*`（掛け算）を関数オブジェクトにしたもの</strong>で、そのままアルゴリズムに渡せます。

!!! tip "ポイント"
    - `std::multiplies<>{}(2 つの値)` は演算子 `*` と同じ結果
    - 型を省略した `std::multiplies<>` が推奨。型を自動で推論する
    - `std::accumulate` や `std::sort` などの引数として渡せる
    - 関数オブジェクトなので、インライン化されやすく、速い

!!! info "このページを読む前に"
    [`<functional>`](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::multiplies {#multiplies}

```cpp
template <class T = void>
struct multiplies {
  constexpr auto operator()(const T& x, const T& y) const;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 値 | 1 つ目の値 |
| `y` | 値 | 2 つ目の値 |

`std::multiplies<>{}(a, b)` は `a * b` と同じ結果を返します。数値の掛け算に加えて、`*` を持つ型（行列やベクトルの自作の型）にも使えます。`std::accumulate` に渡して、全体の積を求めるときによく使います。

## 実際に動かしてみる

```cpp
#include <functional>
#include <numeric>
#include <print>
#include <vector>

int main() {
  std::println("std::multiplies<>{{}}(4, 3) = {}", std::multiplies<>{}(4, 3));
  const std::vector<int> v = {1, 2, 3, 4};
  std::println("v の積 = {}", std::accumulate(v.begin(), v.end(), 1, std::multiplies<>{}));
}
```

```text title="実行結果"
std::multiplies<>{}(4, 3) = 12
v の積 = 24
```

## ゲームでの使いどころ

複数の倍率を掛け合わせた、最終的な倍率を求めます。

```cpp
std::vector<double> rates = {1.5, 2.0, 0.5};
double total = std::accumulate(rates.begin(), rates.end(), 1.0, std::multiplies<>{});   // 1.5
```

## よくあるミス

??? failure "積の初期値を 0 にする"
    `accumulate` の初期値が `0` だと、何を掛けても `0` になります。積の初期値は `1` です。

??? failure "整数であふれる"
    `int` の積は、すぐ桁あふれします（符号つきは未定義動作）。大きくなるなら、`std::int64_t` や `double` で受けます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`plus`](plus.md) | 足し算 |
| [`divides`](divides.md) | 割り算 |
| [`accumulate`](../../algorithms/accumulate.md) | 畳み込みを行うアルゴリズム |

## コンパイラ対応

C++98 から使えます（`<>` の型省略形は C++14 から）。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::multiplies<>` は演算子 `*`（掛け算）の関数オブジェクト
    - [x] 型を省略した `<>` の形が標準
    - [x] アルゴリズムの引数に渡せる

## 関連ページ

- [cpprefjp: std::multiplies](https://cpprefjp.github.io/reference/functional/multiplies.html)
- [cppreference: std::multiplies](https://en.cppreference.com/w/cpp/utility/functional/multiplies)
