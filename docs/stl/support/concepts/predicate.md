---
title: std::predicate
summary: "`bool` として使える結果を返す関数であることを要求するコンセプト。"
order: 7
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::predicate

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <concepts>`
</div>

`std::find_if` や `std::remove_if` に渡す条件の関数は、`bool` として使える値を返す必要があります。`std::predicate<F, Args...>` は、<strong>F を Args... で呼ぶと、`bool` として使える値が返るか</strong>を要求するコンセプトです。

!!! tip "ポイント"
    - `std::predicate<F, Args...>`: 呼べて、結果が `bool` として使える
    - `find_if` などの「条件」を受け取る引数の制約
    - 戻り値が `bool` そのものでなくても、`bool` に変換できればよい
    - 文字列のように `bool` にできない戻り値は、満たさない

!!! info "このページを読む前に"
    [テンプレートの基本](../../../basics/template.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::predicate {#predicate}

<span class="ver ver-20">C++20</span>

```cpp
template <class F, class... Args>
concept predicate = regular_invocable<F, Args...> &&
    boolean-testable<invoke_result_t<F, Args...>>;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `F` | 型 | 呼び出す対象の型 |
| `Args...` | 型の並び | 渡す引数の型 |

`regular_invocable` の条件に加えて、戻り値が条件式で使える（`bool` に変換できる）ことを要求します。`bool` を返すラムダは満たします。`int` を返すラムダも、`bool` に変換できるので満たします。`std::string` を返すラムダは、`bool` に変換できないので満たしません。

## 実際に動かしてみる

```cpp
#include <concepts>
#include <print>
#include <string>

int main() {
  auto is_even = [](int x) { return x % 2 == 0; };
  auto name = [](int) { return std::string{}; };
  std::println("bool を返す      : {}", std::predicate<decltype(is_even), int>);
  std::println("string を返す    : {}", std::predicate<decltype(name), int>);
}
```

```text title="実行結果"
bool を返す      : true
string を返す    : false
```

## ゲームでの使いどころ

条件の関数を受け取る自作のアルゴリズムで使います。

```cpp
template <class It, std::predicate<std::iter_reference_t<It>> Pred>
It FindFirst(It first, It last, Pred pred);
```

## よくあるミス

??? failure "戻り値が `int` でも満たすことに驚く"
    `bool` に変換できれば満たします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`invocable`](invocable.md) | 戻り値の型は問わない |
| [`relation`](relation.md) | 2 つの引数を比べる述語 |

## コンパイラ対応

C++20 の機能です。GCC 10 以降、Clang 10 以降、Visual Studio 2019 16.3 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `predicate<F, Args...>` は F を呼ぶと `bool` として使える値が返るか
    - [x] `find_if` などの条件の関数の制約
    - [x] 戻り値が `bool` に変換できなければ満たさない

## 関連ページ

- [cpprefjp: std::predicate](https://cpprefjp.github.io/reference/concepts/predicate.html)
- [cppreference: std::predicate](https://en.cppreference.com/w/cpp/concepts/predicate)
