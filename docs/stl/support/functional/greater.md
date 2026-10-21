---
title: std::greater
summary: "「大きいか」を比べる関数オブジェクト（`>` の代わり）。"
order: 2
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::greater

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <functional>`
</div>

`std::greater<T>` は、**`a > b` を関数オブジェクトとして使えるようにしたもの**です。大きい順に並べたいとき（`sort`）や、小さいものが先頭にくる `priority_queue` を作るときに渡します。

!!! tip "ポイント"
    - 大きい順の整列: `std::ranges::sort(v, std::greater{})`。
    - 最小が先頭の `priority_queue<int, vector<int>, greater<int>>`。
    - `std::greater{}` と書くと型を推論してくれる（C++14）。

!!! info "このページを読む前に"
    [`<functional>`](../functional.md) の概要を先に読むと分かりやすいです。[ラムダ式](../../../basics/lambda.md) も関係します。

## 関数の詳しい説明

### std::greater {#greater}

```cpp
template <class T = void>
struct greater {
  constexpr bool operator()(const T& a, const T& b) const;  // a > b
};
```

- `a > b` を返す関数オブジェクト。`std::greater{}`（型を省略した版）がおすすめです。大きい順のソート、[priority_queue](../../containers/priority_queue.md) の小さい順、map の逆順に使います

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <functional>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {3, 1, 2};
  std::ranges::sort(v, std::greater{});
  std::println("{}", v);
}
```

```text title="実行結果"
[3, 2, 1]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| スコアの大きい順に並べる | `std::ranges::sort(scores, std::greater{});` |
| A* で、コストが小さいものを先に取り出す | `priority_queue<Node, vector<Node>, greater<>>` |

## よくあるミス

??? failure "priority_queue で less と取り違える"
    `priority_queue` の既定は最大が先頭です。最小を先頭にしたいときだけ `greater`。

## 類似

| 名前 | 違い |
| --- | --- |
| [`less`](less.md) | 小さい順 |
| [`std::priority_queue`](../../containers/priority_queue.md) | greater と組み合わせる |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `>` を関数オブジェクトにしたもの
    - [x] 大きい順の整列に
    - [x] priority_queue で最小先頭

## 関連ページ

- [cpprefjp: std::greater](https://cpprefjp.github.io/reference/functional/greater.html)
- [cppreference: std::greater](https://en.cppreference.com/w/cpp/utility/functional/greater)
