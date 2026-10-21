---
title: std::lerp
summary: "2 つの値の間を、割合で補間する（線形補間）。"
order: 13
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::lerp

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-20">C++20</span>
`#include <cmath>`
</div>

`std::lerp(a, b, t)` は、**a から b まで、割合 t（0〜1）で進んだ位置の値を求める**関数です。ゲームで最もよく使う関数の 1 つで、カメラの追従、フェード、アニメーションに使います。`a + (b - a) * t` と同じですが、`t = 1` で正確に `b` になるなど、誤差の面で安全です。

!!! tip "ポイント"
    - `t = 0` で a、`t = 1` で b、`0.5` で真ん中。
    - t は 0〜1 に限らない（超えると外挿）。
    - 毎フレーム `lerp(cur, target, 0.1f)` は、フレームレートに依存するので注意。

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::lerp {#lerp}

<span class="ver ver-20">C++20</span>

```cpp
constexpr float lerp(float a, float b, float t) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `a` | 浮動小数点 | 始まりの値（t = 0 のとき） |
| `b` | 浮動小数点 | 終わりの値（t = 1 のとき） |
| `t` | 浮動小数点 | 割合。0〜1 の外も使える |

- 戻り値: `a + t * (b - a)`

```cpp
#include <cmath>
#include <print>

int main() {
  float camera = 0.0f;
  float target = 100.0f;
  for (int i = 0; i < 3; ++i) {
    camera = std::lerp(camera, target, 0.5f);  // 毎フレーム半分ずつ近づく
    std::print("{} ", camera);
  }
  std::println("");
}
```

```text title="実行結果"
50 75 87.5 
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| カメラをなめらかに追従させる | `cam = std::lerp(cam, target, 1 - std::exp(-k * dt))` |
| HP バーの色を変える | `std::lerp(a, b, t)` |

## よくあるミス

??? failure "フレームレートに依存する補間"
    `lerp(cur, target, 0.1f)` を毎フレーム呼ぶと、フレームレートで速さが変わります。時間（`dt`）を使った式にします。

## 類似

| 名前 | 違い |
| --- | --- |
| SimpleMath の `Vector3::Lerp` | ベクトルの補間 |
| [`clamp`](../../algorithms/clamp.md) | t を 0〜1 に収める |

## コンパイラ対応

C++98 から使えます。`std::lerp` は C++20、`hypot` の 3 引数は C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 割合で補間する
    - [x] `t` は 0〜1
    - [x] フレームレートに依存しない式に

## 関連ページ

- [cpprefjp: std::lerp](https://cpprefjp.github.io/reference/cmath/lerp.html)
- [cppreference: std::lerp](https://en.cppreference.com/w/cpp/numeric/math/lerp)
