---
title: std::three_way_comparable
summary: "`<=>` と、`==`・`<` などで比べられる型を要求する。"
order: 900
group: 比較（<compare>）
tags:
  - 型・言語サポート
---

# std::three_way_comparable

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <compare>`
</div>

`std::sort` や `std::map` は、要素が大小を比べられることを要求します。C++20 では、比べる手段として `<=>` が増えました。`std::three_way_comparable<T>` は、<strong>型 `T` が三方比較（`<=>`）と、通常の比較演算子で使えるか</strong>を要求するコンセプトです。

!!! tip "ポイント"
    - `std::three_way_comparable<T>`: `T` が `<=>` と `==` で比較できるか
    - `int`、`float`、`std::string` などは満たす
    - `operator<=>` を定義していない構造体は満たさない
    - `<compare>` で宣言される

!!! info "このページを読む前に"
    [STL](../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::three_way_comparable {#three_way_comparable}

<span class="ver ver-20">C++20</span>

```cpp
template <class T, class Cat = std::partial_ordering>
concept three_way_comparable = /* 条件 */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べる型 |
| `Cat` | 順序の型 | 要求する順序の強さ（既定は `partial_ordering`） |

`a <=> b` が書けて、`==`、`!=`、`<`、`>`、`<=`、`>=` もそろっている型が満たします。第 2 引数で、`<=>` の結果が `strong_ordering` 以上であることなども要求できます。

`auto operator<=>(const T&) const = default;` を書いた構造体は、メンバー変数の型がすべて満たしていれば、満たします。

## 実際に動かしてみる

```cpp
#include <compare>
#include <print>
#include <string>

struct Plain {
  int x;
};
struct Ordered {
  int x;
  auto operator<=>(const Ordered&) const = default;
};

int main() {
  std::println("int         : {}", std::three_way_comparable<int>);
  std::println("std::string : {}", std::three_way_comparable<std::string>);
  std::println("Plain       : {}", std::three_way_comparable<Plain>);
  std::println("Ordered     : {}", std::three_way_comparable<Ordered>);
}
```

```text title="実行結果"
int         : true
std::string : true
Plain       : false
Ordered     : true
```

## ゲームでの使いどころ

比較できる型だけを受け付ける、自作の並べ替えや検索に使います。

```cpp
template <std::three_way_comparable T>
T MaxOf(const T& a, const T& b) { return (a <=> b) < 0 ? b : a; }
```

## よくあるミス

??? failure "`==` だけを定義して、満たされない"
    `<=>` も必要です。`= default` で自動生成します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`totally_ordered`](concepts/totally_ordered.md) | 従来の比較演算子版 |
| [`strong_ordering`](strong_ordering.md) | 全順序を表す型 |

## コンパイラ対応

C++20 から使えます。GCC 10 以降、Clang 13 以降、Visual Studio 2019 16.x 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `three_way_comparable<T>` は `<=>` で比べられる型か
    - [x] `operator<=>` を `= default` にすると満たす
    - [x] 従来の比較なら `totally_ordered`

## 関連ページ

- [cpprefjp: std::three_way_comparable](https://cpprefjp.github.io/reference/compare/three_way_comparable.html)
- [cppreference: std::three_way_comparable](https://en.cppreference.com/w/cpp/utility/three_way_comparable)
