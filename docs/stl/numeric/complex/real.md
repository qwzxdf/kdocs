---
title: std::real
summary: "複素数の実部を取り出す。"
order: 900
tags:
  - 数値
---

# std::real

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <complex>`
</div>

複素数 `a + bi` の `a`（実部）を取り出すには、`z.real()` というメンバ関数と、`std::real(z)` という関数の 2 通りがあります。関数版は、`double` などの普通の数にも使えるので、テンプレートで型を問わず書けます。

!!! tip "ポイント"
    - メンバ関数と同名の自由関数がある。
    - ゲームでは 2D の回転や周期的な波の計算で登場する。
    - `float` / `double` / `long double` で使える。

!!! info "このページを読む前に"
    [`std::complex`](../complex.md) を先に読んでください。

## 関数の詳しい説明

### std::real {#real}

```cpp
template <class T> constexpr T real(const complex<T>& z);
constexpr T complex<T>::real() const;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `z` | complex<T> | 対象の複素数 |

- 戻り値: 複素数の実部を取り出す結果
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <complex>
#include <print>

int main() {
  std::complex<double> z{3.0, 4.0};
  std::println("{} {}", std::real(z), z.real());
}
```

```text title="実行結果"
3 3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 2D の向きと回転 | `std::real(z)` |

## よくあるミス

??? failure "float の変数に double を混ぜる"
    `complex<float>` に `double` の値を混ぜると型が合わずコンパイルエラーになります。型をそろえます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::complex`](../complex.md) | 複素数の型 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 複素数の実部を取り出す
    - [x] std::complex の関数
    - [x] 2D の回転で使える

## 関連ページ

- [cpprefjp: std::real](https://cpprefjp.github.io/reference/complex/real.html)
- [cppreference: std::real](https://en.cppreference.com/w/cpp/numeric/complex/real)
