---
title: std::make_unsigned
summary: "符号つき整数の型を、符号なしの同じ大きさの型にする。"
order: 19
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::make_unsigned

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <type_traits>`
</div>

整数型を、同じ大きさの符号なしの型に変えたい。たとえば、ビット演算では、符号つき整数の右シフトの結果が環境によって違うため、先に符号なしに直したい。`std::make_unsigned` は、<strong>同じ大きさの符号なし整数型</strong>を返します。

!!! tip "ポイント"
    - `std::make_unsigned_t<int>` は `unsigned int`
    - 同じ大きさの符号なし型を返す
    - `const` / `volatile` は保たれる
    - `bool` と整数以外は渡せない

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::make_unsigned_t {#make_unsigned}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
using make_unsigned_t = typename make_unsigned<T>::type;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 変換元の型 |

`T` が `int` なら `unsigned int`、`long long` なら `unsigned long long` を返します。`const` や `volatile` は保たれます。`bool` や、整数以外の型は渡せません。

戻り値は型です。実行時には何も起きず、コンパイル時に型が決まります。`std::make_unsigned<T>::type` と書いても同じ型ですが、C++14 以降の `std::make_unsigned_t<T>` のほうが短く書けます。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("std::make_unsigned_t<int> は unsigned int : {}", std::is_same_v<std::make_unsigned_t<int>, unsigned int>);
  std::println("std::make_unsigned_t<char> は unsigned char : {}", std::is_same_v<std::make_unsigned_t<char>, unsigned char>);
  std::println("std::make_unsigned_t<const int> は const unsigned int : {}", std::is_same_v<std::make_unsigned_t<const int>, const unsigned int>);
}
```

```text title="実行結果"
std::make_unsigned_t<int> は unsigned int : true
std::make_unsigned_t<char> は unsigned char : true
std::make_unsigned_t<const int> は const unsigned int : true
```

## ゲームでの使いどころ

符号つき整数のビット演算を、符号なしで安全に行います。

```cpp
template <class Int>
int CountBits(Int value) {
  auto bits = static_cast<std::make_unsigned_t<Int>>(value);   // 符号なしに直す
  return std::popcount(bits);
}
```

## よくあるミス

??? failure "変換後の型を実行時の値と混同する"
    これは型を返します。値を作るには、その型で変数を宣言します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`make_signed`](make_signed.md) | 符号つきにする |
| [`is_unsigned`](is_unsigned.md) | 符号なしか調べる |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::make_unsigned_t<int>` は `unsigned int`
    - [x] 同じ大きさの符号なし型を返す
    - [x] `const` / `volatile` は保たれる

## 関連ページ

- [cpprefjp: std::make_unsigned](https://cpprefjp.github.io/reference/type_traits/make_unsigned.html)
- [cppreference: std::make_unsigned](https://en.cppreference.com/w/cpp/types/make_unsigned)
