---
title: std::remove_volatile
summary: "`volatile` を取り除く。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::remove_volatile

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

`volatile` が付いた型から `volatile` を外したい。`std::remove_volatile` は、<strong>型の最上位の `volatile` を外した型</strong>を返します。

!!! tip "ポイント"
    - `std::remove_volatile_t<volatile int>` は `int`
    - 最上位の `volatile` だけを外す
    - `const` も外すなら `remove_cv`
    - ゲームでは `volatile` を使う場面が少ない

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::remove_volatile_t {#remove_volatile}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
using remove_volatile_t = typename remove_volatile<T>::type;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 変換元の型 |

`T` が `volatile int` なら `int` を返します。付いていない型は、そのまま返します。ポインタが指す先の `volatile` は外れません。

戻り値は型です。実行時には何も起きず、コンパイル時に型が決まります。`std::remove_volatile<T>::type` と書いても同じ型ですが、C++14 以降の `std::remove_volatile_t<T>` のほうが短く書けます。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("std::remove_volatile_t<volatile int> は int : {}", std::is_same_v<std::remove_volatile_t<volatile int>, int>);
  std::println("std::remove_volatile_t<int> は int : {}", std::is_same_v<std::remove_volatile_t<int>, int>);
}
```

```text title="実行結果"
std::remove_volatile_t<volatile int> は int : true
std::remove_volatile_t<int> は int : true
```

## ゲームでの使いどころ

`volatile` を外した型を作ります。レジスタの値を、普通の変数として保存する作業用のコピーを用意するときに使います。

```cpp
template <class T>
auto Snapshot(const volatile T& reg) {
  std::remove_volatile_t<T> value = reg;   // 一度だけ読んで、普通の変数にする
  return value;
}
```

## よくあるミス

??? failure "volatile のオブジェクトの volatile を外せると思う"
    型の変換だけです。`volatile` なオブジェクトのアドレスを `volatile` なしのポインターで扱うと、未定義動作です。

??? failure "const も外れると思う"
    外れるのは `volatile` だけです。`const` も外すなら `remove_cv` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`remove_cv`](remove_cv.md) | `const` と `volatile` の両方を外す |
| [`add_volatile`](add_volatile.md) | `volatile` を付ける |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::remove_volatile_t<volatile int>` は `int`
    - [x] 最上位の `volatile` だけを外す
    - [x] `const` も外すなら `remove_cv`

## 関連ページ

- [cpprefjp: std::remove_volatile](https://cpprefjp.github.io/reference/type_traits/remove_volatile.html)
- [cppreference: std::remove_volatile](https://en.cppreference.com/w/cpp/types/remove_volatile)
