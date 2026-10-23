---
title: std::flat_set
summary: "`vector` で作った `set`。検索と巡回が速い。挿入・削除は遅い。"
order: 19
tags:
  - コンテナ
---

# std::flat_set

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="perf perf-3">○ 普通</span>
<span class="ver ver-23">C++23</span>
`#include <flat_set>`
</div>

`std::flat_set` は、**中身がソート済みの vector になっている set** です。[`std::flat_map`](flat_map.md) のキーだけ版で、使い方は [`std::set`](set.md) と同じです。検索と全要素のループは set より速く、途中の追加・削除は O(n) で遅くなります。

!!! tip "ポイント"
    - <strong>作ってから変更しない「集合」に使う。</strong> 使い方は set と同じ。
    - 実は「vector に入れて sort して unique」したものとほぼ同じ。そちらで代用しても十分。

!!! info "このページを読む前に"
    - [stl/index.md](../index.md)（STL 全体の地図（どこに何があるか））
    - [イテレータ](../../basics/iterator.md)（イテレーターの基礎）

## 宣言

```cpp
template <class Key, class Compare = std::less<Key>,
          class KeyContainer = std::vector<Key>>
class flat_set;
```

## 関数一覧

set と同じ関数は同じ意味で、違うのは計算量だけです。

| 関数 | 重要度 | 何をする | 計算量（flat_set） | 計算量（set） |
| --- | --- | --- | --- | --- |
| [`contains`](#contains) | <span class="rank rank-must">必須</span> | 入っているか | O(log n)（速い） | O(log n) |
| [`begin`](#begin) | <span class="rank rank-must">必須</span> | 最小の値（範囲 for は小さい順） | O(1) | O(1) |
| [`end`](#end) | <span class="rank rank-must">必須</span> | 終わり | O(1) | O(1) |
| [`size`](#size) | <span class="rank rank-often">よく使う</span> | 要素数 | O(1) | O(1) |
| [`empty`](#empty) | <span class="rank rank-often">よく使う</span> | 空か | O(1) | O(1) |
| [`find`](#find) | <span class="rank rank-often">よく使う</span> | 探す | O(log n) | O(log n) |
| [`lower_bound`](#lower_bound) | <span class="rank rank-sometimes">たまに</span> | 以上の最初 | O(log n) | O(log n) |
| [`insert`](#insert) | <span class="rank rank-sometimes">たまに</span> | 追加 | <strong>O(n)</strong> | O(log n) |
| [`erase`](#erase) | <span class="rank rank-sometimes">たまに</span> | 削除 | <strong>O(n)</strong> | O(log n) |
| [`extract`](#extract) | <span class="rank rank-rare">知ってるだけ</span> | 中の vector を取り出す | O(1) | — |
| [`replace`](#replace) | <span class="rank rank-rare">知ってるだけ</span> | 中の vector を入れ替える | O(1) | — |

## よくある使い方

```cpp
#include <flat_set>
#include <print>

int main() {
  std::flat_set<int> walls = {12, 3, 7, 3, 20};  // 壁のあるマス番号
  std::println("{}", walls);
  std::println("7 は壁？ {}", walls.contains(7));
}
```

```text title="実行結果"
{3, 7, 12, 20}
7 は壁？ true
```

## 関数の詳しい説明

### contains {#contains}

```cpp
bool contains(const Key& key) const;
```

- 入っていれば `true`。二分探索なので set より速く引けます

<div class="anim" data-label="s.contains(5)">
1 3 5 7 9 # 整列した配列
1 3 *5 7 9 # 二分探索
</div>

### begin {#begin}

```cpp
iterator begin() noexcept;
```

- 最小の値。中身はソート済み vector なので、範囲 for はとても速いです

### end {#end}

```cpp
iterator end() noexcept;
```

- 終わりのイテレータ

### size {#size}

```cpp
size_type size() const noexcept;
```

- 要素数

### empty {#empty}

```cpp
bool empty() const noexcept;
```

- 空なら `true`

### find {#find}

```cpp
iterator find(const Key& key);
```

- 見つかった要素のイテレータ。無ければ `end()`

<div class="anim" data-label="s.find(5)">
1 3 5 7 9 # 整列した配列
1 3 *5 7 9 # 二分探索
</div>

### lower_bound {#lower_bound}

```cpp
iterator lower_bound(const Key& key);
```

- 以上の最初の要素

<div class="anim" data-label="s.lower_bound(4)">
1 3 5 7 # 整列した配列
1 3 *5 7 # 4 以上で最初の要素
</div>

### insert {#insert}

```cpp
std::pair<iterator, bool> insert(const value_type& value);
template <class InputIt>
void insert(InputIt first, InputIt last);
```

- 1 個版は後ろをずらすので O(n)。たくさん入れるなら範囲版を使います

<div class="anim" data-label="s.insert(4)">
1 3 5 # 整列した配列
1 3 _ >5 # 後ろをずらす
1 3 +4 5 # すき間に入れる
</div>

### erase {#erase}

```cpp
size_type erase(const Key& key);
```

- 削除します。後ろを詰めるので O(n)

<div class="anim" data-label="s.erase(3)">
1 3 5 7 # 整列した配列
1 x3 5 7 # 消す
1 >5 >7 _ # 後ろを詰める
</div>

```cpp
#include <flat_set>
#include <print>

int main() {
  std::flat_set<int> s = {5, 1, 3};
  s.insert(4);
  s.erase(1);
  std::println("{} / 最小 {} / 4 はある？ {}", s, *s.begin(), s.contains(4));
}
```

```text title="実行結果"
{3, 4, 5} / 最小 3 / 4 はある？ true
```

### extract {#extract}

```cpp
container_type extract() &&;
```

- 中のソート済み vector を取り出します。flat_set は空になります

### replace {#replace}

```cpp
void replace(container_type&& cont);
```

- vector を丸ごと入れ替えます。ソート済み・重複なしである必要があります

## フラグ・オプション

| 値 | 意味 |
| --- | --- |
| `std::sorted_unique` | 渡すデータがソート済み・重複なしであることを示す（[flat_map 参照](flat_map.md#フラグオプション)） |

## ゲームでの使いどころ

マップ読み込み時に作る「通れないマス」「イベントのあるマス」の集合など、変更しないものに使えます。

## 類似クラス

| 名前 | 違い |
| --- | --- |
| [`std::set`](set.md) | 追加・削除が速い |
| [`std::unordered_set`](unordered_set.md) | 順番なし |
| vector + sort + unique | 同じことを手で書く |

## コンパイラ対応

| 機能 | MSVC | GCC | Clang (libc++) |
| --- | --- | --- | --- |
| `std::flat_set` <span class="ver ver-23">C++23</span> | VS 2026 18.6 で使用可（18.2 以前は未対応） | 15〜 | 21〜 |

## これだけ覚える

!!! abstract "まとめ"
    - [x] ソート済み vector の set
    - [x] 作ってから変更しない集合に使う

## 関連ページ

- [cpprefjp: std::flat_set](https://cpprefjp.github.io/reference/flat_set/flat_set.html)
- [cppreference: std::flat_set](https://en.cppreference.com/w/cpp/container/flat_set)
