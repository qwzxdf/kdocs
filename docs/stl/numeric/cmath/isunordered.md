---
title: std::isunordered
summary: "浮動小数点を比べる（どちらかが NaN で、大小を比べられないか）。NaN でも例外を出さない。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::isunordered

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cmath>`
</div>

NaN が混ざった 2 つの値は、大小の順序が決まりません。`std::isunordered` は、<strong>2 つの値のどちらかが NaN か</strong>（順序が決まらないか）を例外を立てずに調べます。

!!! tip "ポイント"
    - `std::isunordered(x, y)` は、どちらかが NaN のとき `true`
    - `isnan(x) || isnan(y)` と同じ意味
    - 比較用の `isless` などと組み合わせて使う
    - FE_INVALID を立てない

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::isunordered {#isunordered}

<span class="ver ver-11">C++11</span>

```cpp
bool isunordered(float x, float y);
bool isunordered(double x, double y);
bool isunordered(long double x, long double y);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点数 | 1 つ目の値 |
| `y` | 浮動小数点数 | 2 つ目の値 |

戻り値は、`x` と `y` のどちらかが NaN なら `true` です。両方が普通の数なら `false` です。

比較の前に順序が決まる値かを確かめる用途に向いています。`isless` などの関数は、順序が決まらないときに `false` を返すので、`false` の理由が「小さくない」なのか「比較できない」なのかを区別したいときに、`isunordered` を併用します。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <limits>
#include <print>

int main() {
  const double nan = std::numeric_limits<double>::quiet_NaN();
  std::println("isunordered(1, 2)   = {}", std::isunordered(1.0, 2.0));
  std::println("isunordered(nan, 2) = {}", std::isunordered(nan, 2.0));
}
```

```text title="実行結果"
isunordered(1, 2)   = false
isunordered(nan, 2) = true
```

## ゲームでの使いどころ

値の並べ替えの前に NaN が混ざっていないかを確かめます。NaN が混ざると、比較が一貫しなくなり、`std::sort` が不正な動作をします。

```cpp
for (std::size_t i = 1; i < v.size(); ++i) {
  if (std::isunordered(v[i - 1], v[i])) { /* NaN が混ざっている */ }
}
```

## よくあるミス

??? failure "NaN を含む配列を `std::sort` して、順序が壊れる"
    先に NaN を取り除きます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`isnan`](isnan.md) | 1 つの値が NaN か |
| [`isless`](isless.md) | 例外を立てずに小さいか比べる |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `isunordered(x, y)` はどちらかが NaN のとき `true`
    - [x] `isnan(x) || isnan(y)` と同じ
    - [x] NaN を含む配列は `sort` できない

## 関連ページ

- [cpprefjp: std::isunordered](https://cpprefjp.github.io/reference/cmath/isunordered.html)
- [cppreference: std::isunordered](https://en.cppreference.com/w/cpp/numeric/math/isunordered)
