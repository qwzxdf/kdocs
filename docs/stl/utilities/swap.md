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

`std::swap` は、**2 つの変数の中身を入れ替える**関数です。コンテナのような大きなものは、中身のポインターを入れ替えるだけで済むので、コピーより速く交換できます。ダブルバッファの入れ替え、並べ替えの自作などで使います。

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

| 場面 | 書き方 |
| --- | --- |
| ダブルバッファの前後を入れ替える | `std::swap(front, back);` |
| 並べ替えの自作 | `std::swap(v[i], v[j]);` |

## よくあるミス

??? failure "同じオブジェクトを swap する"
    自分自身との `swap` は安全ですが、何も起きません。

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
