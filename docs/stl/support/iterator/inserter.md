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

`std::set` や `std::map` には、末尾や先頭という位置がありません。`std::copy` で要素を詰めたいときは、`std::inserter` を使います。<strong>コンテナの指定した位置に、`insert` で追加するイテレーター</strong>を作ります。

!!! tip "ポイント"
    - `std::inserter(c, pos)` で、`pos` の位置への挿入イテレーターを作る
    - 代入するたびに `c.insert(pos, value)` が呼ばれる
    - `std::set` / `std::map` / `std::list` などで使える
    - `vector` でも使える（途中への挿入は遅い）

!!! info "このページを読む前に"
    [イテレーターの基礎](../../../basics/iterator.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::inserter {#inserter}

<span class="ver ver-98">C++98</span>

```cpp
template <class Container>
insert_iterator<Container> inserter(Container& c, typename Container::iterator pos);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `c` | コンテナ | 追加先 |
| `pos` | イテレーター | 挿入位置（`set` ならヒント） |

代入のたびに `insert` が呼ばれます。`set` では位置は並び順を決めず、ヒントとして使われます。挿入のたびに位置を進めるので、連続して並んだ位置に挿入できます。

`vector` の途中に挿入すると、後ろの要素を移動するので遅くなります。`vector` の末尾なら `back_inserter` を使います。

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <iterator>
#include <print>
#include <set>
#include <vector>

int main() {
  const std::vector<int> src = {3, 1, 2, 3};
  std::set<int> dst;
  std::copy(src.begin(), src.end(), std::inserter(dst, dst.end()));
  for (int x : dst) std::print("{} ", x);   // 重複は取り除かれ、昇順に並ぶ
  std::println("");
}
```

```text title="実行結果"
1 2 3 
```

## ゲームでの使いどころ

`vector` の内容を `set` に取り込みます。重複が取り除かれ、整列されます。

## よくあるミス

??? failure "`vector` の先頭付近に挿入して遅い"
    `back_inserter` か、別の方法を考えます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`back_insert_iterator`](back_insert_iterator.md) | 末尾に追加 |
| [`insert_iterator`](insert_iterator.md) | 挿入イテレーターの型 |

## コンパイラ対応

C++98 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::inserter(c, pos)` は `insert` で追加するイテレーター
    - [x] `set` / `map` に `copy` するときに使う
    - [x] `vector` の途中への挿入は遅い

## 関連ページ

- [cpprefjp: std::inserter](https://cpprefjp.github.io/reference/iterator/inserter.html)
- [cppreference: std::inserter](https://en.cppreference.com/w/cpp/iterator/inserter)
