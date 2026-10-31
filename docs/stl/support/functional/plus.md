---
title: std::plus
summary: "足し算をする関数オブジェクト（`+` の代わり）。"
order: 4
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::plus

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <functional>`
</div>

アルゴリズムに「足し算をする」「大きい順に並べる」といった演算を渡したいとき、ラムダ `[](int a, int b) { return a + b; }` を毎回書くのは冗長です。`std::plus` は、<strong>演算子 `+`（足し算）を関数オブジェクトにしたもの</strong>で、そのままアルゴリズムに渡せます。

!!! tip "ポイント"
    - `std::plus<>{}(2 つの値)` は演算子 `+` と同じ結果
    - 型を省略した `std::plus<>` が推奨。型を自動で推論する
    - `std::accumulate` や `std::sort` などの引数として渡せる
    - 関数オブジェクトなので、インライン化されやすく、速い

!!! info "このページを読む前に"
    [`<functional>`](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::plus {#plus}

```cpp
template <class T = void>
struct plus {
  constexpr auto operator()(const T& x, const T& y) const;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 値 | 1 つ目の値 |
| `y` | 値 | 2 つ目の値 |

`std::plus<>{}(a, b)` は `a + b` と同じ結果を返します。`int` や `float` の足し算だけでなく、`+` を持つ型なら何でも使えます。`std::string` なら連結、自作のベクトル型なら、そのオーバーロードが呼ばれます。型引数を省略した `std::plus<>` は、`operator()` が任意の型を受け取るので、`int` と `double` のように、違う型を混ぜた足し算もできます。

`std::accumulate` の既定の演算が、まさにこの足し算です。

## 実際に動かしてみる

```cpp
#include <functional>
#include <numeric>
#include <print>
#include <vector>

int main() {
  std::println("std::plus<>{{}}(2, 3) = {}", std::plus<>{}(2, 3));
  const std::vector<int> v = {1, 2, 3, 4};
  std::println("v の合計 = {}", std::accumulate(v.begin(), v.end(), 0, std::plus<>{}));
}
```

```text title="実行結果"
std::plus<>{}(2, 3) = 5
v の合計 = 10
```

## ゲームでの使いどころ

2 つの配列を、要素ごとに足して、新しい配列を作ります。

```cpp
std::vector<int> base = {10, 20, 30};
std::vector<int> bonus = {1, 2, 3};
std::vector<int> total(base.size());
std::transform(base.begin(), base.end(), bonus.begin(), total.begin(), std::plus<>{});   // 11, 22, 33
```

## よくあるミス

??? failure "accumulate の初期値の型で切り捨てられる"
    `std::accumulate(v.begin(), v.end(), 0, std::plus<>{})` の初期値 `0` は `int` なので、`v` が `double` の列でも、途中の合計が `int` に切り捨てられます。`0.0` と書きます。

??? failure "std::plus<int> と固定して、型の混在で変換が起きる"
    `std::plus<int>` は引数を `int` に変換します。`double` の値を渡すと小数点以下が落ちます。`std::plus<>` と省略します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`minus`](minus.md) | 引き算 |
| [`multiplies`](multiplies.md) | 掛け算 |
| [`accumulate`](../../algorithms/accumulate.md) | 合計を取る（既定の演算が `plus`） |

## コンパイラ対応

C++98 から使えます（`<>` の型省略形は C++14 から）。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::plus<>` は演算子 `+`（足し算）の関数オブジェクト
    - [x] 型を省略した `<>` の形が標準
    - [x] アルゴリズムの引数に渡せる

## 関連ページ

- [cpprefjp: std::plus](https://cpprefjp.github.io/reference/functional/plus.html)
- [cppreference: std::plus](https://en.cppreference.com/w/cpp/utility/functional/plus)
