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

NaN には「ペイロード」と呼ばれる、種類を表す付加情報を持たせられます。デバッグで、どこで生まれた NaN かを区別したいときに、`std::nan` が使えます。普通は、ペイロードなしの NaN が欲しいだけで、空の文字列を渡して使います。

!!! tip "ポイント"
    - `std::nan("")` は quiet NaN を返す
    - 引数の文字列で、NaN の付加情報（ペイロード）を指定できる（実装依存）
    - `float` 版は `nanf`、`long double` 版は `nanl`
    - 判定は `std::isnan`

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::nan {#nan}

<span class="ver ver-11">C++11</span>

```cpp
double nan(const char* tagp);
float nanf(const char* tagp);
long double nanl(const char* tagp);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `tagp` | `const char*` | NaN の種類を表す文字列。通常は `""` |

戻り値は、`tagp` に対応する quiet NaN です。`""` を渡すと、既定の NaN になります。数字の文字列を渡すと、その数をペイロードに持つ NaN を作る環境が多いですが、規格上は実装定義です。

型ごとの名前が分かれているのは、C 言語に由来する歴史です。C++ では、`std::numeric_limits<double>::quiet_NaN()` のほうが、型がテンプレート引数で決まるので、使いやすいです。

NaN は、すべての比較が偽になります。判定は必ず `std::isnan` で行います。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  const double x = std::nan("");
  std::println("isnan(nan(\"\")) = {}", std::isnan(x));
  std::println("x == x          = {}", x == x);
}
```

```text title="実行結果"
isnan(nan("")) = true
x == x          = false
```

## ゲームでの使いどころ

デバッグ中に NaN の種類を区別して発生源を探る、という限られた使い方があります。通常は、`numeric_limits<double>::quiet_NaN()` で足ります。

## よくあるミス

??? failure "NaN を `==` で比べる"
    `std::isnan` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`NAN`](nan_macro.md) | `float` のマクロ |
| [`isnan`](isnan.md) | NaN か |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `nan("")` は quiet NaN を返す
    - [x] 文字列でペイロードを指定できる（実装依存）
    - [x] 判定は `isnan`

## 関連ページ

- [cpprefjp: std::nan](https://cpprefjp.github.io/reference/cmath/nan.html)
- [cppreference: std::nan](https://en.cppreference.com/w/cpp/numeric/math/nan)
