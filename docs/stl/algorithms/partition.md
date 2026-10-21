---
title: std::ranges::partition
summary: "条件に合う要素を前、合わない要素を後ろに分ける（並びを入れ替える）。"
order: 46
tags:
  - アルゴリズム
---

# std::ranges::partition

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`std::ranges::partition` は、**条件に合う要素を前に、合わない要素を後ろに**並べ替えるアルゴリズムです。全体を整列する必要はなく、「2 つのグループに分ける」だけなので、`sort` より速く済みます。戻り値は、後ろのグループの先頭を指す範囲です。

!!! tip "ポイント"
    - **元の順序は保たれない**。順序を保ちたいなら [`stable_partition`](stable_partition.md)。
    - 分けたあとの前半・後半は、それぞれ別のループで処理できる。
    - 計算量は O(n)。

!!! info "このページを読む前に"
    [ラムダ式](../../basics/lambda.md)、[イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::ranges::partition {#partition}

```cpp
template <forward_range R, class Proj = identity, class Pred>
constexpr borrowed_subrange_t<R> partition(R&& r, Pred pred, Proj proj = {});
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `r` | 範囲 | 対象 |
| `pred` | 関数 | **前に集めたいもの**で `true` |
| `proj` | プロジェクション | `pred` に渡す前の変換 |

- 戻り値: 条件に**合わない**グループの範囲（`.begin()` が分かれ目）
- 同じグループの中の順番は保たれません

<div class="mem">
<div class="mem-step"><span class="mem-label">前</span><span class="mem-cells"><span class="gone">×</span><span class="move">○</span><span class="gone">×</span><span class="move">○</span><span class="move">○</span></span><span class="mem-note">○ が条件に合う要素</span></div>
<div class="mem-step"><span class="mem-label">partition 後</span><span class="mem-cells"><span class="move">○</span><span class="move">○</span><span class="move">○</span><span class="gone">×</span><span class="gone">×</span></span><span class="mem-note">戻り値の begin() は 4 つ目（最初の ×）</span></div>
</div>

<div class="anim" data-label="std::partition(b, e, is_even)">
1 2 3 4 5 6 # v
1 *2 3 *4 5 *6 # 条件に合うものを前へ集める
>2 >4 >6 >1 >5 >3 # 合う側と合わない側に分かれる（順番は保証されない）
</div>

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3, 4, 5, 6};
  auto rest = std::ranges::partition(v, [](int x) { return x % 2 == 0; });  // 偶数を前に集める
  std::println("前半(偶数)の個数 {}", rest.begin() - v.begin());
}
```

```text title="実行結果"
前半(偶数)の個数 3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 生きている敵を前に、死んだ敵を後ろに寄せる | `partition(enemies, 生きている)` |
| 画面内のオブジェクトを前にまとめる | `partition(objects, 画面内)` |

## よくあるミス

??? failure "前半の個数を、戻り値を使わずに数え直す"
    戻り値の範囲の `begin()` が境目です。`count_if` で数え直さなくても `p.begin() - v.begin()` が前半の個数です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::stable_partition`](stable_partition.md) | 元の順序を保つ |
| [`std::ranges::partition_copy`](partition_copy.md) | 元を残して 2 つに振り分ける |
| [`std::ranges::sort`](sort.md) | 全体を整列する |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 条件に合う順に前へ集める
    - [x] 順序は保たれない
    - [x] 戻り値が境目

## 関連ページ

- [cpprefjp: std::ranges::partition](https://cpprefjp.github.io/reference/algorithm/ranges_partition.html)
- [cppreference: std::ranges::partition](https://en.cppreference.com/w/cpp/algorithm/ranges/partition)
