---
title: std::is_invocable
summary: "指定した引数で呼び出せる型かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_invocable

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <type_traits>`
</div>

テンプレートが受け取った関数 `F` を、`int` 1 つで呼べるのか、引数なしで呼べるのか。呼べない形で呼ぶとコンパイル エラーなので、呼ぶ前に調べたい。`std::is_invocable_v<F, Args...>` は、`F` を `Args...` で呼べるなら `true` を返します。関数・ラムダ・メンバー関数ポインターを、同じ書き方で調べられます。

!!! tip "ポイント"
    - `is_invocable_v<F, Args...>` は、`std::invoke(f, args...)` が書けるかを `bool` で返す
    - コンパイル時に決まるので、`if constexpr` や `static_assert` に使える
    - 呼べるかだけを見る。戻り値の型は見ない（見るなら `is_invocable_r`）
    - 型だけを見る。値は見ない

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_invocable {#is_invocable}

<span class="ver ver-17">C++17</span>

```cpp
template <class F, class... ArgTypes>
struct is_invocable;   // ::value が bool

template <class F, class... ArgTypes>
inline constexpr bool is_invocable_v = is_invocable<F, ArgTypes...>::value;
```

| 引数 | 意味 |
| --- | --- |
| `F` | 呼び出すものの型 |
| `ArgTypes...` | 呼び出すときの引数の型（左辺値は `T&`、右辺値は `T`） |

`F` が関数ポインターやラムダなら、引数の型が合うかを調べます。`std::string` を `int` の引数に渡すような、暗黙の変換ができない組み合わせでは `false` です。`int` から `double` のような、暗黙に変換できる組み合わせは `true` です。

メンバー関数ポインターなら、最初の引数がオブジェクトです。`is_invocable_v<decltype(&Player::Speed), const Player&, int>` のように書きます。

`if constexpr` と組み合わせると、渡された関数の形に応じて、呼び方を切り替えられます。受け取る関数が、`int` を取るなら `int` を渡し、取らないなら何も渡さない、という書き方です。

戻り値の型や、`noexcept` かどうかも調べたいときは、[`is_invocable_r`](is_invocable_r.md)・[`is_nothrow_invocable`](is_nothrow_invocable.md) を使います。

## 実際に動かしてみる

```cpp
#include <functional>
#include <print>
#include <string>
#include <type_traits>

int Damage(int attack) { return attack * 2; }

struct Player {
  double Speed(int level) const { return level * 1.5; }
};

// 引数を取るなら 5 を渡し、取らなければ何も渡さずに呼ぶ
template <class F>
void Visit(F f) {
  if constexpr (std::is_invocable_v<F, int>) {
    std::println("int を渡して呼ぶ");
    f(5);
  } else {
    std::println("引数なしで呼ぶ");
    f();
  }
}

int main() {
  std::println("関数に int: {}", std::is_invocable_v<decltype(&Damage), int>);
  std::println("関数に string: {}", std::is_invocable_v<decltype(&Damage), std::string>);
  std::println("引数の数が違う: {}", std::is_invocable_v<decltype(&Damage), int, int>);
  std::println("メンバー関数: {}", std::is_invocable_v<decltype(&Player::Speed), const Player&, int>);
  std::println("int は呼べない: {}", std::is_invocable_v<int, int>);

  Visit([](int x) { std::println("  x = {}", x); });
  Visit([] { std::println("  引数なし"); });
}
```

```text title="実行結果"
関数に int: true
関数に string: false
引数の数が違う: false
メンバー関数: true
int は呼べない: false
int を渡して呼ぶ
  x = 5
引数なしで呼ぶ
  引数なし
```

## ゲームでの使いどころ

コールバックを受け取るテンプレートで、「引数を取るか取らないか」に応じて、呼び方を切り替えるときに使います。コンセプトの `std::invocable` も、これと同じ判定です。

## よくあるミス

??? failure "値のカテゴリーを無視する"
    右辺値だけ受け取る関数に、左辺値の型 `T&` で調べると `false` になります。

??? failure "戻り値の型まで確かめたつもりになる"
    `is_invocable` は呼べるかだけです。戻り値の型は見ません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_invocable_r`](is_invocable_r.md) | 戻り値の型の変換先まで調べる |
| [`is_nothrow_invocable`](is_nothrow_invocable.md) | `noexcept` かを調べる |
| [`invoke_result`](invoke_result.md) | 戻り値の型を知る |

## コンパイラ対応

C++17 から使えます。

## 関連ページ

- [cpprefjp: std::is_invocable](https://cpprefjp.github.io/reference/type_traits/is_invocable.html)
- [cppreference: std::is_invocable](https://en.cppreference.com/w/cpp/types/is_invocable)
