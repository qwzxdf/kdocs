---
title: std::is_signed
summary: "型が符号付きの算術型かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_signed

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

整数の引き算で負になるか、符号を考える必要があるかを判断したい。`std::is_signed` は、<strong>型が符号つきの算術型か</strong>を調べます。

!!! tip "ポイント"
    - `std::is_signed_v<T>` は、`T` が符号つきの算術型か
    - `float` や `double` も `true`
    - `std::is_signed<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - `char` は環境次第

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_signed_v {#is_signed}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
inline constexpr bool is_signed_v = is_signed<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

符号を持つ算術型が `true` です。`int`、`long` などの符号つきの整数と、`float`、`double` が含まれます。`unsigned int` と `bool` は `false` です。`char` が符号つきかどうかは、環境で決まります。クラスやポインター、列挙型は `false` です。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("int                        -> {}", std::is_signed_v<int>);
  std::println("unsigned int               -> {}", std::is_signed_v<unsigned int>);
  std::println("float                      -> {}", std::is_signed_v<float>);
  std::println("bool                       -> {}", std::is_signed_v<bool>);
}
```

```text title="実行結果"
int                        -> true
unsigned int               -> false
float                      -> true
bool                       -> false
```

## ゲームでの使いどころ

符号つきの型だけに、絶対値の処理を行う関数を書きます。

```cpp
template <class T>
constexpr T Abs(T value) {
  if constexpr (std::is_signed_v<T>) {
    return value < 0 ? -value : value;
  } else {
    return value;   // 符号なしは負にならない
  }
}
```

## よくあるミス

??? failure "float を符号なしだと思う"
    浮動小数点数は符号を持つので `true` です。整数だけを調べたいなら、`is_integral` と組み合わせます。

??? failure "char の符号を決めつける"
    `char` が符号つきかどうかは、環境（とコンパイラのオプション）で変わります。数として使うなら `signed char` か `unsigned char`、または `std::int8_t` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_unsigned`](is_unsigned.md) | 符号なしか |
| [`make_signed`](make_signed.md) | 符号つきの型に直す |
| [`is_integral`](is_integral.md) | 整数型か |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_signed_v<T>` は、`T` が符号つきの算術型か
    - [x] 符号を持つ算術型が `true`
    - [x] `unsigned` と `bool` は `false`

## 関連ページ

- [cpprefjp: std::is_signed](https://cpprefjp.github.io/reference/type_traits/is_signed.html)
- [cppreference: std::is_signed](https://en.cppreference.com/w/cpp/types/is_signed)
