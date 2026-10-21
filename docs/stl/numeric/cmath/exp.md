---
title: std::exp
summary: "e の x 乗（指数関数）を求める。"
order: 17
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::exp

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <cmath>`
</div>

`std::exp` は、**ネイピア数 e の x 乗**を返す関数です。減衰（時間とともに小さくなる）、フレームレートに依存しない補間、確率の計算に使います。

!!! tip "ポイント"
    - `exp(-k * dt)` は、時間 `dt` に応じた減衰率。
    - フレームレート非依存の補間は `1 - exp(-k * dt)`。
    - 2 の累乗は `exp2`。

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::exp {#exp}

```cpp
float exp(float x);
```

- e（約 2.718）の x 乗。フレームレートに依存しない減衰（`velocity *= std::exp(-damping * dt)`）に使えます

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{} {:.4f}", std::exp(0.0), std::exp(1.0));
}
```

```text title="実行結果"
1 2.7183
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| フレームレート非依存のなめらかな追従 | `t = 1 - std::exp(-k * dt)` |

## よくあるミス

??? failure "大きな値を渡す"
    桁あふれで無限大になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`log`](log.md) | 逆関数 |
| [`pow`](pow.md) | べき乗 |
| [`lerp`](lerp.md) | 補間 |

## コンパイラ対応

C++98 から使えます。`std::lerp` は C++20、`hypot` の 3 引数は C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] e の x 乗
    - [x] 減衰と補間に使う
    - [x] 逆関数は log

## 関連ページ

- [cpprefjp: std::exp](https://cpprefjp.github.io/reference/cmath/exp.html)
- [cppreference: std::exp](https://en.cppreference.com/w/cpp/numeric/math/exp)
