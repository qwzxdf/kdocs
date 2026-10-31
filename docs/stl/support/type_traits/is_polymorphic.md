---
title: std::is_polymorphic
summary: "型が仮想関数を持つ（多態的な）かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_polymorphic

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

仮想関数があると、オブジェクトに仮想関数テーブルへのポインタが入ります。`memcpy` でコピーしてはいけない型を判断するとき、`std::is_polymorphic` が役立ちます。

!!! tip "ポイント"
    - `std::is_polymorphic_v<T>` は、`T` が仮想関数を持つクラスか
    - 仮想デストラクターだけでも `true`
    - `std::is_polymorphic<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - `dynamic_cast` の対象にできる型の目印

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_polymorphic_v {#is_polymorphic}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
inline constexpr bool is_polymorphic_v = is_polymorphic<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

仮想関数を 1 つでも宣言した、または継承したクラスが `true` です。仮想デストラクターだけを持つクラスも `true` になります。継承があるだけで、仮想関数がなければ `false` です。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

struct Animal {
  virtual ~Animal() = default;
  virtual void Speak() {}
};
struct Player {
  int hp;
  float x;
};

int main() {
  std::println("Animal                     -> {}", std::is_polymorphic_v<Animal>);
  std::println("Player                     -> {}", std::is_polymorphic_v<Player>);
  std::println("int                        -> {}", std::is_polymorphic_v<int>);
}
```

```text title="実行結果"
Animal                     -> true
Player                     -> false
int                        -> false
```

## ゲームでの使いどころ

実行時の型で判定する `dynamic_cast` を、使える型にだけ使います。

```cpp
template <class To, class From>
To* SafeCast(From* p) {
  if constexpr (std::is_polymorphic_v<From>) {
    return dynamic_cast<To*>(p);   // 実行時の型で判定する
  } else {
    return static_cast<To*>(p);    // 仮想関数がないので、dynamic_cast は使えない
  }
}
```

## よくあるミス

??? failure "仮想デストラクターだけの型を、polymorphic でないと思う"
    仮想デストラクターだけでも `true` です。基底クラスのポインターで消すために付けた場合でも、`dynamic_cast` が使える型になります。

??? failure "継承があれば true だと思う"
    仮想関数が 1 つもなければ、継承していても `false` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_abstract`](is_abstract.md) | 純粋仮想関数を持つか |
| [`is_final`](is_final.md) | 継承できないか |
| [`is_class`](is_class.md) | クラスか |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_polymorphic_v<T>` は、`T` が仮想関数を持つクラスか
    - [x] 仮想関数を持つクラスが `true`
    - [x] 継承しているだけでは `false`

## 関連ページ

- [cpprefjp: std::is_polymorphic](https://cpprefjp.github.io/reference/type_traits/is_polymorphic.html)
- [cppreference: std::is_polymorphic](https://en.cppreference.com/w/cpp/types/is_polymorphic)
