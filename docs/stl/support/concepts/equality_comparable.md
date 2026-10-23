---
title: std::equality_comparable
summary: "`==` と `!=` で比べられる型であることを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::equality_comparable

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <concepts>`
</div>

検索や重複の判定など、等しいかどうかを比べるアルゴリズムのために、`==` が使える型だけを受け付けたい。`std::equality_comparable` は、<strong>T が等しいかを比べられるか</strong>を要求するコンセプトです。

!!! tip "ポイント"
    - `std::equality_comparable<T>` は、`T` が `==` と `!=` で比べられるか
    - `template <std::equality_comparable T>` のように、テンプレートの引数に直接書ける
    - 値は `bool` の定数なので、`static_assert` や `if constexpr` にも使える
    - 条件を満たさないと、分かりやすいエラーメッセージで弾かれる

!!! info "このページを読む前に"
    [テンプレートの基本](../../../basics/template.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::equality_comparable {#equality_comparable}

<span class="ver ver-20">C++20</span>

```cpp
template <class T>
concept equality_comparable = /* 条件 */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べる型 |

`a == b` と `a != b` が書けて、結果が `bool` として使える型が満たします。`int` や `std::string` は満たします。`==` を定義していない構造体は満たしません。

C++20 の `operator==` を `= default` で定義しておくと、構造体も満たすようになります。

コンセプトは、テンプレートの引数に条件を付ける C++20 の機能です。条件を満たさない型を渡すと、テンプレートの深い所でエラーが出るのではなく、呼び出しの場所で「この型は条件を満たしていない」と報告されます。

## 実際に動かしてみる

```cpp
#include <concepts>
#include <print>
#include <string>

struct Player {
  int hp;
  float x;
};

int main() {
  std::println("int                                -> {}", std::equality_comparable<int>);
  std::println("std::string                        -> {}", std::equality_comparable<std::string>);
  std::println("Player                             -> {}", std::equality_comparable<Player>);
}
```

```text title="実行結果"
int                                -> true
std::string                        -> true
Player                             -> false
```

## ゲームでの使いどころ

値で検索する関数に使います。

```cpp
template <std::equality_comparable T>
bool Contains(const std::vector<T>& v, const T& x) {
  return std::find(v.begin(), v.end(), x) != v.end();
}
```

## よくあるミス

??? failure "参照や `const` が付いた型で、期待と違う結果になる"
    `std::remove_cvref_t<T>` で外してから調べます。

??? failure "C++17 以前で使おうとする"
    コンセプトは C++20 の機能です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`same_as`](same_as.md) | 2 つの型が同じ |
| [`integral`](integral.md) | 整数型 |

## コンパイラ対応

C++20 の機能です。GCC 10 以降、Clang 10 以降、Visual Studio 2019 16.3 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::equality_comparable<T>` は、`T` が `==` と `!=` で比べられるか
    - [x] テンプレートの引数に直接書ける
    - [x] `static_assert` と `if constexpr` にも使える

## 関連ページ

- [cpprefjp: std::equality_comparable](https://cpprefjp.github.io/reference/concepts/equality_comparable.html)
- [cppreference: std::equality_comparable](https://en.cppreference.com/w/cpp/concepts/equality_comparable)
