---
title: std::void_t
summary: "どんな型を渡しても `void` になる別名（検出イディオム用）。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::void_t

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <type_traits>`
</div>

型が特定のメンバーを持っているかを、コンパイル時に調べたい。たとえば、「`.size()` を持つ型か」。`std::void_t` は、<strong>どんな型を渡しても `void` になる</strong>だけの型ですが、渡した型が不正だと、置換に失敗して候補から外れます。これを使って、メンバーの有無を検出する書き方（検出イディオム）を作れます。

!!! tip "ポイント"
    - `std::void_t<...>` は常に `void`
    - 渡した型が不正なら、その特殊化が候補から外れる
    - 「`.size()` が書ける型か」のようなメンバーの検出に使う
    - C++20 の `concept` / `requires` のほうが簡単

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::void_t {#void_t}

<span class="ver ver-17">C++17</span>

```cpp
template <class... Ts>
using void_t = void;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `Ts...` | 型の並び | 有効かを確かめたい型 |

`void_t<Ts...>` は、`Ts...` がすべて有効な型なら `void` です。有効でない型が含まれると、置換の失敗（SFINAE）になり、その特殊化は選ばれません。

```cpp
template <class T, class = void>
struct HasSize : std::false_type {};
template <class T>
struct HasSize<T, std::void_t<decltype(std::declval<T>().size())>> : std::true_type {};
```

`T` が `.size()` を持てば、特殊化が選ばれて `true_type` になります。持たなければ、主テンプレートの `false_type` です。

C++20 では、`requires` を使って `requires(T t) { t.size(); }` と書けるので、`void_t` を使う場面は減りました。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>
#include <utility>
#include <vector>

template <class T, class = void>
struct HasSize : std::false_type {};
template <class T>
struct HasSize<T, std::void_t<decltype(std::declval<T>().size())>> : std::true_type {};

int main() {
  std::println("vector は size() を持つ: {}", HasSize<std::vector<int>>::value);
  std::println("int は size() を持たない: {}", HasSize<int>::value);
}
```

```text title="実行結果"
vector は size() を持つ: true
int は size() を持たない: false
```

## ゲームでの使いどころ

メンバーの有無で処理を切り替える、汎用のテンプレートに使います。新しいコードでは `concept` を使います。

```cpp
template <class T>
concept HasSizeMember = requires(T t) { t.size(); };
```

## よくあるミス

??? failure "`concept` が使える環境でも `void_t` を使い続ける"
    `concept` / `requires` のほうが読みやすいです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`enable_if`](enable_if.md) | 条件が偽のとき型が存在しない |
| [`is_same`](is_same.md) | 2 つの型が同じか |

## コンパイラ対応

C++17 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `void_t<...>` は常に `void` だが、不正な型で候補から外れる
    - [x] メンバーの有無を検出する（検出イディオム）
    - [x] 新しいコードは `concept` / `requires`

## 関連ページ

- [cpprefjp: std::void_t](https://cpprefjp.github.io/reference/type_traits/void_t.html)
- [cppreference: std::void_t](https://en.cppreference.com/w/cpp/types/void_t)
