---
title: std::in_place
summary: "optional / variant / any の中に、オブジェクトをその場で構築するための印。"
order: 70
tags:
  - ユーティリティ
---

# std::in_place

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <utility>`
</div>

`std::optional<std::string>` の中に `std::string(3, 'x')` を入れたいとき、`std::optional<std::string>(std::string(3, 'x'))` だと、一時的な文字列を作ってから、ムーブします。`std::in_place` は、`optional` に、「中身を、これから渡す引数で直接作ってください」と伝える印です。

!!! tip "ポイント"
    - `std::optional<T> o(std::in_place, 引数...)` で、中身を引数から直接作る
    - `std::any` と `std::variant` には、型や番号を指定する `in_place_type` と `in_place_index`
    - コピーもムーブもできない型を入れるときに必須
    - C++17

!!! info "このページを読む前に"
    [`std::optional`](optional.md) を先に読んでください。

## 関数の詳しい説明

### std::in_place {#in_place}

<span class="ver ver-17">C++17</span>

```cpp
struct in_place_t { explicit in_place_t() = default; };
inline constexpr std::in_place_t in_place{};
```

`in_place` は、値を持たない空の印です。`optional` のコンストラクターのオーバーロードを選ぶために渡します。

```cpp
std::optional<std::string> o(std::in_place, 3, 'x');   // string(3, 'x') を直接作る
```

`optional<T>` では、`T` が 1 つに決まっているので、`in_place` だけで足ります。`variant` や `any` のように、型を選ぶ必要があるものには、[`in_place_type`](in_place_type.md) と [`in_place_index`](in_place_index.md) を使います。

`std::expected` の `unexpect` も、似た仕組みの印です。

## 実際に動かしてみる

```cpp
#include <mutex>
#include <optional>
#include <print>
#include <string>

struct Locked {
  explicit Locked(int v) : value(v) {}
  std::mutex m;  // コピーもムーブもできない
  int value;
};

int main() {
  // string(3, 'x') を optional の中で直接作る
  std::optional<std::string> a(std::in_place, 3, 'x');
  std::println("{}", *a);

  // ムーブできない型も入れられる
  std::optional<Locked> b(std::in_place, 42);
  std::println("{}", b->value);

  // emplace でも同じことができる
  std::optional<std::string> c;
  c.emplace(2, 'y');
  std::println("{}", *c);
}
```

```text title="実行結果"
xxx
42
yy
```

## ゲームでの使いどころ

ムーブできないリソース（ミューテックスを含む型など）を、`optional` で包むときに使います。後から作るなら、`emplace` が分かりやすくなります。

## よくあるミス

??? failure "in_place を省略して、型の変換が起きる"
    `std::optional<std::string> o("abc")` のような書き方でも作れますが、引数が複数あるときは、`in_place` が必要です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`in_place_type`](in_place_type.md) | 型を選ぶ印 |
| [`in_place_index`](in_place_index.md) | 番号を選ぶ印 |
| [`std::unexpect`](unexpect.md) | `expected` の同様の印 |

## コンパイラ対応

C++17 から使えます。

## 関連ページ

- [cpprefjp: std::in_place](https://cpprefjp.github.io/reference/utility/in_place.html)
- [cppreference: std::in_place](https://en.cppreference.com/w/cpp/utility/in_place)
