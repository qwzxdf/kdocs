---
title: std::back_inserter
summary: "代入するたびに、コンテナの末尾に push_back するイテレータ。"
order: 10
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::back_inserter

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
`#include <iterator>`
</div>

`std::back_inserter(c)` は、**代入するたびにコンテナの末尾へ `push_back` するイテレータ**を作ります。`copy` や `transform` の出力先に渡すと、結果が自動で末尾へ足されます。出力先の大きさを気にしなくてよくなります。

!!! tip "ポイント"
    - `std::ranges::copy(src, std::back_inserter(dst));`
    - `push_back` があるコンテナにだけ使える（`vector`、`deque`、`list`、`string`）。
    - `vector` では、事前に `reserve` すると速い。

!!! info "このページを読む前に"
    [`<iterator>`](../iterator.md) の概要を先に読むと分かりやすいです。[イテレータ](../../../basics/iterator.md) の基本が前提です。

## 関数の詳しい説明

### std::back_inserter {#back_inserter}

```cpp
template <class Container>
std::back_insert_iterator<Container> back_inserter(Container& c);
```

- このイテレータに書き込む（`*it = x`）と、`c.push_back(x)` が呼ばれます。アルゴリズムの出力先に使います

<div class="anim" data-label="std::back_inserter(v)">
1 2 # v
1 2 +3 # 代入するたびに push_back される
1 2 3 +4 # 出力先の大きさを気にしなくてよい
</div>

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <iterator>
#include <print>
#include <vector>

int main() {
  std::vector<int> src = {1, 2, 3};
  std::vector<int> dst;  // 空のまま
  std::ranges::copy(src, std::back_inserter(dst));
  std::println("{}", dst);
}
```

```text title="実行結果"
[1, 2, 3]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 条件に合う要素を別の vector に集める | `copy_if(src, std::back_inserter(dst), pred)` |

## よくあるミス

??? failure "空の vector に begin() を渡す"
    範囲外書き込みです。`back_inserter` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`front_inserter`](front_inserter.md) | 先頭に足す |
| [`inserter`](inserter.md) | 位置を指定して足す |

## コンパイラ対応

C++11 から使えます。`ssize` は C++20 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 末尾に自動で足す出力先
    - [x] copy / transform の出力に
    - [x] 事前に reserve すると速い

## 関連ページ

- [cpprefjp: std::back_inserter](https://cpprefjp.github.io/reference/iterator/back_inserter.html)
- [cppreference: std::back_inserter](https://en.cppreference.com/w/cpp/iterator/back_inserter)
