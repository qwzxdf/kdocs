---
title: std::front_insert_iterator
summary: "代入するたびに、コンテナの先頭へ push_front するイテレータ。"
order: 900
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::front_insert_iterator

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iterator>`
</div>

`front_inserter(c)` が返す型の正体です。`*it = x` と代入するたびに `c.push_front(x)` が呼ばれます。`deque` や `list` で使えます。

!!! tip "ポイント"
    - `<iterator>` の部品。
    - ふつうは補助関数（`back_inserter` など）経由で使う。
    - アルゴリズムの出力先や入力元に渡す。

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::front_insert_iterator {#front_insert_iterator}

```cpp
template <class Container>
class front_insert_iterator;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `Container` | 型 | `push_front` をもつコンテナ |

- 戻り値: 代入で `push_front` する
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <deque>
#include <iterator>
#include <print>

int main() {
  std::deque<int> d;
  std::front_insert_iterator<std::deque<int>> it(d);
  *it = 1;
  ++it;
  *it = 2;
  std::println("{}", d);
}
```

```text title="実行結果"
[2, 1]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 逆順に積み上げる |

## よくあるミス

??? failure "`vector` に使う"
    `vector` には `push_front` がありません。`deque` や `list` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`front_inserter`](front_inserter.md) | 作る関数 |
| [`back_insert_iterator`](back_insert_iterator.md) | 末尾に追加する |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 代入するたびに、コンテナの先頭へ push_front するイテレータ
    - [x] `<iterator>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::front_insert_iterator](https://cpprefjp.github.io/reference/iterator/front_insert_iterator.html)
- [cppreference: std::front_insert_iterator](https://en.cppreference.com/w/cpp/iterator/front_insert_iterator)
