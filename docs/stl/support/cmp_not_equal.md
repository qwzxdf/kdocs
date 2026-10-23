---
title: std::cmp_not_equal
summary: "符号付きと符号なしの整数を、安全に `!=` で比べる。"
order: 900
group: 小さな便利機能（<utility>）
tags:
  - 型・言語サポート
---

# std::cmp_not_equal

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <utility>`
</div>

`-1 < 1u` を実行すると、`false` になります。符号つきの `-1` が、符号なしに変換されて 4294967295 になるためです。コンテナのサイズ（`size_t`、符号なし）と、符号つきの変数を比べるときに、この事故がよく起きます。`std::cmp_not_equal` は、<strong>符号つきと符号なしの整数を、数学的に正しく「等しくない」で比べます</strong>。

!!! tip "ポイント"
    - `std::cmp_not_equal(-1, 4294967295u)` は、符号を考慮して整数を比べる
    - `-1 != 4294967295u` のような変換による誤りが起きない
    - 整数型（`bool` や `char` は不可）が対象
    - `<utility>` で宣言される

!!! info "このページを読む前に"
    [STL](../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::cmp_not_equal {#cmp_not_equal}

<span class="ver ver-20">C++20</span>

```cpp
template <class T, class U>
constexpr bool cmp_not_equal(T t, U u) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `t` | 整数型 | 1 つ目の値 |
| `u` | 整数型 | 2 つ目の値 |

符号つきと符号なしを、暗黙の変換なしに比べます。負の値と符号なしの値を比べるときは、負の数のほうが必ず小さい、という数学的に当然の結果が得られます。

演算子 `!=` との違いは、型が混在するときの変換です。演算子では、符号つきが符号なしに変換されて、負の数が巨大な正の数になります。`cmp_not_equal` はこれを避けます。

`bool`、`char`、`char8_t`、`char16_t`、`char32_t`、`wchar_t` は引数にできません（コンパイルエラー）。整数型（`int`、`long`、`unsigned` など）だけが対象です。

## 実際に動かしてみる

```cpp
#include <print>
#include <utility>

int main() {
  std::println("演算子 -1 != 4294967295u : {}", -1 != 4294967295u);
  std::println("cmp_not_equal : {}", std::cmp_not_equal(-1, 4294967295u));
}
```

```text title="実行結果"
演算子 -1 != 4294967295u : false
cmp_not_equal : true
```

## ゲームでの使いどころ

`size()` が返す符号なしの値と、符号つきのインデックスを比べるときに使います。

```cpp
int index = -1;
if (std::cmp_not_equal(index, items.size())) { /* 符号を考慮した比較 */ }
```

コンパイラの「符号の異なる整数の比較」の警告 (`-Wsign-compare`) も、この関数で解消できます。

## よくあるミス

??? failure "`bool` や `char` を渡してコンパイルエラーになる"
    整数型に直してから渡します。

??? failure "浮動小数点数を渡す"
    整数専用です。浮動小数点数は通常の演算子で比べます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`in_range`](in_range.md) | 値が型の範囲に収まるか |
| [`cmp_less`](cmp_less.md) | 安全な < 比較 |

## コンパイラ対応

C++20 から使えます。GCC 10 以降、Clang 13 以降、Visual Studio 2019 16.x 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `cmp_not_equal` は符号を考慮して整数を比べる
    - [x] 演算子では、符号つきが符号なしに変換されて誤る
    - [x] 整数型だけが対象

## 関連ページ

- [cpprefjp: std::cmp_not_equal](https://cpprefjp.github.io/reference/utility/cmp_not_equal.html)
- [cppreference: std::cmp_not_equal](https://en.cppreference.com/w/cpp/utility/cmp_not_equal)
