---
title: std::negate
summary: "`-a`（符号の反転）を表す関数オブジェクト。"
order: 900
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::negate

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <functional>`
</div>

アルゴリズムに「足し算をする」「大きい順に並べる」といった演算を渡したいとき、ラムダ `[](int a, int b) { return a - b; }` を毎回書くのは冗長です。`std::negate` は、<strong>演算子 `-（単項）`（符号の反転）を関数オブジェクトにしたもの</strong>で、そのままアルゴリズムに渡せます。

!!! tip "ポイント"
    - `std::negate<>{}(値)` は演算子 `-（単項）` と同じ結果
    - 型を省略した `std::negate<>` が推奨。型を自動で推論する
    - `std::accumulate` や `std::sort` などの引数として渡せる
    - 関数オブジェクトなので、インライン化されやすく、速い

!!! info "このページを読む前に"
    [`<functional>`](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::negate {#negate}

```cpp
template <class T = void>
struct negate {
  constexpr auto operator()(const T& x) const;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 値 | 対象の値 |

`std::negate<>{}(x)` は `-x` と同じ結果を返します。引数が 1 つの、単項の関数オブジェクトです。符号つきの整数の最小値（`INT_MIN`）の符号を反転すると、結果が収まらず、未定義動作になります。符号なしの整数では、0 から引いた値（巻き戻った値）になります。

## 実際に動かしてみる

```cpp
#include <functional>
#include <print>

int main() {
  std::println("std::negate<>{{}}(5) = {}", std::negate<>{}(5));
}
```

```text title="実行結果"
std::negate<>{}(5) = -5
```

## ゲームでの使いどころ

方向ベクトルの成分を、まとめて反転します。

```cpp
std::vector<float> direction = {1.0f, -2.0f, 0.5f};
std::transform(direction.begin(), direction.end(), direction.begin(), std::negate<>{});   // -1, 2, -0.5
```

## よくあるミス

??? failure "INT_MIN の符号を反転する"
    `-INT_MIN` は `int` に収まらないので、未定義動作です。

??? failure "符号なし整数に使って負になると思う"
    `unsigned` に使うと、負にならず、`0` から引いた巨大な値になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`minus`](minus.md) | 2 つの値の引き算 |
| [`logical_not`](logical_not.md) | 真偽値の反転 |
| [`bit_not`](bit_not.md) | ビットの反転 |

## コンパイラ対応

C++98 から使えます（`<>` の型省略形は C++14 から）。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::negate<>` は演算子 `-（単項）`（符号の反転）の関数オブジェクト
    - [x] 型を省略した `<>` の形が標準
    - [x] アルゴリズムの引数に渡せる

## 関連ページ

- [cpprefjp: std::negate](https://cpprefjp.github.io/reference/functional/negate.html)
- [cppreference: std::negate](https://en.cppreference.com/w/cpp/utility/functional/negate)
