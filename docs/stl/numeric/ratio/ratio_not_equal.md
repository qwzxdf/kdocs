---
title: std::ratio_not_equal
summary: "2 つの `ratio` を `!=` で比べる（コンパイル時）。"
order: 900
tags:
  - 数値
---

# std::ratio_not_equal

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <ratio>`
</div>

2 つの単位の大小をコンパイル時に調べたい場面があります。たとえば、「この時間の単位は、ミリ秒より細かいか」を `static_assert` で保証したい。`std::ratio_not_equal` は、<strong>2 つの `ratio` について R1 が R2 等しくないかをコンパイル時に</strong>調べます。

!!! tip "ポイント"
    - `std::ratio_not_equal<R1, R2>::value` が結果（`bool`）
    - 約分された値で比べる（`ratio<2, 4>` と `ratio<1, 2>` は等しい）
    - `static_assert` と組み合わせて、単位の前提を保証できる
    - コンパイル時の定数で、実行時のコストはない

!!! info "このページを読む前に"
    [`<ratio>`](../ratio.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::ratio_not_equal {#ratio_not_equal}

<span class="ver ver-11">C++11</span>

```cpp
template <class R1, class R2>
struct ratio_not_equal : std::bool_constant</* R1 と R2 の比較結果 */> {};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `R1` | `ratio` 型 | 1 つ目の分数 |
| `R2` | `ratio` 型 | 2 つ目の分数 |

`std::ratio_not_equal<R1, R2>::value` は、`R1` が `R2` と比べて「等しくない」なら `true` です。値はコンパイル時の定数です。

`ratio` は常に約分された形で保持されるので、`ratio<2, 4>` は内部では `ratio<1, 2>` と同じです。そのため、見た目が違う分数どうしの比較でも、正しい結果が返ります。

比較は、掛け算でオーバーフローしないよう、実装が工夫しています。

C++17 以降は、`std::ratio_not_equal_v<R1, R2>` という変数テンプレートの略記も使えます。

## 実際に動かしてみる

```cpp
#include <ratio>
#include <print>

int main() {
  // 1/2 と 1/3
  std::println("{}", std::ratio_not_equal<std::ratio<1, 2>, std::ratio<1, 3>>::value);
  static_assert(std::ratio_not_equal<std::ratio<1, 2>, std::ratio<1, 3>>::value);   // コンパイル時にも検査できる
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

単位の前提をビルド時に保証します。

```cpp
// 計測の単位がミリ秒以下の細かさであることを要求する
template <class Period>
void StartTimer() {
  static_assert(std::ratio_less_equal<Period, std::milli>::value, "ミリ秒以下の単位が必要");
}
```

## よくあるミス

??? failure "実行時の値を比べようとする"
    `ratio` はコンパイル時の型です。実行時の値には通常の比較を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`ratio_equal`](ratio_equal.md) | 等しい |
| [`ratio_less`](ratio_less.md) | より小さい |
| [`ratio_add`](ratio_add.md) | 足し算 |

## コンパイラ対応

C++11 から使えます。`<ratio>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `ratio_not_equal<R1, R2>::value` は R1 が R2 等しくないかのコンパイル時の判定
    - [x] 約分した値で比べる
    - [x] `static_assert` で単位の前提を保証する

## 関連ページ

- [cpprefjp: std::ratio_not_equal](https://cpprefjp.github.io/reference/ratio/ratio_not_equal.html)
- [cppreference: std::ratio_not_equal](https://en.cppreference.com/w/cpp/numeric/ratio/ratio_equal)
