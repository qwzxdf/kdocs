---
title: std::log2
summary: "底が 2 の対数を求める。"
order: 19
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::log2

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cmath>`
</div>

`std::log2` は、**底が 2 の対数**を返す関数です。「2 を何回かけると x になるか」を表します。ミップマップのレベル数（画像の大きさ → 縮小の段数）、必要なビット数の計算に使います。

!!! tip "ポイント"
    - `log2(1024)` は 10。
    - 整数のビット数なら `std::bit_width` のほうが正確で速い。

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::log2 {#log2}

```cpp
float log2(float x);
```

- 2 を底とする対数。テクスチャの mipmap の段数などに使います

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{} {}", std::log2(1024.0), std::log2(8.0));
}
```

```text title="実行結果"
10 3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ミップマップのレベル数 | `std::floor(std::log2(max(w, h))) + 1` |

## よくあるミス

??? failure "整数の桁数に使って誤差が出る"
    整数には `std::bit_width` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`log`](log.md) | 自然対数 |
| [`std::bit_width`](../bit/bit_width.md) | 整数のビット幅 |

## コンパイラ対応

C++98 から使えます。`std::lerp` は C++20、`hypot` の 3 引数は C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 底が 2 の対数
    - [x] ミップマップの段数に
    - [x] 整数は bit_width

## 関連ページ

- [cpprefjp: std::log2](https://cpprefjp.github.io/reference/cmath/log2.html)
- [cppreference: std::log2](https://en.cppreference.com/w/cpp/numeric/math/log2)
