---
title: std::is_trivial
summary: "型がトリビアル（自明な構築・コピー・破棄ができる）かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_trivial

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

`memset` で初期化してよいか、`memcpy` でコピーしてよいかを知りたい。`std::is_trivial` は、<strong>型がトリビアルか</strong>を調べます。

!!! tip "ポイント"
    - `std::is_trivial_v<T>` は、`T` がトリビアル（コンストラクター・コピー・ムーブ・デストラクターが自明）か
    - 値は `bool` の定数。`static_assert` や `if constexpr` に使える
    - `std::is_trivial<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - 実行時のコストはない（コンパイル時に決まる）

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_trivial_v {#is_trivial}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
inline constexpr bool is_trivial_v = is_trivial<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

自分で定義したコンストラクターやデストラクターを持たない、単純な型は `true` です。`int` や、それだけを持つ構造体は `true` です。`std::string` のように、動的メモリを管理する型は `false` です。

型の性質を調べるだけで、オブジェクトは作りません。テンプレートの中で、型によって処理を分ける（`if constexpr`）、使えない型を早い段階で弾く（`static_assert`、`concept`）、といった用途で使います。

## 実際に動かしてみる

```cpp
#include <print>
#include <string>
#include <type_traits>

struct Player {
  int hp;
  float x;
};

int main() {
  std::println("int                        -> {}", std::is_trivial_v<int>);
  std::println("Player                     -> {}", std::is_trivial_v<Player>);
  std::println("std::string                -> {}", std::is_trivial_v<std::string>);
}
```

```text title="実行結果"
int                        -> true
Player                     -> true
std::string                -> false
```

## ゲームでの使いどころ

型によって処理を切り替えるテンプレートで使います。

```cpp
template <class T>
void Process(const T& value) {
  if constexpr (std::is_trivial_v<T>) {
    // T が条件に当てはまる型のときの処理
  } else {
    // それ以外の型の処理
  }
}
```

## よくあるミス

??? failure "`T` に参照や `const` が付いていて、期待と違う結果になる"
    `std::remove_cvref_t<T>` で外してから調べます。

??? failure "実行時の値に使おうとする"
    調べるのは型です。値の判定には通常の比較を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`<type_traits>`](../type_traits.md) | 型の性質を調べる道具の一覧 |
| [`is_same`](is_same.md) | 2 つの型が同じか |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_trivial_v<T>` は、`T` がトリビアル（コンストラクター・コピー・ムーブ・デストラクターが自明）か
    - [x] `static_assert` と `if constexpr` に使える
    - [x] 参照や `const` が付いた型は、先に `remove_cvref_t` で外す

## 関連ページ

- [cpprefjp: std::is_trivial](https://cpprefjp.github.io/reference/type_traits/is_trivial.html)
- [cppreference: std::is_trivial](https://en.cppreference.com/w/cpp/types/is_trivial)
