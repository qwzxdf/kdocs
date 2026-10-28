---
title: std::three_way_comparable_with
summary: "2 つの型を `<=>` で比べられることを要求する。"
order: 900
group: 比較（<compare>）
tags:
  - 型・言語サポート
---

# std::three_way_comparable_with

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <compare>`
</div>

型の違う 2 つの値を `<=>` で比べたい場面があります。たとえば、`std::string` と `const char*`。`std::three_way_comparable_with<T, U>` は、<strong>型 `T` と `U` が、お互いに三方比較できるか</strong>を要求するコンセプトです。

!!! tip "ポイント"
    - `std::three_way_comparable_with<T, U>`: `T` と `U` が互いに `<=>` で比べられるか
    - `T` どうし、`U` どうしも比べられること
    - `int` と `long`、`std::string` と `const char*` などが満たす
    - `<compare>` で宣言される

!!! info "このページを読む前に"
    [STL](../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::three_way_comparable_with {#three_way_comparable_with}

<span class="ver ver-20">C++20</span>

```cpp
template <class T, class U, class Cat = std::partial_ordering>
concept three_way_comparable_with = /* 条件 */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 1 つ目の型 |
| `U` | 型 | 2 つ目の型 |
| `Cat` | 順序の型 | 要求する順序の強さ |

`T` と `U` の両方が `three_way_comparable` で、さらに共通の型に変換できて、`t <=> u` と `u <=> t` が書けるなら満たします。

異種の型を比べる検索（`std::map` の透過的な比較など）で、キーの型と検索値の型を比べられるかの検査に使います。

## 実際に動かしてみる

```cpp
#include <compare>
#include <print>
#include <string>

struct Plain {
  int x;
};

int main() {
  std::println("int と long              : {}", std::three_way_comparable_with<int, long>);
  std::println("std::string と const char*: {}", std::three_way_comparable_with<std::string, const char*>);
  std::println("int と Plain             : {}", std::three_way_comparable_with<int, Plain>);
}
```

```text title="実行結果"
int と long              : true
std::string と const char*: true
int と Plain             : false
```

## ゲームでの使いどころ

異種の型で検索するコンテナや関数の制約に使います。

## よくあるミス

??? failure "片方向だけ比較できて、満たされない"
    `t <=> u` と `u <=> t` の両方が必要です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`three_way_comparable`](three_way_comparable.md) | 同じ型どうし |
| [`totally_ordered_with`](concepts/totally_ordered_with.md) | 従来の比較版 |

## コンパイラ対応

C++20 から使えます。GCC 10 以降、Clang 13 以降、Visual Studio 2019 16.x 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `three_way_comparable_with<T, U>` は異種の型の三方比較
    - [x] 双方向で比べられる必要がある
    - [x] `T` どうし、`U` どうしも比べられること

## 関連ページ

- [cpprefjp: std::three_way_comparable_with](https://cpprefjp.github.io/reference/compare/three_way_comparable_with.html)
- [cppreference: std::three_way_comparable_with](https://en.cppreference.com/w/cpp/utility/three_way_comparable_with)
