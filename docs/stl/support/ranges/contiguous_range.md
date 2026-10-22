---
title: std::ranges::contiguous_range
summary: "要素がメモリ上で連続して並ぶ範囲を要求するコンセプト。"
order: 900
tags:
  - 型・言語サポート
---

# std::ranges::contiguous_range

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

`vector`・`array`・`string` のように、要素が連続して並ぶ範囲です。`data()` でポインタを取り出して、C の API に渡せます。

!!! tip "ポイント"
    - コンセプトなので、`requires` やテンプレートの制約に書く。
    - `std::ranges::contiguous_range<T>` は `bool` の定数式。
    - `static_assert` でも確かめられる。

!!! info "このページを読む前に"
    [`std::ranges::range`](range.md) を先に読んでください。

## 関数の詳しい説明

### std::ranges::contiguous_range {#contiguous_range}

```cpp
template <class T>
concept contiguous_range = /* begin が contiguous_iterator を返し、data() がある */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べる範囲の型 |

- 戻り値: 条件を満たせば `true`（コンパイル時の定数）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <print>
#include <ranges>

int main() {
    std::println("{}", std::ranges::contiguous_range<std::vector<int>>);
    std::println("{}", std::ranges::contiguous_range<std::deque<int>>);
}
```

```text title="実行結果"
true
false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | テンプレートの引数を制約して、使える範囲だけを受け付ける |

## よくあるミス

??? failure "`deque` を C の API に渡す"
    `deque` は連続していません。`data()` もありません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`random_access_range`](random_access_range.md) | 連続とは限らない |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 要素がメモリ上で連続して並ぶ範囲を要求するコンセプト
    - [x] コンセプトなので、`requires` やテンプレートの制約に書く
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::ranges::contiguous_range](https://cpprefjp.github.io/reference/ranges/contiguous_range.html)
- [cppreference: std::ranges::contiguous_range](https://en.cppreference.com/w/cpp/ranges/contiguous_range)
