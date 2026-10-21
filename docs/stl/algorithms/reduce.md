---
title: std::reduce
summary: "要素を合計などにまとめる。順序を問わないので、並列に実行できる。"
order: 25
tags:
  - アルゴリズム
---

# std::reduce

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <numeric>`
</div>

`std::reduce` は、**範囲の要素を 1 つの値にまとめる**関数で、`accumulate` と似ていますが、**足し込む順序を決めません**。そのため並列に実行でき、大きな範囲の合計が速く求まります。実行ポリシー（`std::execution::par`）を渡すと並列になります。

!!! tip "ポイント"
    - 関数は**交換法則と結合法則**を満たす必要がある（足し算、掛け算、最大値）。引き算や文字列の連結には使えない。
    - `double` の合計は、足す順序で誤差が変わるので、`accumulate` と結果が少しずれることがある。
    - 小さな範囲では並列化のオーバーヘッドのほうが大きい。数万要素以上で効果が出る。

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::reduce <span class="ver ver-17">C++17</span> {#reduce data-toc-label="std::reduce"}

```cpp
template <class InputIt, class T>
T reduce(InputIt first, InputIt last, T init);
template <class ExecutionPolicy, class ForwardIt, class T>
T reduce(ExecutionPolicy&& policy, ForwardIt first, ForwardIt last, T init);
```

- `accumulate` と似ていますが、**計算の順番を問わない**ので、`std::execution::par` を渡すと並列で計算できます
- 足し算のように順番を入れ替えても結果が同じ計算にしか使えません

<div class="anim" data-label="std::reduce(v.begin(), v.end(), 0)">
1 2 3 4 # 初期値 0
*1 *2 3 4 # (1 + 2) と
1 2 *3 *4 # (3 + 4) を別々に計算してもよい
*1 *2 *3 *4 # 最後に合わせて 10。順番は保証されない
</div>

```cpp
#include <numeric>
#include <print>
#include <vector>

int main() {
  std::vector<int> v(1000, 1);
  std::println("{}", std::reduce(v.begin(), v.end(), 0));
}
```

```text title="実行結果"
1000
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 数十万個のパーティクルの合計エネルギー | `reduce(std::execution::par, energies.begin(), energies.end(), 0.0f)` |
| 巨大な配列の合計 | `reduce(v.begin(), v.end())` |

## よくあるミス

??? failure "順序に依存する関数を渡す"
    引き算や文字列の連結のように順序で結果が変わる関数を渡すと、実行のたびに結果が変わります。順序が大事なら `accumulate` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::accumulate`](accumulate.md) | 先頭から順番に足し込む |
| [`std::transform_reduce`](transform_reduce.md) | 変換してから合計する |
| [実行ポリシー](execution.md) | 並列に実行する指定 |

## コンパイラ対応

C++17 の機能です。並列版（実行ポリシー）は、GCC では TBB が必要です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 順序を問わない合計
    - [x] 並列にできる
    - [x] 関数は交換法則・結合法則を満たすこと

## 関連ページ

- [cpprefjp: std::reduce](https://cpprefjp.github.io/reference/numeric/reduce.html)
- [cppreference: std::reduce](https://en.cppreference.com/w/cpp/algorithm/reduce)
