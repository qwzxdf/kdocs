---
title: std::logical_and
summary: "`a && b` を表す関数オブジェクト。"
order: 900
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::logical_and

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <functional>`
</div>

アルゴリズムに「足し算をする」「大きい順に並べる」といった演算を渡したいとき、ラムダ `[](int a, int b) { return a && b; }` を毎回書くのは冗長です。`std::logical_and` は、<strong>演算子 `&&`（論理積）を関数オブジェクトにしたもの</strong>で、そのままアルゴリズムに渡せます。

!!! tip "ポイント"
    - `std::logical_and<>{}(2 つの値)` は演算子 `&&` と同じ結果
    - 型を省略した `std::logical_and<>` が推奨。型を自動で推論する
    - `std::accumulate` や `std::sort` などの引数として渡せる
    - 関数オブジェクトなので、インライン化されやすく、速い

!!! info "このページを読む前に"
    [`<functional>`](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::logical_and {#logical_and}

```cpp
template <class T = void>
struct logical_and {
  constexpr auto operator()(const T& x, const T& y) const;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 値 | 1 つ目の値 |
| `y` | 値 | 2 つ目の値 |

`std::logical_and<>{}(a, b)` は `a && b` と同じ結果を返します。関数オブジェクトにすると、引数は呼び出す前に両方評価されるので、`&&` の短絡評価（左が偽なら右を評価しない）は失われます。

## 実際に動かしてみる

```cpp
#include <functional>
#include <print>

int main() {
  std::println("std::logical_and<>{{}}(true, false) = {}", std::logical_and<>{}(true, false));
}
```

```text title="実行結果"
std::logical_and<>{}(true, false) = false
```

## ゲームでの使いどころ

2 つのフラグの配列を、要素ごとに組み合わせます。

```cpp
std::vector<bool> alive = {true, true, false};
std::vector<bool> visible = {true, false, true};
std::vector<bool> targetable(3);
std::transform(alive.begin(), alive.end(), visible.begin(), targetable.begin(), std::logical_and<>{});   // true, false, false
```

## よくあるミス

??? failure "短絡評価が働くと思う"
    関数オブジェクトの引数は、呼ぶ前に両方評価されます。左の条件で右を守る書き方（`p != nullptr && p->x`）は、`logical_and` では使えません。

??? failure "bit_and と取り違える"
    `logical_and` は真偽値の `&&`、`bit_and` はビットごとの `&` です。`2 && 1` は `true` ですが、`2 & 1` は `0` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`logical_or`](logical_or.md) | 論理和 |
| [`logical_not`](logical_not.md) | 論理否定 |
| [`bit_and`](bit_and.md) | ビットごとの論理積 |

## コンパイラ対応

C++98 から使えます（`<>` の型省略形は C++14 から）。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::logical_and<>` は演算子 `&&`（論理積）の関数オブジェクト
    - [x] 型を省略した `<>` の形が標準
    - [x] アルゴリズムの引数に渡せる

## 関連ページ

- [cpprefjp: std::logical_and](https://cpprefjp.github.io/reference/functional/logical_and.html)
- [cppreference: std::logical_and](https://en.cppreference.com/w/cpp/utility/functional/logical_and)
