---
title: std::bit_and
summary: "`a & b`（ビットごとの AND）を表す関数オブジェクト。"
order: 900
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::bit_and

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <functional>`
</div>

アルゴリズムに「足し算をする」「大きい順に並べる」といった演算を渡したいとき、ラムダ `[](int a, int b) { return a & b; }` を毎回書くのは冗長です。`std::bit_and` は、<strong>演算子 `&`（ビット積）を関数オブジェクトにしたもの</strong>で、そのままアルゴリズムに渡せます。

!!! tip "ポイント"
    - `std::bit_and<>{}(2 つの値)` は演算子 `&` と同じ結果
    - 型を省略した `std::bit_and<>` が推奨。型を自動で推論する
    - `std::accumulate` や `std::sort` などの引数として渡せる
    - 関数オブジェクトなので、インライン化されやすく、速い

!!! info "このページを読む前に"
    [`<functional>`](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::bit_and {#bit_and}

```cpp
template <class T = void>
struct bit_and {
  constexpr auto operator()(const T& x, const T& y) const;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 値 | 1 つ目の値 |
| `y` | 値 | 2 つ目の値 |

`std::bit_and<>{}(a, b)` は `a & b` と同じ結果を返します。整数のビットごとの論理積です。マスクで特定のビットを取り出す、複数の値に共通して立っているビットを求める、といった使い方があります。論理積（`&&`）ではありません。

## 実際に動かしてみる

```cpp
#include <functional>
#include <print>

int main() {
  std::println("std::bit_and<>{{}}(12, 10) = {}", std::bit_and<>{}(12, 10));
}
```

```text title="実行結果"
std::bit_and<>{}(12, 10) = 8
```

## ゲームでの使いどころ

複数のレイヤーマスクに共通して立っているビットを求めます。

```cpp
std::vector<std::uint32_t> masks = {0b1110, 0b0110, 0b1111};
std::uint32_t common = std::accumulate(masks.begin(), masks.end(), ~0u, std::bit_and<>{});   // 0b0110
```

## よくあるミス

??? failure "初期値を 0 にする"
    `accumulate` の初期値が `0` だと、何と `&` しても `0` です。全ビットが立った `~0u` から始めます。

??? failure "enum class に使う"
    `enum class` には `&` が定義されていないので、コンパイルエラーです。`std::to_underlying` で整数にするか、演算子を自作します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`bit_or`](bit_or.md) | ビットごとの論理和 |
| [`bit_xor`](bit_xor.md) | ビットごとの排他的論理和 |
| [`logical_and`](logical_and.md) | 真偽値の論理積 |

## コンパイラ対応

C++98 から使えます（`<>` の型省略形は C++14 から）。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::bit_and<>` は演算子 `&`（ビット積）の関数オブジェクト
    - [x] 型を省略した `<>` の形が標準
    - [x] アルゴリズムの引数に渡せる

## 関連ページ

- [cpprefjp: std::bit_and](https://cpprefjp.github.io/reference/functional/bit_and.html)
- [cppreference: std::bit_and](https://en.cppreference.com/w/cpp/utility/functional/bit_and)
