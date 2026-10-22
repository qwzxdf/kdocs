---
title: std::contiguous_iterator_tag
summary: "連続イテレータ（メモリ上で連続した要素を指す）を表すタグの型。"
order: 900
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::contiguous_iterator_tag

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

アルゴリズムは、渡されたイテレータの能力に合わせて、使う手順を変えます（`advance` が +n と ++ を使い分けるなど）。その能力を型で表した目印が `contiguous_iterator_tag` で、メモリ上で連続した要素を指すイテレータが持つ性質です。

!!! tip "ポイント"
    - メモリ上で連続した要素を指すイテレータの目印。
    - `iterator_traits<It>::iterator_category` で取り出す。
    - C++20 では `iterator_concept` やコンセプトのほうが細かく表せる。

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::contiguous_iterator_tag {#contiguous_iterator_tag}

```cpp
struct contiguous_iterator_tag {};
```

- 戻り値: なし（目印）
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <iterator>
#include <print>

int main() {
  std::println("{}", std::is_same_v<std::iterator_traits<int*>::iterator_concept, std::contiguous_iterator_tag>);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 自作のアルゴリズムでイテレータの能力ごとに実装を切り替える |

## よくあるミス

??? failure "C++20 のコンセプトを使わない"
    C++20 以降は `std::contiguous_iterator<It>` のコンセプトのほうが書きやすいです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`iterator_traits`](iterator_traits.md) | タグを取り出す |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 連続イテレータ（メモリ上で連続した要素を指す）を表すタグの型
    - [x] メモリ上で連続した要素を指すイテレータの目印
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::contiguous_iterator_tag](https://cpprefjp.github.io/reference/iterator/contiguous_iterator_tag.html)
- [cppreference: std::contiguous_iterator_tag](https://en.cppreference.com/w/cpp/iterator/contiguous_iterator_tag)
