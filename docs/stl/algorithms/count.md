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

生き残っている敵が何体か、レアアイテムをいくつ持っているか。条件に合う要素の「数」が必要なとき、カウンター変数を作って、`for` で回して、条件に合ったら `++` する、というコードを書くことになります。`std::ranges::count` は値と等しい要素の数を `count_if` は条件に合う要素の数を 1 行で数えます。

!!! tip "ポイント"
    - 条件で数えるなら `count_if`、値で数えるなら `count`。
    - 必ず全要素を見るので O(n)。「1 つでもあるか」だけなら [`any_of`](any_of.md) のほうが速い（途中で止まる）。
    - 戻り値は符号付き整数（`std::ptrdiff_t` 相当）。

!!! info "このページを読む前に"
    [`ranges` とビュー](../../basics/ranges.md)と[ラムダ式](../../basics/lambda.md)が分かると読みやすいです。

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

残りの敵の数を数えて、HUD に表示するのが定番です。`std::ranges::count_if(enemies, &Enemy::alive)` と書くと、生きている敵の数が得られます。

アイテムの所持数にも使います。インベントリが `vector<ItemId>` なら、`std::ranges::count(inventory, potion_id)` でポーションの個数が分かります。

数が必要ないなら、`any_of` や `all_of` を使います。「1 つでもあるか」を調べるのに `count_if(...) > 0` と書くと、全要素を最後まで調べてしまいます。`any_of` なら、最初に見つかった時点で止まります。

## よくあるミス

??? failure "「あるか」を調べるのに `count_if` を使う"
    `count_if(v, f) > 0` は、必ず全要素を調べます。「1 つでもあるか」なら `any_of(v, f)` のほうが、途中で止まるので速く、意図も伝わります。

??? failure "戻り値を `unsigned` で受けて、比較がおかしくなる"
    `count` の戻り値は符号付きの整数です。`size_t` の変数で受けて `-1` と比べるなど、符号をまたぐ比較で警告が出ます。`auto` で受けるか、`std::ptrdiff_t` で受けます。

??? failure "`map` に対して `ranges::count` を使う"
    `map` の要素は `pair` なので、キーの数を調べたいなら、`map.count(key)` のメンバー関数のほうが速く（O(log n)）、意図も明確です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`any_of`](any_of.md) | 1 つでもあるか。数は要らないとき |
| [`all_of`](all_of.md) | 全部が条件を満たすか |
| [`find`](find.md) | 最初の 1 つを探す |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 値で数えるなら `count`、条件なら `count_if`。
    - [x] 「あるか」だけなら `any_of` のほうが速い。
    - [x] 戻り値は符号付き整数。

## 関連ページ

- [cpprefjp: std::ranges::count_if](https://cpprefjp.github.io/reference/algorithm/ranges_count_if.html)
- [cppreference: std::ranges::count, count_if](https://en.cppreference.com/w/cpp/algorithm/ranges/count)
