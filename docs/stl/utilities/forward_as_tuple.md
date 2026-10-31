---
title: std::forward_as_tuple
summary: "引数を完全転送のまま、参照の tuple にまとめる。"
order: 57
tags:
  - ユーティリティ
---

# std::forward_as_tuple

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <tuple>`
</div>

関数の引数を、そのままの形（左辺値は左辺値、右辺値は右辺値）で `tuple` にまとめて、別の関数に渡したい。`std::forward_as_tuple` は、引数への<strong>転送参照</strong>を要素とする `tuple` を作る関数です。値をコピーせず、参照のまま持ち運びます。

`std::map::emplace` の `piecewise_construct` で、キーと値のコンストラクターの引数を、それぞれ `tuple` にまとめるときに使います。

!!! tip "ポイント"
    - 各要素は、引数の参照（左辺値なら `T&`、右辺値なら `T&&`）
    - コピーもムーブもしない。参照を運ぶだけ
    - 作った `tuple` は、その式の中で使い切る。あとに残さない
    - `std::piecewise_construct` と組み合わせて使う

!!! info "このページを読む前に"
    [`std::tie`](tie.md) と [`std::piecewise_construct`](piecewise_construct.md) を先に読んでください。

## 関数の詳しい説明

### std::forward_as_tuple {#forward_as_tuple}

<span class="ver ver-11">C++11</span>

```cpp
template <class... Types>
constexpr std::tuple<Types&&...> forward_as_tuple(Types&&... args) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `args` | 任意（可変個） | 参照として持つ値 |

戻り値の各要素は、`Types&&` です。`Types` が `int&`（左辺値）なら参照の折りたたみで `int&`、`int`（右辺値）なら `int&&` になります。

`std::tie` との違いは、右辺値も受け付けることです。ただし、右辺値の参照は、元の一時オブジェクトが消えると無効になります。`tuple` を変数に取っておくと、危険です。

主な用途は、`piecewise_construct` を使う `pair` の構築です。

```cpp
std::map<std::string, Player> m;
m.emplace(std::piecewise_construct,
          std::forward_as_tuple("hero"),                 // キーの引数
          std::forward_as_tuple(5, "Hero"));             // 値の引数
```

`Player` を一時オブジェクトとして作って、コピーやムーブをする手間がなく、コンストラクターの引数が直接渡されます。

## 実際に動かしてみる

```cpp
#include <map>
#include <print>
#include <string>
#include <tuple>

struct Player {
  Player(int l, std::string n) : level(l), name(std::move(n)) {}
  int level;
  std::string name;
};

int main() {
  std::map<std::string, Player> m;

  // キーと値のコンストラクター引数を、それぞれ tuple で渡す
  m.emplace(std::piecewise_construct,
            std::forward_as_tuple("hero"),
            std::forward_as_tuple(5, "Hero"));

  const Player& p = m.at("hero");
  std::println("{} {}", p.level, p.name);

  // 要素の型を確かめる
  int x = 1;
  auto t = std::forward_as_tuple(x, 2);
  static_assert(std::is_same_v<decltype(t), std::tuple<int&, int&&>>);
}
```

```text title="実行結果"
5 Hero
```

左辺値の `x` は `int&`、右辺値の `2` は `int&&` として入っています。

## ゲームでの使いどころ

`std::map` や `std::unordered_map` に、コピーできない型や、コピーが重い型を `emplace` で追加するときに使います。

## よくあるミス

??? failure "tuple を変数に取っておく"
    右辺値の参照は、元の一時オブジェクトが消えると無効になります。その文の中で使い切ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::tie`](tie.md) | 左辺値だけ。参照を持つ |
| [`std::make_tuple`](make_tuple.md) | 値をコピーする |
| [`std::piecewise_construct`](piecewise_construct.md) | これと組み合わせる印 |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::forward_as_tuple](https://cpprefjp.github.io/reference/tuple/forward_as_tuple.html)
- [cppreference: std::forward_as_tuple](https://en.cppreference.com/w/cpp/utility/tuple/forward_as_tuple)
