---
title: std::multimap
summary: "同じキーを、複数持てる `map`。同じキーに複数の値をまとめたいときに。"
order: 18
tags:
  - コンテナ
---

# std::multimap

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="perf perf-3">○ 普通</span>
<span class="ver ver-11">C++98〜</span>
`#include <map>`
</div>

`std::multimap` は、**同じキーを何個でも持てる map** です。普通の [`std::map`](map.md) は同じキーを入れると上書きされませんが、multimap は全部残します。キーの順に並ぶのは map と同じです。キーだけを持つ版は [`std::multiset`](multiset.md)、順番なし版は [`std::unordered_multimap`](unordered_multimap.md) です。

!!! tip "ポイント"
    - <strong>ほとんど使わない。</strong> 同じキーに複数の値を持たせたいなら、`std::map<Key, std::vector<T>>` のほうが扱いやすいことが多い。
    - 使うなら、同じキーの要素は `equal_range` でまとめて取り出す。
    - `[]` は**無い**（どの要素か決められないため）。

!!! info "このページを読む前に"
    [`std::map`](map.md) を先に読んでください。

## 宣言

```cpp
template <class Key, class T, class Compare = std::less<Key>,
          class Allocator = std::allocator<std::pair<const Key, T>>>
class multimap;

```

## 関数一覧

`map` と違う点を中心に載せています。

| 関数 | 重要度 | 何をする | 計算量 |
| --- | --- | --- | --- |
| [`insert`](#insert) | <span class="rank rank-must">必須</span> | **同じキーでも必ず追加される** | O(log n) |
| [`equal_range`](#equal_range) | <span class="rank rank-must">必須</span> | 同じキーの要素の範囲を取る | O(log n) |
| [`begin`](#begin) | <span class="rank rank-must">必須</span> | 最小のキーのイテレータ | O(1) |
| [`end`](#end) | <span class="rank rank-must">必須</span> | 終わりのイテレータ | O(1) |
| [`count`](#count) | <span class="rank rank-often">よく使う</span> | 同じキーの個数（0 か 1 ではない） | O(log n + 個数) |
| [`erase`](#erase) | <span class="rank rank-often">よく使う</span> | キー版は**同じキーを全部消す** | O(log n + 個数) |
| [`find`](#find) | <span class="rank rank-often">よく使う</span> | 同じキーのどれか 1 つを探す | O(log n) |
| [`contains`](#contains) | <span class="rank rank-often">よく使う</span> | あるか | O(log n) |
| [`size`](#size) | <span class="rank rank-often">よく使う</span> | 要素数 | O(1) |
| [`empty`](#empty) | <span class="rank rank-often">よく使う</span> | 空か | O(1) |
| [`lower_bound`](#lower_bound) | <span class="rank rank-sometimes">たまに</span> | キーが以上の最初 | O(log n) |
| [`upper_bound`](#upper_bound) | <span class="rank rank-sometimes">たまに</span> | キーがより大きい最初 | O(log n) |
| [`emplace`](#emplace) | <span class="rank rank-sometimes">たまに</span> | その場で構築して追加 | O(log n) |
| [`clear`](#clear) | <span class="rank rank-sometimes">たまに</span> | 全削除 | O(n) |

`operator[]`、`at`、`try_emplace`、`insert_or_assign` は**ありません**（同じキーが複数あるので、どれを指すか決められないため）。

## よくある使い方

### 同点ありのランキング

```cpp
#include <functional>
#include <map>
#include <print>
#include <string>

int main() {
  std::multimap<int, std::string, std::greater<>> ranking;
  ranking.insert({1200, "Bob"});
  ranking.insert({3400, "Alice"});
  ranking.insert({1200, "Carol"});  // 同点でも消えない

  for (const auto& [score, name] : ranking) {
    std::println("{} {}", score, name);
  }

  // 1200 点の人だけ
  auto [first, last] = ranking.equal_range(1200);
  for (auto it = first; it != last; ++it) {
    std::println("1200 点: {}", it->second);
  }
}
```

```text title="実行結果"
3400 Alice
1200 Bob
1200 Carol
1200 点: Bob
1200 点: Carol
```

同じキーの要素は、**入れた順**に並びます。

## 関数の詳しい説明

### insert {#insert}

```cpp
iterator insert(const value_type& value);
```

- **同じキーがあっても必ず追加**されます。戻り値は追加した要素のイテレータだけ（`bool` は無い）
- 同じキーの要素は、入れた順に並びます

<div class="anim" data-label="m.insert({2, &quot;X&quot;})">
1 2 3 # キーは重複できる
1 2 +2 3 # 同じキーの後ろに入る
</div>

### equal_range {#equal_range}

```cpp
std::pair<iterator, iterator> equal_range(const Key& key);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `key` | `const Key&` | 取り出したいキー |

- 戻り値: キーが `key` と等しい要素の `[first, last)`。無ければ `first == last`

<div class="anim" data-label="m.equal_range(2)">
1 2 2 2 3 # キー
1 *2 *2 *2 3 # 同じキーの範囲をまとめて取る
</div>

```cpp
#include <map>
#include <print>
#include <string>

int main() {
  std::multimap<float, std::string> events;
  events.insert({1.0f, "敵出現"});
  events.insert({2.0f, "BGM 変更"});
  events.insert({1.0f, "宝箱出現"});

  auto [first, last] = events.equal_range(1.0f);
  for (auto it = first; it != last; ++it) {
    std::println("1 秒: {}", it->second);
  }
}
```

```text title="実行結果"
1 秒: 敵出現
1 秒: 宝箱出現
```

### begin {#begin}

```cpp
iterator begin() noexcept;
```

- 最小のキーの要素。範囲 for はキーの順（同じキーは入れた順）に回ります

### end {#end}

```cpp
iterator end() noexcept;
```

- 終わりのイテレータ

### count {#count}

```cpp
size_type count(const Key& key) const;
```

- 同じキーの要素がいくつあるか

<div class="anim" data-label="m.count(2)">
1 2 2 2 3 # キー
1 *2 *2 *2 3 # 同じキーの数（3）
</div>

### erase {#erase}

```cpp
size_type erase(const Key& key);
iterator erase(const_iterator pos);
```

- **キー版は同じキーを全部消します**。1 個だけ消すならイテレータ版を使います

<div class="anim" data-label="m.erase(2)">
1 2 2 2 3 # キー
1 x2 x2 x2 3 # 同じキーをすべて消す
1 3 # 完了
</div>

```cpp
#include <map>
#include <print>
#include <string>

int main() {
  std::multimap<int, std::string> m = {{1, "a"}, {1, "b"}, {2, "c"}};
  std::println("キー 1 は {} 個", m.count(1));
  m.erase(m.find(1));  // 1 個だけ消す
  std::println("キー 1 は {} 個", m.count(1));
  m.erase(1);  // 全部消す
  std::println("キー 1 は {} 個 / 全体 {} 個", m.count(1), m.size());
}
```

```text title="実行結果"
キー 1 は 2 個
キー 1 は 1 個
キー 1 は 0 個 / 全体 1 個
```

### find {#find}

```cpp
iterator find(const Key& key);
```

- 同じキーの要素のうち、**どれか 1 つ**のイテレータを返します（どれかは決まっていない）。全部欲しいなら `equal_range`

<div class="anim" data-label="m.find(2)">
1 2 2 3 # キー
1 *2 2 3 # 同じキーのうち最初の 1 つ
</div>

### contains {#contains}

```cpp
bool contains(const Key& key) const;
```

- 1 個以上あれば `true`

### size {#size}

```cpp
size_type size() const noexcept;
```

- 全要素数（同じキーも 1 個ずつ数える）

### empty {#empty}

```cpp
bool empty() const noexcept;
```

- 空なら `true`

### lower_bound {#lower_bound}

```cpp
iterator lower_bound(const Key& key);
```

- キーが `key` 以上の最初の要素（同じキーが複数あるなら、その最初）

<div class="anim" data-label="m.lower_bound(2)">
1 2 2 3 # キー
1 *2 2 3 # 2 以上で最初の要素
</div>

### upper_bound {#upper_bound}

```cpp
iterator upper_bound(const Key& key);
```

- キーが `key` より大きい最初の要素

<div class="anim" data-label="m.upper_bound(2)">
1 2 2 3 # キー
1 2 2 *3 # 2 より大きい最初の要素
</div>

### emplace {#emplace}

```cpp
template <class... Args>
iterator emplace(Args&&... args);
```

- その場で構築して追加します。必ず追加されます

### clear {#clear}

```cpp
void clear() noexcept;
```

- 全削除します

<div class="anim" data-label="m.clear()">
1 2 2 3 # キー
x1 x2 x2 x3 # すべて破棄
_ _ _ _ # 空
</div>

### emplace_hint {#emplace_hint}

```cpp
template <class... Args>
iterator emplace_hint(const_iterator hint, Args&&... args);
```

- 計算量: ヒントが正しければ償却定数

挿入される位置のヒント（直前の位置）を渡して、その場で要素を作ります。ヒントが合っていれば、償却定数で挿入できます。

### swap {#swap}

```cpp
void swap(multimap& other) noexcept;
```

- 計算量: 定数

中身を `other` と入れ替えます。要素のコピーやムーブはせず、内部のポインタを入れ替えるだけなので速いです。

### extract <span class="ver ver-17">C++17</span> {#extract data-toc-label="extract"}

```cpp
node_type extract(const_iterator pos);
node_type extract(const key_type& key);
```

- 計算量: O(log n)（順序つき）、平均 O(1)（unordered）

要素をコピーやムーブなしで、ノードごと取り出します。取り出したノードは、キーを書き換えたり、別のコンテナに `insert` したりできます。

### merge <span class="ver ver-17">C++17</span> {#merge data-toc-label="merge"}

```cpp
template <class C2>
void merge(multimap<..., C2>& source);
```

- 計算量: O(移動する要素数 × log n)

別のコンテナの要素を、ノードごとこちらへ移します。キーが重複するものは、移動元に残ります。

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

### rbegin {#rbegin}

```cpp
reverse_iterator rbegin() noexcept;
```

- 計算量: 定数

逆順の先頭（最後の要素）を指すイテレータ。後ろから前へ走査するときに使います。

### crbegin {#crbegin}

```cpp
const_reverse_iterator crbegin() const noexcept;
```

- 計算量: 定数

逆順の先頭（最後の要素）を指す const イテレータ。

### rend {#rend}

```cpp
reverse_iterator rend() noexcept;
```

- 計算量: 定数

逆順の終端（先頭の手前）を指すイテレータ。

### crend {#crend}

```cpp
const_reverse_iterator crend() const noexcept;
```

- 計算量: 定数

逆順の終端（先頭の手前）を指す const イテレータ。

### max_size {#max_size}

```cpp
size_type max_size() const noexcept;
```

- 計算量: 定数

理論上、入れられる最大の要素数。実装の上限で、実際にそれだけ確保できるとは限りません。

### key_comp {#key_comp}

```cpp
key_compare key_comp() const;
```

- 計算量: 定数

キーの比較に使っている関数オブジェクトのコピー。

### value_comp {#value_comp}

```cpp
value_compare value_comp() const;
```

- 計算量: 定数

要素（キーと値のペア）の比較に使っている関数オブジェクトのコピー。

### get_allocator {#get_allocator}

```cpp
allocator_type get_allocator() const noexcept;
```

- 計算量: 定数

使っているアロケータのコピー。

### operator= {#op_assign}

```cpp
multimap& operator=(const multimap& other);
multimap& operator=(multimap&& other) noexcept;
```

- 計算量: コピーは O(要素数)、ムーブは定数

コピー代入とムーブ代入。ムーブ代入は、中身の所有権を移すだけで、要素をコピーしません。

### operator== {#op_eq}

```cpp
bool operator==(const multimap& a, const multimap& b);
```

- 計算量: O(要素数)

要素の数が同じで、各要素が順に等しければ `true`。

### operator<=> <span class="ver ver-20">C++20</span> {#op_cmp data-toc-label="operator<=>"}

```cpp
auto operator<=>(const multimap& a, const multimap& b);
```

- 計算量: O(要素数)

要素を先頭から順に比べる、辞書順の三方比較。`<`・`>`・`<=`・`>=` も使えるようになります。

## ゲームでの使いどころ

| 場面 | 例 |
| --- | --- |
| 同点ありのランキング | スコア → 名前 |
| 同時刻のイベント | 時刻 → イベント（同じ時刻に複数） |

どちらも「vector に入れて `std::ranges::stable_sort`」で代用できます。

## よくあるミス

??? failure "erase(key) で 1 個だけ消すつもりが全部消える"
    ```cpp
    ranking.erase(1200);  // 1200 点の人が全員消える

    // 1 個だけ消すならイテレータで
    if (auto it = ranking.find(1200); it != ranking.end()) {
      ranking.erase(it);
    }
    ```

## 類似クラス

| 名前 | 違い | こっちを使うとき |
| --- | --- | --- |
| [`std::map`](map.md) | キーの重複なし | ほとんどの場合 |
| [`std::multiset`](multiset.md) | 値を持たず、キーだけ（重複あり） | 値が要らないとき |
| `std::map<Key, std::vector<T>>` | 同じキーの値を vector にまとめる | 同じキーの値をまとめて扱いたい |
| [`std::unordered_multimap`](unordered_multimap.md) | 順番なし（ハッシュ表） | 順番が要らない |

## これだけ覚える

!!! abstract "まとめ"
    - [x] 同じキーを何個でも持てる map
    - [x] 取り出すのは `equal_range`、`[]` は無い
    - [x] `erase(key)` は同じキーを全部消す

## 関連ページ

- [cpprefjp: std::multimap](https://cpprefjp.github.io/reference/map/multimap.html)
- [cppreference: std::multimap](https://en.cppreference.com/w/cpp/container/multimap)
