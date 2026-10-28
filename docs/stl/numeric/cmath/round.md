---
title: std::round
summary: "小数を四捨五入する（半分は 0 から遠いほうへ）。"
order: 10
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::round

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
`#include <cmath>`
</div>

ダメージ計算の結果が `12.5` になったとき、画面には整数で出したいことがあります。切り捨てると `12`、切り上げると `13` です。`std::round` は四捨五入で、`12.5` を `13` にします。ちょうど半分のときの向きが決まっているのが特徴です。

!!! tip "ポイント"
    - ちょうど半分は 0 から遠い側へ丸める（`2.5` は `3`、`-2.5` は `-3`）。
    - 銀行家の丸め（偶数に丸める）が欲しいときは `std::nearbyint` を使う。
    - 戻り値は小数型。整数型で受けたいなら `std::lround` を使う。

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の一覧を先に見ると、ほかの数学関数との関係が分かります。

## 関数の詳しい説明

### std::round {#round}

```cpp
float round(float x);
```

`x` の小数部がちょうど `0.5` のときだけ、丸めの向きが問題になります。`std::round(2.5)` は `3`、`std::round(3.5)` は `4`、`std::round(-2.5)` は `-3` です。常に 0 から遠ざかる向きです。

`std::nearbyint` や `std::rint` は、現在の丸めモード（既定は最近接偶数）で丸めるので、`2.5` が `2`、`3.5` が `4` になります。統計処理で丸めの偏りを避けたいときに使いますが、ゲームではほぼ出番がありません。

- 四捨五入（0.5 は 0 から遠いほうへ）。`std::lround` は long で返します

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{} {} {}", std::round(2.5), std::round(-2.5), std::round(2.4));
}
```

```text title="実行結果"
3 -3 2
```

## ゲームでの使いどころ

ダメージ値やスコアの表示で、小数を整数に直すときに使います。HP が `45.5` のキャラクターに画面上は `46` と見せたい、といった場面です。内部の計算は小数のまま持ち、表示の直前でだけ `round` を呼びます。途中で丸めると、誤差が積み重なります。

ピクセル座標への変換にも使います。3D の座標を画面のピクセルに変換するとき、`static_cast<int>(std::round(x))` で最も近いピクセルを選ぶと、切り捨てるよりもなめらかに見えます。

## よくあるミス

??? failure "半分を偶数に丸めると思う"
    Python の `round()` は偶数に丸めます（`round(2.5)` が `2`）。C++ の `std::round` は違い、`2.5` が `3` です。他の言語から来ると混同しやすいので、半分のときの結果は確かめて使います。

??? failure "途中の計算で丸めてしまう"
    ダメージ計算の途中で `round` を呼ぶと、結果が少しずつズレます。小数のまま最後まで計算して、表示するときだけ丸めます。

??? failure "戻り値を `int` だと思う"
    `std::round` の戻り値は小数型です。`int a = std::round(x);` は警告が出る暗黙の変換になります。`std::lround(x)` を使うと、`long` で受け取れます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`floor`](floor.md) | 常に小さいほうへ |
| [`ceil`](ceil.md) | 常に大きいほうへ |
| [`trunc`](trunc.md) | 0 に向かって切り捨てる |

## コンパイラ対応

C++98 から使えます。`std::lerp` は C++20、`hypot` の 3 引数は C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 半分のときは 0 から遠い側に丸める。
    - [x] 戻り値は小数型。整数で欲しいときは `lround`。
    - [x] 丸めるのは表示の直前だけにする。

## 関連ページ

- [cpprefjp: std::round](https://cpprefjp.github.io/reference/cmath/round.html)
- [cppreference: std::round](https://en.cppreference.com/w/cpp/numeric/math/round)
