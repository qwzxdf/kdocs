---
title: std::acosh
summary: "双曲線逆余弦（cosh の逆関数）を返す。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::acosh

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cmath>`
</div>

`cosh(x)` の逆の計算です。定義域は `x >= 1` で、それより小さい値では NaN になります。

!!! tip "ポイント"
    - `float` / `double` / `long double` の版がある。
    - 引数が整数なら `double` として計算される。
    - 角度はラジアン。

!!! info "このページを読む前に"
    [<cmath>](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::acosh {#acosh}

```cpp
double acosh(double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点 | 1 以上の値 |

- 戻り値: `acosh(x)`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{:.4f}", std::acosh(2.0));
}
```

```text title="実行結果"
1.3170
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 物理の式の計算 |

## よくあるミス

??? failure "1 未満を渡す"
    定義域外では NaN が返ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`cosh`](cosh.md) | 逆の関数 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 双曲線逆余弦（cosh の逆関数）を返す
    - [x] `float` / `double` / `long double` の版がある
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::acosh](https://cpprefjp.github.io/reference/cmath/acosh.html)
- [cppreference: std::acosh](https://en.cppreference.com/w/cpp/numeric/math/acosh)
