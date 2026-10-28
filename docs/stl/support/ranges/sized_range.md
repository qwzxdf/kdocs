---
title: std::ranges::sized_range
summary: "要素数を定数時間で返せる範囲を要求するコンセプト。"
order: 900
tags:
  - 型・言語サポート
---

# std::ranges::sized_range

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

アルゴリズムによって、範囲に求める性質は違います。`std::find` は先頭から読めれば十分ですが、`std::sort` は任意の位置に移動できなければ動きません。`std::ranges::sized_range<R>` は、<strong>R が「`std::ranges::size` で要素数を定数時間で得られる範囲」であること</strong>を要求するコンセプトです。

!!! tip "ポイント"
    - `std::ranges::sized_range<R>`: `R` が`std::ranges::size` で要素数を定数時間で得られる範囲
    - コンテナの種類で、満たすかどうかが決まる
    - アルゴリズムの制約として使われる
    - 他のコンセプトと組み合わせて使える

!!! info "このページを読む前に"
    [範囲（ranges）の基礎](../../../basics/ranges.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::ranges::sized_range {#sized_range}

<span class="ver ver-20">C++20</span>

```cpp
template <class T>
concept sized_range = /* 条件 */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べる範囲の型 |

`std::forward_list` は要素数を数えるのに O(n) かかるので、満たしません。

自作の関数テンプレートに `template <std::ranges::sized_range R>` と書くと、条件を満たさない型を渡されたときに、呼び出しの場所で分かりやすいエラーになります。

## 実際に動かしてみる

```cpp
#include <forward_list>
#include <list>
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::println("std::vector<int>         -> {}", std::ranges::sized_range<std::vector<int>>);
  std::println("std::list<int>           -> {}", std::ranges::sized_range<std::list<int>>);
  std::println("std::forward_list<int>   -> {}", std::ranges::sized_range<std::forward_list<int>>);
}
```

```text title="実行結果"
std::vector<int>         -> true
std::list<int>           -> true
std::forward_list<int>   -> false
```

## ゲームでの使いどころ

範囲を受け取る自作のテンプレートの制約に使います。

```cpp
template <std::ranges::sized_range R>
void Process(R&& r) {
  // r は `std::ranges::size` で要素数を定数時間で得られる範囲
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
    - [x] `std::ranges::sized_range<R>` は`std::ranges::size` で要素数を定数時間で得られる範囲
    - [x] コンテナの種類で決まる
    - [x] アルゴリズムの制約として使われる

## 関連ページ

- [cpprefjp: std::ranges::sized_range](https://cpprefjp.github.io/reference/ranges/sized_range.html)
- [cppreference: std::ranges::sized_range](https://en.cppreference.com/w/cpp/ranges/sized_range)
