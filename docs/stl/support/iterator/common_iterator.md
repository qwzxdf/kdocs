---
title: std::common_iterator
summary: "イテレータと sentinel（終端）を、1 つの型にまとめる。"
order: 900
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::common_iterator

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

C++20 の範囲は、`begin` と `end` が別の型のことがあります。古いアルゴリズムは、同じ型の組を要求します。`common_iterator<It, Sent>` は、2 つの型を 1 つにまとめて、古いアルゴリズムに渡せるようにします。

!!! tip "ポイント"
    - `<iterator>` の部品。
    - ふつうは補助関数（`back_inserter` など）経由で使う。
    - アルゴリズムの出力先や入力元に渡す。

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::common_iterator {#common_iterator}

```cpp
template <input_or_output_iterator It, sentinel_for<It> Sent>
class common_iterator;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `It` | 型 | イテレータの型 |
| `Sent` | 型 | 終端の型 |

- 戻り値: どちらにもなれるイテレータ
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <iterator>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3};
  using CI = std::common_iterator<std::counted_iterator<std::vector<int>::iterator>, std::default_sentinel_t>;
  std::vector<int> out(CI(std::counted_iterator(v.begin(), 2)), CI(std::default_sentinel));
  std::println("{}", out);
}
```

```text title="実行結果"
[1, 2]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 古いアルゴリズムに C++20 の範囲を渡す |

## よくあるミス

??? failure "`views::common` で足りる場面"
    view なら [`views::common`](../../algorithms/views/common.md) で包むほうが簡単です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`views::common`](../../algorithms/views/common.md) | view を common にする |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] イテレータと sentinel（終端）を、1 つの型にまとめる
    - [x] `<iterator>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::common_iterator](https://cpprefjp.github.io/reference/iterator/common_iterator.html)
- [cppreference: std::common_iterator](https://en.cppreference.com/w/cpp/iterator/common_iterator)
