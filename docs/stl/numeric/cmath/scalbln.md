---
title: std::scalbln
summary: "x × 2ⁿ を計算する（指数が long）。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::scalbln

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cmath>`
</div>

`scalbn` の、指数部分が `long` の版です。

!!! tip "ポイント"
    - `float` / `double` / `long double` の版がある。
    - 引数が整数なら `double` として計算される。
    - エラーは `errno` か浮動小数点例外で知らされる。

!!! info "このページを読む前に"
    [<cmath>](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::scalbln {#scalbln}

```cpp
double scalbln(double x, long n);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点 | 元の値 |
| `n` | long | 2 の指数 |

- 戻り値: `x × 2ⁿ`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{}", std::scalbln(1.5, 3));
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

??? failure "`int` 版との違いを気にしない"
    `n` が `int` の範囲に収まるなら `scalbn` で十分です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`scalbn`](scalbn.md) | 指数が int |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] x × 2ⁿ を計算する（指数が long）
    - [x] `float` / `double` / `long double` の版がある
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::scalbln](https://cpprefjp.github.io/reference/cmath/scalbln.html)
- [cppreference: std::scalbln](https://en.cppreference.com/w/cpp/numeric/math/scalbn)
