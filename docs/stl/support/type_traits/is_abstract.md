---
title: std::is_abstract
summary: "型が抽象クラス（純粋仮想関数を持つ）かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_abstract

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

抽象クラスはインスタンスを作れません。`std::is_abstract` は、<strong>型が抽象クラスか</strong>を調べます。

!!! tip "ポイント"
    - `std::is_abstract_v<T>` は、`T` が抽象クラス（純粋仮想関数を持つ）か
    - `= 0` の仮想関数を持つクラスが対象。継承しただけで実装していない派生クラスも含む
    - `std::is_abstract<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - 抽象クラスは、インスタンスを作れない

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_abstract_v {#is_abstract}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
inline constexpr bool is_abstract_v = is_abstract<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

純粋仮想関数（`= 0`）を 1 つでも持つクラスが `true` です。基底の純粋仮想関数をまだ実装していない派生クラスも `true` になります。調べるには、型が完全型（定義が見えている型）でなければなりません。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

struct Shape {
  virtual float Area() const = 0;
};
struct Animal {
  virtual ~Animal() = default;
  virtual void Speak() {}
};
struct Player {
  int hp;
  float x;
};

int main() {
  std::println("Shape                      -> {}", std::is_abstract_v<Shape>);
  std::println("Animal                     -> {}", std::is_abstract_v<Animal>);
  std::println("Player                     -> {}", std::is_abstract_v<Player>);
}
```

```text title="実行結果"
Shape                      -> true
Animal                     -> false
Player                     -> false
```

## ゲームでの使いどころ

オブジェクトを作る工場関数で、抽象クラスを渡されたら、早い段階でコンパイルエラーにします。

```cpp
template <class T, class... Args>
std::unique_ptr<T> Create(Args&&... args) {
  static_assert(!std::is_abstract_v<T>, "抽象クラスはインスタンスにできません");
  return std::make_unique<T>(std::forward<Args>(args)...);
}
```

## よくあるミス

??? failure "実装のある仮想関数だけで抽象クラスだと思う"
    `virtual void Update();` のように、実装のある仮想関数だけなら `false` です。`= 0` の純粋仮想関数があるときだけ `true` です。

??? failure "前方宣言だけの型を渡す"
    定義が見えない型に使うと、未定義動作です。`#include` で定義を見せてから調べます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_polymorphic`](is_polymorphic.md) | 仮想関数を 1 つでも持つか。純粋でなくてもよい |
| [`is_final`](is_final.md) | これ以上継承できないクラスか |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_abstract_v<T>` は、`T` が抽象クラス（純粋仮想関数を持つ）か
    - [x] `= 0` の仮想関数を持つクラス（と、それを実装していない派生クラス）が `true`
    - [x] 型は完全型でなければならない

## 関連ページ

- [cpprefjp: std::is_abstract](https://cpprefjp.github.io/reference/type_traits/is_abstract.html)
- [cppreference: std::is_abstract](https://en.cppreference.com/w/cpp/types/is_abstract)
