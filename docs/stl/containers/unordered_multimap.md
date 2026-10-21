---
title: std::unordered_multimap
summary: "同じキーを複数持てる、ハッシュ表の map。順番はない。"
order: 20
tags:
  - コンテナ
---

# std::unordered_multimap

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="perf perf-3">○ 普通</span>
<span class="ver ver-11">C++11</span>
`#include <unordered_map>`
</div>

`std::unordered_multimap` は、**同じキーを何個でも持てる、ハッシュ表の map** です。[`std::unordered_map`](unordered_map.md) は同じキーを上書きしますが、こちらは全部残します。キーの順には並びません（順番は決まっていません）。

!!! tip "ポイント"
    - <strong>ほとんど使わない。</strong> 同じキーに複数の値が欲しいなら `unordered_map<Key, std::vector<T>>` のほうが扱いやすい。
    - `[]` と `at` は**無い**。同じキーの要素は `equal_range` でまとめて取る。
    - 同じキーの要素の並び順は、決まっていない。

!!! info "このページを読む前に"
    [`std::unordered_map`](unordered_map.md) を先に読んでください。

## 宣言

```cpp
template <class Key, class T, class Hash = std::hash<Key>, class KeyEqual = std::equal_to<Key>,
          class Allocator = std::allocator<std::pair<const Key, T>>>
class unordered_multimap;
```

## 関数の詳しい説明

### insert {#insert}

```cpp
iterator insert(const value_type& value);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `value` | `pair<const Key, T>` | 追加する (キー, 値) の組 |

- 戻り値: 追加した要素のイテレータ。**同じキーがあっても必ず追加**される
- 計算量: 平均 O(1)、最悪 O(n)

### equal_range {#equal_range}

```cpp
std::pair<iterator, iterator> equal_range(const Key& key);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `key` | `const Key&` | 取り出したいキー |

- 戻り値: キーが等しい要素の `[first, last)`。無ければ `first == last`
- 計算量: 平均 O(個数)

### count {#count}

```cpp
size_type count(const Key& key) const;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `key` | `const Key&` | 数えたいキー |

- 戻り値: 同じキーの個数
- 計算量: 平均 O(個数)

```cpp
#include <print>
#include <string>
#include <unordered_map>

int main() {
  std::unordered_multimap<std::string, std::string> loot;
  loot.insert({"slime", "ゼリー"});
  loot.insert({"slime", "コイン"});  // 同じキーでも消えない
  loot.insert({"bat", "つばさ"});

  std::println("slime のドロップは {} 種類", loot.count("slime"));
  loot.erase("slime");  // 同じキーを全部消す
  std::println("消したあと {} 種類 / 全体 {} 個", loot.count("slime"), loot.size());
}
```

```text title="実行結果"
slime のドロップは 2 種類
消したあと 0 種類 / 全体 1 個
```

### erase {#erase}

```cpp
size_type erase(const Key& key);
iterator erase(const_iterator pos);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `key` | `const Key&` | 消したいキー |

- 戻り値: キー版は**同じキーを全部**消し、消した個数を返す。1 個だけなら、イテレータ版を使う
- 計算量: 平均 O(個数)

### find {#find}

```cpp
iterator find(const Key& key);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `key` | `const Key&` | 探したいキー |

- 戻り値: 同じキーのうちどれか 1 つ。無ければ `end()`
- 計算量: 平均 O(1)

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 1 つのキーに複数のデータが紐づく（敵の種類 → ドロップ品） | `loot.equal_range("slime")` |
| 同じ ID のイベントを全部取り出す | `events.equal_range(id)` |

## よくあるミス

??? failure "erase(key) で全部消える"
    1 個だけ消したいときは、`find` で見つけたイテレータを `erase` に渡します。

??? failure "順番を期待する"
    同じキーの要素の並び順も、全体の順番も、決まっていません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::unordered_map`](unordered_map.md) | 同じキーは 1 つだけ |
| [`std::multimap`](multimap.md) | キーの順に並ぶ（木） |
| `unordered_map<Key, vector<T>>` | 同じキーの値を vector にまとめる |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 同じキーを複数持てるハッシュ表
    - [x] `[]` は無い。`equal_range` で取る
    - [x] 順番は決まっていない

## 関連ページ

- [cpprefjp: std::unordered_multimap](https://cpprefjp.github.io/reference/unordered_map/unordered_multimap.html)
- [cppreference: std::unordered_multimap](https://en.cppreference.com/w/cpp/container/unordered_multimap)
