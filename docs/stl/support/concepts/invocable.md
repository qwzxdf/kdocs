---
title: std::invocable
summary: "指定した引数で呼び出せることを要求するコンセプト。"
order: 6
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::invocable

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <concepts>`
</div>

コールバックを受け取る関数で、渡された関数やラムダが期待する引数で呼べるかを調べたい。`std::invocable<F, Args...>` は、<strong>F を Args... で呼び出せるか</strong>を要求するコンセプトです。

!!! tip "ポイント"
    - `std::invocable<F, Args...>`: `F` を `Args...` で呼び出せるか
    - 関数、ラムダ、関数オブジェクト、メンバー関数ポインターを受け付ける
    - 戻り値の型は問わない（問うなら `std::predicate` や `std::convertible_to`）
    - `std::is_invocable` のコンセプト版

!!! info "このページを読む前に"
    [テンプレートの基本](../../../basics/template.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::invocable {#invocable}

<span class="ver ver-20">C++20</span>

```cpp
template <class F, class... Args>
concept invocable = requires(F&& f, Args&&... args) {
  std::invoke(std::forward<F>(f), std::forward<Args>(args)...);
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `F` | 型 | 呼び出す対象の型 |
| `Args...` | 型の並び | 渡す引数の型 |

`std::invoke(f, args...)` が書ければ満たします。引数の数や型が合わなければ満たしません。ラムダの型は `decltype(lambda)` で取ります。

コールバックの型を `template <std::invocable<int> F>` のように制限しておくと、合わない関数を渡したときに、呼び出しの場所で分かりやすいエラーになります。

## 実際に動かしてみる

```cpp
#include <concepts>
#include <print>
#include <string>

int main() {
  auto twice = [](int x) { return x * 2; };
  std::println("twice を int で  : {}", std::invocable<decltype(twice), int>);
  std::println("twice を引数なしで: {}", std::invocable<decltype(twice)>);
  std::println("twice を文字列で : {}", std::invocable<decltype(twice), std::string>);
}
```

```text title="実行結果"
twice を int で  : true
twice を引数なしで: false
twice を文字列で : false
```

## ゲームでの使いどころ

コールバックを受け取る関数の引数を制限します。

```cpp
template <std::invocable<Enemy&> F>
void ForEachEnemy(F&& callback) {
  for (auto& e : enemies) callback(e);
}
```

## よくあるミス

??? failure "ラムダを型でなく値として渡す"
    `decltype(lambda)` で型を取ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`regular_invocable`](regular_invocable.md) | 同じ入力で同じ結果を返すこと（意味上の要求） |
| [`predicate`](predicate.md) | `bool` を返す |
| [`is_invocable`](../type_traits/is_invocable.md) | 型特性版 |

## コンパイラ対応

C++20 の機能です。GCC 10 以降、Clang 10 以降、Visual Studio 2019 16.3 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `invocable<F, Args...>` は F を Args... で呼べるか
    - [x] ラムダや関数オブジェクトに使える
    - [x] コールバックの型の制限に使う

## 関連ページ

- [cpprefjp: std::invocable](https://cpprefjp.github.io/reference/concepts/invocable.html)
- [cppreference: std::invocable](https://en.cppreference.com/w/cpp/concepts/invocable)
