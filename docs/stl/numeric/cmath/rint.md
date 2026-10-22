---
title: std::rint
summary: "現在の丸めモードで整数に丸める（結果は小数）。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::rint

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cmath>`
</div>

丸めの規則を `fesetround` で切り替えられる環境では、`rint` はその規則で丸めます。既定は「最も近い偶数への丸め」で、2.5 は 2、3.5 は 4 になります。

!!! tip "ポイント"
    - `float` / `double` / `long double` の版がある。
    - 引数が整数なら `double` として計算される。
    - エラーは `errno` か浮動小数点例外で知らされる。

!!! info "このページを読む前に"
    [<cmath>](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::rint {#rint}

```cpp
double rint(double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点 | 引数 |

- 戻り値: 丸めた値（小数型）
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{} {}", std::rint(2.5), std::rint(3.5));
}
```

```text title="実行結果"
2 4
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 丸めの偏りを避ける統計処理 |

## よくあるミス

??? failure "四捨五入と同じだと思う"
    既定は偶数丸めです。2.5 が 2 になります。四捨五入は `round` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`round`](round.md) | 四捨五入 |
| [`nearbyint`](nearbyint.md) | 例外を出さない版 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 現在の丸めモードで整数に丸める（結果は小数）
    - [x] `float` / `double` / `long double` の版がある
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::rint](https://cpprefjp.github.io/reference/cmath/rint.html)
- [cppreference: std::rint](https://en.cppreference.com/w/cpp/numeric/math/rint)
