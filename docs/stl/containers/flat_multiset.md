---
title: std::flat_multiset
summary: "同じ値を複数持てる flat_set。vector 上に整列して並ぶ。"
order: 23
tags:
  - コンテナ
---

# std::flat_multiset

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="perf perf-3">○ 普通</span>
<span class="ver ver-23">C++23</span>
`#include <flat_set>`
</div>

`std::flat_multiset` は、**同じ値を複数持てる [`flat_set`](flat_set.md)** です。要素を `vector` 上に小さい順に並べて持ちます。検索と巡回が速く、挿入と削除が遅い、という性質は `flat_set` と同じです。

!!! tip "ポイント"
    - <strong>使う場面は少ない。</strong> 読み込み中心で、同点を残した整列済みの一覧が欲しいとき。
    - `insert` は同じ値の末尾に入る（入れた順）。
    - C++23 の機能。

!!! info "このページを読む前に"
    [`std::flat_set`](flat_set.md) を先に読んでください。

## 宣言

```cpp
template <class Key, class Compare = std::less<Key>, class KeyContainer = std::vector<Key>>
class flat_multiset;
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
- 計算量: O(n)（挿入位置より後ろをずらす）

```cpp
#include <flat_set>
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::flat_multiset<int> scores;
  scores.insert(300);
  scores.insert(500);
  scores.insert(300);

  std::println("{}", scores | std::ranges::to<std::vector>());
  std::println("300 点は {} 人", scores.count(300));
}
```

```text title="実行結果"
[300, 300, 500]
300 点は 2 人
```

### count {#count}

```cpp
size_type count(const Key& value) const;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `value` | `const Key&` | 数えたい値 |

- 戻り値: 同じ値の個数
- 計算量: O(log n + 個数)

### equal_range {#equal_range}

```cpp
std::pair<iterator, iterator> equal_range(const Key& value);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `value` | `const Key&` | 取り出したい値 |

- 戻り値: 値が等しい要素の `[first, last)`
- 計算量: O(log n)

### erase {#erase}

```cpp
size_type erase(const Key& value);
iterator erase(const_iterator pos);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `value` | `const Key&` | 消したい値 |

- 戻り値: 値版は**同じ値を全部**消す
- 計算量: O(n)

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 同点を残した整列済みのスコア一覧（読み込み中心） | `scores.insert(x)` |

## よくあるミス

??? failure "頻繁に挿入する"
    挿入は O(n) です。頻繁に追加するなら [`std::multiset`](multiset.md) です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::flat_set`](flat_set.md) | 同じ値は 1 つだけ |
| [`std::multiset`](multiset.md) | 木（挿入・削除が速い） |
| [`std::flat_multimap`](flat_multimap.md) | 値つき |

## コンパイラ対応

C++23 の機能です。GCC 15 / Clang 20 / MSVC 19.34（VS 2022 17.4）以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 同じ値を持てる `flat_set`
    - [x] 検索・巡回が速く、挿入・削除は遅い
    - [x] C++23

## 関連ページ

- [cpprefjp: std::flat_multiset](https://cpprefjp.github.io/reference/flat_set/flat_multiset.html)
- [cppreference: std::flat_multiset](https://en.cppreference.com/w/cpp/container/flat_multiset)
