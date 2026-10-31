---
title: std::exa
summary: "SI 接頭辞「exa」（100 京倍）を表す `ratio` の別名。"
order: 900
tags:
  - 数値
---

# std::exa

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <ratio>`
</div>

「エクサ」は、`std::ratio` が用意する SI 接頭辞のうち、最大のものです。`std::exa`（エクサ、100 京倍）は `ratio<1000000000000000000, 1>` の別名で、64 ビット環境の `std::intmax_t` に収まる、ぎりぎりの大きさです。

!!! tip "ポイント"
    - 中身は `std::ratio<1000000000000000000, 1>`
    - `::num`（分子）と `::den`（分母）をコンパイル時の定数として取り出せる
    - `std::chrono::duration` の単位（第 2 テンプレート引数）として使う
    - 型の別名であり、関数ではない（値は持たない）

!!! info "このページを読む前に"
    [`<ratio>`](../ratio.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::exa {#exa}

<span class="ver ver-11">C++11</span>

```cpp
using exa = ratio<1000000000000000000, 1>;
```

`std::exa` は、`std::ratio<1000000000000000000, 1>` の別名で、値は 100 京倍 を表します。`std::exa::num` が 1000000000000000000、`std::exa::den` が 1 で、いずれもコンパイル時の定数です。実行時のコストはありません。

`std::ratio` は分数を型で表す仕組みで、分子・分母は約分された形で保持されます。接頭辞の別名は、よく使う分数に名前を付けたものです。

単位の変換を型で表したいとき、この別名を `std::ratio_multiply` などと組み合わせて使えます。

分母や分子が `std::intmax_t` に収まらない接頭辞（`yotta`、`zetta` など）は、環境によっては定義されません。このページの `exa` は、64 ビットの範囲に収まるので、どの環境でも使えます。

## 実際に動かしてみる

```cpp
#include <limits>
#include <print>
#include <ratio>

int main() {
  std::println("exa = {}/{}", std::exa::num, std::exa::den);
  std::println("intmax_t の最大値: {}", std::numeric_limits<std::intmax_t>::max());

  // exa の 9 倍までは収まる。10 倍以上は intmax_t を超えるので、ratio では作れない
  using NineExa = std::ratio_multiply<std::exa, std::ratio<9>>;
  std::println("9 exa = {}/{}", NineExa::num, NineExa::den);
}
```

```text title="実行結果"
exa = 1000000000000000000/1
intmax_t の最大値: 9223372036854775807
9 exa = 9000000000000000000/1
```

`exa` の 9 倍までは `std::intmax_t` に収まります。10 倍にすると超えるので、`std::ratio_multiply<std::exa, std::ratio<10>>` は、コンパイルエラーです。

## ゲームでの使いどころ

ゲームのコードで使うことはありません。`std::ratio` が表せる大きさの上限を知るための例として、頭に入れておくと、桁あふれのエラーの意味が分かります。

## よくあるミス

??? failure "exa 同士を掛ける"
    `ratio_multiply<std::exa, std::exa>` は、桁があふれて、コンパイルエラーになります。

??? failure "zetta や yotta が使えると思う"
    64 ビットの `intmax_t` に収まらないので、標準の `<ratio>` には、通常は定義されません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ratio`](../ratio.md) | 分数を型で表す基本の仕組み |
| [`std::chrono::duration`](../../utilities/chrono/duration.md) | 時間を単位つきで表す |

## コンパイラ対応

C++11 から使えます。`<ratio>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::exa` は `ratio<1000000000000000000, 1>` の別名（100 京倍）
    - [x] `::num` と `::den` が定数として取れる
    - [x] `duration` の単位などに使う

## 関連ページ

- [cpprefjp: std::exa](https://cpprefjp.github.io/reference/ratio/ratio.html)
- [cppreference: std::exa](https://en.cppreference.com/w/cpp/numeric/ratio/ratio)
