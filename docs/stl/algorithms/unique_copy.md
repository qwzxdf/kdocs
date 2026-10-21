---
title: std::ranges::unique_copy
summary: "隣り合う重複をまとめた結果を、元を残したまま別の場所に作る。"
order: 40
tags:
  - アルゴリズム
---

# std::ranges::unique_copy

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`std::ranges::unique_copy` は、[`unique`](unique.md) の「コピー版」です。**元の範囲は変えずに**、隣り合う重複をまとめた結果を別の場所へ書き出します。

!!! tip "ポイント"
    - 元を残したいときに使う。
    - 書き出し先は十分な大きさに。`std::back_inserter` が安全。
    - 全体の重複を除くなら、先に整列しておく。

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::ranges::unique_copy {#unique_copy}

```cpp
template <input_range R, weakly_incrementable O, class Proj = identity, class Comp = ranges::equal_to>
constexpr unique_copy_result<borrowed_iterator_t<R>, O> unique_copy(R&& r, O result, Comp comp = {}, Proj proj = {});
```

- 元はそのままで、連続する重複をまとめたものを `result` に書き込みます

```cpp
#include <algorithm>
#include <iterator>
#include <print>
#include <string>

int main() {
  std::string input = "aaabbbcc";
  std::string compressed;
  std::ranges::unique_copy(input, std::back_inserter(compressed));
  std::println("{}", compressed);
}
```

```text title="実行結果"
abc
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ログから連続した同じメッセージをまとめて表示する | `unique_copy(log, back_inserter(shown))` |

## よくあるミス

??? failure "並べ替えずに全体の重複が消えると思う"
    `unique` と同じで、隣り合う重複だけが対象です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::unique`](unique.md) | 元の範囲の中でまとめる |
| [`std::ranges::copy`](copy.md) | そのままコピーする |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 重複をまとめた結果を別の場所へ作る
    - [x] 元は変わらない
    - [x] 全体の重複は整列してから

## 関連ページ

- [cpprefjp: std::ranges::unique_copy](https://cpprefjp.github.io/reference/algorithm/ranges_unique_copy.html)
- [cppreference: std::ranges::unique_copy](https://en.cppreference.com/w/cpp/algorithm/ranges/unique_copy)
