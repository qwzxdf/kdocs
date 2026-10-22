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

`nextafter` の、向かう先 `y` が `long double` の版です。`float` や `double` の隣を、高い精度の `y` に向かって探せます。

!!! tip "ポイント"
    - `float` / `double` / `long double` の版がある。
    - 引数が整数なら `double` として計算される。
    - エラーは `errno` か浮動小数点例外で知らされる。

!!! info "このページを読む前に"
    [<cmath>](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::nexttoward {#nexttoward}

```cpp
float nexttoward(float x, long double y);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点 | 出発点 |
| `y` | long double | 向かう先 |

- 戻り値: x の隣の値（y の方向）
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cmath>
#include <limits>
#include <print>

int main() {
  std::println("{}", std::nexttoward(1.0f, 2.0L) - 1.0f == std::numeric_limits<float>::epsilon());
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | float の隣の値を調べる |

## よくあるミス

??? failure "`float` に `double` を入れて精度が違う"
    戻りの型は x の型です。`y` だけが `long double` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`nextafter`](nextafter.md) | y が同じ型 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] x の次に表せる値を返す（向かう先が long double）
    - [x] `float` / `double` / `long double` の版がある
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::nexttoward](https://cpprefjp.github.io/reference/cmath/nexttoward.html)
- [cppreference: std::nexttoward](https://en.cppreference.com/w/cpp/numeric/math/nexttoward)
