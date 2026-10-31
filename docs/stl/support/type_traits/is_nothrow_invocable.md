---
title: std::is_nothrow_invocable
summary: "指定した引数で、例外を投げずに呼び出せるかを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_nothrow_invocable

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <type_traits>`
</div>

関数を呼ぶ処理を `noexcept` にしたい。ただし、呼ぶ関数が例外を投げうるのに `noexcept` と書くと、投げられた瞬間に `std::terminate` で落ちます。`std::is_nothrow_invocable_v<F, Args...>` は、`F` を `Args...` で呼べて、しかもその呼び出しが `noexcept` なら `true` です。

!!! tip "ポイント"
    - `is_nothrow_invocable_v<F, Args...>` は、呼べて、`noexcept` な呼び出しなら `true`
    - 呼べない場合は `false`（`noexcept` ではない扱い）
    - 条件つき `noexcept`（`noexcept(...)` の中）に使うのが典型
    - C++17

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_nothrow_invocable {#is_nothrow_invocable}

<span class="ver ver-17">C++17</span>

```cpp
template <class F, class... ArgTypes>
struct is_nothrow_invocable;

template <class F, class... ArgTypes>
inline constexpr bool is_nothrow_invocable_v = is_nothrow_invocable<F, ArgTypes...>::value;
```

引数は [`is_invocable`](is_invocable.md) と同じです。呼べるかに加えて、呼び出しの式が `noexcept` であることを要求します。

`noexcept` は、C++17 から関数の型の一部になりました。`int Safe(int) noexcept` の型は `int(*)(int) noexcept` で、この判定が `true` になります。`noexcept` のないラムダや関数は `false` です。

最もよく使う場所は、ラッパー関数の条件つき `noexcept` です。

```cpp
template <class F>
void Call(F f) noexcept(std::is_nothrow_invocable_v<F, int>) { f(1); }
```

受け取る `F` が `noexcept` ならラッパーも `noexcept`、そうでなければ、ラッパーは例外を通します。標準ライブラリの `std::invoke` なども、この形で書かれています。

`noexcept` は、実行時に例外を禁止するのではなく、「例外が飛ぶなら `terminate` する」という約束です。この判定は、宣言の `noexcept` を見るだけで、関数の中で例外を投げないかの検証はしません。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int Safe(int x) noexcept { return x + 1; }
int Risky(int x) { return x + 1; }   // noexcept と書いていない

// F が noexcept なら、この関数も noexcept
template <class F>
void Call(F f) noexcept(std::is_nothrow_invocable_v<F, int>) {
  f(1);
}

int main() {
  auto lambda_safe = [](int x) noexcept { return x; };
  auto lambda_risky = [](int x) { return x; };

  std::println("Safe: {}", std::is_nothrow_invocable_v<decltype(&Safe), int>);
  std::println("Risky: {}", std::is_nothrow_invocable_v<decltype(&Risky), int>);
  std::println("noexcept ラムダ: {}", std::is_nothrow_invocable_v<decltype(lambda_safe), int>);
  std::println("通常のラムダ: {}", std::is_nothrow_invocable_v<decltype(lambda_risky), int>);
  std::println("呼べない: {}", std::is_nothrow_invocable_v<int, int>);

  std::println("Call(Safe) は noexcept: {}", noexcept(Call(Safe)));
  std::println("Call(Risky) は noexcept: {}", noexcept(Call(Risky)));
}
```

```text title="実行結果"
Safe: true
Risky: false
noexcept ラムダ: true
通常のラムダ: false
呼べない: false
Call(Safe) は noexcept: true
Call(Risky) は noexcept: false
```

## ゲームでの使いどころ

渡されたコールバックの `noexcept` に応じて、自作のラッパーの `noexcept` を決めるときに使います。例外を許さないゲームのメインループでは、`noexcept` を型で表すと、コンパイラが最適化しやすくなります。

## よくあるミス

??? failure "noexcept を信じすぎる"
    宣言を見るだけです。中で例外を投げる `noexcept` 関数は、`terminate` します。

??? failure "呼べないものを true と思い込む"
    呼べない場合は `false` です。呼べるかは、別に確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_invocable`](is_invocable.md) | 呼べるかだけを調べる |
| [`is_nothrow_invocable_r`](is_nothrow_invocable_r.md) | 戻り値の変換も `noexcept` か調べる |
| [`invoke`](../functional/invoke.md) | 実際に呼ぶ関数 |

## コンパイラ対応

C++17 から使えます。

## 関連ページ

- [cpprefjp: std::is_nothrow_invocable](https://cpprefjp.github.io/reference/type_traits/is_nothrow_invocable.html)
- [cppreference: std::is_nothrow_invocable](https://en.cppreference.com/w/cpp/types/is_nothrow_invocable)
