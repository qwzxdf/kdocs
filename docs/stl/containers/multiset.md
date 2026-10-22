---
title: std::multiset
summary: "同じ値を複数持てる set。キーの順に並ぶ。同点を残したいときに。"
order: 19
tags:
  - コンテナ
---

# std::multiset

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="perf perf-3">○ 普通</span>
<span class="ver ver-11">C++98〜</span>
`#include <set>`
</div>

`std::multiset` は、**同じ値を何個でも持てる set** です。普通の [`std::set`](set.md) は同じ値を入れても 1 つしか残りませんが、multiset は全部残します。値は小さい順に並び、同じ値は入れた順に並びます。

!!! tip "ポイント"
    - <strong>ほとんど使わない。</strong> 「個数を数えたいだけ」なら `std::map<T, int>` のほうが扱いやすい。
    - **同点を残したまま、整列した状態を保ちたい**ときに使う（スコアの一覧、待ち時間の一覧）。
    - `[]` は**無い**。同じ値の範囲は `equal_range` で取る。

!!! info "このページを読む前に"
    [`std::set`](set.md) を先に読んでください。

## 宣言

```cpp
template <class Key, class Compare = std::less<Key>,
          class Allocator = std::allocator<Key>>
class multiset;
```

| テンプレート引数 | 意味 | 指定する？ |
| --- | --- | --- |
| `Key` | 要素の型 | 必ず |
| `Compare` | 並べる順の比較 | 大きい順なら `std::greater<Key>`（任意） |

## 関数一覧

`set` と違う点を中心に載せています。

| 関数 | 重要度 | 何をする | 計算量 |
| --- | --- | --- | --- |
| [`insert`](#insert) | <span class="rank rank-must">必須</span> | **同じ値でも必ず追加される** | O(log n) |
| [`equal_range`](#equal_range) | <span class="rank rank-must">必須</span> | 同じ値の要素の範囲を取る | O(log n) |
| [`count`](#count) | <span class="rank rank-often">よく使う</span> | 同じ値の個数（0 か 1 ではない） | O(log n + 個数) |
| [`erase`](#erase) | <span class="rank rank-often">よく使う</span> | 値版は**同じ値を全部消す** | O(log n + 個数) |
| [`find`](#find) | <span class="rank rank-often">よく使う</span> | 同じ値のどれか 1 つを探す | O(log n) |
| [`contains`](#contains) | <span class="rank rank-often">よく使う</span> | あるか | O(log n) |
| [`lower_bound`](#lower_bound) | <span class="rank rank-sometimes">たまに</span> | 値が以上の最初 | O(log n) |
| [`upper_bound`](#upper_bound) | <span class="rank rank-sometimes">たまに</span> | 値がより大きい最初 | O(log n) |

`begin` / `end` / `size` / `empty` / `clear` / `emplace` は `set` と同じです。`operator[]` と `at` は**ありません**。

## よくある使い方

### 同点を残したまま、整列した状態を保つ

```cpp
#include <print>
#include <set>

int main() {
  std::multiset<int> scores;
  scores.insert(300);
  scores.insert(500);
  scores.insert(300);  // 同じ値でも消えない

  for (int s : scores) {
    std::print("{} ", s);
  }
  std::println("");
  std::println("300 点は {} 人", scores.count(300));
}
```

```text title="実行結果"
300 300 500
300 点は 2 人
```

## 関数の詳しい説明

### insert {#insert}

```cpp
iterator insert(const Key& value);
```

- **同じ値があっても必ず追加**されます。戻り値は追加した要素のイテレータだけ（`bool` は無い）
- 計算量: O(log n)

<div class="anim" data-label="s.insert(2)">
1 2 3 # 値は重複できる
1 2 +2 3 # 同じ値の後ろに入る
</div>

### equal_range {#equal_range}

```cpp
std::pair<iterator, iterator> equal_range(const Key& value);
```

- 戻り値: 値が `value` と等しい要素の `[first, last)`。無ければ `first == last`
- 計算量: O(log n)

```cpp
#include <iterator>
#include <print>
#include <set>

int main() {
  std::multiset<int> s = {1, 2, 2, 2, 3};

  auto [first, last] = s.equal_range(2);
  std::println("2 は {} 個", std::distance(first, last));
}
```

```text title="実行結果"
2 は 3 個
```

### count {#count}

```cpp
size_type count(const Key& value) const;
```

- 同じ値の個数。`set` では 0 か 1 ですが、`multiset` では 2 以上になります
- 計算量: O(log n + 個数)

### erase {#erase}

```cpp
size_type erase(const Key& value);
iterator erase(const_iterator pos);
```

- **値版は同じ値を全部消します**。戻り値は消した個数。1 個だけ消すならイテレータ版を使います

```cpp
#include <print>
#include <set>

int main() {
  std::multiset<int> s = {1, 2, 2, 2, 3};

  s.erase(s.find(2));  // 1 個だけ消す
  std::println("2 は {} 個", s.count(2));
  s.erase(2);          // 残りを全部消す
  std::println("2 は {} 個 / 全体 {} 個", s.count(2), s.size());
}
```

```text title="実行結果"
2 は 2 個
2 は 0 個 / 全体 2 個
```

### find {#find}

```cpp
iterator find(const Key& value);
```

- 同じ値のうち、**どれか 1 つ**のイテレータを返します。無ければ `end()`

### contains {#contains}

```cpp
bool contains(const Key& value) const;
```

- 1 個以上あれば `true`（C++20）

### lower_bound {#lower_bound}

```cpp
iterator lower_bound(const Key& value);
```

- `value` 以上の最初の要素

### upper_bound {#upper_bound}

```cpp
iterator upper_bound(const Key& value);
```

- `value` より大きい最初の要素。`lower_bound` との間が、同じ値の範囲

### emplace {#emplace}

```cpp
template <class... Args>
iterator emplace(Args&&... args);
```

- 計算量: O(log n)（順序つき）、平均 O(1)（unordered）

引数から、その場で要素を作って挿入します。コピーやムーブを避けられます。

### emplace_hint {#emplace_hint}

```cpp
template <class... Args>
iterator emplace_hint(const_iterator hint, Args&&... args);
```

- 計算量: ヒントが正しければ償却定数

挿入される位置のヒント（直前の位置）を渡して、その場で要素を作ります。ヒントが合っていれば、償却定数で挿入できます。

### swap {#swap}

```cpp
void swap(multiset& other) noexcept;
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
void merge(multiset<..., C2>& source);
```

- 計算量: O(移動する要素数 × log n)

別のコンテナの要素を、ノードごとこちらへ移します。キーが重複するものは、移動元に残ります。

### begin {#begin}

```cpp
iterator begin() noexcept;
const_iterator begin() const noexcept;
```

- 計算量: 定数

先頭の要素を指すイテレータ。空なら `end()` と同じ。

### cbegin {#cbegin}

```cpp
const_iterator cbegin() const noexcept;
```

- 計算量: 定数

先頭の要素を指す const イテレータ。要素を書き換えられないので、読むだけの走査で使います。

### end {#end}

```cpp
iterator end() noexcept;
const_iterator end() const noexcept;
```

- 計算量: 定数

終端（最後の要素の次）を指すイテレータ。この位置は読めません。

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

### empty {#empty}

```cpp
[[nodiscard]] bool empty() const noexcept;
```

- 計算量: 定数

要素が 1 つもなければ `true`。`size() == 0` より意図が伝わります。

### size {#size}

```cpp
size_type size() const noexcept;
```

- 計算量: 定数

要素の数。

### max_size {#max_size}

```cpp
size_type max_size() const noexcept;
```

- 計算量: 定数

理論上、入れられる最大の要素数。実装の上限で、実際にそれだけ確保できるとは限りません。

### clear {#clear}

```cpp
void clear() noexcept;
```

- 計算量: O(要素数)

全ての要素を削除します。メモリは返さないことがあります。

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
multiset& operator=(const multiset& other);
multiset& operator=(multiset&& other) noexcept;
```

- 計算量: コピーは O(要素数)、ムーブは定数

コピー代入とムーブ代入。ムーブ代入は、中身の所有権を移すだけで、要素をコピーしません。

### operator== {#op_eq}

```cpp
bool operator==(const multiset& a, const multiset& b);
```

- 計算量: O(要素数)

要素の数が同じで、各要素が順に等しければ `true`。

### operator<=> <span class="ver ver-20">C++20</span> {#op_cmp data-toc-label="operator<=>"}

```cpp
auto operator<=>(const multiset& a, const multiset& b);
```

- 計算量: O(要素数)

要素を先頭から順に比べる、辞書順の三方比較。`<`・`>`・`<=`・`>=` も使えるようになります。

## ゲームでの使いどころ

| 場面 | 例 |
| --- | --- |
| 同点を残した整列済みの一覧 | スコア、タイム |
| 同時刻のイベントの待ち行列 | 発火時刻のみを順に取り出す |
| 中央値・上位 N 件の管理 | 追加のたびに整列が保たれる |

## よくあるミス

??? failure "erase(値) で 1 個だけ消すつもりが全部消える"
    ```cpp
    scores.erase(300);  // 300 点が全部消える

    // 1 個だけ消すならイテレータで
    if (auto it = scores.find(300); it != scores.end()) {
      scores.erase(it);
    }
    ```

## 類似クラス

| 名前 | 違い | こっちを使うとき |
| --- | --- | --- |
| [`std::set`](set.md) | 同じ値は 1 つだけ | ほとんどの場合 |
| [`std::multimap`](multimap.md) | キーに値が付く | 同じキーに値を付けたい |
| [`std::unordered_multiset`](unordered_multiset.md) | 順番なし | 順番が要らない |
| [`std::priority_queue`](priority_queue.md) | 最大（最小）だけを取り出す | 先頭しか使わない |

## これだけ覚える

!!! abstract "まとめ"
    - [x] 同じ値を何個でも持てる set
    - [x] 取り出すのは `equal_range`、`[]` は無い
    - [x] `erase(値)` は同じ値を全部消す

## 関連ページ

- [cpprefjp: std::multiset](https://cpprefjp.github.io/reference/set/multiset.html)
- [cppreference: std::multiset](https://en.cppreference.com/w/cpp/container/multiset)
