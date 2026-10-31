---
title: std::ranges::fold_left_with_iter
summary: "左から畳み込み、結果と「どこまで読んだか」の両方を返す。"
order: 900
tags:
  - アルゴリズム
---

# std::ranges::fold_left_with_iter

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <algorithm>`
</div>

`std::ranges::fold_left` は、畳んだ結果の値だけを返します。ところが入力が、1 度しか読めない範囲（入力ストリーム）の場合、読み終えた位置も知りたいことがあります。`std::ranges::fold_left_with_iter` は、結果の値と、入力の終端のイテレータの両方を返します。

!!! tip "ポイント"
    - 畳んだ値と、読み終えたイテレータの組を返す
    - 戻り値は `in`（読み終えた位置）と `value`（結果）を持つ構造体
    - 1 度しか読めない範囲で、続きから使うときに便利
    - C++23

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::ranges::fold_left_with_iter {#fold_left_with_iter}

<span class="ver ver-23">C++23</span>

```cpp
template <input_range R, class T, class F>
constexpr auto fold_left_with_iter(R&& r, T init, F f);
// 戻り値: fold_left_with_iter_result<borrowed_iterator_t<R>, 畳みの結果の型>
```

結果は、`in` と `value` の 2 つのメンバーを持ちます。構造化束縛で、`auto [in, value] = ...;` と受けられます。

`fold_left` は、内部でこれを呼んで、`value` だけを返しています。

入力範囲が `borrowed_range`（一時オブジェクトでない）でなければ、`in` は `dangling` になり、使えません。

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  const std::vector<int> v = {1, 2, 3, 4};

  const auto [in, value] = std::ranges::fold_left_with_iter(v, 0, std::plus<>());
  std::println("合計: {}", value);
  std::println("読み終えた位置: {}", in - v.begin());
}
```

```text title="実行結果"
合計: 10
読み終えた位置: 4
```

## ゲームでの使いどころ

入力ストリームから数値を畳み込みながら、読み終えた位置も使いたいときに使います。

## よくあるミス

??? failure "一時オブジェクトの範囲を渡す"
    `in` が `dangling` になり、使えません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fold_left`](fold_left.md) | 値だけを返す |
| [`fold_left_first_with_iter`](fold_left_first_with_iter.md) | 初期値なし版 |
| [`accumulate`](accumulate.md) | 従来の畳み込み |

## コンパイラ対応

C++23 から使えます。

## 関連ページ

- [cpprefjp: std::ranges::fold_left_with_iter](https://cpprefjp.github.io/reference/algorithm/ranges_fold_left_with_iter.html)
- [cppreference: std::ranges::fold_left_with_iter](https://en.cppreference.com/w/cpp/algorithm/ranges/fold_left_with_iter)
