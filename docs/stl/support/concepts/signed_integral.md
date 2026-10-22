---
title: std::signed_integral
summary: "符号付きの整数型であることを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::signed_integral

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <concepts>`
</div>

`integral` のうち、負の値を持てる整数型だけを受け付けます。`int`・`long` は満たし、`unsigned` や `float` は満たしません。

!!! tip "ポイント"
    - コンセプト。`requires` やテンプレートの制約に書く。
    - `std::signed_integral<...>` は `bool` の定数式。
    - 満たさない型を渡すと、コンパイルエラーの原因が読みやすくなる。

!!! info "このページを読む前に"
    [コンセプト](../../../basics/template.md) の考え方と、[`std::same_as`](same_as.md) を先に読んでください。

## 関数の詳しい説明

### std::signed_integral {#signed_integral}

```cpp
template <class T>
concept signed_integral = /* integral<T> かつ T が符号付き */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べる型 |

- 戻り値: 条件を満たせば `true`（コンパイル時の定数）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <concepts>
#include <print>

int main() {
  std::println("{}", std::signed_integral<int>);
  std::println("{}", std::signed_integral<unsigned>);
  std::println("{}", std::signed_integral<float>);
}
```

```text title="実行結果"
true
false
false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | テンプレートの引数に条件をつけて、使える型を制限する |

## よくあるミス

??? failure "`char` の符号を決めつける"
    `char` の符号は処理系次第です。`signed char` や `unsigned char` を明示します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`integral`](integral.md) | 整数全般 |
| [`unsigned_integral`](unsigned_integral.md) | 符号なし |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 符号付きの整数型であることを要求する
    - [x] コンセプト。`requires` やテンプレートの制約に書く
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::signed_integral](https://cpprefjp.github.io/reference/concepts/signed_integral.html)
- [cppreference: std::signed_integral](https://en.cppreference.com/w/cpp/concepts/signed_integral)
