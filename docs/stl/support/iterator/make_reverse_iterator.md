---
title: std::make_reverse_iterator
summary: "イテレータから reverse_iterator を作る。"
order: 900
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::make_reverse_iterator

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iterator>`
</div>

`reverse_iterator<It>` は型を書く必要があります。`make_reverse_iterator(it)` なら、型を推論して作ってくれます（C++17 以降は CTAD でも書けます）。

!!! tip "ポイント"
    - `<iterator>` の部品。
    - ふつうは補助関数（`back_inserter` など）経由で使う。
    - アルゴリズムの出力先や入力元に渡す。

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::make_reverse_iterator {#make_reverse_iterator}

```cpp
auto make_reverse_iterator(/* ... */);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `c / it` | コンテナ / イテレータ | 対象 |

- 戻り値: イテレータから reverse_iterator を作る
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <iterator>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3};
  auto r = std::make_reverse_iterator(v.end());
  std::println("{}", *r);
}
```

```text title="実行結果"
3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 逆順に走査する |

## よくあるミス

??? failure "`end()` の指す先を読む"
    `make_reverse_iterator(end)` は、`end()` の 1 つ手前の要素を指します。`end()` そのものは読めません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`reverse_iterator`](reverse_iterator.md) | 逆順イテレータの型 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] イテレータから reverse_iterator を作る
    - [x] `<iterator>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::make_reverse_iterator](https://cpprefjp.github.io/reference/iterator/make_reverse_iterator.html)
- [cppreference: std::make_reverse_iterator](https://en.cppreference.com/w/cpp/iterator/make_reverse_iterator)
