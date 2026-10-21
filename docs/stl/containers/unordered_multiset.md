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
