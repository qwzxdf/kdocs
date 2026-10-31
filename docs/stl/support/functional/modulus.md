---
title: std::modulus
summary: "`a % b`（余り）を表す関数オブジェクト。"
order: 900
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::modulus

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <functional>`
</div>

アルゴリズムに「足し算をする」「大きい順に並べる」といった演算を渡したいとき、ラムダ `[](int a, int b) { return a % b; }` を毎回書くのは冗長です。`std::modulus` は、<strong>演算子 `%`（剰余）を関数オブジェクトにしたもの</strong>で、そのままアルゴリズムに渡せます。

!!! tip "ポイント"
    - `std::modulus<>{}(2 つの値)` は演算子 `%` と同じ結果
    - 型を省略した `std::modulus<>` が推奨。型を自動で推論する
    - `std::accumulate` や `std::sort` などの引数として渡せる
    - 関数オブジェクトなので、インライン化されやすく、速い

!!! info "このページを読む前に"
    [`<functional>`](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::modulus {#modulus}

```cpp
template <class T = void>
struct modulus {
  constexpr auto operator()(const T& x, const T& y) const;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 値 | 1 つ目の値 |
| `y` | 値 | 2 つ目の値 |

`std::modulus<>{}(a, b)` は `a % b` と同じ結果を返します。整数どうしにしか使えません。浮動小数点数の余りは `std::fmod` を使います。余りの符号は、割られる数 `a` に従います（`-7 % 3` は `-1`）。

## 実際に動かしてみる

```cpp
#include <functional>
#include <print>

int main() {
  std::println("std::modulus<>{{}}(7, 2) = {}", std::modulus<>{}(7, 2));
}
```

```text title="実行結果"
std::modulus<>{}(7, 2) = 1
```

## ゲームでの使いどころ

インデックスを、リングバッファの大きさに折り返します。

```cpp
std::vector<int> index = {5, 6, 7, 8};
std::vector<int> wrapped(index.size());
std::transform(index.begin(), index.end(), wrapped.begin(),
               [](int i) { return std::modulus<>{}(i, 4); });   // 1, 2, 3, 0
```

## よくあるミス

??? failure "浮動小数点数に使う"
    `%` は整数にしか使えないので、`modulus<>{}(5.0, 2.0)` はコンパイルエラーです。`std::fmod` を使います。

??? failure "負の数の余りを正だと思う"
    `-1 % 4` は `3` ではなく `-1` です。常に 0 以上の余りが欲しいなら、`((a % n) + n) % n` と書きます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`divides`](divides.md) | 割り算の商 |
| [`plus`](plus.md) | 足し算 |
| [`multiplies`](multiplies.md) | 掛け算 |

## コンパイラ対応

C++98 から使えます（`<>` の型省略形は C++14 から）。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::modulus<>` は演算子 `%`（剰余）の関数オブジェクト
    - [x] 型を省略した `<>` の形が標準
    - [x] アルゴリズムの引数に渡せる

## 関連ページ

- [cpprefjp: std::modulus](https://cpprefjp.github.io/reference/functional/modulus.html)
- [cppreference: std::modulus](https://en.cppreference.com/w/cpp/utility/functional/modulus)
