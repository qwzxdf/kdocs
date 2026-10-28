---
title: std::make_const_iterator
summary: "イテレータを、要素が const として見えるイテレータに変換する。"
order: 900
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::make_const_iterator

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <iterator>`
</div>

`const_iterator` を持たない範囲（`views` など）でも、読み取り専用のイテレータが欲しいことがあります。`make_const_iterator(it)` は、すでに const なら何もせず、そうでなければ `basic_const_iterator` で包みます。

!!! tip "ポイント"
    - `<iterator>` の部品。
    - ふつうは補助関数（`back_inserter` など）経由で使う。
    - アルゴリズムの出力先や入力元に渡す。

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::make_const_iterator {#make_const_iterator}

```cpp
template <input_iterator It>
constexpr const_iterator<It> make_const_iterator(It it);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `it` | イテレータ | 変換するイテレータ |

- 戻り値: 要素が const のイテレータ
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <iterator>
#include <print>
#include <type_traits>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3};
  auto it = std::make_const_iterator(v.begin());
  std::println("{}", std::is_const_v<std::remove_reference_t<decltype(*it)>>);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 読み取り専用のイテレータを渡す |

## よくあるミス

??? failure "書き込みに使う"
    const になるため、書き込めません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`basic_const_iterator`](basic_const_iterator.md) | 実体の型 |

## コンパイラ対応

C++23 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] イテレータを要素が const として見えるイテレータに変換する
    - [x] `<iterator>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::make_const_iterator](https://cpprefjp.github.io/reference/iterator/make_const_iterator.html)
- [cppreference: std::make_const_iterator](https://en.cppreference.com/w/cpp/iterator/make_const_iterator)
