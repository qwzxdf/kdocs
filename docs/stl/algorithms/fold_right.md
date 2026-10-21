---
title: std::ranges::fold_right
summary: "範囲を右から畳み込んで、1 つの値にする。"
order: 24
tags:
  - アルゴリズム
---

# std::ranges::fold_right

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <algorithm>`
</div>

`std::ranges::fold_right` は、**範囲の要素を右（末尾）から順に畳み込む**アルゴリズムです。[`fold_left`](fold_left.md) の逆向きで、関数が左右対称でない（引き算、連結など）ときに結果が変わります。

!!! tip "ポイント"
    - `fold_right` は末尾から始めて、`f(要素, 結果)` の形で畳む（引数の順が `fold_left` と逆）。
    - 足し算や掛け算のように、順序が関係しない関数なら `fold_left` と同じ結果。
    - 初期値なしで末尾の要素から始める `fold_right_last` もある。

!!! info "このページを読む前に"
    [ラムダ式](../../basics/lambda.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::ranges::fold_right <span class="ver ver-23">C++23</span> {#fold_right data-toc-label="std::ranges::fold_right"}

```cpp
template <bidirectional_range R, class T, class F>
constexpr auto fold_right(R&& r, T init, F f);
```

- 末尾から畳み込みます。`f` は `(要素, これまでの結果)` の順に受け取ります

```cpp
#include <algorithm>
#include <print>
#include <string>
#include <vector>

int main() {
  std::vector<std::string> v = {"a", "b", "c"};
  auto s = std::ranges::fold_right(
      v, std::string(), [](const std::string& x, std::string acc) { return acc + x; });
  std::println("{}", s);
}
```

```text title="実行結果"
cba
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 右結合の式（例: `a - (b - c)`）の評価 | `fold_right(v, 0, 引き算)` |

## よくあるミス

??? failure "fold_left と同じ引数の順で書く"
    `fold_left` の関数は `f(結果, 要素)`、`fold_right` は `f(要素, 結果)` です。引数の順が逆なので注意します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::fold_left`](fold_left.md) | 左から畳み込む |
| [`std::accumulate`](accumulate.md) | 従来の合計 |

## コンパイラ対応

C++23 の機能です。GCC 13 / Clang 19 / MSVC 19.34（VS 2022 17.4）以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 右（末尾）から畳み込む
    - [x] 関数の引数の順は `f(要素, 結果)`
    - [x] C++23

## 関連ページ

- [cpprefjp: std::ranges::fold_right](https://cpprefjp.github.io/reference/algorithm/ranges_fold_right.html)
- [cppreference: std::ranges::fold_right](https://en.cppreference.com/w/cpp/algorithm/ranges/fold_right)
