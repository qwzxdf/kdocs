---
title: std::bit_not
summary: "`~a`（ビット反転）を表す関数オブジェクト。"
order: 900
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::bit_not

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <functional>`
</div>

アルゴリズムに「足し算をする」「大きい順に並べる」といった演算を渡したいとき、ラムダ `[](int a, int b) { return a ~ b; }` を毎回書くのは冗長です。`std::bit_not` は、<strong>演算子 `~`（ビット反転）を関数オブジェクトにしたもの</strong>で、そのままアルゴリズムに渡せます。

!!! tip "ポイント"
    - `std::bit_not<>{}(値)` は演算子 `~` と同じ結果
    - 型を省略した `std::bit_not<>` が推奨。型を自動で推論する
    - `std::accumulate` や `std::sort` などの引数として渡せる
    - 関数オブジェクトなので、インライン化されやすく、速い

!!! info "このページを読む前に"
    [`<functional>`](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::bit_not {#bit_not}

```cpp
template <class T = void>
struct bit_not {
  constexpr auto operator()(const T& x) const;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 値 | 対象の値 |

`std::bit_not<>{}(x)` は `~x` と同じ結果を返します。引数が 1 つの関数オブジェクトで、全ビットを反転します。`std::uint8_t` のように小さい整数型は、`int` に昇格してから反転されるので、結果の型が `int` になり、負の値になります。

## 実際に動かしてみる

```cpp
#include <functional>
#include <print>

int main() {
  std::println("std::bit_not<>{{}}(0x0Fu) = {:#x}", std::bit_not<>{}(0x0Fu));
}
```

```text title="実行結果"
std::bit_not<>{}(0x0Fu) = 0xfffffff0
```

## ゲームでの使いどころ

マスクの配列を、まとめて反転します（立っていないビットを取り出す）。

```cpp
std::vector<std::uint32_t> masks = {0x0F, 0xF0};
std::transform(masks.begin(), masks.end(), masks.begin(), std::bit_not<>{});   // 0xFFFFFFF0, 0xFFFFFF0F
```

## よくあるミス

??? failure "uint8_t の反転を uint8_t だと思う"
    `std::bit_not<>{}(std::uint8_t{0x0F})` は `int` の `-16` を返します。`static_cast<std::uint8_t>(...)` で戻します。

??? failure "論理否定と取り違える"
    `bit_not` は全ビットの反転（`~`）、`logical_not` は真偽値の反転（`!`）です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`logical_not`](logical_not.md) | 真偽値を反転する |
| [`negate`](negate.md) | 符号を反転する |
| [`bit_xor`](bit_xor.md) | ビットごとの排他的論理和 |

## コンパイラ対応

C++98 から使えます（`<>` の型省略形は C++14 から）。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::bit_not<>` は演算子 `~`（ビット反転）の関数オブジェクト
    - [x] 型を省略した `<>` の形が標準
    - [x] アルゴリズムの引数に渡せる

## 関連ページ

- [cpprefjp: std::bit_not](https://cpprefjp.github.io/reference/functional/bit_not.html)
- [cppreference: std::bit_not](https://en.cppreference.com/w/cpp/utility/functional/bit_not)
