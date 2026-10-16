---
title: std::forward_list
tags:
  - コンテナ
---

# std::forward_list

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="perf perf-1">× 重い</span>
<span class="ver ver-11">C++11</span>
`#include <forward_list>`
</div>

`std::forward_list` は、**次の要素へのポインタだけを持つ「片方向連結リスト」**です。[`std::list`](list.md) から「前の要素へのポインタ」を取り除いて、そのぶん 1 要素あたりのメモリを減らしたものです。前には戻れず、`size()` すらありません。

!!! tip "結論"
    - **使わない。** list でさえほぼ使わないので、その機能を削ったこれを使う場面はさらにない。
    - 「C で書いた片方向リストと同じ大きさ・速さのものが標準にある」と知っておけば十分。

## 宣言

```cpp
template <class T, class Allocator = std::allocator<T>>
class forward_list;
```

## 関数一覧

| 関数 | 重要度 | 何をする | 計算量 |
| --- | --- | --- | --- |
| [`push_front`](#push_front) | <span class="rank rank-often">よく使う</span> | 先頭に追加 | O(1) |
| [`pop_front`](#pop_front) | <span class="rank rank-often">よく使う</span> | 先頭を削除 | O(1) |
| [`front`](#front) | <span class="rank rank-often">よく使う</span> | 先頭の要素 | O(1) |
| [`empty`](#empty) | <span class="rank rank-often">よく使う</span> | 空か | O(1) |
| [`begin`](#begin) | <span class="rank rank-often">よく使う</span> | 先頭のイテレータ | O(1) |
| [`end`](#end) | <span class="rank rank-often">よく使う</span> | 最後の次のイテレータ | O(1) |
| [`insert_after`](#insert_after) | <span class="rank rank-sometimes">たまに</span> | 指定位置の**後ろ**に挿入 | O(1) |
| [`erase_after`](#erase_after) | <span class="rank rank-sometimes">たまに</span> | 指定位置の**後ろ**を削除 | O(1) |
| [`before_begin`](#before_begin) | <span class="rank rank-sometimes">たまに</span> | 先頭の 1 つ前（`insert_after` 用） | O(1) |
| [`clear`](#clear) | <span class="rank rank-sometimes">たまに</span> | 全削除 | O(n) |
| [`emplace_front`](#emplace_front) | <span class="rank rank-rare">知ってるだけ</span> | 先頭にその場で構築 | O(1) |
| [`emplace_after`](#emplace_after) | <span class="rank rank-rare">知ってるだけ</span> | 後ろにその場で構築 | O(1) |
| [`remove_if`](#remove_if) | <span class="rank rank-rare">知ってるだけ</span> | 条件で削除 | O(n) |
| [`remove`](#remove) | <span class="rank rank-rare">知ってるだけ</span> | 値で削除 | O(n) |
| [`sort`](#sort) | <span class="rank rank-rare">知ってるだけ</span> | 並べ替え | O(n log n) |
| [`reverse`](#reverse) | <span class="rank rank-rare">知ってるだけ</span> | 逆順にする | O(n) |
| [`splice_after`](#splice_after) | <span class="rank rank-rare">知ってるだけ</span> | 別のリストから付け替える | O(1)〜O(n) |

`push_back`、`back`、`size` は**ありません**。

## よくある使い方

```cpp
#include <forward_list>
#include <print>

int main() {
  std::forward_list<int> l = {3, 4};
  l.push_front(2);
  l.push_front(1);
  l.insert_after(l.begin(), 9);  // 先頭の「後ろ」に 9
  std::println("{}", l);
}
```

```text title="実行結果"
[1, 9, 2, 3, 4]
```

## 関数の詳しい説明

### push_front {#push_front}

```cpp
void push_front(const T& value);
```

- 先頭に追加します。片方向リストで O(1) で追加できるのは先頭だけです

### pop_front {#pop_front}

```cpp
void pop_front();
```

- 先頭を消します。空のとき未定義動作

### front {#front}

```cpp
reference front();
```

- 先頭の要素。空のとき未定義動作

### empty {#empty}

```cpp
bool empty() const noexcept;
```

- 空なら `true`

### begin {#begin}

```cpp
iterator begin() noexcept;
```

- 先頭のイテレータ。`++` だけでき、`--` はできません

### end {#end}

```cpp
iterator end() noexcept;
```

- 最後の次のイテレータ

### insert_after {#insert_after}

```cpp
iterator insert_after(const_iterator pos, const T& value);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `pos` | `const_iterator` | この要素の**後ろ**に入れる |
| `value` | `const T&` | 入れる値 |

- 片方向リストは「前の要素」が分からないので、「前に入れる」ではなく「後ろに入れる」になります

### erase_after {#erase_after}

```cpp
iterator erase_after(const_iterator pos);
```

- `pos` の**次**の要素を消します

### before_begin {#before_begin}

```cpp
iterator before_begin() noexcept;
```

- 先頭の 1 つ前を指す特別なイテレータ。`insert_after(l.before_begin(), x)` で先頭に入れたり、`erase_after(l.before_begin())` で先頭を消したりするのに使います

```cpp
#include <forward_list>
#include <print>

int main() {
  std::forward_list<int> l = {2, 3};
  l.insert_after(l.before_begin(), 1);  // 先頭に 1
  l.erase_after(l.begin());             // 1 の次（2）を消す
  std::println("{} / 空？ {}", l, l.empty());
}
```

```text title="実行結果"
[1, 3] / 空？ false
```

### clear {#clear}

```cpp
void clear() noexcept;
```

- 全削除します

### emplace_front {#emplace_front}

```cpp
template <class... Args>
reference emplace_front(Args&&... args);
```

- 先頭にその場で構築します

### emplace_after {#emplace_after}

```cpp
template <class... Args>
iterator emplace_after(const_iterator pos, Args&&... args);
```

- `pos` の後ろにその場で構築します

### remove_if {#remove_if}

```cpp
template <class Pred>
size_type remove_if(Pred pred);
```

- 条件に合う要素を全部消します

### remove {#remove}

```cpp
size_type remove(const T& value);
```

- 値と等しい要素を全部消します

### sort {#sort}

```cpp
void sort();
```

- 並べ替えます。`std::ranges::sort` は使えません

### reverse {#reverse}

```cpp
void reverse() noexcept;
```

- 順番を逆にします

### splice_after {#splice_after}

```cpp
void splice_after(const_iterator pos, forward_list& other);
```

- `other` の要素を `pos` の後ろに付け替えます

```cpp
#include <forward_list>
#include <print>

int main() {
  std::forward_list<int> l = {5, 1, 4, 2};
  l.remove(4);
  l.sort();
  l.reverse();
  std::println("{}", l);
}
```

```text title="実行結果"
[5, 2, 1]
```

## ゲームでの使いどころ

ありません。[`std::vector`](vector.md) を使います。

## よくあるミス

??? failure "要素数を調べようとする"
    `size()` は無いので、`std::ranges::distance(l)` で数えます（O(n)）。何度も必要なら別のコンテナを使うべきです。

## 類似クラス

| 名前 | 違い |
| --- | --- |
| [`std::list`](list.md) | 双方向。`size` も `push_back` もある |
| [`std::vector`](vector.md) | ほとんどの場合こちらが速い |

## これだけ覚える

!!! abstract "まとめ"
    - [x] 片方向連結リスト。使わない

## 関連ページ

- [cpprefjp: std::forward_list](https://cpprefjp.github.io/reference/forward_list/forward_list.html)
- [cppreference: std::forward_list](https://en.cppreference.com/w/cpp/container/forward_list)
