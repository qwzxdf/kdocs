---
title: std::add_volatile
summary: "`volatile` を付け足す。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::add_volatile

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

型に `volatile` を付けます。

!!! tip "ポイント"
    - `::type` の代わりに `std::add_volatile_t<T>` と書ける。
    - コンパイル時に型を作り換える。
    - 値ではなく型を扱う。

!!! info "このページを読む前に"
    [<type_traits>](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::add_volatile {#add_volatile}

```cpp
template <class T>
struct add_volatile { using type = /* `volatile` を付け足す */; };
template <class T>
using add_volatile_t = typename add_volatile<T>::type;
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
  using R = std::add_volatile_t<int>;
  std::println("{}", std::is_same_v<R, volatile int>);
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
    `std::add_volatile<T>` は型を持つ構造体です。型そのものが欲しいときは `_t` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`remove_cvref`](remove_cvref.md) | const・volatile・参照をまとめて外す |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `volatile` を付け足す
    - [x] `::type` の代わりに `std::add_volatile_t<T>` と書ける
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::add_volatile](https://cpprefjp.github.io/reference/type_traits/add_volatile.html)
- [cppreference: std::add_volatile](https://en.cppreference.com/w/cpp/types/add_volatile)
