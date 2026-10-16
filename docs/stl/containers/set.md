---
title: std::set
tags:
  - コンテナ
---

# std::set

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="perf perf-3">○ 普通</span>
<span class="ver ver-11">C++98〜</span>
`#include <set>`
</div>

`std::set` は、**重複しない値を小さい順に並べて持つ集合**です。[`std::map`](map.md) から値を取り除いてキーだけにしたもの、または [`std::unordered_set`](unordered_set.md) に「順番」を足したものと考えると分かりやすいです。

!!! tip "結論"
    - **重複を除いて、しかも順番に並べたいときに使う。** 順番が要らないなら `unordered_set`。
    - 使い方は `unordered_set` と同じ（`insert` / `contains` / `erase`）。
    - map と同じく `lower_bound` / `upper_bound` で範囲検索ができる。
    - 一番小さい値は `*s.begin()`、一番大きい値は `*s.rbegin()`。

!!! info "このページを読む前に"
    [`std::map`](map.md) と [`std::unordered_set`](unordered_set.md) の差分だけで理解できます。

## 宣言

```cpp
template <class Key, class Compare = std::less<Key>,
          class Allocator = std::allocator<Key>>
class set;
```

| テンプレート引数 | 意味 | 指定する？ |
| --- | --- | --- |
| `Key` | 入れる値の型。`<` で比較できる必要がある | 必ず |
| `Compare` | 並べる順番 | 逆順（`std::greater<>`）、透過比較（`std::less<>`）にしたいとき |
| `Allocator` | メモリの確保方法 | しない |

## 関数一覧

| 関数 | 重要度 | 何をする | 計算量 |
| --- | --- | --- | --- |
| [`insert`](#insert) | <span class="rank rank-must">必須</span> | 追加（既にあれば何もしない） | O(log n) |
| [`contains`](#contains) | <span class="rank rank-must">必須</span> | 入っているか <span class="ver ver-20">C++20</span> | O(log n) |
| [`erase`](#erase) | <span class="rank rank-must">必須</span> | 削除 | O(log n) |
| [`begin`](#begin) | <span class="rank rank-must">必須</span> | **最小の値**のイテレータ（範囲 for は小さい順） | O(1) |
| [`end`](#end) | <span class="rank rank-must">必須</span> | 終わりのイテレータ | O(1) |
| [`size`](#size) | <span class="rank rank-often">よく使う</span> | 要素数 | O(1) |
| [`empty`](#empty) | <span class="rank rank-often">よく使う</span> | 空か | O(1) |
| [`rbegin`](#rbegin) | <span class="rank rank-often">よく使う</span> | **最大の値**のイテレータ | O(1) |
| [`lower_bound`](#lower_bound) | <span class="rank rank-sometimes">たまに</span> | 以上の最初の要素 | O(log n) |
| [`upper_bound`](#upper_bound) | <span class="rank rank-sometimes">たまに</span> | より大きい最初の要素 | O(log n) |
| [`find`](#find) | <span class="rank rank-sometimes">たまに</span> | 探してイテレータを返す | O(log n) |
| [`clear`](#clear) | <span class="rank rank-sometimes">たまに</span> | 全削除 | O(n) |
| [`std::erase_if`](#erase_if) | <span class="rank rank-sometimes">たまに</span> | 条件で削除 <span class="ver ver-20">C++20</span> | O(n) |
| [`emplace`](#emplace) | <span class="rank rank-rare">知ってるだけ</span> | その場で構築して追加 | O(log n) |
| [`rend`](#rend) | <span class="rank rank-rare">知ってるだけ</span> | 逆順の終わり | O(1) |
| [`equal_range`](#equal_range) | <span class="rank rank-rare">知ってるだけ</span> | 等しい範囲 | O(log n) |
| [`count`](#count) | <span class="rank rank-rare">知ってるだけ</span> | `contains` で十分 | O(log n) |
| [`extract`](#extract) | <span class="rank rank-rare">知ってるだけ</span> | ノードとして取り外す <span class="ver ver-17">C++17</span> | O(log n) |
| [`merge`](#merge) | <span class="rank rank-rare">知ってるだけ</span> | 別の set から移す <span class="ver ver-17">C++17</span> | O(m log n) |
| [`swap`](#swap) | <span class="rank rank-rare">知ってるだけ</span> | 中身を交換 | O(1) |

## よくある使い方

### 1. 重複を除いて並べる

```cpp
#include <print>
#include <set>
#include <vector>

int main() {
  std::vector<int> cleared = {3, 1, 4, 1, 5, 9, 2, 6, 5, 3};
  std::set<int> stages(cleared.begin(), cleared.end());

  std::println("クリアしたステージ: {}", stages);
  std::println("最小 {} / 最大 {}", *stages.begin(), *stages.rbegin());
}
```

```text title="実行結果"
クリアしたステージ: {1, 2, 3, 4, 5, 6, 9}
最小 1 / 最大 9
```

set を `println` すると `{}` で囲まれて出てきます。

### 2. 空いている一番小さい番号を探す

```cpp
#include <print>
#include <set>

int main() {
  // 空いているスロット番号
  std::set<int> free_slots = {0, 1, 2, 3, 4};

  // 一番小さい番号を使う
  auto take = [&] {
    int id = *free_slots.begin();
    free_slots.erase(free_slots.begin());
    return id;
  };

  int a = take();
  int b = take();
  free_slots.insert(a);  // a を返却
  int c = take();
  std::println("{} {} {}", a, b, c);
}
```

```text title="実行結果"
0 1 0
```

## 関数の詳しい説明

使い方の多くは [`std::unordered_set`](unordered_set.md) と同じです。違うのは**計算量が O(log n)** であることと、**小さい順に並んでいる**ことです。

### insert {#insert}

```cpp
std::pair<iterator, bool> insert(const value_type& value);
void insert(InputIt first, InputIt last);
void insert(std::initializer_list<value_type> ilist);
```

- 戻り値: 1 個版は `pair<イテレータ, 新しく入ったか>`
- 計算量: O(log n)

```cpp
#include <print>
#include <set>

int main() {
  std::set<int> s;
  s.insert(30);
  s.insert(10);
  s.insert(20);
  s.insert(10);  // 重複は無視
  std::println("{}", s);
}
```

```text title="実行結果"
{10, 20, 30}
```

### contains <span class="ver ver-20">C++20</span> {#contains data-toc-label="contains"}

```cpp
bool contains(const Key& key) const;
```

- 入っていれば `true`。O(log n)

### erase {#erase}

```cpp
size_type erase(const Key& key);
iterator erase(const_iterator pos);
iterator erase(const_iterator first, const_iterator last);
```

- キー版は消した数、位置版は次の要素のイテレータを返します

```cpp
#include <print>
#include <set>

int main() {
  std::set<int> s = {1, 2, 3, 4, 5, 6};
  s.erase(3);
  s.erase(s.lower_bound(5), s.end());  // 5 以上を全部消す
  std::println("{} {}", s, s.contains(3));
}
```

```text title="実行結果"
{1, 2, 4} false
```

### begin {#begin}

```cpp
iterator begin() noexcept;
```

- **一番小さい値**のイテレータ。範囲 for は小さい順に回ります
- 空のときに `*s.begin()` すると未定義動作

### end {#end}

```cpp
iterator end() noexcept;
```

- 最後の次。`find` や `lower_bound` が「見つからない」ときに返します

### size {#size}

```cpp
size_type size() const noexcept;
```

- 要素数。O(1)

### empty {#empty}

```cpp
bool empty() const noexcept;
```

- 空なら `true`。O(1)

### rbegin {#rbegin}

```cpp
reverse_iterator rbegin() noexcept;
```

- **一番大きい値**を指す逆向きのイテレータ

```cpp
#include <print>
#include <set>

int main() {
  std::set<int> s = {7, 3, 9, 1};
  if (!s.empty()) {
    std::println("最小 {} / 最大 {} / 個数 {}", *s.begin(), *s.rbegin(), s.size());
  }
}
```

```text title="実行結果"
最小 1 / 最大 9 / 個数 4
```

### lower_bound {#lower_bound}

```cpp
iterator lower_bound(const Key& key);
```

- `key` **以上**の最初の要素。無ければ `end()`（[map の lower_bound](map.md#lower_bound) と同じ）

### upper_bound {#upper_bound}

```cpp
iterator upper_bound(const Key& key);
```

- `key` **より大きい**最初の要素。無ければ `end()`

```cpp
#include <print>
#include <set>

int main() {
  std::set<int> checkpoints = {0, 100, 250, 400};
  int x = 180;
  // x より先にある最初のチェックポイント
  if (auto it = checkpoints.upper_bound(x); it != checkpoints.end()) {
    std::println("次のチェックポイント: {}", *it);
  }
  std::println("x 以上: {}", *checkpoints.lower_bound(250));
}
```

```text title="実行結果"
次のチェックポイント: 250
x 以上: 250
```

### find {#find}

```cpp
iterator find(const Key& key);
```

- 見つかった要素のイテレータ。無ければ `end()`

### clear {#clear}

```cpp
void clear() noexcept;
```

- 全要素を削除します。O(n)

### std::erase_if <span class="ver ver-20">C++20</span> {#erase_if data-toc-label="std::erase_if"}

```cpp
template <class K, class C, class A, class Pred>
size_type erase_if(std::set<K, C, A>& c, Pred pred);
```

- `true` を返した要素を消します

```cpp
#include <print>
#include <set>

int main() {
  std::set<int> s = {1, 2, 3, 4, 5};
  std::erase_if(s, [](int x) { return x % 2 == 1; });
  std::println("{}", s);
}
```

```text title="実行結果"
{2, 4}
```

### emplace {#emplace}

```cpp
template <class... Args>
std::pair<iterator, bool> emplace(Args&&... args);
```

- 要素をその場で作って追加します

### rend {#rend}

```cpp
reverse_iterator rend() noexcept;
```

- 逆順の終わり。`rbegin` から `rend` まで回すと大きい順になります

### equal_range {#equal_range}

```cpp
std::pair<iterator, iterator> equal_range(const Key& key);
```

- `{lower_bound(key), upper_bound(key)}`。set では 0 個か 1 個の範囲です（[multiset](multimap.md#equal_range) 向け）

### count {#count}

```cpp
size_type count(const Key& key) const;
```

- 0 か 1 を返します。今は `contains` を使います

### extract <span class="ver ver-17">C++17</span> {#extract data-toc-label="extract"}

```cpp
node_type extract(const Key& key);
```

- 要素をノードとして取り外します。`node.value()` を書き換えて入れ直すと、「値を変更する」ことができます

```cpp
#include <print>
#include <set>
#include <utility>

int main() {
  std::set<int> s = {1, 5, 9};
  auto node = s.extract(5);
  node.value() = 7;  // 値を書き換える
  s.insert(std::move(node));
  std::println("{}", s);
}
```

```text title="実行結果"
{1, 7, 9}
```

### merge <span class="ver ver-17">C++17</span> {#merge data-toc-label="merge"}

```cpp
void merge(set& source);
```

- `source` の要素をこちらへ移します。重複するものは `source` に残ります

### swap {#swap}

```cpp
void swap(set& other) noexcept;
```

- 中身を交換します。O(1)

## フラグ・オプション

`Compare` の指定は [`std::map` のフラグ・オプション](map.md#フラグオプション) と同じです。

## 計算量まとめ

| 操作 | 計算量 |
| --- | --- |
| `insert`, `contains`, `erase`, `find`, `lower_bound` | O(log n) |
| 最小・最大 | O(1) |

## ゲームでの使いどころ

| 場面 | 例 |
| --- | --- |
| 空き番号の管理 | 一番小さい空き ID・空きスロットを使う |
| 順番付きの集合 | クリアしたステージ番号の一覧表示 |
| 優先度を変えられるキュー | `set<pair<コスト, マス>>` で、古いものを `erase` して入れ直す |

## パフォーマンス

map と同じく、要素は木のノードとしてバラバラに確保されます。順番が要らないなら unordered_set、作ってから変更しないなら [`std::flat_set`](flat_set.md) か「vector + sort + unique」のほうが速いです。

## よくあるミス

??? failure "要素を書き換えようとする"
    set の要素は `const` です。書き換えると並び順が崩れるためです。消してから入れ直します。

??? failure "重複を残したいのに set を使う"
    同じ値を何個も持ちたいなら [`std::multiset`](multimap.md) です。

## 理解度チェック

!!! question "Q1. 何が出力される？"
    ```cpp
    std::set<int> s = {5, 3, 5, 1};
    std::println("{}", s);
    ```

    <div class="spoiler" markdown>

    **答え:** `{1, 3, 5}`。重複が除かれ、小さい順に並びます。

    </div>

## 類似クラス

| 名前 | 違い | こっちを使うとき |
| --- | --- | --- |
| [`std::unordered_set`](unordered_set.md) | 順番なし。平均 O(1) | 順番が要らない |
| [`std::map`](map.md) | 値も持てる | キーに対応するデータがある |
| [`std::flat_set`](flat_set.md) | ソート済み vector <span class="ver ver-23">C++23</span> | 作ってから変更しない |
| [`std::multiset`](multimap.md) | 重複を許す | 同じ値を何個も持つ |

## コンパイラ対応

C++98 からある機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 重複なし・小さい順に並ぶ集合
    - [x] 使い方は unordered_set と同じ
    - [x] 最小は `*s.begin()`、最大は `*s.rbegin()`

## 関連ページ

- [cpprefjp: std::set](https://cpprefjp.github.io/reference/set/set.html)
- [cppreference: std::set](https://en.cppreference.com/w/cpp/container/set)
