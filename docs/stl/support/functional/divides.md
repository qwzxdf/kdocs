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

`std::divides<>`（型引数を省略したもの）は、`operator()` が任意の型の引数を受け取り、`/` の結果を返します。`std::divides<int>` のように型を指定する古い書き方もありますが、型が変わるたびに書き直しが必要で、混在した型の演算もできません。省略形が現在の標準です。

戻り値は、演算子と同じ型・同じ値です。演算子をオーバーロードした自作の型でも、そのまま使えます。

ラムダ式で書いても同じ結果ですが、`std::divides<>{}` のほうが短く、意図が名前で伝わります。

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

標準のアルゴリズムや、自作のテンプレートに、演算を値として渡すときに使います。短い演算にはこちら、複雑な演算にはラムダ式、と使い分けます。

## よくあるミス

??? failure "`std::divides<int>` と型を固定して、他の型で変換が起きる"
    `std::divides<>` と省略します。

??? failure "`<functional>` を忘れてコンパイルエラーになる"
    `#include <functional>` を書きます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`<functional>`](../functional.md) | 関数オブジェクトの一覧 |
| [`identity`](identity.md) | 値をそのまま返す |

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
