---
title: std::is_union
summary: "型が共用体（union）かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_union

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

共用体は、同じメモリを異なる型で見る仕組みです。`std::is_union` は、<strong>型が `union` か</strong>を調べます。

!!! tip "ポイント"
    - `std::is_union_v<T>` は、`T` が共用体（`union`）か
    - `struct` / `class` は `false`
    - `std::is_union<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - クラスと共用体は、別々に調べる

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_union_v {#is_union}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
inline constexpr bool is_union_v = is_union<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

`union` で宣言された型が `true` です。`struct` や `class` は `false` です。`std::is_class` は共用体に対して `false` を返すので、この 2 つを使えば、クラスと共用体を区別できます。クラスの中の無名共用体は、名前のある型ではないので、調べる対象になりません。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

union Number {
  int i;
  float f;
};
struct Player {
  int hp;
  float x;
};

int main() {
  std::println("Number                     -> {}", std::is_union_v<Number>);
  std::println("Player                     -> {}", std::is_union_v<Player>);
  std::println("int                        -> {}", std::is_union_v<int>);
}
```

```text title="実行結果"
Number                     -> true
Player                     -> false
int                        -> false
```

## ゲームでの使いどころ

メンバーを順に処理する汎用の関数に、共用体が渡されたらエラーにします。

```cpp
template <class T>
void Reflect(const T& value) {
  static_assert(!std::is_union_v<T>, "共用体は、どのメンバーが有効かが分からないので扱えません");
  // ...
}
```

## よくあるミス

??? failure "union を class だと思う"
    `std::is_class_v<U>` は、共用体 `U` に対して `false` です。共用体は `is_union` で調べます。

??? failure "クラスの中の無名 union を調べる"
    無名共用体は、型の名前がないので、`is_union` を適用できません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_class`](is_class.md) | クラスか。共用体は含まない |
| [`is_enum`](is_enum.md) | 列挙型か |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_union_v<T>` は、`T` が共用体（`union`）か
    - [x] `union` が `true`
    - [x] `is_class` は共用体に `false`

## 関連ページ

- [cpprefjp: std::is_union](https://cpprefjp.github.io/reference/type_traits/is_union.html)
- [cppreference: std::is_union](https://en.cppreference.com/w/cpp/types/is_union)
