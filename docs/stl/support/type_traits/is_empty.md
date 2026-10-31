---
title: std::is_empty
summary: "型が空（非静的なメンバ変数を持たない）かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_empty

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

タグとして使う、データを持たない型かを調べたい。`std::is_empty` は、<strong>型が空のクラスか</strong>を調べます。

!!! tip "ポイント"
    - `std::is_empty_v<T>` は、`T` が空のクラス（非静的メンバーが何もない）か
    - メンバー変数も仮想関数も持たないクラスだけが `true`
    - `std::is_empty<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - C++20 の `[[no_unique_address]]` で、メンバーでも大きさを省ける

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_empty_v {#is_empty}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
inline constexpr bool is_empty_v = is_empty<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

非静的メンバー変数を 1 つも持たず、仮想関数も持たないクラスが `true` です。`sizeof` は 1 バイトですが、基底クラスにすると 0 バイトにしてもらえる（空基底最適化）型の目印になります。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

struct Empty {};
struct Player {
  int hp;
  float x;
};

int main() {
  std::println("Empty                      -> {}", std::is_empty_v<Empty>);
  std::println("Player                     -> {}", std::is_empty_v<Player>);
  std::println("int                        -> {}", std::is_empty_v<int>);
}
```

```text title="実行結果"
Empty                      -> true
Player                     -> false
int                        -> false
```

## ゲームでの使いどころ

状態を持たない関数オブジェクトを、メンバー変数として持つと、1 バイト以上の場所を取ります。基底クラスにすれば 0 バイトにしてもらえるので、空かどうかを見て使い分けます。

```cpp
template <class Deleter>
class Handle : private Deleter {   // Deleter が空なら、この継承は場所を取らない
  int* ptr_ = nullptr;

 public:
  void Reset() {
    Deleter::operator()(ptr_);
    ptr_ = nullptr;
  }
};

static_assert(std::is_empty_v<std::default_delete<int>>);   // 状態を持たない
```

## よくあるミス

??? failure "sizeof が 1 だから中身があると思う"
    空のクラスの `sizeof` も 1 バイトです。同じ型のオブジェクトを別のアドレスに置くための最低の大きさです。

??? failure "仮想関数を持つクラスが true になると思う"
    仮想関数を持つとポインターを持つので、`false` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_class`](is_class.md) | クラスか |
| [`is_polymorphic`](is_polymorphic.md) | 仮想関数を持つか |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_empty_v<T>` は、`T` が空のクラス（非静的メンバーが何もない）か
    - [x] 空のクラスの目印。空基底最適化に使う
    - [x] C++20 では `[[no_unique_address]]` も使える

## 関連ページ

- [cpprefjp: std::is_empty](https://cpprefjp.github.io/reference/type_traits/is_empty.html)
- [cppreference: std::is_empty](https://en.cppreference.com/w/cpp/types/is_empty)
