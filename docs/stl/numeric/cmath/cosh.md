---
title: std::cosh
summary: "双曲線余弦（cosh）を求める。"
order: 31
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::cosh

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cmath>`
</div>

`std::cosh` は、**双曲線余弦**を返す関数です。ロープやケーブルが両端でぶら下がる形（懸垂線）は、`cosh` で表せます。

!!! tip "ポイント"
    - `cosh(0)` は 1。左右対称。
    - `cosh(x) = (e^x + e^−x) / 2`。

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::cosh {#cosh}

```cpp
double cosh(double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点 | 値 |

- 戻り値: 双曲線余弦
- 計算量: O(1)

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{:.4f}", std::cosh(1.0));
}
```

```text title="実行結果"
1.5431
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 吊り橋・ロープのたるみの曲線 | `a * std::cosh(x / a)` |

## よくあるミス

??? failure "cos と混同する"
    周期関数ではなく、1 以上の値です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`sinh`](sinh.md) | 双曲線正弦 |
| [`tanh`](tanh.md) | 双曲線正接 |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 双曲線余弦
    - [x] 1 以上の値
    - [x] 懸垂線

## 関連ページ

- [cpprefjp: std::cosh](https://cpprefjp.github.io/reference/cmath/cosh.html)
- [cppreference: std::cosh](https://en.cppreference.com/w/cpp/numeric/math/cosh)
