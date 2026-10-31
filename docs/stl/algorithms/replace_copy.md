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

元の配列を変えずに、特定の値を別の値に置き換えたコピーを作りたい。`std::replace_copy(first, last, d_first, old, new)` は、`old` に等しい要素を `new` にして、結果を `d_first` に書き出します。

!!! tip "ポイント"
    - 元の範囲は変わらない
    - `old` と等しい要素を `new` に置き換えて、出力先に書く
    - 条件で置き換えるなら `replace_copy_if`
    - 出力の領域は、入力と同じ長さが要る

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::replace_copy {#replace_copy}

<span class="ver ver-11">C++98〜</span>

```cpp
template <class InputIt, class OutputIt, class T>
OutputIt replace_copy(InputIt first, InputIt last, OutputIt d_first,
                      const T& old_value, const T& new_value);
```

戻り値は、出力の最後の次の位置です。

その場で置き換えるなら `std::replace`、コピーを作るなら `replace_copy` です。入力と出力が重なると、結果が保証されません。

C++20 の `std::ranges::replace_copy` は、範囲を直接渡せて、射影も使えます。

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  const std::vector<int> v = {1, 2, 1, 3};
  std::vector<int> out(v.size());

  std::replace_copy(v.begin(), v.end(), out.begin(), 1, 9);

  std::println("元: {}", v);    // 変わらない
  std::println("結果: {}", out);
}
```

```text title="実行結果"
元: [1, 2, 1, 3]
結果: [9, 2, 9, 3]
```

## ゲームでの使いどころ

元のデータを残したまま、特定の値（無効値 -1 など）を置き換えたコピーを作るときに使います。

## よくあるミス

??? failure "出力の領域が足りない"
    入力と同じ長さを用意します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`replace_copy_if`](replace_copy_if.md) | 条件で置き換える |
| [`replace`](replace.md) | その場で置き換える |
| [`copy`](copy.md) | 置き換えないコピー |

## コンパイラ対応

C++98 から使えます。

## 関連ページ

- [cpprefjp: std::ranges::replace_copy](https://cpprefjp.github.io/reference/algorithm/ranges_replace_copy.html)
- [cppreference: std::ranges::replace_copy](https://en.cppreference.com/w/cpp/algorithm/ranges/replace_copy)
