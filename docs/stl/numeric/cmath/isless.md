---
title: std::isless
summary: "浮動小数点を比べる（x が y より小さいか）。NaN でも例外を出さない。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::isless

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cmath>`
</div>

NaN が混ざった比較は、普通の `<` では浮動小数点例外が起きる環境があります。`isless` は、NaN があっても例外を出さずに結果（`false`）を返す、安全な比較です。

!!! tip "ポイント"
    - `float` / `double` / `long double` の版がある。
    - 引数が整数なら `double` として計算される。
    - エラーは `errno` か浮動小数点例外で知らされる。

!!! info "このページを読む前に"
    [<cmath>](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::isless {#isless}

```cpp
bool isless(double x, double y);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x, y` | 浮動小数点 | 比べる 2 つの値 |

- 戻り値: x が y より小さいか
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{}", std::isless(1.0, 2.0));
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | NaN が混ざりうる計算の比較 |

## よくあるミス

??? failure "普通の比較で十分な場面で使う"
    NaN の心配がなければ、`<` `>` のほうが読みやすいです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`isnan`](isnan.md) | NaN の判定 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 浮動小数点を比べる（x が y より小さいか）。NaN でも例外を出さない
    - [x] `float` / `double` / `long double` の版がある
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::isless](https://cpprefjp.github.io/reference/cmath/isless.html)
- [cppreference: std::isless](https://en.cppreference.com/w/cpp/numeric/math/isless)
