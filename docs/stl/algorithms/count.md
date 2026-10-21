---
title: std::ranges::count
summary: "条件に合う要素が、いくつあるかを数える。"
order: 24
tags:
  - アルゴリズム
---

# std::ranges::count

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`std::ranges::count` は**値と等しい要素の数**を、`count_if` は**条件に合う要素の数**を数える関数です。「生き残っている敵は何体か」「レアアイテムをいくつ持っているか」を、for ループとカウンタ変数を書かずに 1 行で数えられます。

!!! tip "ポイント"
    - 条件で数えるなら `count_if`、値で数えるなら `count`。
    - 必ず全要素を見るので O(n)。「1 つでもあるか」だけなら [`any_of`](any_of.md) のほうが速い（途中で止まる）。
    - 戻り値は符号付き整数（`std::ptrdiff_t` 相当）。

## 関数一覧

| 関数 | 重要度 | 何をする | 計算量 |
| --- | --- | --- | --- |
| [`std::ranges::count_if`](#count_if) | <span class="rank rank-often">よく使う</span> | 条件に合う要素の数 | O(n) |
| [`std::ranges::count`](#count) | <span class="rank rank-often">よく使う</span> | 値と等しい要素の数 | O(n) |

## よくある使い方

```cpp
#include <algorithm>
#include <print>
#include <string>
#include <vector>

struct Item {
  std::string name;
  int rarity;
};

int main() {
  std::vector<Item> bag = {{"剣", 1}, {"盾", 3}, {"薬", 1}, {"冠", 5}};

  auto rare = std::ranges::count_if(bag, [](const Item& i) { return i.rarity >= 3; });
  auto common = std::ranges::count(bag, 1, &Item::rarity);
  std::println("レア {} 個 / ノーマル {} 個", rare, common);
}
```

```text title="実行結果"
レア 2 個 / ノーマル 2 個
```

## 関数の詳しい説明

### std::ranges::count_if {#count_if}

```cpp
template <input_range R, class Proj = identity, class Pred>
constexpr range_difference_t<R> count_if(R&& r, Pred pred, Proj proj = {});
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `r` | 範囲 | 数える範囲 | 省略不可 |
| `pred` | 関数・ラムダ | 数えたい要素で `true` を返す | 省略不可 |
| `proj` | プロジェクション | `pred` に渡す前の変換 | そのまま |

- 戻り値: `pred` が `true` になった要素の数（符号付き整数）
- 計算量: O(n)。必ず全部見る

<div class="anim" data-label="std::ranges::count_if(v, is_even)">
1 2 3 4 5 6 # v
1 *2 3 *4 5 *6 # 条件に合うものを数える
1 2 3 4 5 6 # 結果は 3
</div>

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> hp = {0, 30, 0, 12, 50};
  auto alive = std::ranges::count_if(hp, [](int h) { return h > 0; });
  std::println("残り {} 体", alive);
}
```

```text title="実行結果"
残り 3 体
```

### std::ranges::count {#count}

```cpp
template <input_range R, class T, class Proj = identity>
constexpr range_difference_t<R> count(R&& r, const T& value, Proj proj = {});
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `r` | 範囲 | 数える範囲 | 省略不可 |
| `value` | `const T&` | この値と `==` で等しいものを数える | 省略不可 |
| `proj` | プロジェクション | 比べる前の変換 | そのまま |

- 戻り値: 等しい要素の数
- 計算量: O(n)

<div class="anim" data-label="std::ranges::count(v, 2)">
2 1 2 3 2 # v
*2 1 *2 3 *2 # 値が 2 のものを数える（3）
</div>

```cpp
#include <algorithm>
#include <print>
#include <string>

int main() {
  std::string map_row = "..#..#.#";
  std::println("壁の数: {}", std::ranges::count(map_row, '#'));
}
```

```text title="実行結果"
壁の数: 3
```

## フラグ・オプション

`proj` にメンバポインタを渡すと、メンバの値で数えられます（[よくある使い方](#よくある使い方)の `&Item::rarity`）。

## 古い書き方と今の書き方

=== "古い書き方"

    ```cpp
    int alive = 0;
    for (const auto& e : enemies) {
      if (e.hp > 0) {
        ++alive;
      }
    }
    ```

=== "今の書き方（C++20）"

    ```cpp
    auto alive = std::ranges::count_if(enemies, [](const Enemy& e) { return e.hp > 0; });
    ```

## ゲームでの使いどころ

| 場面 | 例 |
| --- | --- |
| 残り数の表示 | 残りの敵、残りのコイン |
| 実績の判定 | 「星 3 のステージが 10 個以上」 |
| デバッグ表示 | 有効なパーティクルの数 |

## よくあるミス

??? failure "「あるかどうか」に count_if を使う"
    `count_if(...) > 0` は全部数えてから比べるので、1 個目で止まる `any_of` より遅くなります。

??? failure "戻り値を size_t と比べて警告が出る"
    戻り値は符号付きなので、`v.size()` と比べると「符号付きと符号なしの比較」の警告が出ます。`std::ssize(v)` と比べるか、キャストします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::any_of`](any_of.md) | 1 つでもあるか（途中で止まる） |
| `m.count(key)`（map などのメンバ） | キーの数を O(log n) / O(1) で |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 条件で数える → `count_if`、値で数える → `count`
    - [x] あるかどうかだけなら `any_of`

## 関連ページ

- [cpprefjp: std::ranges::count_if](https://cpprefjp.github.io/reference/algorithm/ranges_count_if.html)
- [cppreference: std::ranges::count, count_if](https://en.cppreference.com/w/cpp/algorithm/ranges/count)
