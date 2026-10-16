---
title: std::ranges::lower_bound / binary_search
tags:
  - アルゴリズム
---

# std::ranges::lower_bound / binary_search

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`lower_bound`、`upper_bound`、`binary_search`、`equal_range` は、**ソート済みの範囲を「二分探索」で探す**関数です。真ん中を見て、探している値より大きいか小さいかで半分に絞る、を繰り返すので、100 万個あっても 20 回ほどの比較で見つかります（O(log n)）。**ソートされていない範囲に使うと結果がでたらめになります**。

!!! tip "結論"
    - **ソート済みの vector を速く探したいときに使う。** 位置が欲しいなら `lower_bound`、あるかだけなら `binary_search`。
    - `lower_bound` は「以上の最初」、`upper_bound` は「より大きい最初」。
    - 使う前に必ずソートしておく（同じ比較関数・同じプロジェクションで）。
    - 何度も追加・削除するなら、`std::set` / `std::map` を使うほうが楽。

!!! info "このページを読む前に"
    [`std::ranges::sort`](sort.md) と [計算量](../../basics/big-o.md) を先に読むと分かりやすいです。

## 関数一覧

| 関数 | 重要度 | 何をする | 計算量 |
| --- | --- | --- | --- |
| [`std::ranges::lower_bound`](#lower_bound) | <span class="rank rank-sometimes">たまに</span> | 値**以上**の最初の位置 | O(log n) |
| [`std::ranges::binary_search`](#binary_search) | <span class="rank rank-sometimes">たまに</span> | 値があるか | O(log n) |
| [`std::ranges::upper_bound`](#upper_bound) | <span class="rank rank-sometimes">たまに</span> | 値**より大きい**最初の位置 | O(log n) |
| [`std::ranges::equal_range`](#equal_range) | <span class="rank rank-rare">知ってるだけ</span> | 値と等しい範囲 | O(log n) |

<div class="mem">
<div class="mem-step"><span class="mem-label">ソート済み</span><span class="mem-cells"><span>10</span><span>20</span><span class="move">30</span><span class="move">30</span><span class="new">40</span><span>50</span></span></div>
<div class="mem-step"><span class="mem-label">値 30 のとき</span><span class="mem-note">lower_bound → 最初の 30 ／ upper_bound → 40 ／ equal_range → 2 つの 30</span></div>
</div>

## よくある使い方

### ソート済みのリストに順番を保って挿入する

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> ranking = {980, 870, 700, 650};  // 大きい順
  int new_score = 800;

  // 大きい順なので比較は std::greater
  auto pos = std::ranges::lower_bound(ranking, new_score, std::greater{});
  ranking.insert(pos, new_score);
  std::println("{}", ranking);
}
```

```text title="実行結果"
[980, 870, 800, 700, 650]
```

## 関数の詳しい説明

### std::ranges::lower_bound {#lower_bound}

```cpp
template <forward_range R, class T, class Proj = identity, class Comp = ranges::less>
constexpr borrowed_iterator_t<R> lower_bound(R&& r, const T& value, Comp comp = {}, Proj proj = {});
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `r` | 範囲 | **ソート済み**の範囲 | 省略不可 |
| `value` | `const T&` | 探す値 | 省略不可 |
| `comp` | 比較関数 | ソートに使ったのと同じ比較 | `<` |
| `proj` | プロジェクション | ソートに使ったのと同じ変換 | そのまま |

- 戻り値: `value` **以上**（比較的に「前ではない」）の最初の要素。無ければ `end()`
- 計算量: O(log n)（vector などランダムアクセスできる範囲の場合）

```cpp
#include <algorithm>
#include <print>
#include <string>
#include <vector>

struct Item {
  int id;
  std::string name;
};

int main() {
  // id でソート済み
  std::vector<Item> items = {{100, "薬"}, {200, "剣"}, {300, "盾"}};
  auto it = std::ranges::lower_bound(items, 200, {}, &Item::id);
  if (it != items.end() && it->id == 200) {
    std::println("見つかった: {}", it->name);
  }
}
```

```text title="実行結果"
見つかった: 剣
```

!!! note "実際は"
    `lower_bound` は「見つかった」とは限りません（値が無ければ、その値を入れるべき位置が返る）。見つかったか確かめるなら、`it != end()` と「値が等しいか」の両方を見ます。

### std::ranges::binary_search {#binary_search}

```cpp
template <forward_range R, class T, class Proj = identity, class Comp = ranges::less>
constexpr bool binary_search(R&& r, const T& value, Comp comp = {}, Proj proj = {});
```

- 戻り値: `value` と等しい要素があれば `true`。**位置は分からない**

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> walls = {3, 7, 12, 20};  // ソート済み
  std::println("{} {}", std::ranges::binary_search(walls, 12),
               std::ranges::binary_search(walls, 5));
}
```

```text title="実行結果"
true false
```

### std::ranges::upper_bound {#upper_bound}

```cpp
template <forward_range R, class T, class Proj = identity, class Comp = ranges::less>
constexpr borrowed_iterator_t<R> upper_bound(R&& r, const T& value, Comp comp = {}, Proj proj = {});
```

- 戻り値: `value` **より大きい**最初の要素。無ければ `end()`

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  // 経験値のしきい値（レベル 1, 2, 3, 4 の開始）
  std::vector<int> thresholds = {0, 100, 300, 700};
  int exp = 450;
  auto it = std::ranges::upper_bound(thresholds, exp);
  std::println("Lv.{}", it - thresholds.begin());
}
```

```text title="実行結果"
Lv.3
```

### std::ranges::equal_range {#equal_range}

```cpp
template <forward_range R, class T, class Proj = identity, class Comp = ranges::less>
constexpr borrowed_subrange_t<R> equal_range(R&& r, const T& value, Comp comp = {}, Proj proj = {});
```

- 戻り値: `value` と等しい要素の範囲（`lower_bound` から `upper_bound` まで）

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 2, 2, 5};
  auto same = std::ranges::equal_range(v, 2);
  std::println("2 は {} 個", same.size());
}
```

```text title="実行結果"
2 は 3 個
```

## フラグ・オプション

| 引数 | 重要度 | 渡すもの | 意味 |
| --- | --- | --- | --- |
| `comp` | <span class="rank rank-sometimes">たまに</span> | `std::greater{}` | 大きい順にソートされた範囲を探す |
| `proj` | <span class="rank rank-sometimes">たまに</span> | `&Type::member` | メンバでソートされた範囲を探す |

**ソートしたときと同じものを渡す**必要があります。

## 古い書き方と今の書き方

=== "古い書き方"

    ```cpp
    auto it = std::lower_bound(items.begin(), items.end(), 200,
                               [](const Item& a, int id) { return a.id < id; });
    ```

=== "今の書き方（C++20）"

    ```cpp
    auto it = std::ranges::lower_bound(items, 200, {}, &Item::id);
    ```

## ゲームでの使いどころ

| 場面 | 例 |
| --- | --- |
| しきい値の表 | 経験値 → レベル、距離 → LOD |
| マスターデータの検索 | ID でソートした vector から引く |
| 順番を保って挿入 | ランキングに新記録を入れる |
| アニメーションのキーフレーム | 時刻から前後のキーを探す |

## パフォーマンス

- vector なら O(log n) でとても速く、キャッシュ効率も良いです。`std::map` より速いことが多いです。
- `std::list` などランダムアクセスできない範囲では、比較は O(log n) でも移動に O(n) かかります。

## 未定義動作・例外

| やったこと | 結果 |
| --- | --- |
| ソートされていない範囲で使う | 結果がでたらめ（未定義動作ではないが正しくない） |
| ソートと違う比較関数を渡す | 同上 |

## よくあるミス

??? failure "ソートし忘れる"
    二分探索は「真ん中より左は全部小さい」ことを前提にしています。ソートしていないと、あるはずの値が見つかりません。

??? failure "lower_bound の結果を「見つかった」と思い込む"
    `lower_bound` は値が無くても `end()` 以外を返すことがあります。値が等しいかも確かめます。

## 理解度チェック

!!! question "Q1. `{10, 20, 30}` で `lower_bound(25)` と `upper_bound(20)` が指す値は？"
    <div class="spoiler" markdown>

    **答え:** どちらも `30`。

    </div>

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::find`](find.md) | ソート不要。O(n) |
| [`std::map::lower_bound`](../containers/map.md#lower_bound) | map のメンバ版 |
| [`std::flat_map`](../containers/flat_map.md) | ソート済み vector を map として使う |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ソート済みの範囲を O(log n) で探す
    - [x] 以上 → `lower_bound`、より大きい → `upper_bound`
    - [x] ソートと同じ比較・プロジェクションを渡す

## 関連ページ

- [cpprefjp: std::ranges::lower_bound](https://cpprefjp.github.io/reference/algorithm/ranges_lower_bound.html)
- [cppreference: std::ranges::lower_bound](https://en.cppreference.com/w/cpp/algorithm/ranges/lower_bound)
