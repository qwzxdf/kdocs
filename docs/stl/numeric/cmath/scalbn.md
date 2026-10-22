---
title: std::scalbn
summary: "x × 2ⁿ を、乗算を使わずに計算する。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::scalbn

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cmath>`
</div>

2 のべき乗倍は、指数部だけを書き換えれば済むので、乗算より正確で速く計算できます。`ldexp` と同じ働きですが、基数が `FLT_RADIX` の環境でも正しく動きます。

!!! tip "ポイント"
    - `float` / `double` / `long double` の版がある。
    - 引数が整数なら `double` として計算される。
    - エラーは `errno` か浮動小数点例外で知らされる。

!!! info "このページを読む前に"
    [<cmath>](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::scalbn {#scalbn}

```cpp
double scalbn(double x, int n);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点 | 元の値 |
| `n` | int | 2 の指数 |

- 戻り値: `x × 2ⁿ`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{}", std::scalbn(1.5, 3));
}
```

```text title="実行結果"
12
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 2 のべき乗倍のスケール |

## よくあるミス

??? failure "`pow(2, n)` で乗算する"
    桁あふれしやすく、誤差も出ます。`scalbn` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`ldexp`](ldexp.md) | 同じ働き |
| [`scalbln`](scalbln.md) | 指数が long |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] x × 2ⁿ を、乗算を使わずに計算する
    - [x] `float` / `double` / `long double` の版がある
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::scalbn](https://cpprefjp.github.io/reference/cmath/scalbn.html)
- [cppreference: std::scalbn](https://en.cppreference.com/w/cpp/numeric/math/scalbn)
