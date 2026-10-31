---
title: std::divides
summary: "`a / b` を表す関数オブジェクト。"
order: 900
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::divides

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <functional>`
</div>

アルゴリズムに「足し算をする」「大きい順に並べる」といった演算を渡したいとき、ラムダ `[](int a, int b) { return a / b; }` を毎回書くのは冗長です。`std::divides` は、<strong>演算子 `/`（割り算）を関数オブジェクトにしたもの</strong>で、そのままアルゴリズムに渡せます。

!!! tip "ポイント"
    - `std::divides<>{}(2 つの値)` は演算子 `/` と同じ結果
    - 型を省略した `std::divides<>` が推奨。型を自動で推論する
    - `std::accumulate` や `std::sort` などの引数として渡せる
    - 関数オブジェクトなので、インライン化されやすく、速い

!!! info "このページを読む前に"
    [`<functional>`](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::divides {#divides}

```cpp
template <class T = void>
struct divides {
  constexpr auto operator()(const T& x, const T& y) const;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 値 | 1 つ目の値 |
| `y` | 値 | 2 つ目の値 |

`std::divides<>{}(a, b)` は `a / b` と同じ結果を返します。整数どうしの割り算は小数点以下を切り捨て、0 で割ると未定義動作です。浮動小数点数の 0 割りは、無限大か NaN になります。

## 実際に動かしてみる

```cpp
#include <functional>
#include <print>

int main() {
  std::println("std::divides<>{{}}(7, 2) = {}", std::divides<>{}(7, 2));
}
```

```text title="実行結果"
std::divides<>{}(7, 2) = 3
```

## ゲームでの使いどころ

配列の各要素を、別の配列の値で割ります（正規化）。

```cpp
std::vector<float> value = {50.0f, 30.0f, 20.0f};
std::vector<float> total(3, 100.0f);
std::vector<float> ratio(3);
std::transform(value.begin(), value.end(), total.begin(), ratio.begin(), std::divides<>{});   // 0.5, 0.3, 0.2
```

## よくあるミス

??? failure "整数の 0 割り"
    整数を 0 で割ると未定義動作です。割る側が 0 になりうるなら、事前に確かめます。

??? failure "整数の割り算で小数が出ると思う"
    `divides<>{}(1, 2)` は `0` です。小数が欲しいなら、片方を `double` にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`multiplies`](multiplies.md) | 掛け算 |
| [`modulus`](modulus.md) | 割り算の余り |
| [`negate`](negate.md) | 符号を反転する |

## コンパイラ対応

C++98 から使えます（`<>` の型省略形は C++14 から）。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::divides<>` は演算子 `/`（割り算）の関数オブジェクト
    - [x] 型を省略した `<>` の形が標準
    - [x] アルゴリズムの引数に渡せる

## 関連ページ

- [cpprefjp: std::divides](https://cpprefjp.github.io/reference/functional/divides.html)
- [cppreference: std::divides](https://en.cppreference.com/w/cpp/utility/functional/divides)
