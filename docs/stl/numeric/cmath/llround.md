---
title: std::llround
summary: "四捨五入して long long にする。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::llround

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cmath>`
</div>

`round` は小数で結果を返しますが、整数がほしいときは `llround` が便利です。`lround` の `long long` 版で、大きな値でも安全です。

!!! tip "ポイント"
    - `float` / `double` / `long double` の版がある。
    - 引数が整数なら `double` として計算される。
    - エラーは `errno` か浮動小数点例外で知らされる。

!!! info "このページを読む前に"
    [<cmath>](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::llround {#llround}

```cpp
long long llround(double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点 | 引数 |

- 戻り値: 四捨五入した `long long`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{} {}", std::llround(2.5), std::llround(-2.5));
}
```

```text title="実行結果"
3 -3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | ダメージ計算の最後の整数化 |

## よくあるミス

??? failure "0.5 を偶数に丸めると思う"
    `llround` は 0.5 を**絶対値の大きいほう**へ丸めます（2.5 → 3）。偶数丸めは `llrint` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`lround`](lround.md) | long 版 |
| [`round`](round.md) | 小数で返す |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 四捨五入して long long にする
    - [x] `float` / `double` / `long double` の版がある
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::llround](https://cpprefjp.github.io/reference/cmath/llround.html)
- [cppreference: std::llround](https://en.cppreference.com/w/cpp/numeric/math/round)
