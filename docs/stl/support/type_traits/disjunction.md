---
title: std::disjunction
summary: "複数の条件のどれかが真かを調べる（短絡評価）。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::disjunction

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <type_traits>`
</div>

複数の型の性質のうち、どれか 1 つでも当てはまるか調べたい。`std::disjunction` は、<strong>左から順に評価し、真が出た時点で止める</strong>論理和です。

!!! tip "ポイント"
    - `std::disjunction_v<B1, B2, ...>`: どれか 1 つでも真か
    - 最初に真になった時点で評価を止める（短絡評価）
    - 各 `Bi` はトレイト（`::value` を持つ型）
    - C++17 で追加

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::disjunction_v {#disjunction}

<span class="ver ver-17">C++17</span>

```cpp
template <class... B>
inline constexpr bool disjunction_v = disjunction<B...>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `B...` | トレイトの並び | `::value` を持つ型 |

`disjunction<B1, B2, ...>` は、`B1::value`、`B2::value`、…のどれか 1 つでも真なら真です。最初に真が出ると、それ以降のトレイトはインスタンス化されません。

引数が 0 個なら偽です。

用途は、「いくつかの型のうち、どれかに一致する」を書くことです。`disjunction_v<is_same<T, int>, is_same<T, float>>` で、「`T` が `int` か `float`」を表せます。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

template <class T>
inline constexpr bool is_int_or_float = std::disjunction_v<std::is_same<T, int>, std::is_same<T, float>>;

int main() {
  std::println("int    : {}", is_int_or_float<int>);
  std::println("float  : {}", is_int_or_float<float>);
  std::println("double : {}", is_int_or_float<double>);
}
```

```text title="実行結果"
int    : true
float  : true
double : false
```

## ゲームでの使いどころ

許可する型の一覧をテンプレートで表します（上のコード）。

## よくあるミス

??? failure "引数 0 個で真と思う"
    引数が 0 個なら偽です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`conjunction`](conjunction.md) | 論理積 |
| [`negation`](negation.md) | 否定 |

## コンパイラ対応

C++17 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `disjunction_v<B...>` はどれか 1 つでも真か（短絡評価）
    - [x] 引数 0 個は偽
    - [x] 許可する型の一覧を表せる

## 関連ページ

- [cpprefjp: std::disjunction](https://cpprefjp.github.io/reference/type_traits/disjunction.html)
- [cppreference: std::disjunction](https://en.cppreference.com/w/cpp/types/disjunction)
