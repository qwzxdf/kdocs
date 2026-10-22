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

`unsigned int` から `int` を作ります。符号を気にせず、同じサイズの符号付き整数を得たいときに使います。

!!! tip "ポイント"
    - `::type` の代わりに `std::make_signed_t<T>` と書ける。
    - コンパイル時に型を作り換える。
    - 値ではなく型を扱う。

!!! info "このページを読む前に"
    [<type_traits>](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::make_signed {#make_signed}

```cpp
template <class T>
struct make_signed { using type = /* 符号なしの整数型を、同じ大きさの符号付きにする */; };
template <class T>
using make_signed_t = typename make_signed<T>::type;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 元の型 |

- 戻り値: 変換後の型（`::type`）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  using R = std::make_signed_t<unsigned>;
  std::println("{}", std::is_same_v<R, int>);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | テンプレートの中で、型から余計な修飾を取り除く・付け足す |

## よくあるミス

??? failure "`::type` を付け忘れる"
    `std::make_signed<T>` は型を持つ構造体です。型そのものが欲しいときは `_t` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`make_unsigned`](make_unsigned.md) | 逆の変換 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 符号なしの整数型を、同じ大きさの符号付きにする
    - [x] `::type` の代わりに `std::make_signed_t<T>` と書ける
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::make_signed](https://cpprefjp.github.io/reference/type_traits/make_signed.html)
- [cppreference: std::make_signed](https://en.cppreference.com/w/cpp/types/make_signed)
