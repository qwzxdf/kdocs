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

`inserter(c, pos)` が返す型の正体です。`*it = x` と代入するたびに `c.insert(pos, x)` が呼ばれ、位置は挿入した要素の次に進みます。連続して挿すと、順番を保ったまま入ります。

!!! tip "ポイント"
    - `<iterator>` の部品。
    - ふつうは補助関数（`back_inserter` など）経由で使う。
    - アルゴリズムの出力先や入力元に渡す。

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::insert_iterator {#insert_iterator}

```cpp
template <class Container>
class insert_iterator;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `Container` | 型 | `insert` をもつコンテナ |

- 戻り値: 代入で `insert` する
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <iterator>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 4};
  std::insert_iterator<std::vector<int>> it(v, v.begin() + 1);
  *it = 2;
  *it = 3;
  std::println("{}", v);
}
```

```text title="実行結果"
[1, 2, 3, 4]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | `set` や `vector` の途中に順番に挿す |

## よくあるミス

??? failure "毎回 `insert` で `vector` の途中に挿す"
    `vector` の途中への挿入は、後ろの要素を全部ずらします。大量に挿すなら別の方法を検討します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`inserter`](inserter.md) | 作る関数 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 代入するたびに、コンテナの指定位置へ insert するイテレータ
    - [x] `<iterator>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::insert_iterator](https://cpprefjp.github.io/reference/iterator/insert_iterator.html)
- [cppreference: std::insert_iterator](https://en.cppreference.com/w/cpp/iterator/insert_iterator)
