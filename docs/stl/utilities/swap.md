---
title: std::swap
summary: "2 つの値を入れ替える。"
order: 54
tags:
  - ユーティリティ
---

# std::swap

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-11">C++98〜</span>
`#include <utility>`
</div>

描画用のバッファを前と後ろで入れ替える、並べ替えを自作する。2 つの変数の中身を入れ替えるには、一時変数を使って 3 行書くのが定番です。`std::swap` は、これを 1 行で書く関数です。コンテナのような大きなものは、中身のポインターを入れ替えるだけで済むので、コピーよりずっと速く交換できます。

!!! tip "ポイント"
    - コンテナには、専用の高速な `a.swap(b)` もある。
    - 自作クラスの `swap` を作るなら、`using std::swap; swap(a, b);` と書くと、自作版が優先される。
    - `std::ranges::swap`（C++20）もある。

!!! info "このページを読む前に"
    [ムーブ](../../basics/move.md) の考え方を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::swap {#swap}

```cpp
template <class T>
constexpr void swap(T& a, T& b) noexcept(/* 条件 */);
```

- `a` と `b` の中身を交換します。vector や string ならポインタの付け替えだけなので速いです

<div class="anim" data-label="std::swap(a, b)">
A | B # a と b
>B | >A # 中身を入れ替える
</div>

```cpp
#include <print>
#include <utility>

int main() {
  int front = 1;
  int back = 2;
  std::swap(front, back);
  std::println("{} {}", front, back);
}
```

```text title="実行結果"
2 1
```

## ゲームでの使いどころ

ダブルバッファの入れ替えに使います。前フレームの状態と今フレームの状態を `std::swap(prev, curr)` で入れ替えて、次のフレームに備えます。大きなコンテナでも、中身のポインターの交換だけで済みます。

コンテナには、専用の `a.swap(b)` があります。こちらは、要素のコピーもムーブもしません。

自作クラスの `swap` を作るときは、`using std::swap; swap(a, b);` と書くと、自作の `swap` が優先されます。`std::ranges::swap`（C++20）もあります。

## よくあるミス

??? failure "同じオブジェクトを swap する"
    自分自身との `swap` は安全ですが、何も起きません。

??? failure "大きな配列の入れ替えを要素ごとに行う"
    生の配列 `int a[1000]` どうしの `std::swap` は、要素ごとの入れ替えで、遅くなります。`std::array` や `vector` を使えば、中身のポインターの交換で済みます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::exchange`](exchange.md) | 新しい値を入れて古い値を返す |
| [`std::iter_swap`](../algorithms/iter_swap.md) | イテレータが指す要素を入れ替える |
| [`std::ranges::swap_ranges`](../algorithms/swap_ranges.md) | 範囲どうしを入れ替える |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 2 つの値を入れ替える
    - [x] コンテナは `a.swap(b)` が速い
    - [x] 自作の `swap` は `using std::swap;` で呼ぶ

## 関連ページ

- [cpprefjp: std::swap](https://cpprefjp.github.io/reference/utility/swap.html)
- [cppreference: std::swap](https://en.cppreference.com/w/cpp/algorithm/swap)
