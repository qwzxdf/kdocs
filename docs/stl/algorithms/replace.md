---
title: std::ranges::replace / remove
tags:
  - アルゴリズム
---

# std::ranges::replace / remove

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`std::ranges::replace` は、**範囲の中の特定の値を、別の値に置き換える**アルゴリズムです。`replace_if` なら条件で置き換えます。一方 `std::ranges::remove` / `remove_if` は、**消したい要素を除いて残りを前に詰める**だけのアルゴリズムで、要素数は変わりません（実際に消すには [`std::erase_if`](erase_if.md) を使います）。array のように要素数を変えられない範囲で使います。

!!! tip "結論"
    - 値の置き換えは `std::ranges::replace(v, 古い値, 新しい値)`、条件なら `replace_if`。
    - **vector から消すなら [`std::erase_if`](erase_if.md)**。`remove` / `remove_if` 単体では消えない。
    - 元を変えずにコピーを作るなら `replace_copy` / `remove_copy`。

## 関数一覧

| 関数 | 重要度 | 何をする | 計算量 |
| --- | --- | --- | --- |
| [`std::ranges::replace`](#replace) | <span class="rank rank-sometimes">たまに</span> | 値を置き換える | O(n) |
| [`std::ranges::replace_if`](#replace_if) | <span class="rank rank-sometimes">たまに</span> | 条件に合う要素を置き換える | O(n) |
| [`std::ranges::remove_if`](#remove_if) | <span class="rank rank-rare">知ってるだけ</span> | 条件に合わない要素を前に詰める（消さない） | O(n) |
| [`std::ranges::remove`](#remove) | <span class="rank rank-rare">知ってるだけ</span> | 値と等しくない要素を前に詰める（消さない） | O(n) |
| [`std::ranges::replace_copy`](#replace_copy) | <span class="rank rank-rare">知ってるだけ</span> | 置き換えたコピーを別の場所に作る | O(n) |
| [`std::ranges::remove_copy_if`](#remove_copy_if) | <span class="rank rank-rare">知ってるだけ</span> | 条件に合うものを除いたコピーを作る | O(n) |

## よくある使い方

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  // マップの中の「宝箱（2）」を全部「空き箱（3）」に変える
  std::vector<int> map = {0, 2, 1, 2, 0};
  std::ranges::replace(map, 2, 3);
  std::println("{}", map);

  // HP がマイナスになったものを 0 にそろえる
  std::vector<int> hp = {30, -5, 12, -20};
  std::ranges::replace_if(hp, [](int h) { return h < 0; }, 0);
  std::println("{}", hp);
}
```

```text title="実行結果"
[0, 3, 1, 3, 0]
[30, 0, 12, 0]
```

## 関数の詳しい説明

### std::ranges::replace {#replace}

```cpp
template <input_range R, class T1, class T2, class Proj = identity>
constexpr borrowed_iterator_t<R> replace(R&& r, const T1& old_value, const T2& new_value,
                                         Proj proj = {});
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `r` | 範囲 | 対象 |
| `old_value` | 値 | この値と等しい要素を |
| `new_value` | 値 | この値に置き換える |
| `proj` | プロジェクション | 比べる前の変換 |

### std::ranges::replace_if {#replace_if}

```cpp
template <input_range R, class T, class Proj = identity, class Pred>
constexpr borrowed_iterator_t<R> replace_if(R&& r, Pred pred, const T& new_value, Proj proj = {});
```

- `pred` が `true` の要素を `new_value` に置き換えます

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

### std::ranges::replace_copy {#replace_copy}

```cpp
template <input_range R, class T1, class T2, output_iterator<const T2&> O, class Proj = identity>
constexpr replace_copy_result<borrowed_iterator_t<R>, O>
replace_copy(R&& r, O result, const T1& old_value, const T2& new_value, Proj proj = {});
```

- 元は変えずに、置き換えたものを `result` に書き込みます

### std::ranges::remove_copy_if {#remove_copy_if}

```cpp
template <input_range R, weakly_incrementable O, class Proj = identity, class Pred>
constexpr remove_copy_if_result<borrowed_iterator_t<R>, O>
remove_copy_if(R&& r, O result, Pred pred, Proj proj = {});
```

- `pred` が `true` の要素を除いたものを `result` に書き込みます（[copy_if](copy_fill.md#copy_if) の逆）

```cpp
#include <algorithm>
#include <iterator>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 1, 3};
  std::vector<int> replaced;
  std::ranges::replace_copy(v, std::back_inserter(replaced), 1, 9);
  std::vector<int> without_one;
  std::ranges::remove_copy_if(v, std::back_inserter(without_one), [](int x) { return x == 1; });
  auto rest = std::ranges::remove(v, 3);
  std::println("{} {} / remove 後の大きさ {} / 有効 {}", replaced, without_one, v.size(),
               rest.begin() - v.begin());
}
```

```text title="実行結果"
[9, 2, 9, 3] [2, 3] / remove 後の大きさ 4 / 有効 3
```

## フラグ・オプション

フラグはありません。

## ゲームでの使いどころ

| 場面 | 関数 |
| --- | --- |
| タイルの種類を一括で変える | `replace` |
| おかしな値をまとめて直す | `replace_if` |
| 固定長の配列で、使っている分を前に詰める | `remove_if` |

## よくあるミス

??? failure "remove_if で消えたと思う"
    `std::ranges::remove_if(v, pred);` のあとも `v.size()` は変わりません。vector なら `std::erase_if(v, pred)` を使います。

## 理解度チェック

!!! question "Q1. `std::string s = \"a-b-c\";` の `-` を全部 `_` にするには？"
    <div class="spoiler" markdown>

    **答え:** `std::ranges::replace(s, '-', '_');`。

    </div>

## これだけ覚える

!!! abstract "まとめ"
    - [x] 置き換えは replace / replace_if
    - [x] remove 系は詰めるだけ。vector から消すなら std::erase_if

## 関連ページ

- [std::erase_if](erase_if.md)
- [cppreference: std::ranges::replace](https://en.cppreference.com/w/cpp/algorithm/ranges/replace)
