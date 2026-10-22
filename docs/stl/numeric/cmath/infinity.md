---
title: INFINITY
summary: "float の無限大を表すマクロ。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# INFINITY

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cmath>`
</div>

`float` の正の無限大を表します。`-INFINITY` で負の無限大です。除算で作る代わりに、意図を明示して書けます。

!!! tip "ポイント"
    - マクロ（式）。
    - `std::` を付けずに書く。
    - 比較は専用関数（`isnan` など）で。

!!! info "このページを読む前に"
    [<cmath>](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### INFINITY {#infinity}

```cpp
#define INFINITY /* 実装定義 */
```

- 戻り値: マクロの値
- 計算量: なし


## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{} {}", INFINITY, -INFINITY);
}
```

```text title="実行結果"
inf -inf
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 異常値の目印や、エラー処理の分岐に使う |

## よくあるミス

??? failure "値を `==` で比べる"
    NaN は `==` で比べられません。`std::isnan`・`std::isinf` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`isnan`](isnan.md) | NaN の判定 |
| [`isinf`](isinf.md) | 無限大の判定 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] float の無限大を表すマクロ
    - [x] マクロ（式）
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: INFINITY](https://cpprefjp.github.io/reference/cmath/infinity.html)
- [cppreference: INFINITY](https://en.cppreference.com/w/cpp/numeric/math/INFINITY)
