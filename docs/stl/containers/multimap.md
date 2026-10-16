---
title: std::multimap / std::multiset
tags:
  - コンテナ
---

# std::multimap / std::multiset

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="perf perf-3">○ 普通</span>
<span class="ver ver-11">C++98〜</span>
`#include <map>` / `#include <set>`
</div>

`std::multimap` と `std::multiset` は、**同じキーを何個でも持てる map / set** です。普通の [`std::map`](map.md) は同じキーを入れると上書きされますが、multimap は全部残します。キーの順に並ぶのは map と同じです。順番なし版の `std::unordered_multimap` / `std::unordered_multiset` もあります。

!!! tip "結論"
    - **ほとんど使わない。** 同じキーに複数の値を持たせたいなら、`std::map<Key, std::vector<T>>` のほうが扱いやすいことが多い。
    - 使うなら、同じキーの要素は `equal_range` でまとめて取り出す。
    - `[]` は**無い**（どの要素か決められないため）。

!!! info "このページを読む前に"
    [`std::map`](map.md) と [`std::set`](set.md) を先に読んでください。

## 宣言

```cpp
template <class Key, class T, class Compare = std::less<Key>,
          class Allocator = std::allocator<std::pair<const Key, T>>>
class multimap;

template <class Key, class Compare = std::less<Key>,
          class Allocator = std::allocator<Key>>
class multiset;
```

## 関数一覧

map / set と違う点を中心に載せています。

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

### equal_range {#equal_range}

```cpp
std::pair<iterator, iterator> equal_range(const Key& key);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `key` | `const Key&` | 取り出したいキー |

- 戻り値: キーが `key` と等しい要素の `[first, last)`。無ければ `first == last`

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

### erase {#erase}

```cpp
size_type erase(const Key& key);
iterator erase(const_iterator pos);
```

- **キー版は同じキーを全部消します**。1 個だけ消すならイテレータ版を使います

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

### upper_bound {#upper_bound}

```cpp
iterator upper_bound(const Key& key);
```

- キーが `key` より大きい最初の要素

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

`std::multiset` も同じ関数を持ちます（値が無く、キーだけの点が違います）。

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
| [`std::map`](map.md) / [`std::set`](set.md) | キーの重複なし | ほとんどの場合 |
| `std::map<Key, std::vector<T>>` | 同じキーの値を vector にまとめる | 同じキーの値をまとめて扱いたい |
| `std::unordered_multimap` | 順番なし | 順番が要らない |

## これだけ覚える

!!! abstract "まとめ"
    - [x] 同じキーを何個でも持てる map / set
    - [x] 取り出すのは `equal_range`、`[]` は無い
    - [x] `erase(key)` は同じキーを全部消す

## 関連ページ

- [cpprefjp: std::multimap](https://cpprefjp.github.io/reference/map/multimap.html)
- [cppreference: std::multimap](https://en.cppreference.com/w/cpp/container/multimap)
