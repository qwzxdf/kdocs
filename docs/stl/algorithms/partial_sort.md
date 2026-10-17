---
title: std::ranges::partial_sort / nth_element
tags:
  - アルゴリズム
---

# std::ranges::partial_sort / nth_element

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`partial_sort` は、**先頭の N 個だけを正しい順に並べる**関数です（残りの順番はバラバラ）。`nth_element` は、**N 番目の位置にだけ「全部並べたときに来るはずの値」を置き、その前には小さいもの、後ろには大きいものを集める**関数です。どちらも全部を並べる `sort` より速く終わります。

!!! tip "ポイント"
    - 「上位 10 件だけ欲しい」なら `partial_sort`。
    - 「中央値」「N 番目に大きい値」だけ欲しいなら `nth_element`。
    - 要素が少ないなら `sort` で全部並べても差はほぼ無い。要素が多いときの最適化に使う。

## 関数一覧

| 関数 | 重要度 | 何をする | 計算量 |
| --- | --- | --- | --- |
| [`std::ranges::partial_sort`](#partial_sort) | <span class="rank rank-rare">知ってるだけ</span> | 先頭 N 個だけ並べる | O(n log N) |
| [`std::ranges::nth_element`](#nth_element) | <span class="rank rank-rare">知ってるだけ</span> | N 番目だけ正しい値にする | 平均 O(n) |
| [`std::ranges::partial_sort_copy`](#partial_sort_copy) | <span class="rank rank-rare">知ってるだけ</span> | 上位 N 個を並べて別の場所にコピー | O(n log N) |

## よくある使い方

### 上位 3 件だけ表示する

```cpp
#include <algorithm>
#include <functional>
#include <print>
#include <vector>

int main() {
  std::vector<int> scores = {40, 95, 70, 88, 15, 60, 99};
  std::ranges::partial_sort(scores, scores.begin() + 3, std::greater{});
  std::println("トップ 3: {} {} {}", scores[0], scores[1], scores[2]);
}
```

```text title="実行結果"
トップ 3: 99 95 88
```

## 関数の詳しい説明

### std::ranges::partial_sort {#partial_sort}

```cpp
template <random_access_range R, class Comp = ranges::less, class Proj = identity>
constexpr borrowed_iterator_t<R> partial_sort(R&& r, iterator_t<R> middle, Comp comp = {}, Proj proj = {});
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `r` | 範囲 | 対象 | 省略不可 |
| `middle` | イテレータ | ここまで（の手前まで）を並べる。`begin() + N` | 省略不可 |
| `comp` | 比較関数 | 並べる順 | 小さい順 |
| `proj` | プロジェクション | 比べる前の変換 | そのまま |

- `[begin, middle)` が正しい順に並び、`[middle, end)` の順番はバラバラ
- 計算量: O(n log N)（N は並べる個数）

<div class="anim" data-label="std::partial_sort(b, b + 3, e)">
7 2 9 1 5 8 # v
>1 >2 >5 9 7 8 # 小さい順に先頭 3 個だけ整列する
1 2 5 9 7 8 # 残りは順番が決まらない
</div>

### std::ranges::nth_element {#nth_element}

```cpp
template <random_access_range R, class Comp = ranges::less, class Proj = identity>
constexpr borrowed_iterator_t<R> nth_element(R&& r, iterator_t<R> nth, Comp comp = {}, Proj proj = {});
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `r` | 範囲 | 対象 |
| `nth` | イテレータ | この位置にだけ正しい値を置く |
| `comp` / `proj` | | sort と同じ |

- `*nth` は全部並べたときと同じ値になる。`nth` より前はそれ以下、後ろはそれ以上（それぞれの中の順番はバラバラ）
- 計算量: 平均 O(n)

<div class="mem">
<div class="mem-step"><span class="mem-label">前</span><span class="mem-cells"><span>7</span><span>2</span><span>9</span><span>4</span><span>5</span></span></div>
<div class="mem-step"><span class="mem-label">nth = 2 番目</span><span class="mem-cells"><span>2</span><span>4</span><span class="move">5</span><span>9</span><span>7</span></span><span class="mem-note">5 だけが正しい位置。左は 5 以下、右は 5 以上（順番はバラバラ）</span></div>
</div>

<div class="anim" data-label="std::nth_element(b, b + 2, e)">
7 2 9 1 5 8 # v
2 1 *5 7 9 8 # 5 が 3 番目の位置に来る
</div>

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> ping = {30, 250, 45, 60, 38};
  auto mid = ping.begin() + ping.size() / 2;
  std::ranges::nth_element(ping, mid);
  std::println("中央値 {} ms", *mid);
}
```

```text title="実行結果"
中央値 45 ms
```

!!! note "実際は"
    平均値は 1 つの極端な値（250 ms）に引っ張られますが、中央値は引っ張られにくいので、通信遅延やフレーム時間の評価に向いています。

### std::ranges::partial_sort_copy {#partial_sort_copy}

```cpp
template <input_range R1, random_access_range R2, class Comp = ranges::less,
          class Proj1 = identity, class Proj2 = identity>
constexpr partial_sort_copy_result<borrowed_iterator_t<R1>, borrowed_iterator_t<R2>>
partial_sort_copy(R1&& r, R2&& result_r, Comp comp = {}, Proj1 proj1 = {}, Proj2 proj2 = {});
```

- 元を変えずに、上位 `result_r.size()` 個を並べて `result_r` に書き込みます

```cpp
#include <algorithm>
#include <array>
#include <functional>
#include <print>
#include <vector>

int main() {
  std::vector<int> scores = {40, 95, 70, 88, 15};
  std::array<int, 2> top{};
  std::ranges::partial_sort_copy(scores, top, std::greater{});
  std::println("{} / 元はそのまま {}", top, scores);
}
```

```text title="実行結果"
[95, 88] / 元はそのまま [40, 95, 70, 88, 15]
```

## フラグ・オプション

`comp` / `proj` は [`std::ranges::sort` のフラグ・オプション](sort.md#フラグオプション) と同じです。

## ゲームでの使いどころ

| 場面 | 関数 |
| --- | --- |
| ランキングの上位だけ表示 | `partial_sort` |
| 近い敵 N 体だけ処理 | `partial_sort` / `nth_element` |
| フレーム時間の中央値・90 パーセンタイル | `nth_element` |

## よくあるミス

??? failure "partial_sort の後半も並んでいると思う"
    `middle` より後ろの順番はバラバラです。

## 理解度チェック

!!! question "Q1. 1 万体の敵から近い 5 体だけ欲しい。sort と partial_sort どちらが速い？"
    <div class="spoiler" markdown>

    **答え:** `partial_sort`（O(n log 5)）。sort は全部並べる O(n log n) です。

    </div>

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::sort`](sort.md) | 全部並べる |
| [`std::ranges::min_element`](min_element.md) | 1 個だけでいいならこちら |
| [`std::priority_queue`](../containers/priority_queue.md) | 追加しながら上位を保つ |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 上位 N 件 → `partial_sort`
    - [x] N 番目・中央値 → `nth_element`

## 関連ページ

- [cpprefjp: std::ranges::partial_sort](https://cpprefjp.github.io/reference/algorithm/ranges_partial_sort.html)
- [cppreference: std::ranges::nth_element](https://en.cppreference.com/w/cpp/algorithm/ranges/nth_element)
