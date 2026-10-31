---
title: std::execution::unseq
summary: "1 つのスレッドの中で、ベクトル化（SIMD）を許して実行するポリシー。"
order: 900
tags:
  - アルゴリズム
---

# std::execution::unseq

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <execution>`
</div>

`std::execution::unseq`（C++20）は、「1 つのスレッドの中で、SIMD によるベクトル化をしてよい」と許可する実行ポリシーです。複数のスレッドは使いません。ループの複数の反復が、交互に混ざって実行されるかもしれないので、反復どうしが、お互いに依存しない処理だけに使います。

!!! tip "ポイント"
    - 1 つのスレッドの中で、ベクトル化（SIMD）を許可する
    - 型は `std::execution::unsequenced_policy`
    - 要素の処理は、混ざって実行されうる。反復どうしを独立にする
    - 複数スレッドも許可するなら `par_unseq`

!!! info "このページを読む前に"
    [実行ポリシー](execution.md) を先に読んでください。

## 関数の詳しい説明

### std::execution::unseq {#unseq}

<span class="ver ver-20">C++20</span>

```cpp
inline constexpr std::execution::unsequenced_policy unseq{};
```

SIMD では、複数の要素が 1 つの命令で同時に処理されます。そのため、1 つの要素の処理の途中に、別の要素の処理が割り込みます。要素の処理が、ロックを取る、共有の変数を書く、といった動作をすると、混ざって実行されたときに破綻します。

そのため、要素に対する操作は、ミューテックスの取得や、同期を伴う操作を含んではいけません。例外を投げると、`std::terminate` です。

効果は、処理の中身とコンパイラ次第です。単純な算術の変換（`transform`）では大きく、複雑な分岐を含むと、小さくなります。

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <execution>
#include <print>
#include <vector>

int main() {
  std::vector<float> in(1000, 2.0f);
  std::vector<float> out(in.size());

  // 反復どうしが独立な処理に、unseq を許可する
  std::transform(std::execution::unseq, in.begin(), in.end(), out.begin(),
                 [](float x) { return x * x; });

  std::println("{} {}", out.front(), out.back());
}
```

```text title="実行結果"
4 4
```

## ゲームでの使いどころ

大量の要素への単純な算術演算で、SIMD を明示的に許可するときに使います。

## よくあるミス

??? failure "要素の処理でロックを取る"
    混ざって実行されて、破綻します。

??? failure "反復どうしが依存している"
    結果が不定になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`seq`](seq.md) | 順次実行 |
| [`par_unseq`](par_unseq.md) | 並列と SIMD |
| [`execution`](execution.md) | 実行ポリシーの概要 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::execution::unseq](https://cpprefjp.github.io/reference/execution/execution_policy.html)
- [cppreference: std::execution::unseq](https://en.cppreference.com/w/cpp/algorithm/execution_policy_tag)
