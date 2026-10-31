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

実行ポリシーを受け取るテンプレート関数は、引数の型が、実行ポリシーかを区別します。`std::is_execution_policy<T>` は、型 `T` が実行ポリシー（`seq`、`par`、`par_unseq`、`unseq` の型）かを、コンパイル時に調べる型特性です。

!!! tip "ポイント"
    - `is_execution_policy_v<T>` が真なら、`T` は実行ポリシー
    - 標準のポリシーの型は真、それ以外は偽
    - 自作のポリシーは、特殊化して真にする
    - 自作のアルゴリズムで、ポリシーつき版と、なし版を区別するのに使う

!!! info "このページを読む前に"
    [実行ポリシー](execution.md) を先に読んでください。

## 関数の詳しい説明

### std::is_execution_policy {#is_execution_policy}

<span class="ver ver-17">C++17</span>

```cpp
template <class T> struct is_execution_policy;
template <class T> inline constexpr bool is_execution_policy_v = is_execution_policy<T>::value;
```

標準の 4 つのポリシー（`sequenced_policy`、`parallel_policy`、`parallel_unsequenced_policy`、`unsequenced_policy`）で真です。

自作のアルゴリズムで、ポリシーを任意の引数にしたいとき、`std::enable_if_t<std::is_execution_policy_v<std::decay_t<Policy>>>` のように、制約をかけます。そうしないと、ポリシーのつもりで渡した引数が別のオーバーロードに当たり、分かりにくいエラーになります。

C++20 でコンセプトとしては、標準にはありません。`requires std::is_execution_policy_v<std::remove_cvref_t<P>>` と書きます。

## 実際に動かしてみる

```cpp
#include <execution>
#include <print>
#include <type_traits>

// ポリシーを受け取る自作の関数だけに制約をかける
template <class Policy>
  requires std::is_execution_policy_v<std::remove_cvref_t<Policy>>
const char* Describe(Policy&&) {
  return "ポリシーつき";
}

const char* Describe(int) { return "ふつうの引数"; }

int main() {
  std::println("{}", std::is_execution_policy_v<std::execution::parallel_policy>);
  std::println("{}", std::is_execution_policy_v<int>);

  std::println("{}", Describe(std::execution::par));
  std::println("{}", Describe(42));
}
```

```text title="実行結果"
true
false
ポリシーつき
ふつうの引数
```

## ゲームでの使いどころ

自作のアルゴリズムに、実行ポリシーのオーバーロードを足すときに使います。

## よくあるミス

??? failure "decay せずに型を調べる"
    参照や const が付いていると偽になります。`remove_cvref_t` を通します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`seq`](seq.md) | ポリシーの例 |
| [`par_unseq`](par_unseq.md) | ポリシーの例 |
| [`execution`](execution.md) | 実行ポリシーの概要 |

## コンパイラ対応

C++17 から使えます。

## 関連ページ

- [cpprefjp: std::is_execution_policy](https://cpprefjp.github.io/reference/execution/is_execution_policy.html)
- [cppreference: std::is_execution_policy](https://en.cppreference.com/w/cpp/algorithm/is_execution_policy)
