---
title: std::ratio_multiply
summary: "2 つの `ratio` のかけ算を、コンパイル時に計算して `ratio` で返す。"
order: 900
tags:
  - 数値
---

# std::ratio_multiply

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <ratio>`
</div>

単位の変換は、分数の計算です。ミリ秒をマイクロ秒に直すには、1/1000 を 1/1000000 で割ります。これを実行時の浮動小数点数でやると、誤差が出ます。`std::ratio_multiply` は、<strong>2 つの `ratio` の掛け算を、コンパイル時に、誤差なしで</strong>計算します。

!!! tip "ポイント"
    - `std::ratio_multiply<R1, R2>` は、結果の `ratio` 型
    - 結果は `::type`。`::num` と `::den` で取り出す
    - 約分済みの分数になる
    - 計算はコンパイル時。オーバーフローするとコンパイルエラー

!!! info "このページを読む前に"
    [`<ratio>`](../ratio.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::ratio_multiply {#ratio_multiply}

<span class="ver ver-11">C++11</span>

```cpp
template <class R1, class R2>
using ratio_multiply = /* ratio<...> */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `R1` | `ratio` 型 | 1 つ目の分数 |
| `R2` | `ratio` 型 | 2 つ目の分数 |

`std::ratio_multiply<R1, R2>` は、`R1` と `R2` の掛け算を表す `std::ratio` 型です。分子どうし・分母どうしを掛けて約分した分数、約分された形で保持されます。実際の値は、`std::ratio_multiply<R1, R2>::num` と `::den` で取り出します。

計算の途中でオーバーフローしないよう、実装が工夫していますが、結果の分子・分母が `std::intmax_t` に収まらない場合は、コンパイルエラーになります。実行時に失敗するのではなく、ビルドの段階で気づけるのは利点です。

浮動小数点数を使わないので、誤差が入りません。`duration` の単位の変換が正確に行われるのは、この仕組みのおかげです。

## 実際に動かしてみる

```cpp
#include <ratio>
#include <print>

int main() {
  using Result = std::ratio_multiply<std::ratio<1, 2>, std::ratio<2, 3>>;
  std::println("1/2 × 2/3 = {}/{}", Result::num, Result::den);
}
```

```text title="実行結果"
1/2 × 2/3 = 1/3
```

## ゲームでの使いどころ

単位の変換係数を、コンパイル時に組み立てるときに使います。たとえば、ミリ秒（1/1000）の単位を、30 フレーム（1/30 秒）の単位に変換する係数は、2 つの `ratio` の割り算です。

```cpp
using FrameToMilli = std::ratio_divide<std::ratio<1, 30>, std::milli>;   // 1/30 秒 = 約 33.33 ミリ秒
```

通常の `std::chrono::duration_cast` を使えば、自分でこれを書く機会は多くありません。

## よくあるミス

??? failure "実行時の値を渡そうとする"
    `ratio` はコンパイル時の型です。実行時の値には使えません。

??? failure "結果が型に収まらずコンパイルエラーになる"
    分子・分母が大きくなりすぎない単位を選びます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ratio`](../ratio.md) | 分数を型で表す基本 |
| [`ratio_equal`](ratio_equal.md) | 分数の比較 |

## コンパイラ対応

C++11 から使えます。`<ratio>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `ratio_multiply<R1, R2>` は 2 つの `ratio` の掛け算
    - [x] 結果は約分された `ratio` 型。`::num` / `::den` で取る
    - [x] コンパイル時に計算され、誤差がない

## 関連ページ

- [cpprefjp: std::ratio_multiply](https://cpprefjp.github.io/reference/ratio/ratio_multiply.html)
- [cppreference: std::ratio_multiply](https://en.cppreference.com/w/cpp/numeric/ratio/ratio_add)
