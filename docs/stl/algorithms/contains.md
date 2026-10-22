---
title: std::ranges::contains
summary: "範囲に、ある値が含まれているかを `bool` で答える。"
order: 15
tags:
  - アルゴリズム
---

# std::ranges::contains

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-23">C++23</span>
`#include <algorithm>`
</div>

インベントリにそのアイテムがあるか、有効なキーの一覧にこのキーが含まれているか。「あるかどうか」だけを知りたい場面は多いのに、`find` の結果を `end()` と比べる書き方は、意図が一目では伝わりません。C++23 の `std::ranges::contains` は、「範囲に値が含まれているか」を `bool` で答える関数です。`find` を使った判定と、まったく同じ動きをします。

!!! tip "ポイント"
    - あるかどうかだけなら `contains`。位置も欲しいなら [`find`](find.md)。
    - 構造体のメンバで調べるならプロジェクション: `contains(enemies, 42, &Enemy::id)`。
    - 先頭から順に見るので O(n)。何度も調べるなら `unordered_set` を検討する。

!!! info "このページを読む前に"
    [`ranges` とビュー](../../basics/ranges.md)と[ラムダ式](../../basics/lambda.md)が分かると読みやすいです。

## 関数の詳しい説明

### std::ranges::contains <span class="ver ver-23">C++23</span> {#contains data-toc-label="std::ranges::contains"}

```cpp
template <input_range R, class T, class Proj = identity>
constexpr bool contains(R&& r, const T& value, Proj proj = {});
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `r` | 範囲 | 探す範囲 |
| `value` | `const T&` | 探す値 |
| `proj` | プロジェクション | 比べる前の変換 |

- 戻り値: 含まれていれば `true`
- 計算量: O(n)

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> unlocked = {1, 2, 5};
  std::println("{} {}", std::ranges::contains(unlocked, 5),
               std::ranges::contains(unlocked, 3));
}
```

```text title="実行結果"
true false
```

!!! note "実際は"
    `find(...) != end()` と書いていたものが 1 行で済みます。位置が要らないならこちらを使います。


### std::ranges::contains_subrange <span class="ver ver-23">C++23</span> {#contains_subrange data-toc-label="std::ranges::contains_subrange"}

```cpp
template <forward_range R1, forward_range R2, class Pred = ranges::equal_to,
          class Proj1 = identity, class Proj2 = identity>
constexpr bool contains_subrange(R1&& r1, R2&& r2, Pred pred = {}, Proj1 proj1 = {}, Proj2 proj2 = {});
```

- `r1` の中に、`r2` と同じ並びが連続して含まれていれば `true`（[`search`](search.md) の結果が空でないか、と同じ）

```cpp
#include <algorithm>
#include <print>
#include <string>

int main() {
  std::string log = "load,init,run,exit";
  std::println("{}", std::ranges::contains_subrange(log, std::string("init,run")));
  std::println("{}", std::ranges::contains_subrange(log, std::string("run,init")));
}
```

```text title="実行結果"
true
false
```

## 古い書き方と今の書き方

=== "古い書き方"

    ```cpp
    bool has = std::find(v.begin(), v.end(), 5) != v.end();
    ```

=== "今の書き方（C++23）"

    ```cpp
    bool has = std::ranges::contains(v, 5);
    ```

## ゲームでの使いどころ

所持品の判定が、代表的な使い方です。`std::ranges::contains(inventory, item_id)` で、そのアイテムを持っているかを調べます。構造体のメンバで調べるなら、プロジェクションを使って `contains(enemies, 42, &Enemy::id)` と書きます。

許可リストや禁止リストの判定にも使えます。ただし `contains` は先頭から順に調べるので、要素が数百個以上あって何度も呼ぶなら、`unordered_set` に入れて、`set.contains(x)` で調べるほうが速くなります。

連続した並びが含まれているかは、`contains_subrange` で調べます。コマンド入力（↓→パンチ）の判定のような、入力履歴の中に特定の並びがあるかの確認に使えます。

## よくあるミス

??? failure "位置が必要なのに `contains` を使う"
    `contains` は `bool` しか返しません。見つけた要素を取り出したり、書き換えたりしたいなら、`find` で位置を取ります。

??? failure "C++20 以前のコンパイラで使う"
    `contains` は C++23 の機能です。C++20 なら `std::ranges::find(r, x) != std::ranges::end(r)` と書きます。

??? failure "大きな配列で何度も呼ぶ"
    O(n) の探索を毎フレーム、要素数千個で何十回も呼ぶと、無視できない時間になります。`unordered_set` に変えるか、結果をキャッシュします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`find`](find.md) | 位置を返す。要素を使うならこちら |
| [`any_of`](any_of.md) | 条件で調べる。値の一致ではなく、条件式で判断したいとき |
| [`unordered_set`](../containers/unordered_set.md) | 何度も調べるなら、集合のほうが速い |

## コンパイラ対応

C++23 の機能です。GCC 13 / Clang 19 / MSVC 19.34（VS 2022 17.4）以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] あるかどうかだけなら `contains`、位置が欲しいなら `find`。
    - [x] C++23 の機能。C++20 以前は `find` と `end()` の比較で書く。
    - [x] 何度も呼ぶなら `unordered_set`。

## 関連ページ

- [cpprefjp: std::ranges::contains](https://cpprefjp.github.io/reference/algorithm/ranges_contains.html)
- [cppreference: std::ranges::contains](https://en.cppreference.com/w/cpp/algorithm/ranges/contains)
