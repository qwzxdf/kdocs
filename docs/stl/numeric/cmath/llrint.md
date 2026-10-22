---
title: std::llrint
summary: "現在の丸めモードで整数に丸める（long long で返す）。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::llrint

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cmath>`
</div>

`lrint` の `long long` 版です。Windows のように `long` が 32 ビットの環境でも、大きな値を安全に扱えます。

!!! tip "ポイント"
    - `float` / `double` / `long double` の版がある。
    - 引数が整数なら `double` として計算される。
    - エラーは `errno` か浮動小数点例外で知らされる。

!!! info "このページを読む前に"
    [<cmath>](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::llrint {#llrint}

```cpp
long long llrint(double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点 | 引数 |

- 戻り値: 丸めた `long long`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{} {}", std::llrint(2.5), std::llrint(3.5));
}
```

```text title="実行結果"
2 4
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 大きな値の整数化 |

## よくあるミス

??? failure "`long` と取り違える"
    Windows では `long` は 32 ビットです。大きな値は `llrint` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`lrint`](lrint.md) | long 版 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 現在の丸めモードで整数に丸める（long long で返す）
    - [x] `float` / `double` / `long double` の版がある
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::llrint](https://cpprefjp.github.io/reference/cmath/llrint.html)
- [cppreference: std::llrint](https://en.cppreference.com/w/cpp/numeric/math/rint)
