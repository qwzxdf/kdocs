---
title: std::bit_xor
summary: "`a ^ b`（ビットごとの XOR）を表す関数オブジェクト。"
order: 900
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::bit_xor

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <functional>`
</div>

アルゴリズムに「足し算をする」「大きい順に並べる」といった演算を渡したいとき、ラムダ `[](int a, int b) { return a ^ b; }` を毎回書くのは冗長です。`std::bit_xor` は、<strong>演算子 `^`（ビットの排他的論理和）を関数オブジェクトにしたもの</strong>で、そのままアルゴリズムに渡せます。

!!! tip "ポイント"
    - `std::bit_xor<>{}(2 つの値)` は演算子 `^` と同じ結果
    - 型を省略した `std::bit_xor<>` が推奨。型を自動で推論する
    - `std::accumulate` や `std::sort` などの引数として渡せる
    - 関数オブジェクトなので、インライン化されやすく、速い

!!! info "このページを読む前に"
    [`<functional>`](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::bit_xor {#bit_xor}

```cpp
template <class T = void>
struct bit_xor {
  constexpr auto operator()(const T& x, const T& y) const;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 値 | 1 つ目の値 |
| `y` | 値 | 2 つ目の値 |

`std::bit_xor<>{}(a, b)` は `a ^ b` と同じ結果を返します。整数のビットごとの排他的論理和で、同じ値を 2 回 `^` すると、元に戻る性質があります。これを使って、ビットの反転、簡単なチェックサム、値の入れ替えなどができます。

## 実際に動かしてみる

```cpp
#include <functional>
#include <print>

int main() {
  std::println("std::bit_xor<>{{}}(12, 10) = {}", std::bit_xor<>{}(12, 10));
}
```

```text title="実行結果"
std::bit_xor<>{}(12, 10) = 6
```

## ゲームでの使いどころ

バイト列の簡易チェックサム（全体の排他的論理和）を求めます。

```cpp
std::vector<std::uint8_t> bytes = {0x12, 0x34, 0x56};
std::uint8_t checksum = std::accumulate(bytes.begin(), bytes.end(), std::uint8_t{0}, std::bit_xor<>{});   // 0x70
```

## よくあるミス

??? failure "チェックサムを強い検査だと思う"
    排他的論理和だけのチェックサムは、同じバイトが 2 つあると互いに打ち消し合います。壊れたデータを見逃すので、重要な検査には CRC やハッシュを使います。

??? failure "std::uint8_t に使って型が変わる"
    `uint8_t` の `^` は `int` に昇格して計算されます。`accumulate` の初期値の型で結果が丸められるように、型を明示します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`bit_and`](bit_and.md) | ビットごとの論理積 |
| [`bit_or`](bit_or.md) | ビットごとの論理和 |
| [`bit_not`](bit_not.md) | ビットの反転 |

## コンパイラ対応

C++98 から使えます（`<>` の型省略形は C++14 から）。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::bit_xor<>` は演算子 `^`（ビットの排他的論理和）の関数オブジェクト
    - [x] 型を省略した `<>` の形が標準
    - [x] アルゴリズムの引数に渡せる

## 関連ページ

- [cpprefjp: std::bit_xor](https://cpprefjp.github.io/reference/functional/bit_xor.html)
- [cppreference: std::bit_xor](https://en.cppreference.com/w/cpp/utility/functional/bit_xor)
