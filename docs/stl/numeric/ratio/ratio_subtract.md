---
title: std::ratio_subtract
summary: "2 つの `ratio` の引き算を、コンパイル時に計算して `ratio` で返す。"
order: 900
tags:
  - 数値
---

# std::ratio_subtract

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <ratio>`
</div>

単位の換算や精度の計算で、分数どうしの引き算をコンパイル時に済ませておきたいことがあります。`ratio_subtract<R1, R2>` は、約分された結果の `ratio` 型をつくります。実行時のコストはありません。

!!! tip "ポイント"
    - 結果は自動で約分される。
    - `::num` と `::den` で分子と分母を取り出す。
    - 計算がオーバーフローするとコンパイルエラーになる。

!!! info "このページを読む前に"
    [`std::ratio`](../ratio.md) を先に読んでください。

## 関数の詳しい説明

### std::ratio_subtract {#ratio_subtract}

```cpp
template <class R1, class R2>
using ratio_subtract = ratio</* 結果の分子 */, /* 結果の分母 */>;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `R1, R2` | ratio | 計算する 2 つの `ratio` |

- 戻り値: 1/2 - 1/3 = 1/6 を表す `ratio`
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <ratio>
#include <print>

int main() {
  using R = std::ratio_subtract<std::ratio<1, 2>, std::ratio<1, 3>>;
  std::println("{} {}", R::num, R::den);
}
```

```text title="実行結果"
1 6
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 単位の係数をコンパイル時に作る | `ratio_subtract<A, B>::num` |

## よくあるミス

??? failure "オーバーフローを気にしない"
    分子や分母が `intmax_t` に入らないとコンパイルエラーです。極端に大きな値を組み合わせないようにします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ratio`](../ratio.md) | 分数の型 |
| [`ratio_equal`](ratio_equal.md) | 等しいか比べる |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ratio の引き算（コンパイル時）
    - [x] 結果は約分される
    - [x] num / den で取り出す

## 関連ページ

- [cpprefjp: std::ratio_subtract](https://cpprefjp.github.io/reference/ratio/ratio_subtract.html)
- [cppreference: std::ratio_subtract](https://en.cppreference.com/w/cpp/numeric/ratio/ratio_add)
