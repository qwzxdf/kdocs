---
title: std::bidirectional_iterator_tag
summary: "双方向イテレータ（前後どちらにも進める）を表すタグの型。"
order: 900
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::bidirectional_iterator_tag

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iterator>`
</div>

アルゴリズムは、渡されたイテレータの能力に合わせて、使う手順を変えます（`advance` が +n と ++ を使い分けるなど）。その能力を型で表した目印が `bidirectional_iterator_tag` で、前後どちらにも進めるイテレータが持つ性質です。

!!! tip "ポイント"
    - 前後どちらにも進めるイテレータの目印。
    - `iterator_traits<It>::iterator_category` で取り出す。
    - C++20 では `iterator_concept` やコンセプトのほうが細かく表せる。

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::bidirectional_iterator_tag {#bidirectional_iterator_tag}

```cpp
struct bidirectional_iterator_tag {};
```

- 戻り値: なし（目印）
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <iterator>
#include <print>

int main() {
  std::println("{}", std::is_same_v<std::iterator_traits<std::list<int>::iterator>::iterator_category, std::bidirectional_iterator_tag>);
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
    C++20 以降は `std::bidirectional_iterator<It>` のコンセプトのほうが書きやすいです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`iterator_traits`](iterator_traits.md) | タグを取り出す |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 双方向イテレータ（前後どちらにも進める）を表すタグの型
    - [x] 前後どちらにも進めるイテレータの目印
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::bidirectional_iterator_tag](https://cpprefjp.github.io/reference/iterator/bidirectional_iterator_tag.html)
- [cppreference: std::bidirectional_iterator_tag](https://en.cppreference.com/w/cpp/iterator/bidirectional_iterator_tag)
