---
title: std::lcm
summary: "最小公倍数を求める。"
order: 2
group: <numeric> の整数・補間関数
tags:
  - 数値
---

# std::lcm

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <numeric>`
</div>

`std::lcm` は、**2 つの整数の最小公倍数**を返す関数です。2 つの周期的なイベントが、次に同時に起きるまでの時間を求めるときに使います。

!!! tip "ポイント"
    - `lcm(4, 6)` は 12。
    - 桁あふれに注意（大きな値の積）。

!!! info "このページを読む前に"
    [`<numeric>`](numeric.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::lcm {#lcm}

<span class="ver ver-17">C++17</span>

```cpp
template <class M, class N>
constexpr std::common_type_t<M, N> lcm(M m, N n);
```

- 最小公倍数（両方で割り切れる一番小さい数）。周期の違う 2 つのイベントが次に重なるタイミングの計算などに使えます

```cpp
#include <numeric>
#include <print>

int main() {
  int w = 1920;
  int h = 1080;
  int g = std::gcd(w, h);
  std::println("画面比 {}:{}", w / g, h / g);
  std::println("3 秒ごとと 4 秒ごとのイベントは {} 秒ごとに重なる", std::lcm(3, 4));
}
```

```text title="実行結果"
画面比 16:9
3 秒ごとと 4 秒ごとのイベントは 12 秒ごとに重なる
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 2 つの周期的なイベントが重なる周期 | `std::lcm(period_a, period_b)` |

## よくあるミス

??? failure "結果が型に収まらない"
    桁あふれは未定義動作です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`gcd`](gcd.md) | 最大公約数 |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 最小公倍数
    - [x] 周期の同期に
    - [x] C++17

## 関連ページ

- [cpprefjp: std::lcm](https://cpprefjp.github.io/reference/numeric/lcm.html)
- [cppreference: std::lcm](https://en.cppreference.com/w/cpp/numeric/lcm)
