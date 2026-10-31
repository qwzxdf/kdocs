---
title: std::is_unsigned
summary: "型が符号なしの算術型かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_unsigned

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

符号なし整数の引き算は折り返します。符号なしかを調べて警告したいことがあります。`std::is_unsigned` は、<strong>型が符号なしの算術型か</strong>を調べます。

!!! tip "ポイント"
    - `std::is_unsigned_v<T>` は、`T` が符号なしの算術型か
    - `bool` も `true`
    - `std::is_unsigned<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - `char` は環境次第

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_unsigned_v {#is_unsigned}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
inline constexpr bool is_unsigned_v = is_unsigned<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

符号を持たない算術型が `true` です。`unsigned int`、`unsigned char`、`bool` が含まれます。`int` や `float` は `false` です。`char` が符号なしかどうかは、環境で決まります。列挙型は、基になる型が符号なしでも `false` です。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("unsigned int               -> {}", std::is_unsigned_v<unsigned int>);
  std::println("int                        -> {}", std::is_unsigned_v<int>);
  std::println("bool                       -> {}", std::is_unsigned_v<bool>);
  std::println("float                      -> {}", std::is_unsigned_v<float>);
}
```

```text title="実行結果"
unsigned int               -> true
int                        -> false
bool                       -> true
float                      -> false
```

## ゲームでの使いどころ

符号なしの型には、引き算の結果が負になる比較を避ける処理を選びます。

```cpp
template <class T>
constexpr bool Within(T a, T b, T range) {
  if constexpr (std::is_unsigned_v<T>) {
    T diff = a > b ? a - b : b - a;   // 符号なしの引き算は、負になる代わりに巻き戻る
    return diff <= range;
  } else {
    return std::abs(a - b) <= range;
  }
}
```

## よくあるミス

??? failure "bool が false だと思う"
    `bool` は符号を持たない型として扱われ、`true` です。

??? failure "符号なし同士の引き算が負になると思う"
    `3u - 5u` は負にならず、4294967294 になります。差の絶対値を求めるときは、大きい方から引きます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_signed`](is_signed.md) | 符号を持つか |
| [`make_unsigned`](make_unsigned.md) | 符号なしの型に直す |
| [`is_integral`](is_integral.md) | 整数型か |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_unsigned_v<T>` は、`T` が符号なしの算術型か
    - [x] 符号を持たない算術型が `true`
    - [x] `bool` も含まれる

## 関連ページ

- [cpprefjp: std::is_unsigned](https://cpprefjp.github.io/reference/type_traits/is_unsigned.html)
- [cppreference: std::is_unsigned](https://en.cppreference.com/w/cpp/types/is_unsigned)
