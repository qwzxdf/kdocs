---
title: std::forward_list
summary: "片方向だけにつながるリスト。`list` より軽いが使う場面はほとんどない。"
order: 17
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

`std::forward_list` は、<strong>次の要素へのポインタだけを持つ「片方向連結リスト」</strong>です。[`std::list`](list.md) から「前の要素へのポインタ」を取り除いて、そのぶん 1 要素あたりのメモリを減らしたものです。前には戻れず、`size()` すらありません。

!!! tip "ポイント"
    - <strong>使わない。</strong> list でさえほぼ使わないので、その機能を削ったこれを使う場面はさらにない。
    - 「C で書いた片方向リストと同じ大きさ・速さのものが標準にある」と知っておけば十分。

!!! info "このページを読む前に"
    - [STL](../index.md)（STL 全体の地図（どこに何があるか））
    - [イテレータ](../../basics/iterator.md)（イテレーターの基礎）

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

<div class="anim" data-label="f.push_front(5)">
10 20 30 # f
+5 10 20 30 # 先頭につなぐ
</div>

### pop_front {#pop_front}

```cpp
void pop_front();
```

- 先頭を消します。空のとき未定義動作

<div class="anim" data-label="f.pop_front()">
10 20 30 # f
x10 20 30 # 先頭を外す
20 30 # 完了
</div>

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

<div class="anim" data-label="f.insert_after(it, 99)">
10 20 30 # it は 10 を指している
10 +99 20 30 # it の次に入れる。前には入れられない
</div>

### erase_after {#erase_after}

```cpp
iterator erase_after(const_iterator pos);
```

- `pos` の**次**の要素を消します

<div class="anim" data-label="f.erase_after(it)">
10 20 30 # it は 10 を指している
10 x20 30 # it の次を消す
10 30 # 完了
</div>

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

<div class="anim" data-label="f.remove_if(is_odd)">
1 2 3 4 # f
x1 2 x3 4 # 条件に合うノードを消す
2 4 # 完了
</div>

### remove {#remove}

```cpp
size_type remove(const T& value);
```

- 値と等しい要素を全部消します

<div class="anim" data-label="f.remove(2)">
1 2 3 2 # f
1 x2 3 x2 # 値が 2 のノードを消す
1 3 # 完了
</div>

### sort {#sort}

```cpp
void sort();
```

- 並べ替えます。`std::ranges::sort` は使えません

<div class="anim" data-label="f.sort()">
3 1 4 2 # f
>1 >2 >3 >4 # つなぎ替えて並べ替え
</div>

### reverse {#reverse}

```cpp
void reverse() noexcept;
```

- 順番を逆にします

<div class="anim" data-label="f.reverse()">
1 2 3 4 # f
>4 >3 >2 >1 # つなぎ替えで逆順
</div>

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

### assign {#assign}

```cpp
void assign(size_type n, const T& value);
template <class InputIt>
void assign(InputIt first, InputIt last);
void assign(std::initializer_list<T> il);
```

- 計算量: O(要素数)

中身を全部捨てて、新しい要素で置き換えます。

### assign_range <span class="ver ver-23">C++23</span> {#assign_range data-toc-label="assign_range"}

```cpp
template <ranges::input_range R>
void assign_range(R&& rg);
```

- 計算量: O(要素数)

範囲の要素で、中身を置き換えます。

### cbefore_begin {#cbefore_begin}

```cpp
const_iterator cbefore_begin() const noexcept;
```

- 計算量: 定数

先頭の手前を指す const イテレータ。`insert_after` の基点になります。

### insert_range_after <span class="ver ver-23">C++23</span> {#insert_range_after data-toc-label="insert_range_after"}

```cpp
template <ranges::input_range R>
iterator insert_range_after(const_iterator pos, R&& rg);
```

- 計算量: O(挿入数)

範囲の要素を `pos` の次に挿入します。

### prepend_range <span class="ver ver-23">C++23</span> {#prepend_range data-toc-label="prepend_range"}

```cpp
template <ranges::input_range R>
void prepend_range(R&& rg);
```

- 計算量: O(追加数)

範囲の要素を先頭に追加します。

### resize {#resize}

```cpp
void resize(size_type n);
void resize(size_type n, const T& value);
```

- 計算量: O(差)

要素数を `n` にします。増えるぶんは、既定値（または `value`）で埋め、減るぶんは末尾から削除します。

### unique {#unique}

```cpp
size_type unique();
template <class BinaryPred>
size_type unique(BinaryPred pred);
```

- 計算量: O(要素数)

隣り合う同じ要素を 1 つにまとめます（整列済みのリストで重複を消す）。

### merge <span class="ver ver-17">C++17</span> {#merge data-toc-label="merge"}

```cpp
template <class C2>
void merge(forward_list<..., C2>& source);
```

- 計算量: O(移動する要素数 × log n)

別のコンテナの要素をノードごとこちらへ移します。キーが重複するものは、移動元に残ります。

### operator= {#op_assign}

```cpp
forward_list& operator=(const forward_list& other);
forward_list& operator=(forward_list&& other) noexcept;
```

- 計算量: コピーは O(要素数)、ムーブは定数

コピー代入とムーブ代入。ムーブ代入は、中身の所有権を移すだけで、要素をコピーしません。

### operator== {#op_eq}

```cpp
bool operator==(const forward_list& a, const forward_list& b);
```

- 計算量: O(要素数)

要素の数が同じで、各要素が順に等しければ `true`。

### operator<=> <span class="ver ver-20">C++20</span> {#op_cmp data-toc-label="operator<=>"}

```cpp
auto operator<=>(const forward_list& a, const forward_list& b);
```

- 計算量: O(要素数)

要素を先頭から順に比べる、辞書順の三方比較。`<`・`>`・`<=`・`>=` も使えるようになります。

### cbegin {#cbegin}

```cpp
const_iterator cbegin() const noexcept;
```

- 計算量: 定数

先頭の要素を指す const イテレータ。要素を書き換えられないので、読むだけの走査で使います。

### cend {#cend}

```cpp
const_iterator cend() const noexcept;
```

- 計算量: 定数

終端（最後の要素の次）を指す const イテレータ。

### max_size {#max_size}

```cpp
size_type max_size() const noexcept;
```

- 計算量: 定数

理論上、入れられる最大の要素数。実装の上限で、実際にそれだけ確保できるとは限りません。

### get_allocator {#get_allocator}

```cpp
allocator_type get_allocator() const noexcept;
```

- 計算量: 定数

使っているアロケータのコピー。

### swap {#swap}

```cpp
void swap(forward_list& other) noexcept;
```

- 計算量: 定数

中身を `other` と入れ替えます。要素のコピーやムーブはせず、内部のポインタを入れ替えるだけなので速いです。

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
