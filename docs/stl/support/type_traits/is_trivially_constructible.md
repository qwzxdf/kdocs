---
title: std::is_trivially_constructible
summary: "指定した引数で、自明に（特別な処理なしで）構築できる型かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_trivially_constructible

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

特定の引数で構築するとき、実行時の処理が要らないかを知りたい。`std::is_trivially_constructible<T, Args...>` は、<strong>T を Args... から構築する処理が自明か</strong>を調べます。

!!! tip "ポイント"
    - `std::is_trivially_constructible_v<T, Args...>` は、`T` を `Args...` から自明に構築できるか
    - `<T>` は引数なし、`<T, const T&>` はコピー
    - `std::is_trivially_constructible<T, Args...>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - メンバーの既定値で自明でなくなる

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_trivially_constructible_v {#is_trivially_constructible}

<span class="ver ver-11">C++11</span>

```cpp
template <class T, class... Args>
inline constexpr bool is_trivially_constructible_v = is_trivially_constructible<T, Args...>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 構築する型 |
| `Args...` | 型の並び | 構築に渡す引数の型 |

`T(args...)` の呼び出しが、自明な（ビットの複製だけの）処理で済むなら `true` です。引数なしの `<T>` は自明な既定コンストラクター、`<T, const T&>` は自明なコピーコンストラクターの判定になります。

引数の型は、渡す式の型（値カテゴリーを含む）で指定します。`const T&` ならコピー、`T&&` ならムーブの判定になります。

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
  std::println("Player                             -> {}", std::is_trivially_constructible_v<Player>);
  std::println("Player, const Player&              -> {}", std::is_trivially_constructible_v<Player, const Player&>);
  std::println("std::string, const std::string&    -> {}", std::is_trivially_constructible_v<std::string, const std::string&>);
  std::println("int, int                           -> {}", std::is_trivially_constructible_v<int, int>);
}
```

```text title="実行結果"
Player                             -> true
Player, const Player&              -> true
std::string, const std::string&    -> false
int, int                           -> true
```

## ゲームでの使いどころ

範囲をコピーして構築するとき、自明な型なら `memcpy` で写します。

```cpp
template <class T>
void ConstructCopy(T* dst, const T* src, std::size_t n) {
  if constexpr (std::is_trivially_constructible_v<T, const T&>) {
    std::memcpy(dst, src, sizeof(T) * n);          // 自明なコピー
  } else {
    std::uninitialized_copy_n(src, n, dst);         // コンストラクターを 1 つずつ呼ぶ
  }
}
```

## よくあるミス

??? failure "引数の並びを省略する"
    `<T>` は引数なし、`<T, const T&>` はコピーです。調べたい構築に合わせて、`Args...` を渡します。

??? failure "メンバーに既定値があるのに true を期待する"
    `int hp = 100;` のような既定値があると、既定のコンストラクターが自明でなくなるので `false` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_constructible`](is_constructible.md) | 自明さを考えずに、作れるか |
| [`is_trivially_default_constructible`](is_trivially_default_constructible.md) | 引数なしに絞った版 |
| [`is_trivially_copy_constructible`](is_trivially_copy_constructible.md) | コピーに絞った版 |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_trivially_constructible_v<T, Args...>` は、`T` を `Args...` から自明に構築できるか
    - [x] 構築の自明さを調べる
    - [x] memcpy の近道を選ぶ条件になる

## 関連ページ

- [cpprefjp: std::is_trivially_constructible](https://cpprefjp.github.io/reference/type_traits/is_trivially_constructible.html)
- [cppreference: std::is_trivially_constructible](https://en.cppreference.com/w/cpp/types/is_trivially_constructible)
