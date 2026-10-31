---
title: std::is_volatile
summary: "型が `volatile` 修飾されているかを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_volatile

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

ハードウェアのレジスターのように、最適化で読み書きを省いてはいけない変数を `volatile` で表します。`std::is_volatile` は、<strong>型が `volatile` か</strong>を調べます。

!!! tip "ポイント"
    - `std::is_volatile_v<T>` は、`T` が `volatile` 修飾されているか
    - 最上位の `volatile` だけを見る
    - `std::is_volatile<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - `volatile int*` は `false`

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_volatile_v {#is_volatile}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
inline constexpr bool is_volatile_v = is_volatile<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

`volatile int` は `true`、`int` は `false` です。`const` と同じで、最上位の `volatile` だけを見ます。`volatile int*`（`volatile` な `int` を指すポインター）は、ポインター自体は `volatile` ではないので `false` です。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("volatile int               -> {}", std::is_volatile_v<volatile int>);
  std::println("int                        -> {}", std::is_volatile_v<int>);
  std::println("volatile int*              -> {}", std::is_volatile_v<volatile int*>);
}
```

```text title="実行結果"
volatile int               -> true
int                        -> false
volatile int*              -> false
```

## ゲームでの使いどころ

`volatile` が付いた型に対して、通常の処理を適用しないよう、確かめます。

```cpp
template <class T>
class Cache {
  static_assert(!std::is_volatile_v<T>, "volatile な型はキャッシュできません");
  T value_;
};
```

## よくあるミス

??? failure "スレッド間の同期に volatile を使う"
    `volatile` は、スレッド間の同期にはなりません。`std::atomic` を使います。

??? failure "volatile int* を true だと思う"
    `volatile` が付いているのは指す先なので `false` です。ポインター自体が `volatile` なのは `int* volatile` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_const`](is_const.md) | `const` が付いているか |
| [`remove_volatile`](remove_volatile.md) | `volatile` を外した型 |
| [`add_volatile`](add_volatile.md) | `volatile` を付けた型 |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_volatile_v<T>` は、`T` が `volatile` 修飾されているか
    - [x] `volatile` が付いた型が `true`
    - [x] ポインターの先の `volatile` は数えない

## 関連ページ

- [cpprefjp: std::is_volatile](https://cpprefjp.github.io/reference/type_traits/is_volatile.html)
- [cppreference: std::is_volatile](https://en.cppreference.com/w/cpp/types/is_volatile)
