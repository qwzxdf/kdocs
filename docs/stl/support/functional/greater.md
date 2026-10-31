---
title: std::greater
summary: "「大きいか」を比べる関数オブジェクト（`>` の代わり）。"
order: 2
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::greater

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <functional>`
</div>

アルゴリズムに「足し算をする」「大きい順に並べる」といった演算を渡したいとき、ラムダ `[](int a, int b) { return a > b; }` を毎回書くのは冗長です。`std::greater` は、<strong>演算子 `>`（大きいか）を関数オブジェクトにしたもの</strong>で、そのままアルゴリズムに渡せます。

!!! tip "ポイント"
    - `std::greater<>{}(2 つの値)` は演算子 `>` と同じ結果
    - 型を省略した `std::greater<>` が推奨。型を自動で推論する
    - `std::accumulate` や `std::sort` などの引数として渡せる
    - 関数オブジェクトなので、インライン化されやすく、速い

!!! info "このページを読む前に"
    [`<functional>`](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::greater {#greater}

```cpp
template <class T = void>
struct greater {
  constexpr auto operator()(const T& x, const T& y) const;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 値 | 1 つ目の値 |
| `y` | 値 | 2 つ目の値 |

`std::greater<>{}(a, b)` は `a > b` と同じ結果を返します。`std::sort` に渡すと、降順（大きい順）に並びます。`std::priority_queue` に渡すと、最小値が先頭に来るキュー（最小ヒープ）になります。標準のキューは最大値が先頭です。

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <functional>
#include <print>
#include <vector>

int main() {
  std::println("std::greater<>{{}}(3, 2) = {}", std::greater<>{}(3, 2));
  std::vector<int> v = {3, 1, 4, 2};
  std::sort(v.begin(), v.end(), std::greater<>{});
  for (int x : v) std::print("{} ", x);
  std::println("");
}
```

```text title="実行結果"
std::greater<>{}(3, 2) = true
4 3 2 1 
```

## ゲームでの使いどころ

スコアを大きい順に並べます。

```cpp
std::vector<int> score = {40, 90, 10, 70};
std::sort(score.begin(), score.end(), std::greater<>{});   // 90, 70, 40, 10

// 最小値が先頭に来るキュー（A* のオープンリストなど）
std::priority_queue<int, std::vector<int>, std::greater<int>> open;
```

## よくあるミス

??? failure "priority_queue がデフォルトで最小値を返すと思う"
    既定は最大値が先頭です。最小値を先に取り出したいなら、`std::greater` を渡します。

??? failure "降順にしたいのに less を渡す"
    `std::less` は昇順です。逆の向きを間違えやすいので、動かして確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`less`](less.md) | 昇順の比較（既定） |
| [`greater_equal`](greater_equal.md) | 以上を返す |
| [`not_equal_to`](not_equal_to.md) | 等しくないかを返す |

## コンパイラ対応

C++98 から使えます（`<>` の型省略形は C++14 から）。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::greater<>` は演算子 `>`（大きいか）の関数オブジェクト
    - [x] 型を省略した `<>` の形が標準
    - [x] アルゴリズムの引数に渡せる

## 関連ページ

- [cpprefjp: std::greater](https://cpprefjp.github.io/reference/functional/greater.html)
- [cppreference: std::greater](https://en.cppreference.com/w/cpp/utility/functional/greater)
