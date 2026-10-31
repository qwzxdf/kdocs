---
title: std::is_trivially_default_constructible
summary: "既定構築が自明（何もしなくてよい）な型かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_trivially_default_constructible

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

`memset` で 0 初期化してよい型か、配列を確保したあとの初期化を省けるかを知りたい。`std::is_trivially_default_constructible` は、<strong>型が自明な既定コンストラクターを持つか</strong>を調べます。

!!! tip "ポイント"
    - `std::is_trivially_default_constructible_v<T>` は、`T` が自明な既定コンストラクターを持つか
    - 自明な型の既定の初期化は、何もしない（値は不定）
    - `std::is_trivially_default_constructible<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - メンバーの既定値で自明でなくなる

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_trivially_default_constructible_v {#is_trivially_default_constructible}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
inline constexpr bool is_trivially_default_constructible_v = is_trivially_default_constructible<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

引数なしで構築するときに、実行時の処理が何も要らない型なら `true` です。`int` や、メンバーに初期値を持たない構造体がそうです。メンバーに初期値（`int hp = 100;`）を書くと、自明でなくなります。

メンバーの初期値を書くと `false` になります。大量のオブジェクトを確保して初期化を省きたいときに、この性質が効きます。

## 実際に動かしてみる

```cpp
#include <print>
#include <string>
#include <type_traits>

struct Player {
  int hp;
  float x;
};

int main() {
  std::println("Player                             -> {}", std::is_trivially_default_constructible_v<Player>);
  std::println("int                                -> {}", std::is_trivially_default_constructible_v<int>);
  std::println("std::string                        -> {}", std::is_trivially_default_constructible_v<std::string>);
}
```

```text title="実行結果"
Player                             -> true
int                                -> true
std::string                        -> false
```

## ゲームでの使いどころ

大量の要素を確保するとき、自明な型なら初期化を省き、速く確保します。

```cpp
template <class T>
std::unique_ptr<T[]> Allocate(std::size_t n) {
  if constexpr (std::is_trivially_default_constructible_v<T>) {
    return std::make_unique_for_overwrite<T[]>(n);   // 初期化を省く
  } else {
    return std::make_unique<T[]>(n);                 // 1 つずつ構築する
  }
}
```

## よくあるミス

??? failure "初期化されていない値を、ゼロだと思う"
    自明な型を既定の初期化で作ると、値は不定です。ゼロが欲しいなら `T{}` で値初期化します。

??? failure "メンバーに既定値を書く"
    `int hp = 100;` と書くと、自明ではなくなります。確保が遅くなる場面では、既定値を外すことも検討します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_default_constructible`](is_default_constructible.md) | 自明さを考えずに、引数なしで作れるか |
| [`is_trivially_constructible`](is_trivially_constructible.md) | 任意の引数の自明さ |
| [`is_trivial`](is_trivial.md) | 構築とコピーの自明さ |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_trivially_default_constructible_v<T>` は、`T` が自明な既定コンストラクターを持つか
    - [x] 何もしない構築が `true`
    - [x] 値は不定になる

## 関連ページ

- [cpprefjp: std::is_trivially_default_constructible](https://cpprefjp.github.io/reference/type_traits/is_trivially_default_constructible.html)
- [cppreference: std::is_trivially_default_constructible](https://en.cppreference.com/w/cpp/types/is_trivially_default_constructible)
