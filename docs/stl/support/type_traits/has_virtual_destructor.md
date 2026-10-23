---
title: std::has_virtual_destructor
summary: "型が仮想デストラクタを持つかを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::has_virtual_destructor

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

基底クラスのポインターで派生クラスを `delete` するには、基底クラスのデストラクターが仮想でなければなりません。`std::has_virtual_destructor` は、<strong>型が仮想デストラクターを持つか</strong>を調べます。

!!! tip "ポイント"
    - `std::has_virtual_destructor_v<T>` は、`T` が仮想デストラクターを持つか
    - 値は `bool` の定数。`static_assert` や `if constexpr` に使える
    - `std::has_virtual_destructor<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - 実行時のコストはない（コンパイル時に決まる）

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::has_virtual_destructor_v {#has_virtual_destructor}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
inline constexpr bool has_virtual_destructor_v = has_virtual_destructor<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

基底クラスのデストラクターが `virtual` なら `true` です。継承で受け継いだ場合も `true` です。仮想デストラクターを持たない基底クラスから派生して、ポインターで破棄すると、未定義動作になります。

型の性質を調べるだけで、オブジェクトは作りません。テンプレートの中で、型によって処理を分ける（`if constexpr`）、使えない型を早い段階で弾く（`static_assert`、`concept`）、といった用途で使います。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

struct Animal {
  virtual ~Animal() = default;
};
struct Player {
  int hp;
  float x;
};

int main() {
  std::println("Animal                             -> {}", std::has_virtual_destructor_v<Animal>);
  std::println("Player                             -> {}", std::has_virtual_destructor_v<Player>);
  std::println("int                                -> {}", std::has_virtual_destructor_v<int>);
}
```

```text title="実行結果"
Animal                             -> true
Player                             -> false
int                                -> false
```

## ゲームでの使いどころ

基底クラスのテンプレートで、破棄の安全性を保証します。

```cpp
template <class Base>
class Handle {
  static_assert(std::has_virtual_destructor_v<Base>, "基底クラスには仮想デストラクターが必要です");
};
```

## よくあるミス

??? failure "`T` に参照や `const` が付いていて、期待と違う結果になる"
    `std::remove_cvref_t<T>` で外してから調べます。

??? failure "実行時の値に使おうとする"
    調べるのは型です。値の判定には通常の比較を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`<type_traits>`](../type_traits.md) | 型の性質を調べる道具の一覧 |
| [`is_same`](is_same.md) | 2 つの型が同じか |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::has_virtual_destructor_v<T>` は、`T` が仮想デストラクターを持つか
    - [x] `static_assert` と `if constexpr` に使える
    - [x] 参照や `const` が付いた型は、先に `remove_cvref_t` で外す

## 関連ページ

- [cpprefjp: std::has_virtual_destructor](https://cpprefjp.github.io/reference/type_traits/has_virtual_destructor.html)
- [cppreference: std::has_virtual_destructor](https://en.cppreference.com/w/cpp/types/has_virtual_destructor)
