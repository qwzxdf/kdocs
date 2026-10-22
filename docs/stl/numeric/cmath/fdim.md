---
title: std::fdim
summary: "x − y が正ならその値、そうでなければ 0 を返す。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::fdim

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cmath>`
</div>

「差があれば差、なければ 0」を `max(x - y, 0)` と書く代わりに、`fdim` が使えます。残りの体力やゲージの不足分を求めるときなどです。

!!! tip "ポイント"
    - `float` / `double` / `long double` の版がある。
    - 引数が整数なら `double` として計算される。
    - エラーは `errno` か浮動小数点例外で知らされる。

!!! info "このページを読む前に"
    [<cmath>](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::fdim {#fdim}

```cpp
double fdim(double x, double y);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x, y` | 浮動小数点 | x から y を引く |

- 戻り値: `max(x - y, 0)`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{} {}", std::fdim(5.0, 3.0), std::fdim(3.0, 5.0));
}
```

```text title="実行結果"
2 0
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | ダメージ計算で、防御を差し引いた最低 0 のダメージ |

## よくあるミス

??? failure "符号付きの差を期待する"
    `fdim(3, 5)` は -2 ではなく 0 です。負の差が欲しいときは普通に引き算します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fmax`](fmax.md) | 大きいほうを選ぶ |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] x − y が正ならその値、そうでなければ 0 を返す
    - [x] `float` / `double` / `long double` の版がある
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::fdim](https://cpprefjp.github.io/reference/cmath/fdim.html)
- [cppreference: std::fdim](https://en.cppreference.com/w/cpp/numeric/math/fdim)
