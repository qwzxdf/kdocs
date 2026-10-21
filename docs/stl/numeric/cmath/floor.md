---
title: std::floor
summary: "小数を切り捨てる（小さいほうの整数にする）。"
order: 9
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::floor

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
`#include <cmath>`
</div>

`std::floor` は、**小数を負の無限大の方向へ切り捨てて、整数値にする**関数です。タイルマップで座標がどのマスかを求めるときに使います。**負の数でも常に小さいほう**です（−1.5 → −2）。

!!! tip "ポイント"
    - `(int)` のキャストは 0 に向かって切り捨てる。**負の数で結果が違う**。
    - マスの座標を求めるときは `floor`。
    - 戻り値は小数型。`int` にするには `static_cast<int>`。

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::floor {#floor}

```cpp
float floor(float x);
```

- x 以下で一番大きい整数（マイナスでも「小さいほう」へ）。座標からマスの番号を出すのに使います

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{} {}", std::floor(-1.5), std::floor(1.5));
}
```

```text title="実行結果"
-2 1
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ワールド座標からタイル座標へ | `int tx = static_cast<int>(std::floor(x / kTileSize));` |

## よくあるミス

??? failure "負の座標で (int) キャストを使う"
    `(int)(-1.5)` は −1、`floor(-1.5)` は −2 です。座標がマイナスにも広がるなら `floor` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`ceil`](ceil.md) | 切り上げ |
| [`round`](round.md) | 四捨五入 |
| [`trunc`](trunc.md) | 0 に向かって切り捨て |

## コンパイラ対応

C++98 から使えます。`std::lerp` は C++20、`hypot` の 3 引数は C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 小さいほうへ切り捨て
    - [x] 負の数でも常に小さいほう
    - [x] タイル座標に使う

## 関連ページ

- [cpprefjp: std::floor](https://cpprefjp.github.io/reference/cmath/floor.html)
- [cppreference: std::floor](https://en.cppreference.com/w/cpp/numeric/math/floor)
