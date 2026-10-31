---
title: std::less_equal
summary: "`a <= b` を表す関数オブジェクト。"
order: 900
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::less_equal

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <functional>`
</div>

アルゴリズムに「足し算をする」「大きい順に並べる」といった演算を渡したいとき、ラムダ `[](int a, int b) { return a <= b; }` を毎回書くのは冗長です。`std::less_equal` は、<strong>演算子 `<=`（以下か）を関数オブジェクトにしたもの</strong>で、そのままアルゴリズムに渡せます。

!!! tip "ポイント"
    - `std::less_equal<>{}(2 つの値)` は演算子 `<=` と同じ結果
    - 型を省略した `std::less_equal<>` が推奨。型を自動で推論する
    - `std::accumulate` や `std::sort` などの引数として渡せる
    - 関数オブジェクトなので、インライン化されやすく、速い

!!! info "このページを読む前に"
    [`<functional>`](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::less_equal {#less_equal}

```cpp
template <class T = void>
struct less_equal {
  constexpr auto operator()(const T& x, const T& y) const;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 値 | 1 つ目の値 |
| `y` | 値 | 2 つ目の値 |

`std::less_equal<>{}(a, b)` は `a <= b` と同じ結果を返します。`greater_equal` と同じで、`std::sort` の比較関数には使えません。「以下」は、等しい値でも `true` になり、厳密な弱順序の条件を破るからです。

## 実際に動かしてみる

```cpp
#include <functional>
#include <print>

int main() {
  std::println("std::less_equal<>{{}}(3, 3) = {}", std::less_equal<>{}(3, 3));
}
```

```text title="実行結果"
std::less_equal<>{}(3, 3) = true
```

## ゲームでの使いどころ

全部の値が上限以下かを調べます。

```cpp
std::vector<int> damage = {30, 50, 45};
std::vector<int> cap = {50, 50, 50};
bool ok = std::equal(damage.begin(), damage.end(), cap.begin(), std::less_equal<>{});   // true
```

## よくあるミス

??? failure "sort の比較関数に使う"
    等しい要素に `true` を返すので、未定義動作の原因になります。昇順なら `std::less` を使います。

??? failure "浮動小数点数の NaN を比べる"
    NaN との比較は、どれも `false` です。`less_equal` も `false` を返します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`less`](less.md) | 厳密な「より小さい」 |
| [`greater_equal`](greater_equal.md) | 以上を返す |
| [`equal_to`](equal_to.md) | 等しいかを返す |

## コンパイラ対応

C++98 から使えます（`<>` の型省略形は C++14 から）。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::less_equal<>` は演算子 `<=`（以下か）の関数オブジェクト
    - [x] 型を省略した `<>` の形が標準
    - [x] アルゴリズムの引数に渡せる

## 関連ページ

- [cpprefjp: std::less_equal](https://cpprefjp.github.io/reference/functional/less_equal.html)
- [cppreference: std::less_equal](https://en.cppreference.com/w/cpp/utility/functional/less_equal)
