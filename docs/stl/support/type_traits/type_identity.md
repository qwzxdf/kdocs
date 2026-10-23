---
title: std::type_identity
summary: "何もしない型変換（テンプレート引数の推論を止めるのに使う）。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::type_identity

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <type_traits>`
</div>

テンプレートの引数を推論させたくない場所があります。たとえば、`Clamp(T value, T low, T high)` で、`Clamp(x, 0, 1)` のように型が揃わない引数が渡されると、推論が矛盾します。`std::type_identity` は、<strong>何も変換せず型をそのまま返す</strong>型で、その型を推論の対象外にするために使います。

!!! tip "ポイント"
    - `std::type_identity_t<T>` は `T` そのもの
    - 引数の型に使うと、その引数から `T` を推論しなくなる
    - 型が揃わない引数を、他の引数に合わせたいときに使う
    - C++20 で追加

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::type_identity_t {#type_identity}

<span class="ver ver-20">C++20</span>

```cpp
template <class T>
struct type_identity {
  using type = T;
};
template <class T>
using type_identity_t = typename type_identity<T>::type;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 返したい型 |

`std::type_identity_t<T>` は `T` そのものです。何も変えません。ただし、これを関数の引数の型に使うと、その引数からは `T` が推論されなくなります（推論されない文脈になる）。

他の引数から推論された `T` に合わせて、この引数を変換させたいときに便利です。

戻り値は型です。実行時には何も起きず、コンパイル時に型が決まります。`std::type_identity<T>::type` と書いても同じ型ですが、C++14 以降の `std::type_identity_t<T>` のほうが短く書けます。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("std::type_identity_t<int> は int : {}", std::is_same_v<std::type_identity_t<int>, int>);
  std::println("std::type_identity_t<const float&> は const float& : {}", std::is_same_v<std::type_identity_t<const float&>, const float&>);
}
```

```text title="実行結果"
std::type_identity_t<int> は int : true
std::type_identity_t<const float&> は const float& : true
```

## ゲームでの使いどころ

推論させたくない引数に使います。

```cpp
template <class T>
T Lerp(T a, T b, std::type_identity_t<T> t) {   // t は a から推論された T に合わせる
  return a + (b - a) * t;
}
auto v = Lerp(1.0f, 3.0f, 0.5);   // t は double だが float に変換される
```

## よくあるミス

??? failure "変換後の型を実行時の値と混同する"
    これは型を返します。値を作るには、その型で変数を宣言します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`<type_traits>`](../type_traits.md) | 型の性質を調べる・変換する道具の一覧 |

## コンパイラ対応

C++20 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::type_identity_t<T>` は `T` そのもの
    - [x] 引数の型に使うと、その引数から `T` を推論しなくなる
    - [x] 型が揃わない引数を、他の引数に合わせたいときに使う

## 関連ページ

- [cpprefjp: std::type_identity](https://cpprefjp.github.io/reference/type_traits/type_identity.html)
- [cppreference: std::type_identity](https://en.cppreference.com/w/cpp/types/type_identity)
