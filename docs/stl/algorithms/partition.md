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

生きている敵と死んでいる敵を配列の前と後ろに分けたい。全体を整列するほどではなく、2 つのグループに分けるだけです。`std::ranges::partition` は、条件に合う要素を前に合わない要素を後ろに並べ替えます。`sort` より速く済み、計算量は O(n) です。戻り値は、後ろのグループの先頭を指します。

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

毎フレームの掃除に使います。生きている敵を前に集めて、死んだ敵は後ろに寄せる。`erase` で消す前に境目を調べられます。`erase_if` より細かい制御が必要なとき、たとえば後ろのグループを別の処理（アニメーションを再生してから消す）に回したいときに便利です。

描画の前に不透明なオブジェクトと半透明なオブジェクトを分けるのにも使います。不透明を前に集め、それぞれ別のルールで並べ替えます。

元の順序は保たれません。保ちたいなら、`stable_partition` です。

## よくあるミス

??? failure "前半の個数を戻り値を使わずに数え直す"
    戻り値の範囲の `begin()` が境目です。`count_if` で数え直さなくても `p.begin() - v.begin()` が前半の個数です。

??? failure "元の順序が保たれると思う"
    `partition` は、グループ内の順序を保証しません。順序が大切なら `stable_partition` を使います。計算量はやや増えます。

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
