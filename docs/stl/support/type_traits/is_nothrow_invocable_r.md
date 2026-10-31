---
title: std::is_nothrow_invocable_r
summary: "指定した引数で例外を投げずに呼び出せ、結果を R に変換できるかを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_nothrow_invocable_r

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <type_traits>`
</div>

呼び出しが `noexcept` なだけでは足りないことがあります。戻り値を別の型に変換するとき、その変換が例外を投げるかもしれないからです。`std::is_nothrow_invocable_r_v<R, F, Args...>` は、`F` を `Args...` で呼べて、その呼び出しも、結果の `R` への変換も `noexcept` なら `true` です。

!!! tip "ポイント"
    - `is_nothrow_invocable_r_v<R, F, Args...>` は、呼び出しと変換の両方が `noexcept` なら `true`
    - `R` が `void` なら、変換が無いので呼び出しだけを見る
    - `std::string` のような、確保で例外を投げうる型への変換は `false` になりやすい
    - C++17

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_nothrow_invocable_r {#is_nothrow_invocable_r}

<span class="ver ver-17">C++17</span>

```cpp
template <class R, class F, class... ArgTypes>
struct is_nothrow_invocable_r;

template <class R, class F, class... ArgTypes>
inline constexpr bool is_nothrow_invocable_r_v = is_nothrow_invocable_r<R, F, ArgTypes...>::value;
```

引数は [`is_invocable_r`](is_invocable_r.md) と同じで、`R` が先頭です。

`true` になる条件は 2 つあります。1 つは、`F` の呼び出し自体が `noexcept` であること。もう 1 つは、戻り値から `R` への暗黙の変換が `noexcept` であることです。

数値の変換（`int` から `double` など）は例外を投げないので、呼び出しが `noexcept` なら `true` です。一方、`const char*` から `std::string` への変換は、メモリの確保が必要で、例外を投げうるので `noexcept` ではありません。関数が `noexcept` でも、結果は `false` です。

`R` が `void` のときは、戻り値を捨てるだけなので、呼び出しだけを見ます。

## 実際に動かしてみる

```cpp
#include <print>
#include <string>
#include <type_traits>

int Level() noexcept { return 10; }
int LevelRisky() { return 10; }          // noexcept ではない
const char* Name() noexcept { return "hero"; }

int main() {
  std::println("Level -> double: {}", std::is_nothrow_invocable_r_v<double, decltype(&Level)>);
  std::println("LevelRisky -> double: {}", std::is_nothrow_invocable_r_v<double, decltype(&LevelRisky)>);

  // Name は noexcept でも、string への変換は確保で例外を投げうる
  std::println("Name -> string (呼べる): {}", std::is_invocable_r_v<std::string, decltype(&Name)>);
  std::println("Name -> string (noexcept): {}", std::is_nothrow_invocable_r_v<std::string, decltype(&Name)>);

  // R が void なら、変換が無いので呼び出しだけを見る
  std::println("Level -> void: {}", std::is_nothrow_invocable_r_v<void, decltype(&Level)>);
}
```

```text title="実行結果"
Level -> double: true
LevelRisky -> double: false
Name -> string (呼べる): true
Name -> string (noexcept): false
Level -> void: true
```

## ゲームでの使いどころ

`noexcept` な戻り値の変換までを要求する、細かい制約をテンプレートに付けたいときに使います。ふつうのゲーム コードでは、使う場面は稀です。

## よくあるミス

??? failure "関数が noexcept なら全体も noexcept と思い込む"
    戻り値の変換が例外を投げうるなら、`false` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_invocable_r`](is_invocable_r.md) | 例外は考えない版 |
| [`is_nothrow_invocable`](is_nothrow_invocable.md) | 変換を見ない版 |
| [`is_nothrow_convertible`](is_nothrow_convertible.md) | 変換だけの判定 |

## コンパイラ対応

C++17 から使えます。

## 関連ページ

- [cpprefjp: std::is_nothrow_invocable_r](https://cpprefjp.github.io/reference/type_traits/is_nothrow_invocable_r.html)
- [cppreference: std::is_nothrow_invocable_r](https://en.cppreference.com/w/cpp/types/is_nothrow_invocable_r)
