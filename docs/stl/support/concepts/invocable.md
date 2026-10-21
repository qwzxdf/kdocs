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

`std::invocable<F, Args...>` は、**関数 `F` が、引数 `Args...` で呼び出せること**を要求するコンセプトです。コールバックを受け取るテンプレートの制約に使います。戻り値が `bool` であることまで要求するのは [`predicate`](predicate.md) です。

!!! tip "ポイント"
    - `template <std::invocable<int> F>` は「int を受け取って呼べる関数」。
    - ラムダ式、関数ポインター、`std::function` に使える。

!!! info "このページを読む前に"
    [テンプレートとコンセプト](../../../basics/template.md) の基本が前提です。

## 関数の詳しい説明

### std::invocable {#invocable}

```cpp
template <class T>
concept invocable = /* 条件 */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | テンプレート引数 | 調べる型 |

- 戻り値: 条件を満たせば `true`（コンパイル時の定数）
- 計算量: コンパイル時

```cpp
#include <concepts>
#include <print>
#include <string>

int main() {
  auto f = [](int x) { return x * 2; };
  std::println("{} {}", std::invocable<decltype(f), int>, std::invocable<decltype(f), std::string>);
}
```

```text title="実行結果"
true false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| コールバックを受け取る関数テンプレート | `template <std::invocable<Enemy&> F> void ForEachEnemy(F f)` |

## よくあるミス

??? failure "戻り値の型まで確認しない"
    戻り値も条件にするなら `std::regular_invocable` や `predicate` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`predicate`](predicate.md) | 戻り値が bool |
| [`invoke`](../functional/invoke.md) | 呼び出す関数 |

## コンパイラ対応

C++20 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 呼び出せることを要求
    - [x] コールバックの制約に
    - [x] 戻り値は別の条件

## 関連ページ

- [cpprefjp: std::invocable](https://cpprefjp.github.io/reference/concepts/invocable.html)
- [cppreference: std::invocable](https://en.cppreference.com/w/cpp/concepts/invocable)
