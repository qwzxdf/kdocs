---
title: std::has_unique_object_representations
summary: "同じ値なら必ず同じビット列になる型かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::has_unique_object_representations

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <type_traits>`
</div>

2 つの値が等しいかをバイト列の比較（`memcmp`）で判定してよいかを知りたい。ハッシュ値をバイト列から作ってよいかも同じ問題です。`std::has_unique_object_representations` は、<strong>等しい値が必ず等しいビット列になるか</strong>を調べます。

!!! tip "ポイント"
    - `std::has_unique_object_representations_v<T>` は、`T` の値がビット表現と 1 対 1 に対応するか
    - 値は `bool` の定数。`static_assert` や `if constexpr` に使える
    - `std::has_unique_object_representations<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - 実行時のコストはない（コンパイル時に決まる）

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::has_unique_object_representations_v {#has_unique_object_representations}

<span class="ver ver-17">C++17</span>

```cpp
template <class T>
inline constexpr bool has_unique_object_representations_v = has_unique_object_representations<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

内部に詰め物（パディング）がなく、同じ値が 1 通りのビット列でしか表されない型なら `true` です。`int` は `true` です。`float` は、`+0.0` と `-0.0` が等しいのにビット列が違うので `false` です。メンバーの間に詰め物が入る構造体も `false` です。

型の性質を調べるだけで、オブジェクトは作りません。テンプレートの中で、型によって処理を分ける（`if constexpr`）、使えない型を早い段階で弾く（`static_assert`、`concept`）、といった用途で使います。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

struct Pair {
  int a;
  int b;
};
struct Player {
  int hp;
  float x;
};

int main() {
  std::println("int                                -> {}", std::has_unique_object_representations_v<int>);
  std::println("float                              -> {}", std::has_unique_object_representations_v<float>);
  std::println("Pair                               -> {}", std::has_unique_object_representations_v<Pair>);
  std::println("Player                             -> {}", std::has_unique_object_representations_v<Player>);
}
```

```text title="実行結果"
int                                -> true
float                              -> false
Pair                               -> true
Player                             -> false
```

## ゲームでの使いどころ

構造体のバイト列から、ハッシュ値を計算してよいかを検査します。

```cpp
template <class T>
std::size_t HashBytes(const T& value) {
  static_assert(std::has_unique_object_representations_v<T>, "詰め物や浮動小数点を含む型は、バイト列でハッシュできません");
  // …value のバイト列からハッシュを計算…
}
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

C++17 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::has_unique_object_representations_v<T>` は、`T` の値がビット表現と 1 対 1 に対応するか
    - [x] `static_assert` と `if constexpr` に使える
    - [x] 参照や `const` が付いた型は、先に `remove_cvref_t` で外す

## 関連ページ

- [cpprefjp: std::has_unique_object_representations](https://cpprefjp.github.io/reference/type_traits/has_unique_object_representations.html)
- [cppreference: std::has_unique_object_representations](https://en.cppreference.com/w/cpp/types/has_unique_object_representations)
