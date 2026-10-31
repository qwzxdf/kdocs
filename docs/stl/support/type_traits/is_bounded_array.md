---
title: std::is_bounded_array
summary: "型が要素数の決まった配列かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_bounded_array

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <type_traits>`
</div>

`int[3]` のように要素数が型に含まれる配列と、`int[]` のように含まれない配列を区別したい。`std::is_bounded_array` は、<strong>要素数が決まった配列か</strong>を調べます。

!!! tip "ポイント"
    - `std::is_bounded_array_v<T>` は、`T` が要素数の決まった配列か
    - `int[3]` は `true`、`int[]` は `false`
    - `std::is_bounded_array<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - `extent_v<T>` が 0 でない配列の目印にもなる

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_bounded_array_v {#is_bounded_array}

<span class="ver ver-20">C++20</span>

```cpp
template <class T>
inline constexpr bool is_bounded_array_v = is_bounded_array<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

要素数が決まった配列（`int[3]`）が `true` です。`int[]` のような要素数のない配列は、`false` です。C++20 で追加されました。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("int[3]                     -> {}", std::is_bounded_array_v<int[3]>);
  std::println("int[]                      -> {}", std::is_bounded_array_v<int[]>);
  std::println("int*                       -> {}", std::is_bounded_array_v<int*>);
}
```

```text title="実行結果"
int[3]                     -> true
int[]                      -> false
int*                       -> false
```

## ゲームでの使いどころ

`std::make_unique` のように、配列型を受け取る関数が、要素数つきの配列を弾く場面で使えます。

```cpp
template <class T>
auto MakeBuffer(std::size_t n) {
  static_assert(!std::is_bounded_array_v<T>, "要素数は引数で渡します。T[] を指定してください");
  return std::make_unique<T>(n);   // T が int[] なら、n 個の配列
}
```

## よくあるミス

??? failure "int[] も true だと思う"
    要素数がない `int[]` は `false` です。`is_unbounded_array` で調べます。

??? failure "std::array を調べる"
    `std::array<int, 3>` は、配列ではなくクラスなので `false` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_unbounded_array`](is_unbounded_array.md) | 要素数が決まっていない配列か |
| [`is_array`](is_array.md) | どちらの配列も `true` |
| [`extent`](extent.md) | 配列の要素数を取り出す |

## コンパイラ対応

C++20 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_bounded_array_v<T>` は、`T` が要素数の決まった配列か
    - [x] 要素数が決まった配列型だけが `true`（C++20）
    - [x] 要素数のない配列は `is_unbounded_array`

## 関連ページ

- [cpprefjp: std::is_bounded_array](https://cpprefjp.github.io/reference/type_traits/is_bounded_array.html)
- [cppreference: std::is_bounded_array](https://en.cppreference.com/w/cpp/types/is_bounded_array)
