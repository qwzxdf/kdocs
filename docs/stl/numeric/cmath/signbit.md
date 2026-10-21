---
title: std::signbit
summary: "符号ビットが立っているか（負か）を調べる。"
order: 27
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::signbit

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cmath>`
</div>

`std::signbit` は、**値の符号ビット（負かどうか）を調べる**関数です。`x < 0` と違い、**`-0.0` も負と判定**します。符号を正確に扱いたいときに使います。

!!! tip "ポイント"
    - `signbit(-0.0)` は `true`。`-0.0 < 0` は `false`。
    - NaN の符号も調べられる。

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::signbit {#signbit}

```cpp
bool signbit(double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点 | 調べる値 |

- 戻り値: 負（`-0.0` や負の NaN を含む）なら `true`
- 計算量: O(1)

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{} {} {}", std::signbit(-0.0), std::signbit(3.0), -0.0 < 0);
}
```

```text title="実行結果"
true false false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 速度が負か（−0 を含めて）正確に判定する | `std::signbit(v)` |

## よくあるミス

??? failure "x < 0 で -0.0 を負と思う"
    `-0.0 < 0` は `false` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`copysign`](copysign.md) | 符号をコピーする |
| [`abs`](abs.md) | 絶対値 |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 符号ビットを調べる
    - [x] -0.0 も負
    - [x] x < 0 とは違う

## 関連ページ

- [cpprefjp: std::signbit](https://cpprefjp.github.io/reference/cmath/signbit.html)
- [cppreference: std::signbit](https://en.cppreference.com/w/cpp/numeric/math/signbit)
