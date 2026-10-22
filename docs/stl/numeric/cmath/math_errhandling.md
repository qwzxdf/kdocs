---
title: math_errhandling
summary: "数学関数のエラーの知らせ方を表すマクロ。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# math_errhandling

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cmath>`
</div>

数学関数が範囲外の入力などを受けたとき、`errno` を設定するか、浮動小数点例外を立てるかは処理系で決まります。`math_errhandling` は、その方式を表すビットフラグ（`MATH_ERRNO`・`MATH_ERREXCEPT`）です。

!!! tip "ポイント"
    - マクロ（式）。
    - `std::` を付けずに書く。
    - 比較は専用関数（`isnan` など）で。

!!! info "このページを読む前に"
    [<cmath>](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### math_errhandling {#math_errhandling}

```cpp
#define math_errhandling /* 実装定義 */
```

- 戻り値: マクロの値
- 計算量: なし


## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{}", (math_errhandling & (MATH_ERRNO | MATH_ERREXCEPT)) != 0);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 異常値の目印や、エラー処理の分岐に使う |

## よくあるミス

??? failure "値を `==` で比べる"
    `math_errhandling` は、環境で値が変わります。両方のビットを確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`isnan`](isnan.md) | NaN の判定 |
| [`isinf`](isinf.md) | 無限大の判定 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 数学関数のエラーの知らせ方を表すマクロ
    - [x] マクロ（式）
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: math_errhandling](https://cpprefjp.github.io/reference/cmath/math_errhandling.html)
- [cppreference: math_errhandling](https://en.cppreference.com/w/cpp/numeric/math/math_errhandling)
