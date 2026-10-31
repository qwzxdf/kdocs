---
title: std::is_void
summary: "型が `void` かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_void

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

関数の戻り値が `void` かどうかで処理を分けたい。テンプレートの中で、`void` だけが他の型と違う扱いを受ける場面は多くあります（値を返せない、変数を作れない）。`std::is_void` は、<strong>型が `void` か</strong>を調べます。

!!! tip "ポイント"
    - `std::is_void_v<T>` は、`T` が `void`（`const` や `volatile` 付きを含む）か
    - `void*` ではなく、`void` そのものが対象
    - `std::is_void<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - 戻り値の型が `void` かどうかの分岐に使う

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_void_v {#is_void}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
inline constexpr bool is_void_v = is_void<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

`void` と、`const void`・`volatile void` のように修飾が付いたものが `true` です。`void*` はポインターなので `false` です。関数の戻り値が `void` かどうかを知りたいときに、`std::invoke_result_t` と組み合わせて使います。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("void                       -> {}", std::is_void_v<void>);
  std::println("const void                 -> {}", std::is_void_v<const void>);
  std::println("void*                      -> {}", std::is_void_v<void*>);
  std::println("int                        -> {}", std::is_void_v<int>);
}
```

```text title="実行結果"
void                       -> true
const void                 -> true
void*                      -> false
int                        -> false
```

## ゲームでの使いどころ

渡された関数を呼んで、結果があれば返し、戻り値が `void` なら何も返さない、汎用の実行関数を書けます。

```cpp
template <class F>
auto Run(F&& f) {
  if constexpr (std::is_void_v<std::invoke_result_t<F>>) {
    f();                 // 戻り値がないので、そのまま呼ぶだけ
  } else {
    return f();          // 戻り値を呼び出し側へ返す
  }
}
```

## よくあるミス

??? failure "void* を true だと思う"
    `void*` はポインター型なので `false` です。`void` そのものだけが `true` です。

??? failure "戻り値を変数に受けようとする"
    `void` の戻り値は、`auto x = f();` で変数に入れられません。`is_void` で分けて、別々に書きます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_pointer`](is_pointer.md) | ポインターか。`void*` は `true` |
| [`invoke_result`](invoke_result.md) | 関数を呼んだときの戻り値の型 |
| [`is_null_pointer`](is_null_pointer.md) | `nullptr` の型か |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_void_v<T>` は、`T` が `void`（`const` や `volatile` 付きを含む）か
    - [x] `void` だけが `true`
    - [x] `void*` は `false`

## 関連ページ

- [cpprefjp: std::is_void](https://cpprefjp.github.io/reference/type_traits/is_void.html)
- [cppreference: std::is_void](https://en.cppreference.com/w/cpp/types/is_void)
