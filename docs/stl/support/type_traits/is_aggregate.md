---
title: std::is_aggregate
summary: "集成体（波かっこでメンバを順に初期化できる型）かを調べる。"
order: 13
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_aggregate

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <type_traits>`
</div>

`Player p{100, 1.0f};` のように、メンバーを順に並べて初期化できる型かを調べたい。`std::is_aggregate` は、<strong>型が集成体か</strong>を調べます。

!!! tip "ポイント"
    - `std::is_aggregate_v<T>` は、`T` が集成体（ブレース初期化できる単純な型）か
    - 配列と、ユーザー定義のコンストラクターを持たないクラスが `true`
    - `std::is_aggregate<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - 波括弧の並びでメンバーを順に初期化できるかの目安になる

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_aggregate_v {#is_aggregate}

<span class="ver ver-17">C++17</span>

```cpp
template <class T>
inline constexpr bool is_aggregate_v = is_aggregate<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

ユーザーが書いたコンストラクターを持たず、private なメンバー変数も仮想関数も持たないクラスと、配列が `true` です。`Player{100, 50}` のように、波括弧に並べた値でメンバーを順に初期化できる型の目安になります。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

struct Player {
  int hp;
  float x;
};
class Hidden {
  int secret_ = 0;
};

int main() {
  std::println("Player                     -> {}", std::is_aggregate_v<Player>);
  std::println("Hidden                     -> {}", std::is_aggregate_v<Hidden>);
  std::println("int[3]                     -> {}", std::is_aggregate_v<int[3]>);
  std::println("int                        -> {}", std::is_aggregate_v<int>);
}
```

```text title="実行結果"
Player                     -> true
Hidden                     -> false
int[3]                     -> true
int                        -> false
```

## ゲームでの使いどころ

引数の並びからオブジェクトを作る関数で、コンストラクターを呼ぶ形と、波括弧で初期化する形を切り替えます。

```cpp
template <class T, class... Args>
T Make(Args&&... args) {
  if constexpr (std::is_constructible_v<T, Args...>) {
    return T(std::forward<Args>(args)...);
  } else {
    static_assert(std::is_aggregate_v<T>, "コンストラクターも波括弧の初期化も使えません");
    return T{std::forward<Args>(args)...};
  }
}
```

## よくあるミス

??? failure "コンストラクターを 1 つ書いただけで集成体でなくなる"
    ユーザー定義のコンストラクターがあると、`Player{100, 50}` のような初期化が使えなくなります（C++20 では、宣言しただけでも集成体ではなくなります）。

??? failure "private なメンバー変数を足す"
    `private` や `protected` のメンバー変数が 1 つでもあると、集成体ではありません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_trivial`](is_trivial.md) | コンストラクターやコピーが自明か |
| [`is_standard_layout`](is_standard_layout.md) | C 言語と同じ並びのメモリ配置か |

## コンパイラ対応

C++17 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_aggregate_v<T>` は、`T` が集成体（ブレース初期化できる単純な型）か
    - [x] コンストラクターなし・private メンバーなし・仮想関数なしが集成体
    - [x] `T{a, b}` で初期化できる型の見分けに使う

## 関連ページ

- [cpprefjp: std::is_aggregate](https://cpprefjp.github.io/reference/type_traits/is_aggregate.html)
- [cppreference: std::is_aggregate](https://en.cppreference.com/w/cpp/types/is_aggregate)
