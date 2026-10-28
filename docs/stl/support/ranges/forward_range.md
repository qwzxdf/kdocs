---
title: std::ranges::forward_range
summary: "何度でも先頭から読み直せる範囲を要求するコンセプト。"
order: 900
tags:
  - 型・言語サポート
---

# std::ranges::forward_range

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

アルゴリズムによって、範囲に求める性質は違います。`std::find` は先頭から読めれば十分ですが、`std::sort` は任意の位置に移動できなければ動きません。`std::ranges::forward_range<R>` は、<strong>R が「何度でも先頭から読み直せる範囲」であること</strong>を要求するコンセプトです。

!!! tip "ポイント"
    - `std::ranges::forward_range<R>`: `R` が何度でも先頭から読み直せる範囲
    - コンテナの種類で、満たすかどうかが決まる
    - アルゴリズムの制約として使われる
    - 階層があり、強い条件は弱い条件を含む（`random_access` ⊃ `bidirectional` ⊃ `forward` ⊃ `input`）

!!! info "このページを読む前に"
    [範囲（ranges）の基礎](../../../basics/ranges.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::ranges::forward_range {#forward_range}

<span class="ver ver-20">C++20</span>

```cpp
template <class T>
concept forward_range = /* 条件 */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べる範囲の型 |

`std::forward_list` のように、前へ進む操作だけができる範囲も満たします。

自作の関数テンプレートに `template <std::ranges::forward_range R>` と書くと、条件を満たさない型を渡されたときに、呼び出しの場所で分かりやすいエラーになります。

## 実際に動かしてみる

```cpp
#include <forward_list>
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::println("std::forward_list<int>   -> {}", std::ranges::forward_range<std::forward_list<int>>);
  std::println("std::vector<int>         -> {}", std::ranges::forward_range<std::vector<int>>);
  std::println("int                      -> {}", std::ranges::forward_range<int>);
}
```

```text title="実行結果"
std::forward_list<int>   -> true
std::vector<int>         -> true
int                      -> false
```

## ゲームでの使いどころ

範囲を受け取る自作のテンプレートの制約に使います。

```cpp
template <std::ranges::forward_range R>
void Process(R&& r) {
  // r は 何度でも先頭から読み直せる範囲
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
    - [x] `std::ranges::forward_range<R>` は何度でも先頭から読み直せる範囲
    - [x] コンテナの種類で決まる
    - [x] アルゴリズムの制約として使われる

## 関連ページ

- [cpprefjp: std::ranges::forward_range](https://cpprefjp.github.io/reference/ranges/forward_range.html)
- [cppreference: std::ranges::forward_range](https://en.cppreference.com/w/cpp/ranges/forward_range)
