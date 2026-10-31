---
title: std::execution::par_unseq
summary: "複数のスレッドで、しかもベクトル化も許して実行するポリシー。"
order: 900
tags:
  - アルゴリズム
---

# std::execution::par_unseq

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <execution>`
</div>

`std::execution::par_unseq` は、「複数のスレッドで並列に、さらに各スレッドの中で SIMD も使ってよい」と許可する、最も自由度の高い実行ポリシーです。大量のデータの変換や集計を、最大限に速くしたいときに使います。ただし、要素の処理に課される制約が、最も厳しいポリシーです。

!!! tip "ポイント"
    - 並列と SIMD の両方を許可する
    - 型は `std::execution::parallel_unsequenced_policy`
    - 要素の処理は、ロックや同期を伴ってはいけない
    - 例外を投げると `std::terminate`

!!! info "このページを読む前に"
    [実行ポリシー](execution.md) を先に読んでください。

## 関数の詳しい説明

### std::execution::par_unseq {#par_unseq}

<span class="ver ver-17">C++17</span>

```cpp
inline constexpr std::execution::parallel_unsequenced_policy par_unseq{};
```

`par`（並列のみ）では、要素の処理で、ロックを取れます。`par_unseq` では、SIMD で混ざって実行されるので、ロックを取ると、同じスレッドが 2 回ロックを取るような状態になり、デッドロックします。

使える条件は、次のとおりです。

- 要素の処理が、他の要素の処理に依存しない
- 共有データの書き込みは、`std::atomic` など、ロックなしの操作に限る
- 例外を投げない

要素数が少ないと、スレッドの管理のコストが、並列化の利益を上回ります。数万要素以上から、効果が出るのが目安です。

MSVC では、並列実行にスレッド プールを使います。GCC では、Intel の TBB ライブラリが必要です。

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <execution>
#include <numeric>
#include <print>
#include <vector>

int main() {
  std::vector<int> v(100000);
  std::iota(v.begin(), v.end(), 1);

  // 並列に 2 倍する
  std::vector<int> doubled(v.size());
  std::transform(std::execution::par_unseq, v.begin(), v.end(), doubled.begin(),
                 [](int x) { return x * 2; });

  // 並列に合計する
  const long long sum = std::reduce(std::execution::par_unseq, doubled.begin(), doubled.end(), 0LL);
  std::println("{}", sum);
}
```

```text title="実行結果"
10000100000
```

## ゲームでの使いどころ

ミップマップの生成、大量のパーティクルの更新など、独立な要素の大量処理で使います。

## よくあるミス

??? failure "要素の処理でミューテックスを取る"
    デッドロックします。

??? failure "少ない要素に使う"
    スレッドのコストで、かえって遅くなります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`seq`](seq.md) | 順次実行 |
| [`unseq`](unseq.md) | SIMD のみ |
| [`reduce`](reduce.md) | 並列に合計する |

## コンパイラ対応

C++17 から使えます。

## 関連ページ

- [cpprefjp: std::execution::par_unseq](https://cpprefjp.github.io/reference/execution/execution_policy.html)
- [cppreference: std::execution::par_unseq](https://en.cppreference.com/w/cpp/algorithm/execution_policy_tag)
