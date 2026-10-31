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

書き込み専用のイテレータを表す、中身のない空の構造体が `std::output_iterator_tag` です。イテレータの種類を、型として表すためだけにあります。`std::iterator_traits<It>::iterator_category` に、このタグの型が入ります。

!!! tip "ポイント"
    - 中身のない空の構造体。型としてだけ意味がある
    - タグの継承関係が、イテレータの強さの順序になる
    - アルゴリズムが、タグでオーバーロードを選ぶ
    - C++20 では `iterator_concept` で、より細かく表せる

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) を先に読んでください。

## 関数の詳しい説明

### std::output_iterator_tag {#output_iterator_tag}

<span class="ver ver-11">C++98〜</span>

```cpp
struct output_iterator_tag {};
```

タグの強さの順は、`input_iterator_tag` ← `forward_iterator_tag` ← `bidirectional_iterator_tag` ← `random_access_iterator_tag` ← `contiguous_iterator_tag`（C++20）です。矢印の先が派生クラスで、強いタグは弱いタグとして扱えます。`output_iterator_tag` は、この列とは別の枠で、書き込み専用のイテレータを表します。

たとえば `std::advance` は、`random_access_iterator_tag` なら `it += n` の 1 回で済ませ、`input_iterator_tag` なら `++it` を n 回繰り返します。この切り替えにタグが使われます。

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <deque>
#include <forward_list>
#include <iterator>
#include <list>
#include <print>
#include <ranges>
#include <sstream>
#include <string>
#include <type_traits>
#include <vector>

int main() {
  using Tag = std::iterator_traits<std::back_insert_iterator<std::vector<int>>>::iterator_category;
  std::println("back_insert_iterator のカテゴリ: {}", std::is_same_v<Tag, std::output_iterator_tag>);
}
```

```text title="実行結果"
back_insert_iterator のカテゴリ: true
```

## ゲームでの使いどころ

アルゴリズムを自作するときに、イテレータの種類でオーバーロードを選ぶために使います。C++20 以降は、コンセプトで制約する書き方が主流です。

## よくあるミス

??? failure "コンセプトの代わりにタグで制約する"
    C++20 以降は、`std::forward_iterator` などのコンセプトを使うほうが明確です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`iterator_traits`](iterator_traits.md) | タグを取り出す |
| [`advance`](advance.md) | タグで実装を切り替える例 |
| [`iter_value_t`](iter_value_t.md) | イテレータの型の問い合わせ |

## コンパイラ対応

C++98 から使えます。

## 関連ページ

- [cpprefjp: std::output_iterator_tag](https://cpprefjp.github.io/reference/iterator/output_iterator_tag.html)
- [cppreference: std::output_iterator_tag](https://en.cppreference.com/w/cpp/iterator/output_iterator_tag)
