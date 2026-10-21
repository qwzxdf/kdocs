---
title: std::views::lazy_split
summary: "区切りで分割する（入力範囲にも使える、遅延する版）。"
order: 11
group: ビュー（std::views）
tags:
  - アルゴリズム
---

# std::views::lazy_split

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

`std::views::lazy_split` は、[`split`](split.md) と同じく区切りで分割しますが、**1 回しか読めない入力範囲**（`istream` の範囲など）にも使えます。そのかわり、各部分は連続したメモリとは限らず、`string_view` に直接変換できません。

!!! tip "ポイント"
    - 普通の文字列には [`split`](split.md) のほうが扱いやすい。
    - 各部分は「遅延して読む範囲」で、`std::string(part.begin(), part.end())` のように文字列へ変換する。
    - C++23 で `split` が整った今は、`lazy_split` の出番は少ない。

!!! info "このページを読む前に"
    [ranges とビュー](../../../basics/ranges.md)、[ラムダ式](../../../basics/lambda.md) を先に読むと分かりやすいです。

## 関数の詳しい説明

### views::lazy_split {#lazy_split}

```cpp
s | std::views::lazy_split(delimiter)
std::views::lazy_split(s, delimiter)
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `delimiter` | 値または範囲 | 区切りにする値、または並び |

- 戻り値: 部分範囲を並べたビュー
- 計算量: O(n)

```cpp
#include <print>
#include <ranges>
#include <string>

int main() {
  std::string line = "a-b-c";

  for (auto part : line | std::views::lazy_split('-')) {
    std::println("{}", std::string(part.begin(), part.end()));
  }
}
```

```text title="実行結果"
a
b
c
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 1 回しか読めない入力を、区切りで分けながら読む | `input | lazy_split(',')` |

## よくあるミス

??? failure "各部分を string_view にしようとする"
    `lazy_split` の部分範囲は連続したメモリとは限らないので、`string_view` にできません。`std::string` にコピーします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::views::split`](split.md) | 普通の範囲向け。こちらが扱いやすい |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 入力範囲にも使える分割
    - [x] 各部分は `string_view` にできない
    - [x] 普通は `split` を使う

## 関連ページ

- [cpprefjp: std::ranges::lazy_split_view](https://cpprefjp.github.io/reference/ranges/lazy_split_view.html)
- [cppreference: std::ranges::lazy_split_view](https://en.cppreference.com/w/cpp/ranges/lazy_split_view)
