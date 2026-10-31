---
title: std::not_equal_to
summary: "`a != b` を表す関数オブジェクト。"
order: 900
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::not_equal_to

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <functional>`
</div>

アルゴリズムに「足し算をする」「大きい順に並べる」といった演算を渡したいとき、ラムダ `[](int a, int b) { return a != b; }` を毎回書くのは冗長です。`std::not_equal_to` は、<strong>演算子 `!=`（等しくないか）を関数オブジェクトにしたもの</strong>で、そのままアルゴリズムに渡せます。

!!! tip "ポイント"
    - `std::not_equal_to<>{}(2 つの値)` は演算子 `!=` と同じ結果
    - 型を省略した `std::not_equal_to<>` が推奨。型を自動で推論する
    - `std::accumulate` や `std::sort` などの引数として渡せる
    - 関数オブジェクトなので、インライン化されやすく、速い

!!! info "このページを読む前に"
    [`<functional>`](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::not_equal_to {#not_equal_to}

```cpp
template <class T = void>
struct not_equal_to {
  constexpr auto operator()(const T& x, const T& y) const;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 値 | 1 つ目の値 |
| `y` | 値 | 2 つ目の値 |

`std::not_equal_to<>{}(a, b)` は `a != b` と同じ結果を返します。2 つの値が違うときに `true` を返す、という性質を使って、`std::inner_product` に渡し、違う要素の数（ハミング距離）を数えられます。

## 実際に動かしてみる

```cpp
#include <functional>
#include <print>

int main() {
  std::println("std::not_equal_to<>{{}}(2, 3) = {}", std::not_equal_to<>{}(2, 3));
}
```

```text title="実行結果"
std::not_equal_to<>{}(2, 3) = true
```

## ゲームでの使いどころ

2 つの配列で、違う要素の個数を数えます。

```cpp
std::vector<int> a = {1, 2, 3, 4};
std::vector<int> b = {1, 9, 3, 8};
int diff = std::inner_product(a.begin(), a.end(), b.begin(), 0, std::plus<>{}, std::not_equal_to<>{});   // 2
```

## よくあるミス

??? failure "inner_product の初期値の型"
    初期値が `0`（`int`）だから、違いの個数が `int` で数えられます。初期値を `false`（`bool`）にすると、合計が `true` と `false` に丸められて、個数が分かりません。

??? failure "ポインターのアドレスを比べて、中身が違うと思う"
    `not_equal_to` はポインターの値を比べます。中身の比較には、指す先の値を取り出します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`equal_to`](equal_to.md) | 等しいかを返す |
| [`greater`](greater.md) | 大小の比較 |
| [`logical_not`](logical_not.md) | 真偽値の反転 |

## コンパイラ対応

C++98 から使えます（`<>` の型省略形は C++14 から）。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::not_equal_to<>` は演算子 `!=`（等しくないか）の関数オブジェクト
    - [x] 型を省略した `<>` の形が標準
    - [x] アルゴリズムの引数に渡せる

## 関連ページ

- [cpprefjp: std::not_equal_to](https://cpprefjp.github.io/reference/functional/not_equal_to.html)
- [cppreference: std::not_equal_to](https://en.cppreference.com/w/cpp/utility/functional/not_equal_to)
