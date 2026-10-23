---
title: std::to_array
summary: "配列リテラルや C の配列から、std::array を作る。"
order: 900
tags:
  - コンテナ
---

# std::to_array

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <array>`
</div>

`std::array<int, 3> a = {1, 2, 3};` と書くとき、要素数の `3` を自分で書く必要があります。要素を増やしたときに、数を直し忘れると、ビルドエラーか、意図しない初期化になります。`std::to_array({1, 2, 3})` は、要素を数えて、`std::array<int, 3>` を作ってくれます。C の配列や文字列リテラルからも作れます。

!!! tip "ポイント"
    - 要素数を数えなくてよい（推論される）。
    - 文字列リテラルからは、終端の `'\0'` も含む `array<char, N>` になる。
    - C 配列からのコピーやムーブもできる。

!!! info "このページを読む前に"
    [`std::array`](array.md) を先に読んでください。

## 関数の詳しい説明

### std::to_array {#to_array}

```cpp
template <class T, std::size_t N>
constexpr std::array<std::remove_cv_t<T>, N> to_array(T (&a)[N]);
template <class T, std::size_t N>
constexpr std::array<std::remove_cv_t<T>, N> to_array(T (&&a)[N]);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `a` | 配列 | 元の配列（C の配列、または `{...}` の初期化子） |

- 戻り値: `std::array<T, N>`
- 計算量: O(N)


## 実際に動かしてみる

```cpp
#include <array>
#include <print>

int main() {
  auto a = std::to_array({1, 2, 3});
  auto s = std::to_array("ab");
  std::println("{} {}", a.size(), s.size());
}
```

```text title="実行結果"
3 3
```

## ゲームでの使いどころ

定数の表を `std::array` で作るときに使います。`constexpr auto kDirs = std::to_array<Offset>({{0, 1}, {1, 0}, {0, -1}, {-1, 0}});` と書けば、方向の数を数えずに済みます。

C の配列から `std::array` に移行するときにも便利です。`int a[] = {...};` を `std::to_array(a)` で `std::array` にできます。

文字列リテラルからは、終端の `'\0'` も含む `std::array<char, N>` になります。長さに注意します。

## よくあるミス

??? failure "型が混ざった初期化子を渡す"
    `{1, 2.5}` のように型が混ざると、型が決まらずコンパイルエラーです。型をそろえるか、要素の型を指定します（`std::to_array<double>({1, 2.5})`）。

??? failure "型を推論できず、コンパイルエラーになる"
    `std::to_array({1, 2.5})` のように、型の違う要素が混ざると、推論に失敗します。型を明示して `std::to_array<double>({1, 2.5})` と書きます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`array`](array.md) | 固定長配列 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 要素数を推論して std::array を作る
    - [x] 文字列リテラルは終端も含む
    - [x] 型は 1 つにそろえる

## 関連ページ

- [cpprefjp: std::to_array](https://cpprefjp.github.io/reference/array/to_array.html)
- [cppreference: std::to_array](https://en.cppreference.com/w/cpp/container/array/to_array)
