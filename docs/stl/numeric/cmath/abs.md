---
title: std::abs
summary: "絶対値を求める（整数・小数に対応）。"
order: 2
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::abs

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
`#include <cmath>`
</div>

`std::abs` は、**絶対値（符号を取り除いた値）を返す**関数です。整数にも小数にも使えます。`<cmath>`（小数）と `<cstdlib>`（整数）で別々に宣言されているので、ヘッダーに注意します。

!!! tip "ポイント"
    - 小数は `<cmath>`、整数は `<cstdlib>` を include する。
    - `int` の最小値の `abs` は、桁あふれで未定義動作。
    - `float` に `abs`（C の関数）を使うと、`int` に変換されるので注意（`std::abs` を使う）。

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::abs {#abs}

```cpp
int abs(int x);
float abs(float x);
double abs(double x);
```

- 絶対値（マイナスを取った値）。整数版は `<cstdlib>`、浮動小数点版は `<cmath>` にあります

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{} {}", std::abs(-5), std::abs(-2.5f));
  std::println("{}", std::sqrt(16.0f));
}
```

```text title="実行結果"
5 2.5
4
```

## 実際に動かしてみる

```cpp
#include <cmath>
#include <cstdlib>
#include <print>

int main() {
  std::println("{} {}", std::abs(-3.5), std::abs(-4));
}
```

```text title="実行結果"
3.5 4
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 2 つの値の差の大きさ | `std::abs(a - b)` |
| 許容誤差の判定 | `std::abs(a - b) < 1e-5f` |

## よくあるミス

??? failure "std:: を付けずに abs を使う"
    C の `abs(int)` が呼ばれて、`float` が整数に切り捨てられます。`std::abs` と書きます。

## 類似

| 名前 | 違い |
| --- | --- |
| `std::fabs` | C 由来の小数用（`std::abs` で足りる） |
| [`copysign`](copysign.md) | 符号をコピーする |

## コンパイラ対応

C++98 から使えます。`std::lerp` は C++20、`hypot` の 3 引数は C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 絶対値
    - [x] `std::abs` と書く
    - [x] 小数は `<cmath>`

## 関連ページ

- [cpprefjp: std::abs](https://cpprefjp.github.io/reference/cmath/abs.html)
- [cppreference: std::abs](https://en.cppreference.com/w/cpp/numeric/math/abs)
