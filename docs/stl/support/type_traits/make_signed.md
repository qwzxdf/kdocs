---
title: std::make_signed
summary: "符号なしの整数型を、同じ大きさの符号付きにする。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::make_signed

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

整数型を同じ大きさの符号つきの型に変えたい。`std::make_signed` は、<strong>同じ大きさの符号つき整数型</strong>を返します。

!!! tip "ポイント"
    - `std::make_signed_t<unsigned int>` は `int`
    - 同じ大きさの符号つき型を返す
    - `size_t` から符号つきの差の型を作れる
    - `bool` と整数以外は渡せない

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::make_signed_t {#make_signed}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
using make_signed_t = typename make_signed<T>::type;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 変換元の型 |

`T` が `unsigned int` なら `int`、`unsigned long long` なら `long long` を返します。`const` や `volatile` は保たれます。`bool` と整数以外は渡せません。

`std::size_t` を符号つきにしたいときに便利です。コンテナの添字の差を負になりうる型で受けるときに使います。

戻り値は型です。実行時には何も起きず、コンパイル時に型が決まります。`std::make_signed<T>::type` と書いても同じ型ですが、C++14 以降の `std::make_signed_t<T>` のほうが短く書けます。

## 実際に動かしてみる

```cpp
#include <cstddef>
#include <print>
#include <type_traits>

int main() {
  std::println("std::make_signed_t<unsigned int> は int : {}", std::is_same_v<std::make_signed_t<unsigned int>, int>);
  std::println("std::make_signed_t<unsigned char> は signed char : {}", std::is_same_v<std::make_signed_t<unsigned char>, signed char>);
  std::println("std::make_signed_t<std::size_t> は std::ptrdiff_t : {}", std::is_same_v<std::make_signed_t<std::size_t>, std::ptrdiff_t>);
}
```

```text title="実行結果"
std::make_signed_t<unsigned int> は int : true
std::make_signed_t<unsigned char> は signed char : true
std::make_signed_t<std::size_t> は std::ptrdiff_t : true
```

## ゲームでの使いどころ

型を加工するテンプレートで使います。ゲームのコードで直接書く機会は多くありませんが、汎用のテンプレート（コンテナ、イベントシステム、ECS）の内部ではよく登場します。

## よくあるミス

??? failure "変換後の型を実行時の値と混同する"
    これは型を返します。値を作るには、その型で変数を宣言します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`make_unsigned`](make_unsigned.md) | 符号なしにする |
| [`is_signed`](is_signed.md) | 符号つきか調べる |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::make_signed_t<unsigned int>` は `int`
    - [x] 同じ大きさの符号つき型を返す
    - [x] `size_t` から符号つきの差の型を作れる

## 関連ページ

- [cpprefjp: std::make_signed](https://cpprefjp.github.io/reference/type_traits/make_signed.html)
- [cppreference: std::make_signed](https://en.cppreference.com/w/cpp/types/make_signed)
