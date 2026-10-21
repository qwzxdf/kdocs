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

`std::ranges::contains` は、**範囲の中に、ある値が含まれているかどうかを `bool` で答える**関数です。`find` の結果を `end()` と比べる書き方を、1 つの関数にしたものです。`contains_subrange` を使うと、「連続した並び」が含まれているかも調べられます。

!!! tip "ポイント"
    - あるかどうかだけなら `contains`。位置も欲しいなら [`find`](find.md)。
    - 構造体のメンバで調べるならプロジェクション: `contains(enemies, 42, &Enemy::id)`。
    - 先頭から順に見るので O(n)。何度も調べるなら `unordered_set` を検討する。

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

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

| 場面 | 書き方 |
| --- | --- |
| アイテムを持っているか | `contains(inventory, item_id)` |
| 解放済みのステージか | `contains(unlocked, stage_id)` |
| 禁止ワードが含まれているか | `contains(banned, word)` |

## よくあるミス

??? failure "頻繁に調べるのに vector を使う"
    要素が多く、何度も `contains` を呼ぶなら、`std::unordered_set` の `contains`（C++20）のほうがずっと速いです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::find`](find.md) | 位置を返す |
| [`std::ranges::any_of`](any_of.md) | 条件に合うものがあるか |
| `std::set::contains` / `unordered_set::contains` | コンテナのメンバ関数。ハッシュや木を使うので速い |

## コンパイラ対応

C++23 の機能です。GCC 13 / Clang 19 / MSVC 19.34（VS 2022 17.4）以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] あるかどうかだけなら `contains`
    - [x] 位置が欲しいなら `find`
    - [x] C++23

## 関連ページ

- [cpprefjp: std::ranges::contains](https://cpprefjp.github.io/reference/algorithm/ranges_contains.html)
- [cppreference: std::ranges::contains](https://en.cppreference.com/w/cpp/algorithm/ranges/contains)
