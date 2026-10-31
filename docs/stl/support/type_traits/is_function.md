---
title: std::is_function
summary: "型が関数の型かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_function

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

関数そのものの型と、関数へのポインタの型は別物です。`std::is_function` は、<strong>型が関数型か</strong>を調べます。

!!! tip "ポイント"
    - `std::is_function_v<T>` は、`T` が関数型か
    - 関数型だけが `true`。関数ポインターやラムダは `false`
    - `std::is_function<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - `void(int)` のような型は、普段あまり書かない

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_function_v {#is_function}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
inline constexpr bool is_function_v = is_function<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

関数の型（`void(int)` や `int(float, float)`）が `true` です。関数への**ポインター**（`void(*)(int)`）や、ラムダ式の型は `false` です。型として出会うことは少なく、`std::function` の内部実装や、`std::decay` の動作を理解するときに登場します。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("void(int)                  -> {}", std::is_function_v<void(int)>);
  std::println("void(*)(int)               -> {}", std::is_function_v<void(*)(int)>);
  std::println("int                        -> {}", std::is_function_v<int>);
}
```

```text title="実行結果"
void(int)                  -> true
void(*)(int)               -> false
int                        -> false
```

## ゲームでの使いどころ

関数型と関数ポインターを区別して、テンプレートの引数の扱いを決めます。

```cpp
template <class F>
void Register(F&& f) {
  using Raw = std::remove_reference_t<F>;
  if constexpr (std::is_function_v<Raw>) {
    handlers_.push_back(&f);        // 関数そのもの: アドレスを取る
  } else {
    handlers_.push_back(f);         // 関数ポインターや関数オブジェクト: そのまま
  }
}
```

## よくあるミス

??? failure "関数ポインターが true になると思う"
    `void(*)(int)` は、ポインターなので `false` です。関数そのものの型 `void(int)` だけが `true` です。

??? failure "ラムダ式を調べる"
    ラムダ式の型はクラスなので `false` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_pointer`](is_pointer.md) | ポインターか。関数ポインターは `true` |
| [`is_member_function_pointer`](is_member_function_pointer.md) | メンバー関数へのポインターか |
| [`decay`](decay.md) | 関数型を関数ポインターに変える |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_function_v<T>` は、`T` が関数型か
    - [x] 関数型（`R(Args...)`）だけが `true`
    - [x] 関数ポインターは `is_pointer` で調べる

## 関連ページ

- [cpprefjp: std::is_function](https://cpprefjp.github.io/reference/type_traits/is_function.html)
- [cppreference: std::is_function](https://en.cppreference.com/w/cpp/types/is_function)
