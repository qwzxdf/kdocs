---
title: std::forward_iterator_tag
summary: "前方イテレータ（何度でも読み返せる（一方向））を表すタグの型。"
order: 900
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::forward_iterator_tag

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iterator>`
</div>

アルゴリズムは、渡されたイテレータの能力に合わせて、使う手順を変えます（`advance` が +n と ++ を使い分けるなど）。その能力を型で表した目印が `forward_iterator_tag` で、何度でも読み返せる（一方向）イテレータが持つ性質です。

!!! tip "ポイント"
    - 何度でも読み返せる（一方向）イテレータの目印。
    - `iterator_traits<It>::iterator_category` で取り出す。
    - C++20 では `iterator_concept` やコンセプトのほうが細かく表せる。

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::forward_iterator_tag {#forward_iterator_tag}

```cpp
struct forward_iterator_tag {};
```

- 戻り値: なし（目印）
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <iterator>
#include <print>

int main() {
  std::println("{}", std::is_same_v<std::iterator_traits<std::forward_list<int>::iterator>::iterator_category, std::forward_iterator_tag>);
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
    C++20 以降は `std::forward_iterator<It>` のコンセプトのほうが書きやすいです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`iterator_traits`](iterator_traits.md) | タグを取り出す |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 前方イテレータ（何度でも読み返せる（一方向））を表すタグの型
    - [x] 何度でも読み返せる（一方向）イテレータの目印
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::forward_iterator_tag](https://cpprefjp.github.io/reference/iterator/forward_iterator_tag.html)
- [cppreference: std::forward_iterator_tag](https://en.cppreference.com/w/cpp/iterator/forward_iterator_tag)
