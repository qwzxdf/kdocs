---
title: std::ranges::random_access_range
summary: "添字で好きな位置へ飛べる範囲を要求するコンセプト。"
order: 900
tags:
  - 型・言語サポート
---

# std::ranges::random_access_range

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

アルゴリズムによって、範囲に求める性質は違います。`std::find` は先頭から読めれば十分ですが、`std::sort` は任意の位置に移動できなければ動きません。`std::ranges::random_access_range<R>` は、<strong>R が「任意の位置に定数時間で移動できる範囲」であること</strong>を要求するコンセプトです。

!!! tip "ポイント"
    - `std::ranges::random_access_range<R>`: `R` が任意の位置に定数時間で移動できる範囲
    - コンテナの種類で、満たすかどうかが決まる
    - アルゴリズムの制約として使われる
    - 階層があり、強い条件は弱い条件を含む（`random_access` ⊃ `bidirectional` ⊃ `forward` ⊃ `input`）

!!! info "このページを読む前に"
    [範囲（ranges）の基礎](../../../basics/ranges.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::ranges::random_access_range {#random_access_range}

<span class="ver ver-20">C++20</span>

```cpp
template <class T>
concept random_access_range = /* 条件 */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べる範囲の型 |

`std::sort` が要求する条件です。

自作の関数テンプレートに `template <std::ranges::random_access_range R>` と書くと、条件を満たさない型を渡されたときに、呼び出しの場所で分かりやすいエラーになります。

## 実際に動かしてみる

```cpp
#include <deque>
#include <list>
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::println("std::vector<int>         -> {}", std::ranges::random_access_range<std::vector<int>>);
  std::println("std::deque<int>          -> {}", std::ranges::random_access_range<std::deque<int>>);
  std::println("std::list<int>           -> {}", std::ranges::random_access_range<std::list<int>>);
}
```

```text title="実行結果"
std::vector<int>         -> true
std::deque<int>          -> true
std::list<int>           -> false
```

## ゲームでの使いどころ

範囲を受け取る自作のテンプレートの制約に使います。

```cpp
template <std::ranges::random_access_range R>
void Process(R&& r) {
  // r は 任意の位置に定数時間で移動できる範囲
}
```

## よくあるミス

??? failure "コンテナの種類を誤解して、期待と違う結果になる"
    `std::list` は `random_access_range` ではありません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`range`](range.md) | 最も基本の範囲 |
| [`random_access_range`](random_access_range.md) | ランダムアクセスできる範囲 |
| [`contiguous_range`](contiguous_range.md) | メモリ上に連続する範囲 |

## コンパイラ対応

C++20 から使えます。GCC 10 以降、Clang 13 以降、Visual Studio 2019 16.10 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::ranges::random_access_range<R>` は任意の位置に定数時間で移動できる範囲
    - [x] コンテナの種類で決まる
    - [x] アルゴリズムの制約として使われる

## 関連ページ

- [cpprefjp: std::ranges::random_access_range](https://cpprefjp.github.io/reference/ranges/random_access_range.html)
- [cppreference: std::ranges::random_access_range](https://en.cppreference.com/w/cpp/ranges/random_access_range)
