---
title: std::is_object
summary: "型がオブジェクト型（関数・参照・`void` 以外）かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_object

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

オブジェクト（変数として実体を持てる型）かを調べたい。`std::is_object` は、<strong>型がオブジェクト型か</strong>を調べます。

!!! tip "ポイント"
    - `std::is_object_v<T>` は、`T` が関数、参照、`void` のどれでもない型か
    - 参照・関数・`void` 以外が `true`
    - `std::is_object<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - コンテナの要素型の条件に近い

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_object_v {#is_object}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
inline constexpr bool is_object_v = is_object<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

関数型、参照型、`void` 以外のすべてが `true` です。`int`、ポインター、クラス、配列、列挙型などが含まれます。「変数として宣言できる型」の目安です。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

struct Player {
  int hp;
  float x;
};

int main() {
  std::println("int                        -> {}", std::is_object_v<int>);
  std::println("Player                     -> {}", std::is_object_v<Player>);
  std::println("int&                       -> {}", std::is_object_v<int&>);
  std::println("void                       -> {}", std::is_object_v<void>);
}
```

```text title="実行結果"
int                        -> true
Player                     -> true
int&                       -> false
void                       -> false
```

## ゲームでの使いどころ

自作のコンテナで、要素の型にできないものを、早い段階で弾きます。

```cpp
template <class T>
class Stack {
  static_assert(std::is_object_v<T>, "参照、関数、void は要素にできません");
  std::vector<T> items_;
};
```

## よくあるミス

??? failure "参照を要素にしようとする"
    `Stack<int&>` のように、参照を要素にしようとすると `false` で、弾かれます。参照を持ちたいときは `std::reference_wrapper` を使います。

??? failure "関数型を要素にする"
    関数型は `false` です。要素にするなら、関数ポインターか `std::function` にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_reference`](is_reference.md) | 参照型か |
| [`is_function`](is_function.md) | 関数型か |
| [`is_scalar`](is_scalar.md) | 算術型・ポインターなどか |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_object_v<T>` は、`T` が関数、参照、`void` のどれでもない型か
    - [x] 関数・参照・`void` 以外が `true`
    - [x] 参照を持ちたいときは `reference_wrapper`

## 関連ページ

- [cpprefjp: std::is_object](https://cpprefjp.github.io/reference/type_traits/is_object.html)
- [cppreference: std::is_object](https://en.cppreference.com/w/cpp/types/is_object)
