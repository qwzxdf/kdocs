---
title: std::output_iterator_tag
summary: "出力イテレータ（書き込みながら進められる）を表すタグの型。"
order: 900
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::output_iterator_tag

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iterator>`
</div>

アルゴリズムは、渡されたイテレータの能力に合わせて、使う手順を変えます（`advance` が +n と ++ を使い分けるなど）。その能力を型で表した目印が `output_iterator_tag` で、書き込みながら進められるイテレータが持つ性質です。

!!! tip "ポイント"
    - 書き込みながら進められるイテレータの目印。
    - `iterator_traits<It>::iterator_category` で取り出す。
    - C++20 では `iterator_concept` やコンセプトのほうが細かく表せる。

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::output_iterator_tag {#output_iterator_tag}

```cpp
struct output_iterator_tag {};
```

- 戻り値: なし（目印）
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <iterator>
#include <print>

int main() {
  std::println("{}", std::is_same_v<std::iterator_traits<std::back_insert_iterator<std::vector<int>>>::iterator_category, std::output_iterator_tag>);
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
    C++20 以降は `std::output_iterator<It>` のコンセプトのほうが書きやすいです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`iterator_traits`](iterator_traits.md) | タグを取り出す |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 出力イテレータ（書き込みながら進められる）を表すタグの型
    - [x] 書き込みながら進められるイテレータの目印
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::output_iterator_tag](https://cpprefjp.github.io/reference/iterator/output_iterator_tag.html)
- [cppreference: std::output_iterator_tag](https://en.cppreference.com/w/cpp/iterator/output_iterator_tag)
