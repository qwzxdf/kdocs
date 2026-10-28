---
title: std::ranges::common_range
summary: "begin と end が同じ型の範囲を要求するコンセプト。"
order: 900
tags:
  - 型・言語サポート
---

# std::ranges::common_range

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

アルゴリズムによって、範囲に求める性質は違います。`std::find` は先頭から読めれば十分ですが、`std::sort` は任意の位置に移動できなければ動きません。`std::ranges::common_range<R>` は、<strong>R が「`begin` と `end` が同じ型の範囲」であること</strong>を要求するコンセプトです。

!!! tip "ポイント"
    - `std::ranges::common_range<R>`: `R` が`begin` と `end` が同じ型の範囲
    - コンテナの種類で、満たすかどうかが決まる
    - アルゴリズムの制約として使われる
    - 他のコンセプトと組み合わせて使える

!!! info "このページを読む前に"
    [範囲（ranges）の基礎](../../../basics/ranges.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::ranges::common_range {#common_range}

<span class="ver ver-20">C++20</span>

```cpp
template <class T>
concept common_range = /* 条件 */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べる範囲の型 |

従来のアルゴリズム（イテレーターを 2 つ取る版）に、範囲を渡せる条件です。無限に続く範囲や、`take_while` のように末尾の型が違うビューは満たしません。

自作の関数テンプレートに `template <std::ranges::common_range R>` と書くと、条件を満たさない型を渡されたときに、呼び出しの場所で分かりやすいエラーになります。

## 実際に動かしてみる

```cpp
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::println("std::vector<int>         -> {}", std::ranges::common_range<std::vector<int>>);
}
```

```text title="実行結果"
std::vector<int>         -> true
```

## ゲームでの使いどころ

範囲を受け取る自作のテンプレートの制約に使います。

```cpp
template <std::ranges::common_range R>
void Process(R&& r) {
  // r は `begin` と `end` が同じ型の範囲
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
    - [x] `std::ranges::common_range<R>` は`begin` と `end` が同じ型の範囲
    - [x] コンテナの種類で決まる
    - [x] アルゴリズムの制約として使われる

## 関連ページ

- [cpprefjp: std::ranges::common_range](https://cpprefjp.github.io/reference/ranges/common_range.html)
- [cppreference: std::ranges::common_range](https://en.cppreference.com/w/cpp/ranges/common_range)
