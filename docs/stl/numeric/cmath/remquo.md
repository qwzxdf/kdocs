---
title: std::remquo
summary: "割り算の余りと、商の下位ビットをいっしょに返す。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::remquo

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cmath>`
</div>

`fmod` は余りだけを返します。`remquo` は余りに加えて、商の下位の数ビットも受け取れます。周期的な関数（`sin` など）で、どの象限にいるかを知りたいときに使います。余りは `x - n·y`（n は商に最も近い整数）です。

!!! tip "ポイント"
    - `float` / `double` / `long double` の版がある。
    - 引数が整数なら `double` として計算される。
    - エラーは `errno` か浮動小数点例外で知らされる。

!!! info "このページを読む前に"
    [<cmath>](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::remquo {#remquo}

```cpp
double remquo(double x, double y, int* quo);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x, y` | 浮動小数点 | 割られる数・割る数 |
| `quo` | int* | 商の下位ビットを受け取る場所 |

- 戻り値: 余り（`x - n·y`）
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  int q = 0;
  double r = std::remquo(10.0, 3.0, &q);
  std::println("{} {}", r, q);
}
```

```text title="実行結果"
1 3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 周期関数の引数を象限ごとに分ける |

## よくあるミス

??? failure "`fmod` と同じ余りだと思う"
    `remquo` の余りは**最も近い整数**への丸めで決まるので、負になることがあります。`fmod` は 0 以上です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fmod`](fmod.md) | 切り捨て基準の余り |
| [`remainder`](remainder.md) | 余りだけ |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 割り算の余りと、商の下位ビットをいっしょに返す
    - [x] `float` / `double` / `long double` の版がある
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::remquo](https://cpprefjp.github.io/reference/cmath/remquo.html)
- [cppreference: std::remquo](https://en.cppreference.com/w/cpp/numeric/math/remquo)
