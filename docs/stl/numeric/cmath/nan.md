---
title: std::nan
summary: "指定した文字列に対応する NaN（非数）を返す。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::nan

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cmath>`
</div>

NaN（Not a Number）は、「値がない」を表すために使われる特別な小数の値です。`std::nan("")` で作れます。「未設定の浮動小数点」を表したいときに使いますが、比較が全部 `false` になるので扱いに注意が必要です。

!!! tip "ポイント"
    - `float` / `double` / `long double` の版がある。
    - 引数が整数なら `double` として計算される。
    - エラーは `errno` か浮動小数点例外で知らされる。

!!! info "このページを読む前に"
    [<cmath>](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::nan {#nan}

```cpp
double nan(const char* tagp);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `tagp` | 文字列 | NaN の種類を示す文字列（普通は空文字列） |

- 戻り値: NaN
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  double v = std::nan("");
  std::println("{}", std::isnan(v));
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 「まだ計算されていない」値の目印 |

## よくあるミス

??? failure "`==` で NaN を調べる"
    NaN は自分自身とも等しくありません。`std::isnan` で調べます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`isnan`](isnan.md) | NaN かを調べる |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 指定した文字列に対応する NaN（非数）を返す
    - [x] `float` / `double` / `long double` の版がある
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::nan](https://cpprefjp.github.io/reference/cmath/nan.html)
- [cppreference: std::nan](https://en.cppreference.com/w/cpp/numeric/math/nan)
