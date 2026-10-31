---
title: std::logical_not
summary: "`!a` を表す関数オブジェクト。"
order: 900
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::logical_not

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <functional>`
</div>

アルゴリズムに「足し算をする」「大きい順に並べる」といった演算を渡したいとき、ラムダ `[](int a, int b) { return a ! b; }` を毎回書くのは冗長です。`std::logical_not` は、<strong>演算子 `!`（論理否定）を関数オブジェクトにしたもの</strong>で、そのままアルゴリズムに渡せます。

!!! tip "ポイント"
    - `std::logical_not<>{}(値)` は演算子 `!` と同じ結果
    - 型を省略した `std::logical_not<>` が推奨。型を自動で推論する
    - `std::accumulate` や `std::sort` などの引数として渡せる
    - 関数オブジェクトなので、インライン化されやすく、速い

!!! info "このページを読む前に"
    [`<functional>`](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::logical_not {#logical_not}

```cpp
template <class T = void>
struct logical_not {
  constexpr auto operator()(const T& x) const;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 値 | 対象の値 |

`std::logical_not<>{}(x)` は `!x` と同じ結果を返します。引数が 1 つの関数オブジェクトで、`bool` に変換できる型なら何でも受け取ります。ポインターに使うと、`nullptr` のとき `true` になります。

## 実際に動かしてみる

```cpp
#include <functional>
#include <print>

int main() {
  std::println("std::logical_not<>{{}}(true) = {}", std::logical_not<>{}(true));
}
```

```text title="実行結果"
std::logical_not<>{}(true) = false
```

## ゲームでの使いどころ

フラグの配列を、まとめて反転します。

```cpp
std::vector<bool> alive = {true, false, true};
std::vector<bool> dead(alive.size());
std::transform(alive.begin(), alive.end(), dead.begin(), std::logical_not<>{});   // false, true, false
```

## よくあるミス

??? failure "述語を反転したいときに使う"
    述語（引数を取って `bool` を返す関数）の結果を反転するには、`std::not_fn` を使います。`logical_not` は値を反転するもので、述語を包めません。

??? failure "bit_not と取り違える"
    `logical_not` は真偽値の `!`、`bit_not` はビットごとの `~` です。`!5` は `false` ですが、`~5` は `-6` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`not_fn`](not_fn.md) | 述語の結果を反転する |
| [`bit_not`](bit_not.md) | ビットを反転する |
| [`negate`](negate.md) | 符号を反転する |

## コンパイラ対応

C++98 から使えます（`<>` の型省略形は C++14 から）。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::logical_not<>` は演算子 `!`（論理否定）の関数オブジェクト
    - [x] 型を省略した `<>` の形が標準
    - [x] アルゴリズムの引数に渡せる

## 関連ページ

- [cpprefjp: std::logical_not](https://cpprefjp.github.io/reference/functional/logical_not.html)
- [cppreference: std::logical_not](https://en.cppreference.com/w/cpp/utility/functional/logical_not)
