---
title: std::is_final
summary: "型が `final`（継承できない）かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_final

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-14">C++14</span>
`#include <type_traits>`
</div>

`final` を付けたクラスは、継承できません。`std::is_final` は、<strong>型が `final` か</strong>を調べます。

!!! tip "ポイント"
    - `std::is_final_v<T>` は、`T` が `final` クラスか
    - クラス自体に `final` が付いているかを調べる
    - `std::is_final<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - 仮想関数の `final` は対象外

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_final_v {#is_final}

<span class="ver ver-14">C++14</span>

```cpp
template <class T>
inline constexpr bool is_final_v = is_final<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

`final` を付けたクラスが `true` です。それ以上、継承できないクラスの目印です。`final` を付けた仮想関数は数えません。クラスでなければ `false` です。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

struct Boss final {
  int hp;
};
struct Player {
  int hp;
  float x;
};

int main() {
  std::println("Boss                       -> {}", std::is_final_v<Boss>);
  std::println("Player                     -> {}", std::is_final_v<Player>);
  std::println("int                        -> {}", std::is_final_v<int>);
}
```

```text title="実行結果"
Boss                       -> true
Player                     -> false
int                        -> false
```

## ゲームでの使いどころ

クラスの継承を前提にしたテンプレートで、継承できない型を弾きます。

```cpp
template <class Base>
struct Wrapper : Base {   // Base を継承して機能を足す
  static_assert(!std::is_final_v<Base>, "final なクラスは継承できません");
};
```

## よくあるミス

??? failure "final な仮想関数を持つクラスが true になると思う"
    `final` の対象はクラスです。仮想関数に付けた `final` は数えません。

??? failure "クラス以外に使う"
    `int` などのクラスでない型は `false` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_abstract`](is_abstract.md) | 抽象クラスか |
| [`is_polymorphic`](is_polymorphic.md) | 仮想関数を持つか |

## コンパイラ対応

C++14 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_final_v<T>` は、`T` が `final` クラスか
    - [x] `final` クラスが `true`
    - [x] 継承するラッパーに渡す型の確認に使う

## 関連ページ

- [cpprefjp: std::is_final](https://cpprefjp.github.io/reference/type_traits/is_final.html)
- [cppreference: std::is_final](https://en.cppreference.com/w/cpp/types/is_final)
