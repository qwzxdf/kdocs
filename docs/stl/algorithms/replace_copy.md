---
title: std::ranges::replace_copy
summary: "値を置き換えた結果を、元を残したまま別の場所へ作る。"
order: 44
tags:
  - アルゴリズム
---

# std::ranges::replace_copy

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`std::ranges::replace_copy` は、[`replace`](replace.md) の「コピー版」です。**元の範囲は変えずに**、置き換えた結果を別の場所へ書き出します。条件で置き換える `replace_copy_if` もあります。

!!! tip "ポイント"
    - 元のデータを残したいとき（セーブデータ、元の入力）に使う。
    - 書き出し先は十分な大きさに。`std::back_inserter` が安全。

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::ranges::replace_copy {#replace_copy}

```cpp
template <input_range R, class T1, class T2, output_iterator<const T2&> O, class Proj = identity>
constexpr replace_copy_result<borrowed_iterator_t<R>, O>
replace_copy(R&& r, O result, const T1& old_value, const T2& new_value, Proj proj = {});
```

- 元は変えずに、置き換えたものを `result` に書き込みます

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <iterator>
#include <print>
#include <vector>

int main() {
  std::vector<int> src = {1, 2, 1};
  std::vector<int> out;
  std::ranges::replace_copy(src, std::back_inserter(out), 1, 9);   // 元は変えず、結果を別の場所へ
  std::println("{} {}", src, out);
}
```

```text title="実行結果"
[1, 2, 1] [9, 2, 9]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 読み込んだ元のデータは残して、表示用に値を置き換える | `replace_copy(src, back_inserter(view), kInvalid, 0)` |

## よくあるミス

??? failure "書き出し先が小さい"
    足りないと範囲外に書き込みます。`back_inserter` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::replace`](replace.md) | 元の範囲を書き換える |
| [`std::ranges::remove_copy`](remove_copy.md) | 取り除いた結果をコピーする |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 置き換えた結果を別の場所に作る
    - [x] 元は変わらない
    - [x] 条件版は `replace_copy_if`

## 関連ページ

- [cpprefjp: std::ranges::replace_copy](https://cpprefjp.github.io/reference/algorithm/ranges_replace_copy.html)
- [cppreference: std::ranges::replace_copy](https://en.cppreference.com/w/cpp/algorithm/ranges/replace_copy)
