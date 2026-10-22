---
title: std::unordered_multiset
summary: "同じ値を複数持てる、ハッシュ表の set。順番はない。"
order: 21
tags:
  - コンテナ
---

# std::unordered_multiset

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="perf perf-3">○ 普通</span>
<span class="ver ver-11">C++11</span>
`#include <unordered_set>`
</div>

`std::unordered_multiset` は、**同じ値を何個でも持てる、ハッシュ表の set** です。[`std::unordered_set`](unordered_set.md) は同じ値を 1 つにしますが、こちらは全部残します。「何個入っているか」を数えるのが主な使い道です。

!!! tip "ポイント"
    - <strong>ほとんど使わない。</strong> 個数を数えたいだけなら `unordered_map<T, int>` のほうが分かりやすい。
    - `count(値)` で個数が取れる。
    - 順番は決まっていない。

!!! info "このページを読む前に"
    [`std::unordered_set`](unordered_set.md) を先に読んでください。

## 宣言

```cpp
template <class Key, class Hash = std::hash<Key>, class KeyEqual = std::equal_to<Key>,
          class Allocator = std::allocator<Key>>
class unordered_multiset;
```

## 関数の詳しい説明

### insert {#insert}

```cpp
iterator insert(const Key& value);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `value` | `const Key&` | 追加する値 |

- 戻り値: 追加した要素のイテレータ。**同じ値があっても必ず追加**される
- 計算量: 平均 O(1)

### count {#count}

```cpp
size_type count(const Key& value) const;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `value` | `const Key&` | 数えたい値 |

- 戻り値: 同じ値の個数
- 計算量: 平均 O(個数)

```cpp
#include <print>
#include <unordered_set>

int main() {
  std::unordered_multiset<int> dice;
  for (int roll : {3, 5, 3, 6, 3}) {
    dice.insert(roll);
  }
  std::println("3 の目は {} 回", dice.count(3));
  std::println("全部で {} 回", dice.size());
}
```

```text title="実行結果"
3 の目は 3 回
全部で 5 回
```

### equal_range {#equal_range}

```cpp
std::pair<iterator, iterator> equal_range(const Key& value);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `value` | `const Key&` | 取り出したい値 |

- 戻り値: 値が等しい要素の `[first, last)`
- 計算量: 平均 O(個数)

### erase {#erase}

```cpp
size_type erase(const Key& value);
iterator erase(const_iterator pos);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `value` | `const Key&` | 消したい値 |

- 戻り値: 値版は**同じ値を全部**消し、消した個数を返す。1 個だけなら、イテレータ版
- 計算量: 平均 O(個数)

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
void swap(unordered_multiset& other) noexcept;
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
void merge(unordered_multiset<..., C2>& source);
```

- 計算量: O(移動する要素数 × log n)

別のコンテナの要素を、ノードごとこちらへ移します。キーが重複するものは、移動元に残ります。

### find {#find}

```cpp
iterator find(const key_type& key);
const_iterator find(const key_type& key) const;
```

- 計算量: O(log n)、平均 O(1)（unordered）

指定したキーの要素を探し、見つかればそのイテレータ、なければ `end()` を返します。

### contains <span class="ver ver-20">C++20</span> {#contains data-toc-label="contains"}

```cpp
bool contains(const key_type& key) const;
```

- 計算量: O(log n)、平均 O(1)（unordered）

指定したキーの要素があれば `true`。`find(...) != end()` を短く書けます。

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

### bucket_count {#bucket_count}

```cpp
size_type bucket_count() const noexcept;
```

- 計算量: 定数

バケット（要素を振り分ける箱）の数。

### max_bucket_count {#max_bucket_count}

```cpp
size_type max_bucket_count() const noexcept;
```

- 計算量: 定数

バケットの数の上限。

### bucket_size {#bucket_size}

```cpp
size_type bucket_size(size_type n) const;
```

- 計算量: O(要素数)

n 番目のバケットに入っている要素の数。偏りの確認に使います。

### bucket {#bucket}

```cpp
size_type bucket(const key_type& key) const;
```

- 計算量: 定数

キーが入るバケットの番号。

### load_factor {#load_factor}

```cpp
float load_factor() const noexcept;
```

- 計算量: 定数

平均の負荷（要素数 ÷ バケット数）。1 に近づくと、衝突が増えて遅くなります。

### max_load_factor {#max_load_factor}

```cpp
float max_load_factor() const noexcept;
void max_load_factor(float ml);
```

- 計算量: 定数

負荷の上限。これを超えると、自動でバケットを増やします（リハッシュ）。

### rehash {#rehash}

```cpp
void rehash(size_type count);
```

- 計算量: 平均 O(要素数)

バケットの数を `count` 以上にして、全ての要素を再配置します。

### reserve {#reserve}

```cpp
void reserve(size_type count);
```

- 計算量: 平均 O(要素数)

`count` 個の要素が入っても、リハッシュが起きないようにバケットを用意します。

### hash_function {#hash_function}

```cpp
hasher hash_function() const;
```

- 計算量: 定数

キーのハッシュ値を作る関数オブジェクトのコピー。

### key_eq {#key_eq}

```cpp
key_equal key_eq() const;
```

- 計算量: 定数

キーの等しさを判定する関数オブジェクトのコピー。

### get_allocator {#get_allocator}

```cpp
allocator_type get_allocator() const noexcept;
```

- 計算量: 定数

使っているアロケータのコピー。

### operator= {#op_assign}

```cpp
unordered_multiset& operator=(const unordered_multiset& other);
unordered_multiset& operator=(unordered_multiset&& other) noexcept;
```

- 計算量: コピーは O(要素数)、ムーブは定数

コピー代入とムーブ代入。ムーブ代入は、中身の所有権を移すだけで、要素をコピーしません。

### operator== {#op_eq}

```cpp
bool operator==(const unordered_multiset& a, const unordered_multiset& b);
```

- 計算量: O(要素数)

要素の数が同じで、各要素が順に等しければ `true`。

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 出た目の回数を数える | `dice.count(3)` |
| 同じアイテムを複数持つ集合 | `items.count(id)` |

## よくあるミス

??? failure "erase(値) で全部消える"
    1 個だけ消したいときは、`find` で見つけたイテレータを `erase` に渡します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::unordered_set`](unordered_set.md) | 同じ値は 1 つだけ |
| [`std::multiset`](multiset.md) | 値の順に並ぶ（木） |
| `unordered_map<T, int>` | 個数を数えるならこちらが分かりやすい |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 同じ値を複数持てるハッシュ表
    - [x] 個数は `count`
    - [x] 順番は決まっていない

## 関連ページ

- [cpprefjp: std::unordered_multiset](https://cpprefjp.github.io/reference/unordered_set/unordered_multiset.html)
- [cppreference: std::unordered_multiset](https://en.cppreference.com/w/cpp/container/unordered_multiset)
