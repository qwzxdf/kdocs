---
title: std::greater_equal
summary: "`a >= b` を表す関数オブジェクト。"
order: 900
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::greater_equal

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <functional>`
</div>

アルゴリズムに「足し算をする」「大きい順に並べる」といった演算を渡したいとき、ラムダ `[](int a, int b) { return a >= b; }` を毎回書くのは冗長です。`std::greater_equal` は、<strong>演算子 `>=`（以上か）を関数オブジェクトにしたもの</strong>で、そのままアルゴリズムに渡せます。

!!! tip "ポイント"
    - `std::greater_equal<>{}(2 つの値)` は演算子 `>=` と同じ結果
    - 型を省略した `std::greater_equal<>` が推奨。型を自動で推論する
    - `std::accumulate` や `std::sort` などの引数として渡せる
    - 関数オブジェクトなので、インライン化されやすく、速い

!!! info "このページを読む前に"
    [`<functional>`](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::greater_equal {#greater_equal}

```cpp
template <class T = void>
struct greater_equal {
  constexpr auto operator()(const T& x, const T& y) const;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 値 | 1 つ目の値 |
| `y` | 値 | 2 つ目の値 |

`std::greater_equal<>{}(a, b)` は `a >= b` と同じ結果を返します。`std::sort` などの比較関数としては使えません。比較関数には「厳密な弱順序」が要り、等しい値に対して `true` を返す `>=` は、その条件を満たさないためです。

## 実際に動かしてみる

```cpp
#include <functional>
#include <print>

int main() {
  std::println("std::greater_equal<>{{}}(3, 3) = {}", std::greater_equal<>{}(3, 3));
}
```

```text title="実行結果"
std::greater_equal<>{}(3, 3) = true
```

## ゲームでの使いどころ

全部の能力値が、必要な値以上かを調べます。

```cpp
std::vector<int> stats = {10, 15, 8};
std::vector<int> required = {10, 12, 5};
bool ok = std::equal(stats.begin(), stats.end(), required.begin(), std::greater_equal<>{});   // true
```

## よくあるミス

??? failure "sort の比較関数に使う"
    等しい要素に `true` を返す比較関数は、`sort` で未定義動作の原因になります。降順なら `std::greater` を使います。

??? failure "equal に渡すと、全体が等しい意味だと思う"
    `std::equal` は 2 つ目の引数を、述語として使えます。ここでは、全要素が条件を満たすかを調べているだけで、全体の等しさではありません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`greater`](greater.md) | 厳密な「より大きい」 |
| [`less_equal`](less_equal.md) | 以下を返す |
| [`equal_to`](equal_to.md) | 等しいかを返す |

## コンパイラ対応

C++98 から使えます（`<>` の型省略形は C++14 から）。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::greater_equal<>` は演算子 `>=`（以上か）の関数オブジェクト
    - [x] 型を省略した `<>` の形が標準
    - [x] アルゴリズムの引数に渡せる

## 関連ページ

- [cpprefjp: std::greater_equal](https://cpprefjp.github.io/reference/functional/greater_equal.html)
- [cppreference: std::greater_equal](https://en.cppreference.com/w/cpp/utility/functional/greater_equal)
