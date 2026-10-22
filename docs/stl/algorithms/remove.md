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

`vector` から条件に合う要素を取り除くとき、`std::remove` を呼んだだけでは、`vector` の大きさが変わりません。要素が前に詰められるだけで、後ろにはゴミが残ります。この動きを知らないと、「消したはずなのに残っている」というバグになります。`remove` と `erase` を組み合わせる書き方（remove-erase イディオム）が必要でした。C++20 以降は、`std::erase_if` で 1 行にできます。

!!! tip "ポイント"
    - `v.erase(std::ranges::remove(v, x).begin(), v.end())` が定番の形（remove-erase のイディオム）。
    - C++20 以降は、これを 1 行にした [`std::erase_if`](erase_if.md) / `std::erase` を使うのが普通。
    - remove のあとの、詰めた後ろの要素は**不定**。読んではいけない。

!!! info "このページを読む前に"
    取り除くだけなら、このページの `remove` より [`erase_if`](erase_if.md) のほうが簡単です。`remove` は、仕組みを知る必要があるときと、`erase` を呼べない範囲（配列など）で使います。

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

新しいコードでは、`std::erase_if` を使います。`remove` を直接使うのは、`vector` ではなく C の配列や `std::array`、あるいは `erase` を呼べない範囲に対してです。大きさを変えられない範囲では、前に詰めたあとの「新しい終わり」を返してもらい、その手前だけを使います。

古いコードを読むときには、`v.erase(std::remove_if(v.begin(), v.end(), pred), v.end())` という形に出会います。これが remove-erase イディオムで、`erase_if` と同じ意味です。意味が分かれば、読み替えられます。

## よくあるミス

??? failure "`remove` だけ呼んで消えたと思う"
    `std::ranges::remove(v, x)` だけでは、`v.size()` は変わりません。戻り値の `subrange` の `begin()` から `v.end()` までを `erase` で消して、はじめて本当に消えます。`erase_if` を使えば、この手間はありません。

??? failure "詰めたあとの後ろの要素を読む"
    `remove` のあと、新しい終わりより後ろの要素は不定です（ムーブされたあとの抜け殻）。読んではいけません。

??? failure "`list` や `map` で `remove` を使う"
    `list` には専用のメンバー関数 `remove`、`map` には `erase_if` があります。汎用の `remove` は要素を移動するので、`map` のようなキーが const の入れ物には使えません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`erase_if`](erase_if.md) | remove-erase を 1 行にした関数。新しいコードはこれ |
| [`unique`](unique.md) | 連続した重複を取り除く。同じく `erase` と組み合わせて使う |
| [`partition`](partition.md) | 条件で 2 つのグループに分ける。要素を捨てたくないとき |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `remove` は前に詰めるだけで、大きさは変わらない。
    - [x] 本当に消すには `erase`。新しいコードは `erase_if`。
    - [x] 新しい終わりより後ろは読まない。

## 関連ページ

- [cpprefjp: std::ranges::remove](https://cpprefjp.github.io/reference/algorithm/ranges_remove.html)
- [cppreference: std::ranges::remove](https://en.cppreference.com/w/cpp/algorithm/ranges/remove)
