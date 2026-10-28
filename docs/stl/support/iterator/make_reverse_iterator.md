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

`std::reverse_iterator<std::vector<int>::iterator>(it)` と型名を書くのは長いです。`std::make_reverse_iterator(it)` は、<strong>型を推論して `reverse_iterator` を作る</strong>補助関数です。

!!! tip "ポイント"
    - `std::make_reverse_iterator(it)` は `reverse_iterator` を作る
    - 型名を書かなくてよい
    - `std::copy` の入力に、逆順の範囲を渡せる
    - C++14 で追加

!!! info "このページを読む前に"
    [イテレーターの基礎](../../../basics/iterator.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::make_reverse_iterator {#make_reverse_iterator}

<span class="ver ver-14">C++14</span>

```cpp
template <class It>
constexpr reverse_iterator<It> make_reverse_iterator(It it);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `it` | 双方向イテレーター | 包む元のイテレーター |

`reverse_iterator<It>(it)` と同じ値を作ります。範囲を逆順で渡したいときは、`make_reverse_iterator(last)` と `make_reverse_iterator(first)` を組にします。

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <iterator>
#include <print>
#include <vector>

int main() {
  const std::vector<int> src = {1, 2, 3};
  std::vector<int> dst;
  std::copy(std::make_reverse_iterator(src.end()), std::make_reverse_iterator(src.begin()), std::back_inserter(dst));
  for (int x : dst) std::print("{} ", x);
  std::println("");
}
```

```text title="実行結果"
3 2 1 
```

## ゲームでの使いどころ

逆順にコピーします。`std::ranges::reverse_view` を使うほうが、書きやすい場面もあります。

## よくあるミス

??? failure "範囲の始点と終点の順を逆にする"
    `make_reverse_iterator(last)`、`make_reverse_iterator(first)` の順です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`reverse_iterator`](reverse_iterator.md) | アダプターの型 |

## コンパイラ対応

C++14 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `make_reverse_iterator(it)` は `reverse_iterator` を作る
    - [x] 型名を書かなくてよい
    - [x] 範囲は終点、始点の順に渡す

## 関連ページ

- [cpprefjp: std::make_reverse_iterator](https://cpprefjp.github.io/reference/iterator/make_reverse_iterator.html)
- [cppreference: std::make_reverse_iterator](https://en.cppreference.com/w/cpp/iterator/make_reverse_iterator)
