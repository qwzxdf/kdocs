---
title: std::insert_iterator
summary: "代入するたびに、コンテナの指定位置へ insert するイテレータ。"
order: 900
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::insert_iterator

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iterator>`
</div>

`std::inserter` が返す、挿入用のイテレーターの型が `std::insert_iterator` です。型名を直接書く機会は少なく、`std::inserter(c, pos)` で作ります。

!!! tip "ポイント"
    - `std::inserter(c, pos)` が返す型
    - 代入するたびに `c.insert(pos, value)` を呼ぶ
    - `set` / `map` / `list` / `vector` などに使える
    - 通常は型名を書かず、補助関数で作る

!!! info "このページを読む前に"
    [イテレーターの基礎](../../../basics/iterator.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::insert_iterator {#insert_iterator}

<span class="ver ver-98">C++98</span>

```cpp
template <class Container>
class insert_iterator {
 public:
  insert_iterator(Container& c, typename Container::iterator pos);
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `c` | コンテナ | 追加先 |
| `pos` | イテレーター | 挿入位置 |

出力イテレーターとして `*it = value` で `insert` を呼び、挿入した位置の次に位置を進めます。入力としては使えません（読み取れない）。

C++ では、型名を書かずに `auto` で受けたり、`std::inserter` を呼んだりするのが普通です。

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <iterator>
#include <list>
#include <print>

int main() {
  std::list<int> l = {1, 4};
  auto pos = std::next(l.begin());        // 4 の位置
  std::insert_iterator<std::list<int>> out(l, pos);
  *out = 2;
  *out = 3;                                // 4 の手前に 2, 3 が入る
  for (int x : l) std::print("{} ", x);
  std::println("");
}
```

```text title="実行結果"
1 2 3 4 
```

## ゲームでの使いどころ

型名を明示したい場面で使います。通常は `std::inserter` を使います。

## よくあるミス

??? failure "入力として使おうとする"
    出力専用です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`inserter`](inserter.md) | 作成用の補助関数 |
| [`back_insert_iterator`](back_insert_iterator.md) | 末尾に追加 |

## コンパイラ対応

C++98 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `insert_iterator` は `insert` で追加する出力イテレーター
    - [x] 通常は `std::inserter` で作る
    - [x] 入力としては使えない

## 関連ページ

- [cpprefjp: std::insert_iterator](https://cpprefjp.github.io/reference/iterator/insert_iterator.html)
- [cppreference: std::insert_iterator](https://en.cppreference.com/w/cpp/iterator/insert_iterator)
