---
title: std::flat_multimap
summary: "同じキーを複数持てる flat_map。vector 上に整列して並ぶ。"
order: 22
tags:
  - コンテナ
---

# std::flat_multimap

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="perf perf-3">○ 普通</span>
<span class="ver ver-23">C++23</span>
`#include <flat_map>`
</div>

`std::flat_multimap` は、**同じキーを複数持てる [`flat_map`](flat_map.md)** です。キーの配列と値の配列を `vector` 上に並べ、キーの順に整列させます。検索と巡回が速く、挿入と削除が遅いという `flat_map` の性質を、そのまま引き継ぎます。

!!! tip "ポイント"
    - <strong>使う場面は少ない。</strong> 読み込み中心で、同じキーの複数の値を高速に回したいときだけ。
    - `[]` と `at` は**無い**。
    - 同じキーの要素は、入れた順に並ぶ。

!!! info "このページを読む前に"
    [`std::flat_map`](flat_map.md) を先に読んでください。

## 宣言

```cpp
template <class Key, class T, class Compare = std::less<Key>,
          class KeyContainer = std::vector<Key>, class MappedContainer = std::vector<T>>
class flat_multimap;
```

## 関数の詳しい説明

### emplace {#emplace}

```cpp
template <class... Args>
iterator emplace(Args&&... args);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `args...` | 可変個 | `(キー, 値)` のコンストラクタ引数 |

- 戻り値: 追加した要素のイテレータ。**同じキーでも必ず追加**される
- 計算量: O(n)（挿入位置より後ろをずらす）

```cpp
#include <flat_map>
#include <print>
#include <string>

int main() {
  std::flat_multimap<int, std::string> events;
  events.emplace(2, "b");
  events.emplace(1, "a");
  events.emplace(2, "c");  // 同じキーでも追加される

  for (const auto& [time, name] : events) {
    std::println("{} {}", time, name);
  }
}
```

```text title="実行結果"
1 a
2 b
2 c
```

### equal_range {#equal_range}

```cpp
std::pair<iterator, iterator> equal_range(const Key& key);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `key` | `const Key&` | 取り出したいキー |

- 戻り値: キーが等しい要素の `[first, last)`
- 計算量: O(log n)

### count {#count}

```cpp
size_type count(const Key& key) const;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `key` | `const Key&` | 数えたいキー |

- 戻り値: 同じキーの個数
- 計算量: O(log n + 個数)

### erase {#erase}

```cpp
size_type erase(const Key& key);
iterator erase(const_iterator pos);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `key` | `const Key&` | 消したいキー |

- 戻り値: キー版は**同じキーを全部**消し、消した個数を返す
- 計算量: O(n)

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 時刻でまとめたイベント表（読み込み中心） | `events.equal_range(time)` |

## よくあるミス

??? failure "頻繁に挿入・削除する"
    挿入・削除は O(n) です。頻繁に追加するなら [`std::multimap`](multimap.md) のほうが速いです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::flat_map`](flat_map.md) | 同じキーは 1 つだけ |
| [`std::multimap`](multimap.md) | 木（挿入・削除が速い） |
| [`std::flat_multiset`](flat_multiset.md) | キーだけ（値なし） |

## コンパイラ対応

C++23 の機能です。GCC 15 / Clang 20 / MSVC 19.34（VS 2022 17.4）以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 同じキーを持てる `flat_map`
    - [x] 検索・巡回が速く、挿入・削除は遅い
    - [x] C++23

## 関連ページ

- [cpprefjp: std::flat_multimap](https://cpprefjp.github.io/reference/flat_map/flat_multimap.html)
- [cppreference: std::flat_multimap](https://en.cppreference.com/w/cpp/container/flat_multimap)
