---
title: std::frexp
summary: "小数を、仮数（0.5〜1）と 2 の指数に分ける。"
order: 42
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::frexp

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cmath>`
</div>

`std::frexp` は、**小数を「仮数（0.5 以上 1 未満）× 2 の指数乗」に分ける**関数です。浮動小数点数の内部の形を調べる、桁数を調べる、といった低レベルの処理に使います。

!!! tip "ポイント"
    - `x = 仮数 × 2^指数`。仮数は 0.5〜1 未満。
    - 指数は第 2 引数に入る。
    - `ldexp` で元に戻せる。

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::frexp {#frexp}

```cpp
double frexp(double x, int* exp);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点 | 分ける値 |
| `exp` | `int*` | 指数の書き込み先 |

- 戻り値: 仮数（0.5 以上 1 未満）
- 計算量: O(1)

```cpp
#include <cmath>
#include <print>

int main() {
  int e = 0;
  double m = std::frexp(24.0, &e);  // 24 = 0.75 × 2^5
  std::println("{} {}", m, e);
}
```

```text title="実行結果"
0.75 5
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 値の大きさ（2 の何乗くらいか）を調べる | `std::frexp(v, &e)` |

## よくあるミス

??? failure "0 の扱い"
    0 の仮数は 0、指数も 0 です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`ldexp`](ldexp.md) | 元に戻す |
| [`log2`](log2.md) | 2 の対数 |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 仮数と指数に分ける
    - [x] 仮数は 0.5〜1 未満
    - [x] `ldexp` の逆

## 関連ページ

- [cpprefjp: std::frexp](https://cpprefjp.github.io/reference/cmath/frexp.html)
- [cppreference: std::frexp](https://en.cppreference.com/w/cpp/numeric/math/frexp)
