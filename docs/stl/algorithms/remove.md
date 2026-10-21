---
title: std::ranges::remove
summary: "条件に合う要素を前に詰めて取り除く（remove-erase のイディオム）。"
order: 43
tags:
  - アルゴリズム
---

# std::ranges::remove

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`std::ranges::remove` は、**範囲から、ある値と等しい要素を取り除いて、残りを前に詰める**アルゴリズムです。条件で取り除く `remove_if` もあります。ただし**コンテナの大きさは変わりません**。詰めた後ろの要素は不定になり、戻り値の「新しい終わり」から `erase` で本当に消します（remove-erase のイディオム）。

!!! tip "ポイント"
    - `v.erase(std::ranges::remove(v, x).begin(), v.end())` が定番の形（remove-erase のイディオム）。
    - C++20 以降は、これを 1 行にした [`std::erase_if`](erase_if.md) / `std::erase` を使うのが普通。
    - remove のあとの、詰めた後ろの要素は**不定**。読んではいけない。

!!! info "このページを読む前に"
    [ラムダ式](../../basics/lambda.md)、[イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::ranges::remove_if {#remove_if}

```cpp
template <forward_range R, class Proj = identity, class Pred>
constexpr borrowed_subrange_t<R> remove_if(R&& r, Pred pred, Proj proj = {});
```

- `pred` が `true` の要素を**除いて**、残りを前に詰めます。**要素数は変わりません**
- 戻り値: 詰めたあとに残った「ゴミ」の範囲。vector ならここを `erase` すると本当に消えます

<div class="mem">
<div class="mem-step"><span class="mem-label">前</span><span class="mem-cells"><span>1</span><span class="gone">×</span><span>3</span><span class="gone">×</span><span>5</span></span></div>
<div class="mem-step"><span class="mem-label">remove_if 後</span><span class="mem-cells"><span>1</span><span class="move">3</span><span class="move">5</span><span class="free">?</span><span class="free">?</span></span><span class="mem-note">? は戻り値の範囲。大きさは 5 のまま</span></div>
</div>

<div class="anim" data-label="std::remove_if(b, e, is_even)">
1 2 3 4 5 # v
1 x2 3 x4 5 # 条件に合うものが対象
1 >3 >5 _ _ # 残りを前に詰める。size は変わらない
1 3 5 # erase で後ろを切り捨てて完成
</div>

```cpp
#include <algorithm>
#include <array>
#include <print>

int main() {
  // array は大きさを変えられないので、詰めた個数を覚えておく
  std::array<int, 5> slots = {1, 0, 3, 0, 5};
  auto rest = std::ranges::remove_if(slots, [](int x) { return x == 0; });
  auto used = rest.begin() - slots.begin();
  std::println("使っているのは先頭 {} 個: {} {} {}", used, slots[0], slots[1], slots[2]);
}
```

```text title="実行結果"
使っているのは先頭 3 個: 1 3 5
```

### std::ranges::remove {#remove}

```cpp
template <forward_range R, class T, class Proj = identity>
constexpr borrowed_subrange_t<R> remove(R&& r, const T& value, Proj proj = {});
```

- `value` と等しい要素を除いて前に詰めます（remove_if の値版）

<div class="anim" data-label="std::remove(b, e, 2)">
1 2 3 2 4 # v
1 x2 3 x2 4 # 値が 2 のものを消す対象にする
1 >3 >4 _ _ # 残りを前に詰める。size は変わらない
1 3 4 # erase で後ろを切り捨てて完成
</div>

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 死んだ敵を `vector` から消す | `std::erase_if(enemies, 死んでいる)`（内部でこの処理） |
| 配列から特定のアイテムを取り除く | `remove` + `erase` |

## よくあるミス

??? failure "remove しただけで、要素が減ったと思う"
    `remove` は詰めるだけで、`size()` は変わりません。`erase` まで呼ぶか、`std::erase_if` を使います。

??? failure "戻り値を無視する"
    戻り値（新しい終わり）を無視すると、ゴミの要素が残ったままです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::erase_if`](erase_if.md) | remove と erase を 1 行で |
| [`std::ranges::replace`](replace.md) | 値を書き換える |
| [`std::ranges::unique`](unique.md) | 隣り合う重複を詰める |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 条件に合う要素を前に詰める
    - [x] 大きさは変わらない
    - [x] C++20 以降は `std::erase_if`

## 関連ページ

- [cpprefjp: std::ranges::remove](https://cpprefjp.github.io/reference/algorithm/ranges_remove.html)
- [cppreference: std::ranges::remove](https://en.cppreference.com/w/cpp/algorithm/ranges/remove)
