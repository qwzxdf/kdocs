---
title: std::is_const
summary: "`const` が付いた型かを調べる。"
order: 9
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_const

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <type_traits>`
</div>

`const` の型かどうかで、書き込めるかを判断したい。`std::is_const` は、<strong>型そのものが `const` か</strong>を調べます。

!!! tip "ポイント"
    - `std::is_const_v<T>` は、`T` が `const` 修飾されているか
    - 最上位の `const` だけを見る。ポインターの先の `const` は数えない
    - `std::is_const<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - 参照は `const` を持てないので、常に `false`

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_const_v {#is_const}

```cpp
template <class T>
inline constexpr bool is_const_v = is_const<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

最上位に `const` が付いた型が `true` です。`const int` は `true` ですが、`const int*`（`const` な `int` を指すポインター）は、ポインター自体は `const` ではないので `false` です。`int* const`（ポインターが `const`）は `true` です。参照は `const` を持てないので、`const int&` も `false` です。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("const int                  -> {}", std::is_const_v<const int>);
  std::println("int                        -> {}", std::is_const_v<int>);
  std::println("const int*                 -> {}", std::is_const_v<const int*>);
  std::println("int* const                 -> {}", std::is_const_v<int* const>);
}
```

```text title="実行結果"
const int                  -> true
int                        -> false
const int*                 -> false
int* const                 -> true
```

## ゲームでの使いどころ

出力用の引数に、`const` なものが渡されたら、コンパイルエラーにします。

```cpp
template <class T>
void Fill(T& out) {
  static_assert(!std::is_const_v<T>, "const なものには書き込めません");
  out = T{};
}
```

## よくあるミス

??? failure "const int& が true になると思う"
    参照そのものは `const` にできないので `false` です。`std::remove_reference_t` で参照を外してから調べます。

??? failure "const int* が true になると思う"
    `const` が付いているのは指している先なので `false` です。ポインター自体が `const` なのは `int* const` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_volatile`](is_volatile.md) | `volatile` が付いているか |
| [`remove_const`](remove_const.md) | 最上位の `const` を外した型 |
| [`add_const`](add_const.md) | `const` を付けた型 |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_const_v<T>` は、`T` が `const` 修飾されているか
    - [x] `const int*` は `false`、`int* const` は `true`
    - [x] 参照の `const` は `remove_reference_t` で外して調べる

## 関連ページ

- [cpprefjp: std::is_const](https://cpprefjp.github.io/reference/type_traits/is_const.html)
- [cppreference: std::is_const](https://en.cppreference.com/w/cpp/types/is_const)
