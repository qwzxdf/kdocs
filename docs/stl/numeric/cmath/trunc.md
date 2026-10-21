---
title: std::trunc
summary: "小数部を捨てる（0 に向かって切り捨てる）。"
order: 12
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::trunc

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cmath>`
</div>

`std::trunc` は、**小数部を捨てて、0 に向かって整数値にする**関数です。`static_cast<int>` と同じ向きの切り捨てです。負の数では、`floor` と結果が違います（−1.5 → −1）。

!!! tip "ポイント"
    - `(int)` キャストと同じ向き。
    - 負の数で `floor` とは違う。

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::trunc {#trunc}

```cpp
float trunc(float x);
```

- 小数部分を捨てる（0 の方向へ）。`static_cast<int>(x)` と同じ向き

```cpp
#include <cmath>
#include <print>

int main() {
  for (float x : {2.5f, -2.5f}) {
    std::println("{}: floor {} / ceil {} / round {} / trunc {}", x, std::floor(x),
                 std::ceil(x), std::round(x), std::trunc(x));
  }
  constexpr float kTileSize = 32.0f;
  float player_x = -10.0f;
  std::println("マス {}", static_cast<int>(std::floor(player_x / kTileSize)));
}
```

```text title="実行結果"
2.5: floor 2 / ceil 3 / round 3 / trunc 2
-2.5: floor -3 / ceil -2 / round -3 / trunc -2
マス -1
```

マイナスの座標でマスの番号を出すときは、`floor` を使わないと `-10 / 32` が 0 になってしまいます。

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 小数部を取り除く | `std::trunc(v)` |

## よくあるミス

??? failure "floor と取り違える"
    負の数で結果が違います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`floor`](floor.md) | 小さいほうへ |
| [`round`](round.md) | 四捨五入 |

## コンパイラ対応

C++98 から使えます。`std::lerp` は C++20、`hypot` の 3 引数は C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 0 に向かって切り捨て
    - [x] `(int)` キャストと同じ向き
    - [x] 負の数は floor と違う

## 関連ページ

- [cpprefjp: std::trunc](https://cpprefjp.github.io/reference/cmath/trunc.html)
- [cppreference: std::trunc](https://en.cppreference.com/w/cpp/numeric/math/trunc)
