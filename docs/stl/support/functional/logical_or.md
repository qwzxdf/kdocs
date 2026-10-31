---
title: std::logical_or
summary: "`a || b` を表す関数オブジェクト。"
order: 900
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::logical_or

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <functional>`
</div>

アルゴリズムに「足し算をする」「大きい順に並べる」といった演算を渡したいとき、ラムダ `[](int a, int b) { return a || b; }` を毎回書くのは冗長です。`std::logical_or` は、<strong>演算子 `||`（論理和）を関数オブジェクトにしたもの</strong>で、そのままアルゴリズムに渡せます。

!!! tip "ポイント"
    - `std::logical_or<>{}(2 つの値)` は演算子 `||` と同じ結果
    - 型を省略した `std::logical_or<>` が推奨。型を自動で推論する
    - `std::accumulate` や `std::sort` などの引数として渡せる
    - 関数オブジェクトなので、インライン化されやすく、速い

!!! info "このページを読む前に"
    [`<functional>`](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::logical_or {#logical_or}

```cpp
template <class T = void>
struct logical_or {
  constexpr auto operator()(const T& x, const T& y) const;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 値 | 1 つ目の値 |
| `y` | 値 | 2 つ目の値 |

`std::logical_or<>{}(a, b)` は `a || b` と同じ結果を返します。関数オブジェクトの引数は、呼ぶ前に両方評価されるので、`||` の短絡評価は失われます。

## 実際に動かしてみる

```cpp
#include <functional>
#include <print>

int main() {
  std::println("std::logical_or<>{{}}(true, false) = {}", std::logical_or<>{}(true, false));
}
```

```text title="実行結果"
std::logical_or<>{}(true, false) = true
```

## ゲームでの使いどころ

複数のフラグのどれかが立っているかを、`accumulate` で調べます。

```cpp
std::vector<bool> hit = {false, false, true, false};
bool any_hit = std::accumulate(hit.begin(), hit.end(), false, std::logical_or<>{});   // true
```

## よくあるミス

??? failure "短絡評価を期待して重い関数を渡す"
    引数は両方評価されるので、重い関数は常に呼ばれます。早く打ち切りたいなら `std::any_of` を使います。

??? failure "bit_or と取り違える"
    `logical_or` は真偽値の `||` です。ビットを重ねるのは `bit_or` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`logical_and`](logical_and.md) | 論理積 |
| [`logical_not`](logical_not.md) | 論理否定 |
| [`bit_or`](bit_or.md) | ビットごとの論理和 |

## コンパイラ対応

C++98 から使えます（`<>` の型省略形は C++14 から）。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::logical_or<>` は演算子 `||`（論理和）の関数オブジェクト
    - [x] 型を省略した `<>` の形が標準
    - [x] アルゴリズムの引数に渡せる

## 関連ページ

- [cpprefjp: std::logical_or](https://cpprefjp.github.io/reference/functional/logical_or.html)
- [cppreference: std::logical_or](https://en.cppreference.com/w/cpp/utility/functional/logical_or)
