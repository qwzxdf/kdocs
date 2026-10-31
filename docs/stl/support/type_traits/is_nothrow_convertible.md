---
title: std::is_nothrow_convertible
summary: "暗黙の変換が例外を投げないかを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_nothrow_convertible

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <type_traits>`
</div>

変換が失敗しない（例外を投げない）と保証できるかを知りたい。`std::is_nothrow_convertible<From, To>` は、<strong>暗黙の変換が `noexcept` か</strong>を調べます。

!!! tip "ポイント"
    - `std::is_nothrow_convertible_v<From, To>` は、`From` から `To` への変換が例外を投げずにできるか
    - 暗黙の変換だけが対象（`explicit` は `false`）
    - `std::is_nothrow_convertible<From, To>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - C++20 で追加された

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_nothrow_convertible_v {#is_nothrow_convertible}

<span class="ver ver-20">C++20</span>

```cpp
template <class From, class To>
inline constexpr bool is_nothrow_convertible_v = is_nothrow_convertible<From, To>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `From` | 型 | 変換元の型 |
| `To` | 型 | 変換先の型 |

`From` の値を `To` に暗黙に変換でき、その変換が `noexcept` と宣言されていれば `true` です。`is_convertible` に `noexcept` の条件を足したものです。C++20 で追加されました。`void` から `void` への変換は、`true` として扱われます。

## 実際に動かしてみる

```cpp
#include <print>
#include <string>
#include <type_traits>

struct Base {};
struct Derived : Base {};

int main() {
  std::println("int, float                         -> {}", std::is_nothrow_convertible_v<int, float>);
  std::println("const char*, std::string           -> {}", std::is_nothrow_convertible_v<const char*, std::string>);
  std::println("Derived*, Base*                    -> {}", std::is_nothrow_convertible_v<Derived*, Base*>);
}
```

```text title="実行結果"
int, float                         -> true
const char*, std::string           -> false
Derived*, Base*                    -> true
```

## ゲームでの使いどころ

変換演算子を持つ型で、変換先ごとに `noexcept` を決める実装に使えます。

```cpp
template <class T>
class Meters {
 public:
  explicit Meters(T v) : value_(v) {}

  template <class U>
  operator U() const noexcept(std::is_nothrow_convertible_v<T, U>) {
    return static_cast<U>(value_);
  }

 private:
  T value_;
};
```

## よくあるミス

??? failure "explicit な変換を調べる"
    `explicit` のコンストラクターや変換演算子は、暗黙の変換ではないので `false` です。明示的な構築は `is_nothrow_constructible` で調べます。

??? failure "C++17 以前で使う"
    C++20 で追加されました。それ以前は `noexcept(To(std::declval<From>()))` のような式で代用します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_convertible`](is_convertible.md) | 例外を考えずに、暗黙に変換できるか |
| [`is_nothrow_constructible`](is_nothrow_constructible.md) | 明示的な構築も含めて調べる |

## コンパイラ対応

C++20 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_nothrow_convertible_v<From, To>` は、`From` から `To` への変換が例外を投げずにできるか
    - [x] 暗黙の変換の `noexcept` を調べる
    - [x] C++20 で追加された

## 関連ページ

- [cpprefjp: std::is_nothrow_convertible](https://cpprefjp.github.io/reference/type_traits/is_nothrow_convertible.html)
- [cppreference: std::is_nothrow_convertible](https://en.cppreference.com/w/cpp/types/is_nothrow_convertible)
