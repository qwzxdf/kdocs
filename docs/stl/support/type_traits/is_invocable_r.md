---
title: std::is_invocable_r
summary: "指定した引数で呼び出せ、結果を `R` に変換できる型かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_invocable_r

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <type_traits>`
</div>

関数を呼べるだけでなく、結果が欲しい型（`double` など）に変換できるのかも、まとめて確かめたい。`std::is_invocable_r_v<R, F, Args...>` は、`F` を `Args...` で呼べて、その結果を `R` に暗黙に変換できるなら `true` です。

!!! tip "ポイント"
    - `is_invocable_r_v<R, F, Args...>` は、呼べて、結果が `R` へ暗黙に変換できるなら `true`
    - `R` が `void` なら、戻り値が何型でも `true`（結果を捨てるだけ）
    - `R` は先頭の引数（`is_invocable` とは順序が違う）
    - C++17

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_invocable_r {#is_invocable_r}

<span class="ver ver-17">C++17</span>

```cpp
template <class R, class F, class... ArgTypes>
struct is_invocable_r;

template <class R, class F, class... ArgTypes>
inline constexpr bool is_invocable_r_v = is_invocable_r<R, F, ArgTypes...>::value;
```

| 引数 | 意味 |
| --- | --- |
| `R` | 結果の変換先の型 |
| `F` | 呼び出すものの型 |
| `ArgTypes...` | 呼び出すときの引数の型 |

引数の並びが、`is_invocable` と違い、`R` が先頭になっています。`R` は「戻り値の変換先」で、`F` と引数は、そのあとです。

`R` が `void` のときは、戻り値が何型でも `true` です。戻り値を捨てるだけなので、変換を考えなくてよいからです。

`R` が `void` でなければ、結果から `R` を暗黙に変換できるかを調べます。`int` を返す関数に対して、`R = double` は `true`、`R = std::string` は `false` です。`const char*` を返す関数に対して `R = std::string` は、暗黙に変換できるので `true` です。

`std::function<R(Args...)>` に代入できるかの判定は、これと同じです。`std::function` に入れられる関数かどうかを、事前に確かめられます。

## 実際に動かしてみる

```cpp
#include <print>
#include <string>
#include <type_traits>

int GetLevel() { return 10; }
const char* GetName() { return "hero"; }

int main() {
  std::println("GetLevel -> int: {}", std::is_invocable_r_v<int, decltype(&GetLevel)>);
  std::println("GetLevel -> double: {}", std::is_invocable_r_v<double, decltype(&GetLevel)>);
  std::println("GetLevel -> string: {}", std::is_invocable_r_v<std::string, decltype(&GetLevel)>);
  std::println("GetLevel -> void (捨てる): {}", std::is_invocable_r_v<void, decltype(&GetLevel)>);
  std::println("GetName -> string: {}", std::is_invocable_r_v<std::string, decltype(&GetName)>);
}
```

```text title="実行結果"
GetLevel -> int: true
GetLevel -> double: true
GetLevel -> string: false
GetLevel -> void (捨てる): true
GetName -> string: true
```

## ゲームでの使いどころ

`std::function<double(int)>` に入れられる関数かを、あらかじめ確かめるときや、コールバックの戻り値の型を制約するテンプレートに使います。

## よくあるミス

??? failure "R と F の順序を間違える"
    `is_invocable_r_v<F, R>` のように逆に書くと、意味が変わります。`R` が先頭です。

??? failure "暗黙の変換とみなされないものを期待する"
    `explicit` なコンストラクターでしか作れない型へは、変換できません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_invocable`](is_invocable.md) | 呼べるかだけを調べる |
| [`is_nothrow_invocable_r`](is_nothrow_invocable_r.md) | 例外を投げないかも調べる |
| [`std::function`](../../utilities/function.md) | 同じ条件で代入できる |

## コンパイラ対応

C++17 から使えます。

## 関連ページ

- [cpprefjp: std::is_invocable_r](https://cpprefjp.github.io/reference/type_traits/is_invocable_r.html)
- [cppreference: std::is_invocable_r](https://en.cppreference.com/w/cpp/types/is_invocable_r)
