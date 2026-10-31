---
title: std::piecewise_construct
summary: "pair の 2 つの要素を、それぞれ別のコンストラクタ引数で作るための印。"
order: 60
tags:
  - ユーティリティ
---

# std::piecewise_construct

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <utility>`
</div>

`std::pair<std::string, Player>` を作るとき、`Player` のコンストラクターが複数の引数を取ると、`pair(key, Player(5, "Hero"))` では、一時的な `Player` を作ってからムーブすることになります。`std::piecewise_construct` は、`pair` のコンストラクターに「各要素のコンストラクターの引数を、`tuple` で別々に渡します」と伝える印で、要素をその場で直接作れます。

!!! tip "ポイント"
    - `std::pair(std::piecewise_construct, tuple1, tuple2)` の形で使う
    - `tuple1` が `first` の、`tuple2` が `second` のコンストラクター引数
    - 一時オブジェクトを作らず、コピーもムーブも不要
    - `map::emplace` で、コピーやムーブができない値型を入れるときに必要

!!! info "このページを読む前に"
    [`std::forward_as_tuple`](forward_as_tuple.md) を先に読んでください。

## 関数の詳しい説明

### std::piecewise_construct {#piecewise_construct}

<span class="ver ver-11">C++11</span>

```cpp
struct piecewise_construct_t { explicit piecewise_construct_t() = default; };
inline constexpr std::piecewise_construct_t piecewise_construct{};
```

`piecewise_construct` は、値を持たない空の印です。`std::pair` のコンストラクターの、オーバーロードを選ぶために渡します。

```cpp
template <class... Args1, class... Args2>
pair(std::piecewise_construct_t, std::tuple<Args1...> first_args, std::tuple<Args2...> second_args);
```

`first_args` を `first` のコンストラクターに、`second_args` を `second` のコンストラクターに、それぞれ展開して渡します。引数を `tuple` に入れるのに、`std::forward_as_tuple` を使います。

`std::map::emplace(piecewise_construct, ...)` や `std::unordered_map::emplace` も、同じ形です。コピーも ムーブもできない型（`std::mutex` を持つ型など）を、値として入れるときは、この形が必須です。

## 実際に動かしてみる

```cpp
#include <map>
#include <mutex>
#include <print>
#include <string>
#include <tuple>

struct Player {
  Player(int l, std::string n) : level(l), name(std::move(n)) {}
  int level;
  std::string name;
};

// コピーもムーブもできない型
struct Locked {
  explicit Locked(int v) : value(v) {}
  std::mutex m;
  int value;
};

int main() {
  // pair を、各要素のコンストラクター引数から作る
  std::pair<std::string, Player> p(std::piecewise_construct,
                                   std::forward_as_tuple("hero"),
                                   std::forward_as_tuple(5, "Hero"));
  std::println("{} {} {}", p.first, p.second.level, p.second.name);

  // ムーブできない型を map に入れる
  std::map<int, Locked> m;
  m.emplace(std::piecewise_construct,
            std::forward_as_tuple(1),
            std::forward_as_tuple(42));
  std::println("{}", m.at(1).value);
}
```

```text title="実行結果"
hero 5 Hero
42
```

`Locked` は `std::mutex` を持つので、コピーもムーブもできませんが、`piecewise_construct` を使えば、`map` の中で直接作れます。

## ゲームでの使いどころ

スレッドの同期オブジェクトや、ムーブできない大きなオブジェクトを、`map` の値として持つときに使います。

## よくあるミス

??? failure "引数を tuple に入れ忘れる"
    各要素の引数は、必ず `tuple`（`forward_as_tuple`）にします。値を直接渡すと、別のオーバーロードが選ばれて、コンパイル エラーになります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::forward_as_tuple`](forward_as_tuple.md) | 引数を `tuple` にまとめる |
| [`std::make_pair`](make_pair.md) | 値から `pair` を作る |
| `std::map::try_emplace` | キーがなければ、値を直接作る。C++17 |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::piecewise_construct](https://cpprefjp.github.io/reference/utility/piecewise_construct.html)
- [cppreference: std::piecewise_construct](https://en.cppreference.com/w/cpp/utility/piecewise_construct)
