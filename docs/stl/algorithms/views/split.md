---
title: std::views::split
summary: "区切りの値（または並び）で、範囲を分割して見る。"
order: 10
group: ビュー（std::views）
tags:
  - アルゴリズム
---

# std::views::split

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

カンマ区切りの文字列を、項目ごとに分けたい。設定ファイルの `key=value` を分けたい。文字列の分割は、`find` と `substr` を繰り返す書き方だと、添え字の計算が面倒です。`std::views::split` は、区切りの値や並びで範囲を分割し、部分範囲の列として見せるビューです。分けた結果の各部分も範囲で、区切りそのものは結果に含まれません。

!!! tip "ポイント"
    - 各部分は `subrange`。文字列として使うなら `std::string_view(part.begin(), part.end())`。
    - 区切りそのものは、結果に含まれない。
    - 連続した区切りの間には、空の部分範囲ができる。

!!! info "このページを読む前に"
    [ranges とビュー](../../../basics/ranges.md)、[ラムダ式](../../../basics/lambda.md) を先に読むと分かりやすいです。

## 関数の詳しい説明

### views::split {#split}

```cpp
s | std::views::split(delimiter)
std::views::split(s, delimiter)
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `delimiter` | 値または範囲 | 区切りにする値、または並び |

- 戻り値: 部分範囲を並べたビュー
- 計算量: 取り出しながら探すので、全体で O(n)

```cpp
#include <print>
#include <ranges>
#include <string>
#include <string_view>

int main() {
  std::string line = "hp,mp,atk";

  for (auto part : line | std::views::split(',')) {
    std::println("{}", std::string_view(part.begin(), part.end()));
  }
}
```

```text title="実行結果"
hp
mp
atk
```

### std::ranges::split_view <span class="ver ver-20">C++20</span> {#split_view data-toc-label="std::ranges::split_view"}

```cpp
template <forward_range V, forward_range Pattern>
class split_view;
```

- 戻り値: `begin()` / `end()` をもつ view の型
- 計算量: begin / end は定数。要素の取り出しは元の範囲と同じ

区切りで分割する view。`views::split(sep)` が作ります。

ふつうは `views::split` を使って書くので、この型の名前を自分で書くことは少なく、`auto` で受けます。型名が必要なとき（関数の戻り値の型を明示したいときなど）や、CTAD（クラステンプレートの引数推論）で `std::ranges::split_view v(r, ...)` と直接作るときにだけ登場します。

## ゲームでの使いどころ

CSV や設定ファイルの行を分割するときに使います。`line | std::views::split(',')` で、カンマごとの部分範囲になります。各部分は `subrange` なので、文字列として使うなら `std::string_view(part.begin(), part.end())` に変換します。C++23 では `std::string_view(part)` と書けます。

コピーを作らないので、軽く済みます。ただし、元の文字列が生きている間だけ有効です。

連続した区切りの間には、空の部分範囲ができます。「,,」は、空の項目が 1 つできます。空を捨てたいなら、`filter` で除きます。

## よくあるミス

??? failure "分けた部分を、そのまま文字列だと思う"
    各部分は `subrange` です。`std::string_view` か `std::string` に変換して使います。

??? failure "元の文字列が消える"
    部分範囲は元の文字列を参照しています。元の `std::string` を先に破棄しないでください。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::views::lazy_split`](lazy_split.md) | 入力範囲（1 回しか読めない）にも使える版 |
| [`std::views::join_with`](join_with.md) | 逆に、区切りを挟んでつなぐ |
| `std::string::find` | 位置を 1 つずつ探す方法 |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 区切りで分割して見る
    - [x] 各部分は `subrange`
    - [x] 文字列にするなら `string_view`

## 関連ページ

- [cpprefjp: std::ranges::split_view](https://cpprefjp.github.io/reference/ranges/split_view.html)
- [cppreference: std::ranges::split_view](https://en.cppreference.com/w/cpp/ranges/split_view)
