---
title: std::execution::seq
summary: "並列化せず、順番に実行するポリシー。"
order: 900
tags:
  - アルゴリズム
---

# std::execution::seq

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <execution>`
</div>

`std::sort(v.begin(), v.end())` に、実行ポリシーを足すと、並列化や SIMD 化をアルゴリズムに許可できます。`std::execution::seq` は、そのうち「並列にも SIMD にもしない」ポリシーで、呼び出しスレッドで、順番に実行します。ポリシーを受け取る関数に、一般の引数として渡すときの、基準の値です。

!!! tip "ポイント"
    - `std::execution::seq` は、順次実行のポリシー
    - 型は `std::execution::sequenced_policy`
    - 例外が出ても、`std::terminate` にならない（他のポリシーと違い）
    - 並列版との比較・切り替えに使う

!!! info "このページを読む前に"
    [実行ポリシー](execution.md) を先に読んでください。

## 関数の詳しい説明

### std::execution::seq {#seq}

<span class="ver ver-17">C++17</span>

```cpp
inline constexpr std::execution::sequenced_policy seq{};
```

`seq` を渡すと、ポリシーなしの呼び出しと同じように、呼び出しスレッドで実行されます。ただし、要素に対する操作の順序は、アルゴリズムごとの規定に従います（ポリシーなしと同じとは限りません）。

他の並列ポリシーとの違いは、例外の扱いです。`par` や `par_unseq` では、要素の操作が例外を投げると、`std::terminate` が呼ばれます。`seq` は、呼び出し側へ例外が伝わります。

並列化の効果を測るときに、同じコードで `seq` と `par` を切り替えて比べると便利です。

```cpp
template <class Policy>
void Run(Policy&& policy, std::vector<int>& v) {
  std::sort(std::forward<Policy>(policy), v.begin(), v.end());
}
```

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <execution>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {5, 2, 8, 1, 9, 3};
  std::sort(std::execution::seq, v.begin(), v.end());
  std::println("{}", v);

  std::println("ポリシーである: {}",
               std::is_execution_policy_v<std::execution::sequenced_policy>);
}
```

```text title="実行結果"
[1, 2, 3, 5, 8, 9]
ポリシーである: true
```

## ゲームでの使いどころ

並列化の効果を測るために、`seq` と `par` を切り替えて、同じ処理の時間を比べます。

## よくあるミス

??? failure "seq なら例外が terminate になると思う"
    `seq` は、例外が呼び出し側に伝わります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`unseq`](unseq.md) | SIMD を許可する |
| [`par_unseq`](par_unseq.md) | 並列と SIMD を許可する |
| [`is_execution_policy`](is_execution_policy.md) | ポリシーの型かを調べる |

## コンパイラ対応

C++17 から使えます。

## 関連ページ

- [cpprefjp: std::execution::seq](https://cpprefjp.github.io/reference/execution/execution_policy.html)
- [cppreference: std::execution::seq](https://en.cppreference.com/w/cpp/algorithm/execution_policy_tag)
