---
title: std::lrint
summary: "現在の丸めモードで整数に丸める（long で返す）。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::lrint

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cmath>`
</div>

`rint` の結果を `long` で受け取る版です。丸めの規則は `rint` と同じです。

!!! tip "ポイント"
    - `float` / `double` / `long double` の版がある。
    - 引数が整数なら `double` として計算される。
    - エラーは `errno` か浮動小数点例外で知らされる。

!!! info "このページを読む前に"
    [<cmath>](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::lrint {#lrint}

```cpp
long lrint(double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点 | 引数 |

- 戻り値: 丸めた `long`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{} {}", std::lrint(2.5), std::lrint(3.5));
}
```

```text title="実行結果"
2 4
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 丸めた値を整数で受け取る |

## よくあるミス

??? failure "範囲外の値を渡す"
    `long` に収まらない値は未定義の結果になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`rint`](rint.md) | 小数で返す版 |
| [`llrint`](llrint.md) | long long 版 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 現在の丸めモードで整数に丸める（long で返す）
    - [x] `float` / `double` / `long double` の版がある
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::lrint](https://cpprefjp.github.io/reference/cmath/lrint.html)
- [cppreference: std::lrint](https://en.cppreference.com/w/cpp/numeric/math/rint)
