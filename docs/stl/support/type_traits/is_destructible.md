---
title: std::is_destructible
summary: "破棄できる型かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_destructible

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

`delete` や、スコープを抜けたときの破棄が書ける型かを調べます。

!!! tip "ポイント"
    - `std::is_destructible_v<T>` は、`T` が破棄できるか
    - private や削除されたデストラクターは `false`
    - `std::is_destructible<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - 参照型と配列型は `true`

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_destructible_v {#is_destructible}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
inline constexpr bool is_destructible_v = is_destructible<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

破棄できる（デストラクターを呼べる）かを調べます。private や `= delete` のデストラクターを持つ型は `false` です。参照型と配列型は、破棄できるので `true` で、`void` と不完全型は `false` です。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

struct Player {
  int hp;
  float x;
};

int main() {
  std::println("Player                     -> {}", std::is_destructible_v<Player>);
  std::println("int                        -> {}", std::is_destructible_v<int>);
  std::println("void                       -> {}", std::is_destructible_v<void>);
}
```

```text title="実行結果"
Player                     -> true
int                        -> true
void                       -> false
```

## ゲームでの使いどころ

プールが保持する型が、普通に破棄できることを確かめます。

```cpp
template <class T>
class Pool {
  static_assert(std::is_destructible_v<T>, "破棄できない型はプールに置けません");
  // ...
};
```

## よくあるミス

??? failure "private のデストラクターを持つ型を置く"
    シングルトンのように、デストラクターを private にした型は `false` です。コンテナには入れられません。

??? failure "void を調べる"
    `void` は `false` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_nothrow_destructible`](is_nothrow_destructible.md) | 破棄で例外を投げないか |
| [`is_trivially_destructible`](is_trivially_destructible.md) | 破棄が何もしないか |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_destructible_v<T>` は、`T` が破棄できるか
    - [x] デストラクターを呼べるかを調べる
    - [x] `void` や private のデストラクターは `false`

## 関連ページ

- [cpprefjp: std::is_destructible](https://cpprefjp.github.io/reference/type_traits/is_destructible.html)
- [cppreference: std::is_destructible](https://en.cppreference.com/w/cpp/types/is_destructible)
