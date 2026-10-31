---
title: std::monostate
summary: "何も入っていない状態を表す、空の型。variant の先頭に置く。"
order: 58
tags:
  - ユーティリティ
---

# std::monostate

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <variant>`
</div>

`std::variant<A, B>` は、既定では、最初の型 `A` を既定の構築で作ります。`A` が既定のコンストラクターを持たないと、`variant` も既定の構築ができません。そこで、最初の選択肢に、何も持たない空の型 `std::monostate` を置くと、「まだ何も入っていない」状態を、明示的に表せます。

!!! tip "ポイント"
    - `std::monostate` は、状態を持たない空の型
    - `variant<monostate, A, B>` で、`variant` を既定の構築できるようにする
    - 「まだ値がない」を表す。`optional` 的な使い方
    - 比較は常に等しい。ハッシュも決まった値

!!! info "このページを読む前に"
    [`std::variant`](variant.md) と [`std::variant_npos`](variant_npos.md) を先に読んでください。

## 関数の詳しい説明

### std::monostate {#monostate}

<span class="ver ver-17">C++17</span>

```cpp
struct monostate {};
constexpr bool operator==(monostate, monostate) noexcept { return true; }
// <=>、std::hash も用意されている
```

`monostate` のオブジェクトは、すべて等しいものとして比較されます。大小の比較では、どれも等しいので、`<`、`>` は偽、`<=`、`>=` は真です。

`std::variant<std::monostate, std::string>` は、既定の構築で `monostate` を持ちます。あとで文字列を代入できます。

```cpp
std::variant<std::monostate, std::string> v;     // monostate が入った状態
v = std::string("Hero");                         // 文字列に切り替わる
```

`monostate` を選択肢に置くのと、`std::optional<std::variant<A, B>>` を使うのは、似た働きですが、`monostate` のほうが、1 つの型で済みます。

「値がない」を明示する別の方法として、`variant_npos`（valueless）がありますが、これは例外が飛んだあとの異常な状態です。通常の「空」には、`monostate` を使います。

## 実際に動かしてみる

```cpp
#include <print>
#include <string>
#include <variant>

// 既定のコンストラクターを持たない型
struct Weapon {
  explicit Weapon(int power) : power(power) {}
  int power;
};

int main() {
  // monostate がないと、既定の構築ができない
  std::variant<std::monostate, Weapon, std::string> v;
  std::println("最初は monostate: {}", std::holds_alternative<std::monostate>(v));

  v = Weapon{10};
  std::println("武器: {}", std::get<Weapon>(v).power);

  v = std::string("Hero");
  std::println("文字列: {}", std::get<std::string>(v));

  // monostate どうしは常に等しい
  std::println("等しい: {}", std::monostate{} == std::monostate{});
}
```

```text title="実行結果"
最初は monostate: true
武器: 10
文字列: Hero
等しい: true
```

## ゲームでの使いどころ

装備スロットのように、「何も装備していない」状態も含めた、複数の型を持つ値を作るときに使います。

## よくあるミス

??? failure "monostate を最初に置かない"
    既定の構築は、最初の型で行われます。空にしたいなら、`monostate` を先頭に置きます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::optional`](optional.md) | 値が 1 種類で、空かもしれない |
| [`std::variant`](variant.md) | 複数の型のうち 1 つ |
| [`std::variant_npos`](variant_npos.md) | 異常な空の状態 |

## コンパイラ対応

C++17 から使えます。

## 関連ページ

- [cpprefjp: std::monostate](https://cpprefjp.github.io/reference/variant/monostate.html)
- [cppreference: std::monostate](https://en.cppreference.com/w/cpp/utility/variant/monostate)
