---
title: std::make_tuple
summary: "型を推論して tuple を作る。"
order: 53
tags:
  - ユーティリティ
---

# std::make_tuple

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <tuple>`
</div>

関数が「名前と HP と座標」を返したい、でも構造体を作るほどでもない。そんなとき、複数の値をまとめて 1 つの値として扱えるのが `std::tuple` です。`std::make_tuple(a, b, c)` は、渡した値の型を推論して `tuple` を作る関数で、`std::tuple<int, std::string, float>` のような長い型を書かずに済みます。

C++17 からは、クラステンプレートの型推論（CTAD）で `std::tuple(a, b, c)` と書けます。`make_tuple` は、それ以前のコードや、型を明示したくない場面で出てきます。

!!! tip "ポイント"
    - 引数の型を推論して `tuple` を作る。中身はコピー（またはムーブ）される
    - `std::ref(x)` を渡した所だけ、参照が入る
    - C++17 以降は `std::tuple(a, b, c)` で足りる
    - 要素は `std::get<0>(t)` か、構造化束縛 `auto [a, b, c] = t;` で取り出す

!!! info "このページを読む前に"
    [`std::tuple`](tuple.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::make_tuple {#make_tuple}

<span class="ver ver-11">C++11</span>

```cpp
template <class... Types>
constexpr std::tuple<std::unwrap_ref_decay_t<Types>...> make_tuple(Types&&... args);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `args` | 任意の型（可変個） | `tuple` の要素にする値 |

各引数は、`decay`（配列やポインタの変換、`const` と参照の除去）された型でコピーされます。文字列リテラル `"abc"` を渡すと、要素は `const char*` になり、`std::string` にはなりません。`std::string` にしたいときは、`std::string("abc")` と書きます。

参照を保持したいときは、`std::ref(x)` か `std::cref(x)` を渡します。`unwrap_ref_decay_t` により、`reference_wrapper<T>` は `T&` になります。ただし、参照をまとめるのは `std::tie` のほうが目的に合います。

戻り値は `std::tuple` です。`constexpr` なので、コンパイル時にも使えます。

## 実際に動かしてみる

```cpp
#include <print>
#include <string>
#include <tuple>

int main() {
  auto t = std::make_tuple(10, std::string("Hero"), 1.5f);  // tuple<int, string, float>
  std::println("{} {} {}", std::get<0>(t), std::get<1>(t), std::get<2>(t));

  // 文字列リテラルは const char* になる
  auto u = std::make_tuple("abc");
  static_assert(std::is_same_v<decltype(u), std::tuple<const char*>>);

  // std::ref を渡すと、参照が入る
  int hp = 30;
  auto r = std::make_tuple(std::ref(hp));
  std::get<0>(r) = 99;
  std::println("hp = {}", hp);

  // 構造化束縛で取り出す
  auto [level, name, scale] = t;
  std::println("{} {} {}", level, name, scale);
}
```

```text title="実行結果"
10 Hero 1.5
hp = 99
10 Hero 1.5
```

`std::ref(hp)` を渡した要素への代入が、元の `hp` を書き換えています。

## ゲームでの使いどころ

関数から複数の値を返すとき、`std::tuple` は手軽です。ただし、要素の意味が型からは分からないので、3 つ以上になったら、名前の付いた構造体にするほうが読みやすくなります。

## よくあるミス

??? failure "文字列リテラルが std::string になると思う"
    要素は `const char*` です。`std::string("abc")` と書きます。

??? failure "参照が入ると思って、コピーされる"
    普通に渡した値はコピーされます。参照を持たせたいなら `std::ref` か `std::tie` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::tie`](tie.md) | 参照の `tuple` を作る |
| [`std::forward_as_tuple`](forward_as_tuple.md) | 転送参照の `tuple`。コピーしない |
| [`std::make_pair`](make_pair.md) | 2 要素の `pair` |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::make_tuple](https://cpprefjp.github.io/reference/tuple/make_tuple.html)
- [cppreference: std::make_tuple](https://en.cppreference.com/w/cpp/utility/tuple/make_tuple)
