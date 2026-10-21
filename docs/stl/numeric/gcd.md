---
title: std::gcd
summary: "最大公約数を求める。"
order: 1
group: <numeric> の整数・補間関数
tags:
  - 数値
---

# std::gcd

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-17">C++17</span>
`#include <numeric>`
</div>

`std::gcd` は、**2 つの整数の最大公約数**を返す関数です。分数を約分する、タイルの繰り返しパターンの周期を求める、といった処理に使います。

!!! tip "ポイント"
    - `gcd(12, 18)` は 6。
    - 片方が 0 なら、もう片方。
    - C++17 で追加。

!!! info "このページを読む前に"
    [`<numeric>`](numeric.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::gcd {#gcd}

<span class="ver ver-17">C++17</span>

```cpp
template <class M, class N>
constexpr std::common_type_t<M, N> gcd(M m, N n);
```

- 最大公約数（両方を割り切れる一番大きい数）。整数のみ

## 実際に動かしてみる

```cpp
#include <numeric>
#include <print>

int main() {
  std::println("{} {}", std::gcd(12, 18), std::gcd(0, 5));
}
```

```text title="実行結果"
6 5
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 分数の約分、アスペクト比の簡約（1920x1080 → 16:9） | `g = std::gcd(w, h); w / g, h / g` |

## よくあるミス

??? failure "型が違う"
    符号つきと符号なしを混ぜると警告です。同じ型にそろえます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`lcm`](lcm.md) | 最小公倍数 |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 最大公約数
    - [x] アスペクト比の簡約に
    - [x] C++17

## 関連ページ

- [cpprefjp: std::gcd](https://cpprefjp.github.io/reference/numeric/gcd.html)
- [cppreference: std::gcd](https://en.cppreference.com/w/cpp/numeric/gcd)
