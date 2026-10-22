---
title: std::atanh
summary: "双曲線逆正接（tanh の逆関数）を返す。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::atanh

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cmath>`
</div>

`tanh(x)` の逆の計算です。定義域は `-1 < x < 1`、±1 では無限大になります。

!!! tip "ポイント"
    - `float` / `double` / `long double` の版がある。
    - 引数が整数なら `double` として計算される。
    - 角度はラジアン。

!!! info "このページを読む前に"
    [<cmath>](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::atanh {#atanh}

```cpp
double atanh(double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点 | -1 〜 1 の値 |

- 戻り値: `atanh(x)`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{:.4f}", std::atanh(0.5));
}
```

```text title="実行結果"
0.5493
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 値を非線形に引き伸ばす |

## よくあるミス

??? failure "範囲外を渡す"
    絶対値が 1 を超えると NaN が返ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`tanh`](tanh.md) | 逆の関数 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 双曲線逆正接（tanh の逆関数）を返す
    - [x] `float` / `double` / `long double` の版がある
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::atanh](https://cpprefjp.github.io/reference/cmath/atanh.html)
- [cppreference: std::atanh](https://en.cppreference.com/w/cpp/numeric/math/atanh)
