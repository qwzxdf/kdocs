---
title: std::is_default_constructible
summary: "引数なしで作れる型かを調べる。"
order: 10
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_default_constructible

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <type_traits>`
</div>

配列や `std::vector<T>(n)` は、既定のコンストラクターを要求します。`std::is_default_constructible` は、<strong>型が引数なしで作れるか</strong>を調べます。

!!! tip "ポイント"
    - `std::is_default_constructible_v<T>` は、`T` が引数なしで構築できるか
    - 引数が必要なコンストラクターだけの型は `false`
    - `std::is_default_constructible<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - `T() = default;` を足すと `true` になる

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_default_constructible_v {#is_default_constructible}

```cpp
template <class T>
inline constexpr bool is_default_constructible_v = is_default_constructible<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

引数なしで作れるか（`T()` や `T{}` が書けるか）を調べます。コンストラクターに引数が必要な型や、参照メンバーを持つ型は `false` です。`std::vector::resize` や、配列の確保は、この条件が前提です。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

struct Player {
  int hp;
  float x;
};
struct NoDefault {
  explicit NoDefault(int) {}
};

int main() {
  std::println("Player                     -> {}", std::is_default_constructible_v<Player>);
  std::println("NoDefault                  -> {}", std::is_default_constructible_v<NoDefault>);
  std::println("int                        -> {}", std::is_default_constructible_v<int>);
}
```

```text title="実行結果"
Player                     -> true
NoDefault                  -> false
int                        -> true
```

## ゲームでの使いどころ

要素を一括で作るコンテナで、既定の構築ができない型を、早い段階で弾きます。

```cpp
template <class T>
class Grid {
  static_assert(std::is_default_constructible_v<T>, "マスの型は引数なしで作れる必要があります");
  std::vector<T> cells_;

 public:
  Grid(int w, int h) : cells_(w * h) {}   // 引数なしで T を作る
};
```

## よくあるミス

??? failure "引数つきのコンストラクターだけを持つ型"
    デフォルトコンストラクターが暗黙に作られないので、`false` です。`T() = default;` を足すか、引数に既定値を付けます。

??? failure "参照メンバーを持つ型"
    参照メンバーは、初期化しないと作れないので、`false` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_constructible`](is_constructible.md) | 引数を指定して作れるか |
| [`is_trivially_default_constructible`](is_trivially_default_constructible.md) | 作る処理が何もしないか |
| [`is_nothrow_default_constructible`](is_nothrow_default_constructible.md) | 例外を投げないか |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_default_constructible_v<T>` は、`T` が引数なしで構築できるか
    - [x] `T()` と書けるかを調べる
    - [x] 引数が必要な型は `false`

## 関連ページ

- [cpprefjp: std::is_default_constructible](https://cpprefjp.github.io/reference/type_traits/is_default_constructible.html)
- [cppreference: std::is_default_constructible](https://en.cppreference.com/w/cpp/types/is_default_constructible)
