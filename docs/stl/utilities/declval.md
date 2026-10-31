---
title: std::declval
summary: "式の中でだけ使う、「その型の値があるとみなす」ための関数（decltype 専用）。"
order: 74
tags:
  - ユーティリティ
---

# std::declval

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <utility>`
</div>

テンプレートの中で、「`T` の関数 `Get()` の戻り値の型」を知りたい。でも `T` が既定のコンストラクターを持たないと、`T()` と書いて式を作れません。`std::declval<T>()` は、<strong>実際には呼ばれない、「`T` 型の値が手元にあるつもり」の式</strong>を作る関数です。`decltype` の中などで、型を調べるためだけに使います。

!!! tip "ポイント"
    - `decltype(std::declval<T>().Get())` のように、型の計算の中でだけ使う
    - 戻り値は `T&&`。`std::declval<T&>()` なら左辺値
    - 評価される場所（普通の式）で呼ぶと、コンパイル エラー
    - 定義を持たない関数。実行時には存在しない

!!! info "このページを読む前に"
    [`decltype`](../../basics/template.md) とテンプレートの基本を先に読んでください。

## 関数の詳しい説明

### std::declval {#declval}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
std::add_rvalue_reference_t<T> declval() noexcept;
```

宣言だけがあって、定義がありません。`decltype`、`sizeof`、`noexcept(...)`、`requires` のような、<strong>式が評価されない場所</strong>でしか使えません。普通の式の中で呼ぶと、リンク時に未定義、または `static_assert` で失敗します。

`std::declval<T>()` は `T&&` を返す式なので、右辺値として扱われます。左辺値として扱いたいときは、`std::declval<T&>()` と書きます。メンバー関数の修飾（`&` や `const`）によって、呼べるかどうかが変わる場面で、使い分けます。

典型的な使い方は、メンバーの型を取り出すことです。

```cpp
template <class T>
using GetResult = decltype(std::declval<T&>().Get());
```

`T` が `Get()` を持たなければ、置換に失敗して、オーバーロードの候補から外れます（SFINAE）。型特性（`is_invocable`、`is_constructible` など）は、内部でこれを使っています。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>
#include <utility>

// 既定のコンストラクターを持たない型
struct Weapon {
  explicit Weapon(int power) : power(power) {}
  int Power() const { return power; }
  int power;
};

// Get() を持つ型だけが選ばれる
template <class T>
auto Describe(T& t) -> decltype(std::declval<T&>().Power()) {
  return t.Power();
}

int main() {
  // Weapon を作らずに、戻り値の型だけを調べる
  using R = decltype(std::declval<Weapon>().Power());
  static_assert(std::is_same_v<R, int>);

  // 左辺値として扱う
  static_assert(std::is_same_v<decltype(std::declval<Weapon&>()), Weapon&>);
  static_assert(std::is_same_v<decltype(std::declval<Weapon>()), Weapon&&>);

  Weapon w{10};
  std::println("{}", Describe(w));
}
```

```text title="実行結果"
10
```

`Weapon` は既定のコンストラクターを持たないので、`Weapon()` とは書けません。`declval` を使うと、オブジェクトを作らずに、型だけを問い合わせられます。

## ゲームでの使いどころ

ゲームのコードで直接書くことは少なく、テンプレートで「この型は `Update()` を持つか」のような条件を作る、エンジン側のコードに出てきます。

## よくあるミス

??? failure "普通の式の中で呼ぶ"
    `auto x = std::declval<T>();` は、コンパイル エラーです。`decltype` の中だけで使います。

??? failure "左辺値が必要なのに、右辺値で調べる"
    `std::declval<T>()` は右辺値です。`&` 修飾のメンバー関数を調べるなら、`std::declval<T&>()` にします。

## 類似

| 名前 | 違い |
| --- | --- |
| `std::is_invocable` | 呼べるかを調べる型特性。内部で使う |
| `decltype` | 式の型を調べる |
| [`std::addressof`](addressof.md) | オブジェクトのアドレスを取る |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::declval](https://cpprefjp.github.io/reference/utility/declval.html)
- [cppreference: std::declval](https://en.cppreference.com/w/cpp/utility/declval)
