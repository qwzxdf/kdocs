---
title: std::is_nothrow_swappable
summary: "`swap` が例外を投げない型かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_nothrow_swappable

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <type_traits>`
</div>

`vector` の並べ替えが強い例外保証を持つかは、要素の `swap` が `noexcept` かに左右されます。`std::is_nothrow_swappable` は、<strong>入れ替えが `noexcept` か</strong>を調べます。

!!! tip "ポイント"
    - `std::is_nothrow_swappable_v<T>` は、`T` の `swap` が例外を投げないか
    - `swap` を自作するとき、`noexcept` の条件に使う
    - `std::is_nothrow_swappable<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - 自作の型は、ムーブに `noexcept` を付ければ `true`

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_nothrow_swappable_v {#is_nothrow_swappable}

<span class="ver ver-17">C++17</span>

```cpp
template <class T>
inline constexpr bool is_nothrow_swappable_v = is_nothrow_swappable<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

`swap(a, b)`（`using std::swap;` を前に置いた形で、引数ごとの `swap` も含めて探す）が書けて、その呼び出しが `noexcept` なら `true` です。自作の型は、ムーブコンストラクターとムーブ代入に `noexcept` を付ければ `true` になります。

## 実際に動かしてみる

```cpp
#include <print>
#include <string>
#include <type_traits>

struct MayThrow {
  MayThrow() = default;
  MayThrow(MayThrow&&) noexcept(false) {}
  MayThrow& operator=(MayThrow&&) noexcept(false) { return *this; }
};

int main() {
  std::println("int                                -> {}", std::is_nothrow_swappable_v<int>);
  std::println("std::string                        -> {}", std::is_nothrow_swappable_v<std::string>);
  std::println("MayThrow                           -> {}", std::is_nothrow_swappable_v<MayThrow>);
}
```

```text title="実行結果"
int                                -> true
std::string                        -> true
MayThrow                           -> false
```

## ゲームでの使いどころ

`swap` を自作するとき、メンバーの入れ替えが `noexcept` のときだけ、`noexcept` にします。

```cpp
template <class T>
struct Slot {
  T value;

  friend void swap(Slot& a, Slot& b) noexcept(std::is_nothrow_swappable_v<T>) {
    using std::swap;
    swap(a.value, b.value);
  }
};
```

## よくあるミス

??? failure "常に noexcept にしてしまう"
    中の型の入れ替えが例外を投げうるのに `noexcept` を付けると、例外で `std::terminate` です。条件つきで書きます。

??? failure "ムーブを削除した型で true を期待する"
    ムーブ構築もムーブ代入も使えない型は、標準の `swap` で入れ替えられないので `false` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_swappable`](is_swappable.md) | 例外を考えずに、入れ替えられるか |
| [`is_nothrow_swappable_with`](is_nothrow_swappable_with.md) | 型の違う 2 つの入れ替え |
| [`is_nothrow_move_assignable`](is_nothrow_move_assignable.md) | ムーブ代入が例外を投げないか |

## コンパイラ対応

C++17 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_nothrow_swappable_v<T>` は、`T` の `swap` が例外を投げないか
    - [x] `swap` の呼び出しの `noexcept` を調べる
    - [x] 自作の `swap` では条件つきで `noexcept` にする

## 関連ページ

- [cpprefjp: std::is_nothrow_swappable](https://cpprefjp.github.io/reference/type_traits/is_nothrow_swappable.html)
- [cppreference: std::is_nothrow_swappable](https://en.cppreference.com/w/cpp/types/is_nothrow_swappable)
