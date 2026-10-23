---
title: std::conjunction
summary: "複数の条件がすべて真かを調べる（短絡評価）。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::conjunction

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <type_traits>`
</div>

複数の型の性質が全部当てはまるか調べたい。`is_integral_v<T> && is_signed_v<T>` と書けますが、これは全部の条件を先に評価します。`std::conjunction` は、<strong>左から順に評価し、偽が出た時点で止める</strong>論理積です。

!!! tip "ポイント"
    - `std::conjunction_v<B1, B2, ...>`: 全部が真か
    - 最初に偽になった時点で評価を止める（短絡評価）
    - 各 `Bi` はトレイト（`::value` を持つ型）
    - C++17 で追加

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::conjunction_v {#conjunction}

<span class="ver ver-17">C++17</span>

```cpp
template <class... B>
inline constexpr bool conjunction_v = conjunction<B...>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `B...` | トレイトの並び | `::value` を持つ型 |

`conjunction<B1, B2, ...>` は、`B1::value`、`B2::value`、…が全部真なら真です。1 つでも偽が出ると、それ以降のトレイトは、インスタンス化されません。

この短絡評価が重要になるのは、前の条件が偽のとき、後ろの条件が不正になる場合です。たとえば、`conjunction_v<is_class<T>, is_empty<T>>` のように、「クラスのときだけ `is_empty` を調べる」と書けます。

引数が 0 個なら真です。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("整数かつ符号つき (int)      : {}", std::conjunction_v<std::is_integral<int>, std::is_signed<int>>);
  std::println("整数かつ符号つき (unsigned) : {}", std::conjunction_v<std::is_integral<unsigned>, std::is_signed<unsigned>>);
  std::println("引数なし                   : {}", std::conjunction_v<>);
}
```

```text title="実行結果"
整数かつ符号つき (int)      : true
整数かつ符号つき (unsigned) : false
引数なし                   : true
```

## ゲームでの使いどころ

複数の条件を満たす型だけを受け付けるテンプレートに使います。

```cpp
template <class... Ts>
void Register(Ts... items) {
  static_assert(std::conjunction_v<std::is_trivially_copyable<Ts>...>, "全部の型が memcpy 可能である必要があります");
}
```

## よくあるミス

??? failure "`&&` で書いて、後ろの条件が不正でエラーになる"
    `conjunction` で短絡評価します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`disjunction`](disjunction.md) | 論理和 |
| [`negation`](negation.md) | 否定 |

## コンパイラ対応

C++17 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `conjunction_v<B...>` は全部が真か（短絡評価）
    - [x] 引数 0 個は真
    - [x] 可変長の型の並びを一度に調べられる

## 関連ページ

- [cpprefjp: std::conjunction](https://cpprefjp.github.io/reference/type_traits/conjunction.html)
- [cppreference: std::conjunction](https://en.cppreference.com/w/cpp/types/conjunction)
