---
title: std::next
summary: "イテレータを n 個進めた位置を返す（元は変えない）。"
order: 1
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::next

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <iterator>`
</div>

イテレーターを 3 つ進めたい。`it + 3` は、ランダムアクセスのイテレーター（`vector`）にしか使えません。`std::list` や `std::set` のイテレーターは `+` がありません。`std::next(it, n)` は、<strong>どんなイテレーターでも `n` 個進めた新しいイテレーターを返します</strong>。

!!! tip "ポイント"
    - `std::next(it, n)` は `it` を `n` 個進めたコピーを返す
    - `n` の既定は 1。元の `it` は変わらない
    - `std::list` などの双方向イテレーターでも使える
    - `n` が負の数なら戻る（双方向イテレーター以上）

!!! info "このページを読む前に"
    [イテレーターの基礎](../../../basics/iterator.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::next {#next}

<span class="ver ver-11">C++11</span>

```cpp
template <class It>
constexpr It next(It it, typename std::iterator_traits<It>::difference_type n = 1);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `it` | イテレーター | 出発点 |
| `n` | 整数 | 進める数。既定は 1 |

元のイテレーターは変えず、`n` 個先のイテレーターを新しく返します。ランダムアクセスのイテレーターなら 1 回の計算、そうでなければ `n` 回のインクリメントです（計算量は O(n)）。

範囲外に進めると、未定義動作になります。`std::list` の 3 番目の要素を取るときなどは、先に要素数を確かめます。

## 実際に動かしてみる

```cpp
#include <iterator>
#include <list>
#include <print>

int main() {
  std::list<int> l = {10, 20, 30, 40};
  std::println("3 番目: {}", *std::next(l.begin(), 2));
  std::println("最後の要素: {}", *std::prev(l.end()));
}
```

```text title="実行結果"
3 番目: 30
最後の要素: 40
```

## ゲームでの使いどころ

`list` の途中の要素に、アクセスします。

```cpp
auto second = std::next(items.begin());   // 2 番目
```

## よくあるミス

??? failure "範囲外まで進めて未定義動作になる"
    要素数を先に確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`prev`](prev.md) | 戻る |
| [`advance`](advance.md) | 元のイテレーターを進める |
| [`distance`](distance.md) | 距離 |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::next(it, n)` は `n` 個進めたコピー
    - [x] 元は変わらない
    - [x] `list` でも使える（O(n)）

## 関連ページ

- [cpprefjp: std::next](https://cpprefjp.github.io/reference/iterator/next.html)
- [cppreference: std::next](https://en.cppreference.com/w/cpp/iterator/next)
