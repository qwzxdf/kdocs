---
title: std::bit_or
summary: "`a | b`（ビットごとの OR）を表す関数オブジェクト。"
order: 900
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::bit_or

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <functional>`
</div>

アルゴリズムに「足し算をする」「大きい順に並べる」といった演算を渡したいとき、ラムダ `[](int a, int b) { return a | b; }` を毎回書くのは冗長です。`std::bit_or` は、<strong>演算子 `|`（ビット和）を関数オブジェクトにしたもの</strong>で、そのままアルゴリズムに渡せます。

!!! tip "ポイント"
    - `std::bit_or<>{}(2 つの値)` は演算子 `|` と同じ結果
    - 型を省略した `std::bit_or<>` が推奨。型を自動で推論する
    - `std::accumulate` や `std::sort` などの引数として渡せる
    - 関数オブジェクトなので、インライン化されやすく、速い

!!! info "このページを読む前に"
    [`<functional>`](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::bit_or {#bit_or}

```cpp
template <class T = void>
struct bit_or {
  constexpr auto operator()(const T& x, const T& y) const;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 値 | 1 つ目の値 |
| `y` | 値 | 2 つ目の値 |

`std::bit_or<>{}(a, b)` は `a | b` と同じ結果を返します。整数のビットごとの論理和で、フラグを重ねるのに使います。論理和（`||`）ではありません。

## 実際に動かしてみる

```cpp
#include <functional>
#include <print>

int main() {
  std::println("std::bit_or<>{{}}(12, 10) = {}", std::bit_or<>{}(12, 10));
}
```

```text title="実行結果"
std::bit_or<>{}(12, 10) = 14
```

## ゲームでの使いどころ

複数のフラグを 1 つの値にまとめます。

```cpp
std::vector<std::uint32_t> flags = {0b0001, 0b0100, 0b1000};
std::uint32_t all = std::accumulate(flags.begin(), flags.end(), 0u, std::bit_or<>{});   // 0b1101
```

## よくあるミス

??? failure "初期値を 0 以外にする"
    `accumulate` の初期値が `~0u` だと、何と `|` しても全ビットが立ちます。重ねる場合は `0` から始めます。

??? failure "enum class に使う"
    `enum class` には `|` が定義されていないので、コンパイルエラーです。演算子を自作するか、`std::to_underlying` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`bit_and`](bit_and.md) | ビットごとの論理積 |
| [`bit_xor`](bit_xor.md) | ビットごとの排他的論理和 |
| [`logical_or`](logical_or.md) | 真偽値の論理和 |

## コンパイラ対応

C++98 から使えます（`<>` の型省略形は C++14 から）。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::bit_or<>` は演算子 `|`（ビット和）の関数オブジェクト
    - [x] 型を省略した `<>` の形が標準
    - [x] アルゴリズムの引数に渡せる

## 関連ページ

- [cpprefjp: std::bit_or](https://cpprefjp.github.io/reference/functional/bit_or.html)
- [cppreference: std::bit_or](https://en.cppreference.com/w/cpp/utility/functional/bit_or)
