---
title: std::remove_cvref
summary: "`const`・`volatile`・参照をすべて外した型にする。"
order: 14
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::remove_cvref

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-20">C++20</span>
`#include <type_traits>`
</div>

テンプレートの関数は、`const int&` や `int&&`、`int` など、様々な形で引数を受け取ります。型を比べたいとき、これらがすべて別の型として扱われると、一つ一つ書き分けるのが大変です。`std::remove_cvref_t<T>` は、型 `T` から `const`、`volatile`、参照を全部外した型を返します。受け取った型の「素の型」に直して比べるために使います。

!!! tip "ポイント"
    - `is_same_v<remove_cvref_t<T>, int>` の形が定番。
    - C++20 の機能。それ以前は `decay_t` で代用。
    - ポインターの指す先の `const` は外れない。

!!! info "このページを読む前に"
    テンプレートの基本（型を引数にする関数やクラス）が分かると読みやすいです。

## 関数の詳しい説明

### std::remove_cvref_t {#remove_cvref}

<span class="ver ver-20">C++20</span>

```cpp
template <class T>
using remove_cvref_t = /* const・volatile・参照を取り除いた T */;
```

- `const std::string&` → `std::string`。テンプレートで受け取った型を「素の型」にして比べるのに使います

## しくみ

`remove_cvref_t<T>` は、`remove_cv_t<remove_reference_t<T>>` と同じです。参照を先に外し、その結果から `const` と `volatile` を外します。

ポインターの指す先の `const` は外れません。`const int*` は、`int` を指す `const` なポインターではなく、`const int` を指すポインターという型で、`remove_cvref_t<const int*>` は `const int*` のままです。

配列や関数の型は変わりません。それらを値渡し用の型に変えたいときは、`std::decay_t` を使います。C++20 より前の環境では、`decay_t` で代用していました。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("{} {}", std::is_same_v<std::remove_cvref_t<const int&>, int>, std::is_same_v<std::remove_cvref_t<int&&>, int>);
}
```

```text title="実行結果"
true true
```

## ゲームでの使いどころ

転送参照（`T&&`）の引数を受けるテンプレートで、本当の型を調べるときに使います。

```cpp
template <class T>
void Add(T&& component) {
  using Raw = std::remove_cvref_t<T>;
  // Raw は、const も参照も付かない素の型
  static_assert(std::is_same_v<Raw, Position>, "Position のみ");
}
```

ECS で、コンポーネントの型をキーにして保存する場面では、`const` や参照の違いで別の型として登録されないよう、`remove_cvref_t` を通します。`std::type_index(typeid(Raw))` の形が定番です。

コンセプトの定義でも使います。`std::same_as<std::remove_cvref_t<T>, int>` と書けば、引数の渡され方にかかわらず、「`int` かどうか」を調べられます。

## よくあるミス

??? failure "ポインターの指す先の `const` も外れると思う"
    `remove_cvref_t<const int*>` は `const int*` のままです。外れるのは、型そのものについた `const` や参照だけです。指す先の `const` を外したいなら、`remove_pointer_t` と `remove_cv_t` を順に適用します。

??? failure "配列や関数の型を渡して、期待と違う結果になる"
    `remove_cvref_t<int[3]>` は `int[3]` のままで、`int*` にはなりません。配列を値渡し用の型にしたいときは `decay_t` です。

??? failure "C++17 以前で使おうとする"
    `remove_cvref_t` は C++20 の機能です。C++17 以前では `std::decay_t` で代用するか、`remove_cv_t<remove_reference_t<T>>` と書きます。

## 類似

| 名前 | 違い |
| --- | --- |
| `std::decay` | 配列や関数も値渡し用の型に変える。`remove_cvref` より広く変換する |
| `std::remove_const` | `const` だけを外す |
| `std::remove_reference` | 参照だけを外す |

## コンパイラ対応

C++11 から使えます。`_v` と `_t` の簡略形は C++14 / C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `const`、`volatile`、参照をすべて外した「素の型」にする。
    - [x] 転送参照の型を調べるときに使う。
    - [x] ポインターの指す先の `const` は外れない。

## 関連ページ

- [cpprefjp: std::remove_cvref](https://cpprefjp.github.io/reference/type_traits/remove_cvref.html)
- [cppreference: std::remove_cvref](https://en.cppreference.com/w/cpp/types/remove_cvref)
