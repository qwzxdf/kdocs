---
title: std::ranges::starts_with
summary: "範囲が、別の範囲の並びで始まるかを調べる。"
order: 63
tags:
  - アルゴリズム
---

# std::ranges::starts_with

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <algorithm>`
</div>

`std::ranges::starts_with` は、**範囲が別の範囲の並びで始まっているか**を調べます。文字列だけでなく、`vector` など任意の範囲に使えます。`std::string` には、同じ名前のメンバ関数（C++20）もあります。

!!! tip "ポイント"
    - 先頭の並びを調べるだけなので、`search` で全体を探すより速い。
    - `std::string` や `std::string_view` なら、メンバ関数 `s.starts_with(...)` のほうが手軽。
    - 空の範囲を渡すと必ず `true`。

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::ranges::starts_with {#starts_with}

```cpp
template <input_range R1, input_range R2, class Pred = ranges::equal_to,
          class Proj1 = identity, class Proj2 = identity>
constexpr bool starts_with(R1&& r1, R2&& r2, Pred pred = {}, Proj1 proj1 = {}, Proj2 proj2 = {});
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `r1` | 範囲 | 調べる範囲 |  |
| `r2` | 範囲 | 先頭にあるはずの並び |  |
| `pred` | 関数 | 「等しい」の判定 | `==` |

- 戻り値: `r1` が `r2` で始まっていれば `true`。`r2` のほうが長ければ `false`
- 計算量: O(m)（m は `r2` の長さ）

```cpp
#include <algorithm>
#include <print>
#include <string>
#include <string_view>
#include <vector>

int main() {
  std::string path = "assets/textures/hero.png";
  std::string_view prefix = "assets/";
  std::println("{}", std::ranges::starts_with(path, prefix));

  std::vector<int> v = {1, 2, 3, 4};
  std::println("{}", std::ranges::starts_with(v, std::vector{1, 2}));
}
```

```text title="実行結果"
true
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| アセットのパスが特定のフォルダか | `starts_with(path, "assets/")` |
| コマンドの入力履歴が決まった並びで終わったか | `starts_with(history, command)` |

## よくあるミス

??? failure "古いコンパイラで使えない"
    C++23 の機能です。GCC 13 / MSVC 19.31 以降で使えます。使えないときは `std::string` のメンバ関数、または `std::ranges::equal` と `std::views::take` / `drop` を組み合わせます。

## 類似

| 名前 | 違い |
| --- | --- |
| `std::string::starts_with` | 文字列専用。C++20 から |
| [`std::ranges::search`](search.md) | 途中のどこかに含まれているか |
| [`std::ranges::equal`](equal.md) | 全体が同じか |

## コンパイラ対応

C++23 の機能です。GCC 13 / Clang 17 / MSVC 19.31（VS 2022 17.1）以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 先頭が同じ並びかを調べる
    - [x] 文字列にもコンテナにも使える
    - [x] C++23

## 関連ページ

- [cpprefjp: std::ranges::starts_with](https://cpprefjp.github.io/reference/algorithm/ranges_starts_with.html)
- [cppreference: std::ranges::starts_with](https://en.cppreference.com/w/cpp/algorithm/ranges/starts_with)
