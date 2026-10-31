---
title: views::concat
summary: "複数の範囲を、1 本につなげて見せる view。"
order: 900
group: ビュー（std::views）
tags:
  - アルゴリズム
---

# views::concat

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-26">C++26</span>
`#include <ranges>`
</div>

複数の範囲を、1 つの範囲として、続けて走査したい。`std::views::concat(a, b, c)` は、`a` の要素、`b` の要素、`c` の要素を、順につなげた 1 つのビューを作ります。範囲の型が違っていても、要素の型が共通で使えればつなげられます。

!!! tip "ポイント"
    - 複数の範囲を、順につなげて 1 つのビューにする
    - 範囲の型は違ってもよい（`vector` と `array` など）
    - 元の要素を参照するので、書き換えもできる
    - C++26

!!! info "このページを読む前に"
    [ビュー](../views.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::views::concat {#concat}

<span class="ver ver-26">C++26</span>

```cpp
inline constexpr /* 未規定 */ concat = /* 未規定 */;
// views::concat(r1, r2, ...)
```

`join` との違いは、`join` が「範囲の範囲」を平らにするのに対し、`concat` は、並べた複数の範囲を直接つなげる点です。

すべての範囲の要素の型から、共通の参照型が決まる必要があります。`int&` と `const int&` が混ざると、共通の参照型は `const int&` になり、書き換えられなくなります。

範囲が `random_access_range` かつ `sized_range` なら、結果もランダム アクセスです。1 つでも `input_range` どまりなら、結果もそれになります。

## 使い方の形

手元の MSVC では使えないので、動かさずに、形だけを示します。

```cpp
std::vector<int> a = {1, 2, 3};
std::array<int, 2> b = {4, 5};

for (int x : std::views::concat(a, b)) {
  // 1, 2, 3, 4, 5 の順
}

// 元の要素を書き換えられる
for (int& x : std::views::concat(a, b)) x *= 2;
```

## ゲームでの使いどころ

複数の配列に分かれたデータを、1 つのループで処理するときに使います。

## よくあるミス

??? failure "join と取り違える"
    `join` は、範囲の範囲を平らにする別の機能です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`join`](join.md) | 範囲の範囲を平らにする |
| [`single`](single.md) | 1 要素のビュー |
| [`all`](all.md) | 範囲をビューにする |

## コンパイラ対応

C++26 の機能です。手元の MSVC（Visual Studio 2026）では未対応のため、サンプルは動かしていません。

## 関連ページ

- [cpprefjp: views::concat](https://cpprefjp.github.io/reference/ranges/concat_view.html)
- [cppreference: views::concat](https://en.cppreference.com/w/cpp/ranges/concat_view)
