---
title: std::back_insert_iterator
summary: "代入するたびに、コンテナの末尾へ push_back するイテレータ。"
order: 900
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::back_insert_iterator

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iterator>`
</div>

`back_inserter(c)` が返す型の正体です。`*it = x` と代入するたびに `c.push_back(x)` が呼ばれます。出力先の大きさを気にせず、結果を `vector` に積み上げられます。

!!! tip "ポイント"
    - `<iterator>` の部品。
    - ふつうは補助関数（`back_inserter` など）経由で使う。
    - アルゴリズムの出力先や入力元に渡す。

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::back_insert_iterator {#back_insert_iterator}

```cpp
template <class Container>
class back_insert_iterator;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `Container` | 型 | `push_back` をもつコンテナ |

- 戻り値: 代入で `push_back` する
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <iterator>
#include <print>
#include <vector>

int main() {
  std::vector<int> v;
  std::back_insert_iterator<std::vector<int>> it(v);
  *it = 1;
  ++it;
  *it = 2;
  std::println("{}", v);
}
```

```text title="実行結果"
[1, 2]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | アルゴリズムの結果を `vector` に積む |

## よくあるミス

??? failure "`vector` の末尾以外に挿したい"
    末尾に追加するだけです。位置を指定するなら `insert_iterator` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`back_inserter`](back_inserter.md) | 作る関数 |
| [`front_insert_iterator`](front_insert_iterator.md) | 先頭に挿す |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 代入するたびに、コンテナの末尾へ push_back するイテレータ
    - [x] `<iterator>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::back_insert_iterator](https://cpprefjp.github.io/reference/iterator/back_insert_iterator.html)
- [cppreference: std::back_insert_iterator](https://en.cppreference.com/w/cpp/iterator/back_insert_iterator)
