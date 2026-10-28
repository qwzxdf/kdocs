---
title: std::front_inserter
summary: "代入するたびに、コンテナの先頭に push_front するイテレータ。"
order: 11
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::front_inserter

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iterator>`
</div>

`std::front_inserter(c)` は、**代入するたびにコンテナの先頭へ `push_front` するイテレータ**を作ります。`deque` や `list` など、先頭に足せるコンテナで使えます。要素の順序が逆になる点に注意します。

!!! tip "ポイント"
    - `push_front` があるコンテナ（`deque`、`list`）だけ。
    - 要素は逆順で並ぶ。

!!! info "このページを読む前に"
    [`<iterator>`](../iterator.md) の概要を先に読むと分かりやすいです。[イテレータ](../../../basics/iterator.md) の基本が前提です。

## 関数の詳しい説明

### std::front_inserter {#front_inserter}

```cpp
template <class Container>
std::front_insert_iterator<Container> front_inserter(Container& c);
```

- 書き込むと `c.push_front(x)` が呼ばれます（deque、list 用）。逆順に入ります

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <deque>
#include <iterator>
#include <print>
#include <vector>

int main() {
  std::vector<int> src = {1, 2, 3};
  std::deque<int> dst;
  std::ranges::copy(src, std::front_inserter(dst));  // 先頭に足していくので逆順になる
  std::println("{}", dst);
}
```

```text title="実行結果"
[3, 2, 1]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 履歴の先頭に新しいものを足していく | `copy(src, std::front_inserter(history))` |

## よくあるミス

??? failure "vector に使う"
    `push_front` が無いのでコンパイルエラーです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`back_inserter`](back_inserter.md) | 末尾に足す |

## コンパイラ対応

C++11 から使えます。`ssize` は C++20 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 先頭に自動で足す出力先
    - [x] deque / list 用
    - [x] 逆順になる

## 関連ページ

- [cpprefjp: std::front_inserter](https://cpprefjp.github.io/reference/iterator/front_inserter.html)
- [cppreference: std::front_inserter](https://en.cppreference.com/w/cpp/iterator/front_inserter)
