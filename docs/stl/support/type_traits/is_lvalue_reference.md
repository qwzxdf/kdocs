---
title: std::is_lvalue_reference
summary: "型が左辺値参照かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_lvalue_reference

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

転送参照のテンプレートで、渡された引数が左辺値かどうかで処理を分けたい。`std::is_lvalue_reference` は、<strong>型が左辺値参照か</strong>を調べます。

!!! tip "ポイント"
    - `std::is_lvalue_reference_v<T>` は、`T` が左辺値参照（`T&`）か
    - 万能参照では、左辺値のとき `T` が `X&` になる
    - `std::is_lvalue_reference<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - `std::forward` の実装の考え方と同じ

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_lvalue_reference_v {#is_lvalue_reference}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
inline constexpr bool is_lvalue_reference_v = is_lvalue_reference<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

`int&` のような左辺値参照型が `true` です。`int&&` は `false` です。万能参照（`T&&` の引数）で、テンプレート引数 `T` が左辺値で推論されたとき、`T` は `X&` になるので、`true` になります。右辺値のときは `T` が `X` になり、`false` です。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("int&                       -> {}", std::is_lvalue_reference_v<int&>);
  std::println("int&&                      -> {}", std::is_lvalue_reference_v<int&&>);
  std::println("int                        -> {}", std::is_lvalue_reference_v<int>);
}
```

```text title="実行結果"
int&                       -> true
int&&                      -> false
int                        -> false
```

## ゲームでの使いどころ

万能参照を受けて、左辺値ならコピー、右辺値ならムーブで保存します。

```cpp
template <class T>
void Store(T&& value) {
  if constexpr (std::is_lvalue_reference_v<T>) {
    items_.push_back(value);              // 左辺値: コピー
  } else {
    items_.push_back(std::move(value));   // 右辺値: ムーブ
  }
}
```

## よくあるミス

??? failure "T&& の引数が右辺値参照だと思う"
    テンプレートの `T&&` は、`T` が `X&` になることがあるので、必ずしも右辺値参照ではありません。`T` を調べます。

??? failure "値を調べようとする"
    調べるのは型です。変数 `value` が左辺値かどうかは、`decltype` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_rvalue_reference`](is_rvalue_reference.md) | 右辺値参照か |
| [`is_reference`](is_reference.md) | どちらの参照か |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_lvalue_reference_v<T>` は、`T` が左辺値参照（`T&`）か
    - [x] `X&` が `true`、`X&&` は `false`
    - [x] 万能参照の `T` を調べて、左辺値かどうかを知る

## 関連ページ

- [cpprefjp: std::is_lvalue_reference](https://cpprefjp.github.io/reference/type_traits/is_lvalue_reference.html)
- [cppreference: std::is_lvalue_reference](https://en.cppreference.com/w/cpp/types/is_lvalue_reference)
