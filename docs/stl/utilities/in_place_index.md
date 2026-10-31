---
title: std::in_place_index
summary: "variant に、番号を指定してその場で作らせる目印。"
order: 900
tags:
  - ユーティリティ
---

# std::in_place_index

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <utility>`
</div>

`std::variant<int, int>` のように、同じ型が複数ある `variant` では、型で選択肢を選べません。何番目の選択肢で作るかを、番号で伝える印が `std::in_place_index<I>` です。型が重複しない場合にも、使えます。

!!! tip "ポイント"
    - `variant` のコンストラクターで、番号を選んで、引数から直接作る
    - 番号は 0 始まり
    - 同じ型が複数ある `variant` では、これが唯一の選び方
    - C++17

!!! info "このページを読む前に"
    [`std::in_place_type`](in_place_type.md) を先に読んでください。

## 関数の詳しい説明

### std::in_place_index {#in_place_index}

<span class="ver ver-17">C++17</span>

```cpp
template <std::size_t I> struct in_place_index_t { explicit in_place_index_t() = default; };
template <std::size_t I> inline constexpr std::in_place_index_t<I> in_place_index{};
```

```cpp
std::variant<int, int> v(std::in_place_index<1>, 5);   // 2 つ目の int に 5
```

`I` が選択肢の個数以上なら、コンパイル エラーです。選択肢の個数は、[`variant_size_v`](variant_size.md) です。

`variant::emplace<I>(引数...)` も、番号で作り直す形があります。

型の重複があるときの番号の割り当ては、位置で決まります。`variant<int, int>` なら、番号 0 と 1 は、どちらも `int` ですが、別の選択肢として区別されます。`index()` で、どちらを持っているかが分かります。

## 実際に動かしてみる

```cpp
#include <print>
#include <string>
#include <variant>

int main() {
  // 同じ型が 2 回ある variant
  std::variant<int, int> v(std::in_place_index<1>, 5);
  std::println("番号 {} 値 {}", v.index(), std::get<1>(v));

  // 型が違う場合でも、番号で選べる
  std::variant<int, std::string> w(std::in_place_index<1>, 3, 'x');
  std::println("番号 {} 値 {}", w.index(), std::get<1>(w));

  // 作り直し
  w.emplace<0>(9);
  std::println("番号 {} 値 {}", w.index(), std::get<0>(w));
}
```

```text title="実行結果"
番号 1 値 5
番号 1 値 xxx
番号 0 値 9
```

## ゲームでの使いどころ

同じ型を意味の違う選択肢として持つ `variant`（たとえば、`variant<Pos, Pos>` で「開始」と「終了」）に使いますが、意味の違いは、名前の付いた型で表すほうが分かりやすくなります。

## よくあるミス

??? failure "番号が範囲外"
    `variant_size_v` 以上の番号は、コンパイル エラーです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`in_place_type`](in_place_type.md) | 型で選ぶ |
| [`in_place`](in_place.md) | `optional` 用 |
| [`std::variant_size`](variant_size.md) | 選択肢の個数 |

## コンパイラ対応

C++17 から使えます。

## 関連ページ

- [cpprefjp: std::in_place_index](https://cpprefjp.github.io/reference/utility/in_place_index_t.html)
- [cppreference: std::in_place_index](https://en.cppreference.com/w/cpp/utility/in_place)
