---
title: std::integral
summary: "整数型であることを要求するコンセプト。"
order: 2
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::integral

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-20">C++20</span>
`#include <concepts>`
</div>

`std::integral<T>` は、**T が整数型（`int`、`char`、`bool` など）であること**を要求するコンセプトです。`is_integral_v` のコンセプト版で、整数だけを受け取る関数テンプレートを書けます。

!!! tip "ポイント"
    - `template <std::integral T> T Half(T v)` のように書く。
    - 符号つきだけは `std::signed_integral`、符号なしだけは `std::unsigned_integral`。
    - `bool` も整数型。

!!! info "このページを読む前に"
    [テンプレートとコンセプト](../../../basics/template.md) の基本が前提です。

## 関数の詳しい説明

### std::integral {#integral}

```cpp
template <class T>
concept integral = /* 条件 */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | テンプレート引数 | 調べる型 |

- 戻り値: 条件を満たせば `true`（コンパイル時の定数）
- 計算量: コンパイル時

```cpp
#include <concepts>
#include <print>

template <std::integral T>
T Half(T v) {
  return v / 2;
}

int main() {
  std::println("{}", Half(7));       // 整数だけ受け取る
  // Half(7.0);                      // コンパイルエラー: 小数は渡せない
}
```

```text title="実行結果"
3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 整数専用の関数（ビット演算・添字計算） | `template <std::integral T>` |

## よくあるミス

??? failure "bool も受け入れる"
    `bool` は整数型です。排除したいなら条件を追加します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`floating_point`](floating_point.md) | 小数型 |
| [`is_integral`](../type_traits/is_integral.md) | 変数テンプレート版 |

## コンパイラ対応

C++20 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 整数型を要求
    - [x] 符号つき・符号なしも別にある
    - [x] `is_integral_v` のコンセプト版

## 関連ページ

- [cpprefjp: std::integral](https://cpprefjp.github.io/reference/concepts/integral.html)
- [cppreference: std::integral](https://en.cppreference.com/w/cpp/concepts/integral)
