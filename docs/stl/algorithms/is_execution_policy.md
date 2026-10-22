---
title: std::is_execution_policy
summary: "型が実行ポリシーかを調べる型特性。"
order: 900
tags:
  - アルゴリズム
---

# std::is_execution_policy

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <execution>`
</div>

ジェネリックな関数で、第 1 引数がポリシーかそうでないかを区別したいことがあります。`is_execution_policy_v<T>` は、`T` が `seq`・`par`・`par_unseq`・`unseq` の型なら `true` です。

!!! tip "ポイント"
    - `_v` 版で `bool` が取れる。
    - ポリシーつきとなしのオーバーロードを書き分けるときに使う。
    - 型に `const` や参照がついていない形（`remove_cvref_t`）で調べる。

!!! info "このページを読む前に"
    [実行ポリシー](execution.md) を先に読んでください。

## 関数の詳しい説明

### std::is_execution_policy {#is_execution_policy}

```cpp
template <class T>
struct is_execution_policy;
template <class T>
inline constexpr bool is_execution_policy_v = is_execution_policy<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べる型 |

- 戻り値: 実行ポリシーなら `true`
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <execution>
#include <print>
#include <type_traits>

int main() {
  using Par = std::remove_cvref_t<decltype(std::execution::par)>;
  std::println("{}", std::is_execution_policy_v<Par>);
  std::println("{}", std::is_execution_policy_v<int>);
}
```

```text title="実行結果"
true
false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ポリシーを受け取るテンプレートを制約する | `std::enable_if_t<std::is_execution_policy_v<std::decay_t<P>>>` |

## よくあるミス

??? failure "参照つきの型を渡す"
    `const auto&` のままだと `false` です。`std::remove_cvref_t` で外してから調べます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`execution`](execution.md) | 実行ポリシー |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 実行ポリシーかを調べる型特性
    - [x] _v 版で bool
    - [x] 参照を外してから調べる

## 関連ページ

- [cpprefjp: std::is_execution_policy](https://cpprefjp.github.io/reference/execution/is_execution_policy.html)
- [cppreference: std::is_execution_policy](https://en.cppreference.com/w/cpp/algorithm/is_execution_policy)
