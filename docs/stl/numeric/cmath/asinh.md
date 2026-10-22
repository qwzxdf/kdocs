---
title: std::asinh
summary: "双曲線逆正弦（sinh の逆関数）を返す。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::asinh

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cmath>`
</div>

`sinh(x)` の逆の計算です。ゲームではほとんど使いませんが、物理や信号処理の式に出てきます。

!!! tip "ポイント"
    - `float` / `double` / `long double` の版がある。
    - 引数が整数なら `double` として計算される。
    - 角度はラジアン。

!!! info "このページを読む前に"
    [<cmath>](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::asinh {#asinh}

```cpp
double asinh(double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点 | 引数 |

- 戻り値: `asinh(x)`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{:.4f}", std::asinh(1.0));
}
```

```text title="実行結果"
0.8814
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 物理の式の計算 |

## よくあるミス

??? failure "定義域を気にしない"
    `asinh` は全ての実数で定義されます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`sinh`](sinh.md) | 逆の関数 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 双曲線逆正弦（sinh の逆関数）を返す
    - [x] `float` / `double` / `long double` の版がある
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::asinh](https://cpprefjp.github.io/reference/cmath/asinh.html)
- [cppreference: std::asinh](https://en.cppreference.com/w/cpp/numeric/math/asinh)
