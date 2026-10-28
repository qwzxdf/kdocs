---
title: std::nexttoward
summary: "x の次に表せる値を返す（向かう先が long double）。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::nexttoward

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cmath>`
</div>

`std::nextafter` と同じく、隣の表現できる値を返しますが、第 2 引数（向かう方向）が常に `long double` の版です。`float` や `double` の値をより精度の高い値の方向へ進めたいときに使えます。

!!! tip "ポイント"
    - `std::nexttoward(1.0f, 2.0L)` は `1.0f` の次に大きい `float` の値
    - 第 2 引数は `long double`
    - 戻り値の型は第 1 引数の型
    - 通常は `nextafter` で足りる

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::nexttoward {#nexttoward}

<span class="ver ver-11">C++11</span>

```cpp
float nexttoward(float from, long double to);
double nexttoward(double from, long double to);
long double nexttoward(long double from, long double to);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `from` | 浮動小数点数 | 出発点 |
| `to` | `long double` | 向かう方向 |

戻り値は、`from` から `to` の方向に向かって、`from` の型で表せる隣の値です。`nextafter` との違いは、第 2 引数の型です。`to` が `long double` なので、`double` でちょうど表せない値の方向にも進めます。

`from == to` のときは `to` を `from` の型に変換した値を返します。

`nextafter` で足りることがほとんどです。精度の高い目標値の方向に進める、特殊な数値計算でしか必要になりません。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  const float next = std::nexttoward(1.0f, 2.0L);
  std::println("1.0f より大きい: {}", next > 1.0f);
}
```

```text title="実行結果"
1.0f より大きい: true
```

## ゲームでの使いどころ

`nextafter` で足ります。この関数を使う場面は、ほとんどありません。

## よくあるミス

??? failure "`nextafter` の違いが分からず、迷う"
    第 2 引数の型だけが違います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`nextafter`](nextafter.md) | 第 2 引数が同じ型 |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `nexttoward(from, to)` は `from` の隣の値（`to` は `long double`）
    - [x] 戻り値の型は `from` の型
    - [x] 通常は `nextafter` で足りる

## 関連ページ

- [cpprefjp: std::nexttoward](https://cpprefjp.github.io/reference/cmath/nexttoward.html)
- [cppreference: std::nexttoward](https://en.cppreference.com/w/cpp/numeric/math/nexttoward)
