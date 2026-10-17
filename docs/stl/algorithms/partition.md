---
title: std::ranges::partition
tags:
  - アルゴリズム
---

# std::ranges::partition

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`std::ranges::partition` は、**条件に合う要素を前に、合わない要素を後ろに集める**アルゴリズムです（並べ替えるが、ソートはしない）。全部並べる `sort` より速く（O(n)）、「生きている敵を前に集めて、死んだ敵を後ろにまとめて消す」「画面内のものを前に集めて、その分だけ描く」のように使えます。

!!! tip "ポイント"
    - 「条件で 2 グループに分ける」なら `partition`（O(n)）。sort より速い。
    - 元の順番を保ちたいなら `stable_partition`（少し遅い）。
    - 戻り値の位置が「条件に合わないグループの先頭」。

## 関数一覧

| 関数 | 重要度 | 何をする | 計算量 |
| --- | --- | --- | --- |
| [`std::ranges::partition`](#partition) | <span class="rank rank-sometimes">たまに</span> | 条件に合うものを前に集める | O(n) |
| [`std::ranges::stable_partition`](#stable_partition) | <span class="rank rank-sometimes">たまに</span> | 順番を保って前に集める | O(n log n)〜O(n) |
| [`std::ranges::partition_point`](#partition_point) | <span class="rank rank-rare">知ってるだけ</span> | 分かれ目を二分探索で探す | O(log n) |
| [`std::ranges::is_partitioned`](#is_partitioned) | <span class="rank rank-rare">知ってるだけ</span> | 分かれているか調べる | O(n) |
| [`std::ranges::partition_copy`](#partition_copy) | <span class="rank rank-rare">知ってるだけ</span> | 2 つの場所に分けてコピー | O(n) |

## よくある使い方

```cpp
#include <algorithm>
#include <print>
#include <vector>

struct Enemy {
  int id;
  int hp;
};

int main() {
  std::vector<Enemy> enemies = {{1, 0}, {2, 30}, {3, 0}, {4, 50}};

  // 生きている敵を前に集める
  auto dead = std::ranges::stable_partition(enemies, [](const Enemy& e) { return e.hp > 0; });
  std::println("生きている: {} 体", dead.begin() - enemies.begin());

  enemies.erase(dead.begin(), dead.end());  // 後ろの死んだ敵をまとめて消す
  for (const auto& e : enemies) {
    std::print("{} ", e.id);
  }
  std::println("");
}
```

```text title="実行結果"
生きている: 2 体
2 4 
```

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

### std::ranges::stable_partition {#stable_partition}

```cpp
template <bidirectional_range R, class Proj = identity, class Pred>
borrowed_subrange_t<R> stable_partition(R&& r, Pred pred, Proj proj = {});
```

- partition と同じですが、**それぞれのグループの中の順番が元のまま**です。追加のメモリが取れれば O(n)

<div class="anim" data-label="std::stable_partition(b, e, is_even)">
1 2 3 4 5 6 # v
1 *2 3 *4 5 *6 # 条件に合うものを前へ集める
>2 >4 >6 >1 >3 >5 # それぞれの中の順番は元のまま
</div>

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3, 4, 5, 6};
  std::vector<int> stable = v;
  std::ranges::partition(v, [](int x) { return x % 2 == 0; });  // 偶数を前に（順番は不定）
  std::ranges::stable_partition(stable, [](int x) { return x % 2 == 0; });
  std::println("偶数が前？ {} / stable {}",
               std::ranges::is_partitioned(v, [](int x) { return x % 2 == 0; }), stable);
}
```

```text title="実行結果"
偶数が前？ true / stable [2, 4, 6, 1, 3, 5]
```

### std::ranges::partition_point {#partition_point}

```cpp
template <forward_range R, class Proj = identity, class Pred>
constexpr borrowed_iterator_t<R> partition_point(R&& r, Pred pred, Proj proj = {});
```

- すでに分かれている範囲の、分かれ目（最初に `pred` が false になる位置）を二分探索で探します

### std::ranges::is_partitioned {#is_partitioned}

```cpp
template <input_range R, class Proj = identity, class Pred>
constexpr bool is_partitioned(R&& r, Pred pred, Proj proj = {});
```

- `pred` が true の要素が全部 false の要素より前にあれば `true`

### std::ranges::partition_copy {#partition_copy}

```cpp
template <input_range R, weakly_incrementable O1, weakly_incrementable O2, class Proj = identity,
          class Pred>
constexpr partition_copy_result<borrowed_iterator_t<R>, O1, O2>
partition_copy(R&& r, O1 out_true, O2 out_false, Pred pred, Proj proj = {});
```

- 条件に合うものを `out_true` に、合わないものを `out_false` に、元を変えずにコピーします

```cpp
#include <algorithm>
#include <iterator>
#include <print>
#include <vector>

int main() {
  std::vector<int> scores = {80, 45, 92, 30};
  std::vector<int> pass;
  std::vector<int> fail;
  std::ranges::partition_copy(scores, std::back_inserter(pass), std::back_inserter(fail),
                              [](int s) { return s >= 50; });
  std::vector<int> sorted = {9, 7, 5, 2, 1};  // 5 以上が前に分かれている
  auto p = std::ranges::partition_point(sorted, [](int x) { return x >= 5; });
  std::println("{} {} / 分かれ目 {}", pass, fail, *p);
}
```

```text title="実行結果"
[80, 92] [45, 30] / 分かれ目 2
```

## フラグ・オプション

フラグはありません。

## ゲームでの使いどころ

| 場面 | 例 |
| --- | --- |
| 生きている・死んだで分ける | 死んだものを後ろに集めてまとめて消す |
| 画面内・画面外で分ける | 前の n 個だけ描画する |
| 有効・無効で分ける | オブジェクトプールの使用中を前に詰める |

## よくあるミス

??? failure "partition の後に順番が変わって困る"
    描画順などが大事なら `stable_partition` を使います。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 条件で 2 つに分けるのは partition
    - [x] 順番を保つなら stable_partition
    - [x] 戻り値の begin() が分かれ目

## 関連ページ

- [std::ranges::sort](sort.md)
- [std::erase_if](erase_if.md)
