---
title: std::inserter
summary: "代入するたびに、指定した位置にコンテナへ挿入するイテレータ。"
order: 12
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::inserter

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <iterator>`
</div>

`std::inserter(c, pos)` は、**代入するたびに、`pos` の位置へ `insert` するイテレータ**を作ります。`set` や `map` のように `push_back` が無いコンテナへの出力先として、よく使います。

!!! tip "ポイント"
    - `std::ranges::copy(src, std::inserter(set, set.end()))`。
    - `set` では、位置はヒントとして使われる。
    - `vector` の途中にも挿入できる。

!!! info "このページを読む前に"
    [`<iterator>`](../iterator.md) の概要を先に読むと分かりやすいです。[イテレータ](../../../basics/iterator.md) の基本が前提です。

## 関数の詳しい説明

### std::inserter {#inserter}

```cpp
template <class Container>
std::insert_iterator<Container> inserter(Container& c, typename Container::iterator pos);
```

- 書き込むと `c.insert(pos, x)` が呼ばれます。set や map に結果を入れるのに使います

```cpp
#include <algorithm>
#include <iterator>
#include <print>
#include <set>
#include <vector>

int main() {
  std::vector<int> drops = {3, 1, 3, 2};
  std::set<int> kinds;
  std::ranges::copy(drops, std::inserter(kinds, kinds.end()));
  std::println("{}", kinds);
}
```

```text title="実行結果"
{1, 2, 3}
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 結果を set に集める | `std::ranges::copy(v, std::inserter(s, s.end()))` |

## よくあるミス

??? failure "set の出力に back_inserter を使う"
    `set` に `push_back` はありません。`inserter` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`back_inserter`](back_inserter.md) | 末尾に足す |

## コンパイラ対応

C++11 から使えます。`ssize` は C++20 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 位置を指定して挿入する出力先
    - [x] set / map の出力に
    - [x] `vector` の途中にも使える

## 関連ページ

- [cpprefjp: std::inserter](https://cpprefjp.github.io/reference/iterator/inserter.html)
- [cppreference: std::inserter](https://en.cppreference.com/w/cpp/iterator/inserter)
