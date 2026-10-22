---
title: std::iterator_traits
summary: "イテレータの性質（要素の型、種類など）を取り出す。"
order: 900
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::iterator_traits

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iterator>`
</div>

自作のアルゴリズムで、渡されたイテレータが指す要素の型や、前後に進めるかを知りたいことがあります。`iterator_traits<It>` は、`value_type`・`difference_type`・`iterator_category` などを取り出す統一の入り口です。生ポインタにも使えます。

!!! tip "ポイント"
    - `value_type`・`difference_type`・`pointer`・`reference`・`iterator_category` を取れる。
    - 生ポインタ `T*` にも特殊化がある。
    - C++20 では `iter_value_t` などが使いやすい。

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::iterator_traits {#iterator_traits}

```cpp
template <class It>
struct iterator_traits {
  using difference_type = /* 差の型 */;
  using value_type = /* 要素の型 */;
  using pointer = /* ポインタ型 */;
  using reference = /* 参照型 */;
  using iterator_category = /* 種類 */;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `It` | 型 | 調べるイテレータの型 |

- 戻り値: 型メンバ
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <iterator>
#include <print>
#include <type_traits>
#include <vector>

int main() {
  using It = std::vector<int>::iterator;
  std::println("{}", std::is_same_v<std::iterator_traits<It>::value_type, int>);
  std::println("{}", std::is_same_v<std::iterator_traits<It>::iterator_category, std::random_access_iterator_tag>);
}
```

```text title="実行結果"
true
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | ジェネリックなアルゴリズムで、要素の型を取り出す |

## よくあるミス

??? failure "C++20 のコードで使い続ける"
    C++20 以降は `std::iter_value_t<It>` のほうが、コンセプトとの相性がよく、安全です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`iter_value_t`](iter_value_t.md) | C++20 の取り出し方 |
| [`iterator_category`](input_iterator_tag.md) | 種類のタグ |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] イテレータの性質（要素の型、種類など）を取り出す
    - [x] `value_type`・`difference_type`・`pointer`・`reference`・`iterator_category` を取れる
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::iterator_traits](https://cpprefjp.github.io/reference/iterator/iterator_traits.html)
- [cppreference: std::iterator_traits](https://en.cppreference.com/w/cpp/iterator/iterator_traits)
