---
title: std::is_unbounded_array
summary: "型が要素数の決まっていない配列かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_unbounded_array

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <type_traits>`
</div>

`int[]` のように、要素数が型に含まれない配列かを調べます。`std::make_unique<int[]>(n)` の戻り値の型などで登場します。

!!! tip "ポイント"
    - `std::is_unbounded_array_v<T>` は、`T` が要素数の決まっていない配列か
    - `T[]` が `true`、`T[N]` が `false`
    - `std::is_unbounded_array<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - `make_unique<T[]>(n)` の型を見分けるのに使う

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_unbounded_array_v {#is_unbounded_array}

<span class="ver ver-20">C++20</span>

```cpp
template <class T>
inline constexpr bool is_unbounded_array_v = is_unbounded_array<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

要素数が決まっていない配列（`int[]`）が `true` です。`int[3]` のような要素数のある配列は `false` です。C++20 で追加されました。`std::make_unique<int[]>(n)` のような、後から要素数を指定する配列を受ける関数で、型を見分けるのに使います。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("int[]                      -> {}", std::is_unbounded_array_v<int[]>);
  std::println("int[3]                     -> {}", std::is_unbounded_array_v<int[3]>);
  std::println("int*                       -> {}", std::is_unbounded_array_v<int*>);
}
```

```text title="実行結果"
int[]                      -> true
int[3]                     -> false
int*                       -> false
```

## ゲームでの使いどころ

`T[]` の形で型を受け取る関数に、要素数つきの型を渡されたらエラーにします。

```cpp
template <class T>
auto MakeArray(std::size_t n) {
  static_assert(std::is_unbounded_array_v<T>, "T[] の形で指定してください");
  return std::make_unique<T>(n);
}

// auto a = MakeArray<int[]>(10);
```

## よくあるミス

??? failure "int[3] が true になると思う"
    要素数のある配列は `false` です。`is_bounded_array` で調べます。

??? failure "ポインターを配列と混同する"
    `int*` は配列ではないので `false` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_bounded_array`](is_bounded_array.md) | 要素数が決まった配列か |
| [`is_array`](is_array.md) | どちらの配列も `true` |
| [`remove_extent`](remove_extent.md) | 配列の 1 次元ぶんを外した型 |

## コンパイラ対応

C++20 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_unbounded_array_v<T>` は、`T` が要素数の決まっていない配列か
    - [x] 要素数の決まっていない配列だけが `true`（C++20）
    - [x] 要素数つきは `is_bounded_array`

## 関連ページ

- [cpprefjp: std::is_unbounded_array](https://cpprefjp.github.io/reference/type_traits/is_unbounded_array.html)
- [cppreference: std::is_unbounded_array](https://en.cppreference.com/w/cpp/types/is_unbounded_array)
