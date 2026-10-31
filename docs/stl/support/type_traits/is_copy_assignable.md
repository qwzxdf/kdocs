---
title: std::is_copy_assignable
summary: "コピー代入できる型かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_copy_assignable

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

`a = b` が書ける型かを調べたい。`std::is_copy_assignable` は、<strong>型がコピー代入できるか</strong>を調べます。

!!! tip "ポイント"
    - `std::is_copy_assignable_v<T>` は、`T` がコピー代入できるか
    - `const` メンバーや参照メンバーを持つクラスは `false`
    - `std::is_copy_assignable<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - `unique_ptr` のようなムーブ専用の型も `false`

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_copy_assignable_v {#is_copy_assignable}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
inline constexpr bool is_copy_assignable_v = is_copy_assignable<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

同じ型のオブジェクトを `const T&` から代入できるかを調べます。`std::vector` や `std::string` は `true`、`std::unique_ptr` は `false` です。`const` なメンバー変数や参照のメンバー変数を持つクラスは、代入演算子が暗黙に削除されるため、`false` になります。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

struct Player {
  int hp;
  float x;
};
struct NoCopy {
  NoCopy() = default;
  NoCopy(const NoCopy&) = delete;
  NoCopy& operator=(const NoCopy&) = delete;
};

int main() {
  std::println("Player                     -> {}", std::is_copy_assignable_v<Player>);
  std::println("NoCopy                     -> {}", std::is_copy_assignable_v<NoCopy>);
  std::println("const Player               -> {}", std::is_copy_assignable_v<const Player>);
}
```

```text title="実行結果"
Player                     -> true
NoCopy                     -> false
const Player               -> false
```

## ゲームでの使いどころ

コンポーネントを配列に詰め直す処理で、コピー代入できる型だけを受け付けます。

```cpp
template <class Component>
struct Pool {
  static_assert(std::is_copy_assignable_v<Component>, "コピー代入できる型にしてください");
  std::vector<Component> items;
};
```

## よくあるミス

??? failure "const メンバーを持つクラスが代入できると思う"
    `const int id;` のようなメンバーがあると、代入演算子が削除されて `false` になります。

??? failure "ムーブ専用の型で true を期待する"
    `std::unique_ptr` のような型は `false` です。ムーブ代入は `is_move_assignable` で調べます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_move_assignable`](is_move_assignable.md) | ムーブ代入できるか |
| [`is_copy_constructible`](is_copy_constructible.md) | コピー構築できるか |
| [`is_trivially_copy_assignable`](is_trivially_copy_assignable.md) | コピー代入がメモリのコピーだけか |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_copy_assignable_v<T>` は、`T` がコピー代入できるか
    - [x] コピー代入が使えるかを調べる
    - [x] `const` メンバーや参照メンバーがあると `false`

## 関連ページ

- [cpprefjp: std::is_copy_assignable](https://cpprefjp.github.io/reference/type_traits/is_copy_assignable.html)
- [cppreference: std::is_copy_assignable](https://en.cppreference.com/w/cpp/types/is_copy_assignable)
