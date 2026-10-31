---
title: std::make_from_tuple
summary: "tuple の要素を引数にして、クラスのオブジェクトを作る。"
order: 55
tags:
  - ユーティリティ
---

# std::make_from_tuple

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <tuple>`
</div>

`std::apply` が関数を呼ぶのに対し、`std::make_from_tuple<T>(t)` は、`tuple` の要素を引数にして、型 `T` のコンストラクターを呼び、オブジェクトを作ります。保存しておいた引数から、あとでオブジェクトを作る、遅延生成に使います。

!!! tip "ポイント"
    - `make_from_tuple<T>(t)` は `T(get<0>(t), get<1>(t), ...)` と同じ
    - 戻り値は `T` の値。ムーブやコピーの省略が効く
    - `pair` や `std::array` も渡せる
    - 関数を呼ぶなら `std::apply`

!!! info "このページを読む前に"
    [`std::apply`](apply.md) を先に読んでください。

## 関数の詳しい説明

### std::make_from_tuple {#make_from_tuple}

<span class="ver ver-17">C++17</span>

```cpp
template <class T, class Tuple>
constexpr T make_from_tuple(Tuple&& t);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | テンプレート引数 | 作るオブジェクトの型 |
| `t` | `tuple` / `pair` / `array` | コンストラクターの引数 |

`t` の要素を引数に、`T` のコンストラクターを呼びます。波括弧の初期化（`T{...}`）ではなく、丸括弧（`T(...)`）の形です。要素の数と型が、コンストラクターに合わなければ、コンパイル エラーです。

戻り値の `T` は、C++17 の保証されたコピー省略により、コピーもムーブもなしで作られます。コピーできない型でも作れます。

## 実際に動かしてみる

```cpp
#include <print>
#include <string>
#include <tuple>

struct Player {
  Player(int level, std::string name) : level(level), name(std::move(name)) {}
  int level;
  std::string name;
};

int main() {
  // 引数を tuple に保存しておき、あとで Player を作る
  auto args = std::make_tuple(5, std::string("Hero"));
  Player p = std::make_from_tuple<Player>(std::move(args));
  std::println("{} {}", p.level, p.name);

  // pair からも作れる
  auto s = std::make_from_tuple<std::string>(std::make_pair(3, 'x'));  // string(3, 'x')
  std::println("{}", s);
}
```

```text title="実行結果"
5 Hero
xxx
```

`string(3, 'x')` は、`'x'` を 3 個並べた文字列を作るコンストラクターです。

## ゲームでの使いどころ

エンティティの生成要求を、「型とコンストラクターの引数」の組で記録しておき、あとでまとめて生成するときに使います。

## よくあるミス

??? failure "波括弧の初期化を期待する"
    丸括弧で呼ばれます。`std::initializer_list` のコンストラクターは選ばれません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::apply`](apply.md) | 関数を呼ぶ |
| [`std::make_unique`](make_unique.md) | 引数からヒープ上にオブジェクトを作る |
| [`std::tuple_cat`](tuple_cat.md) | `tuple` をつなげる |

## コンパイラ対応

C++17 から使えます。

## 関連ページ

- [cpprefjp: std::make_from_tuple](https://cpprefjp.github.io/reference/tuple/make_from_tuple.html)
- [cppreference: std::make_from_tuple](https://en.cppreference.com/w/cpp/utility/make_from_tuple)
