---
title: std::views::as_rvalue
summary: "要素を右辺値（ムーブ可能）として見る。"
order: 26
group: ビュー（std::views）
tags:
  - アルゴリズム
---

# std::views::as_rvalue

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <ranges>`
</div>

`std::views::as_rvalue` は、**範囲の要素を右辺値として見せる**ビューです。コピーのアルゴリズム（`copy` など）に使うと、コピーではなく**ムーブ**になります。`std::string` の `vector` を、中身を移しながら別の場所へ渡したいときに便利です。

!!! tip "ポイント"
    - `std::move` を要素ごとに書く代わりに、範囲全体に対して 1 回で済む。
    - 元の要素はムーブされて「不定」になる。
    - C++23 の機能。

!!! info "このページを読む前に"
    [ranges とビュー](../../../basics/ranges.md)、[ラムダ式](../../../basics/lambda.md) を先に読むと分かりやすいです。

## 関数の詳しい説明

### views::as_rvalue {#as_rvalue}

```cpp
r | std::views::as_rvalue
std::views::as_rvalue(r)
```

- 戻り値: 要素を右辺値として返すビュー
- 計算量: O(1)

```cpp
#include <algorithm>
#include <iterator>
#include <print>
#include <ranges>
#include <string>
#include <vector>

int main() {
  std::vector<std::string> src = {"alpha", "beta"};
  std::vector<std::string> dst;

  // as_rvalue を挟むと、copy が「ムーブしながらコピー」になる
  std::ranges::copy(src | std::views::as_rvalue, std::back_inserter(dst));
  std::println("{}", dst);
}
```

```text title="実行結果"
["alpha", "beta"]
```

### std::ranges::as_rvalue_view <span class="ver ver-23">C++23</span> {#as_rvalue_view data-toc-label="std::ranges::as_rvalue_view"}

```cpp
template <input_range V>
class as_rvalue_view;
```

- 戻り値: `begin()` / `end()` をもつ view の型
- 計算量: begin / end は定数。要素の取り出しは元の範囲と同じ

要素を右辺値として見せる（ムーブさせる）view。`views::as_rvalue` が作ります。

ふつうは `views::as_rvalue` を使って書くので、この型の名前を自分で書くことは少なく、`auto` で受けます。型名が必要なとき（関数の戻り値の型を明示したいときなど）や、CTAD（クラステンプレートの引数推論）で `std::ranges::as_rvalue_view v(r, ...)` と直接作るときにだけ登場します。

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 巨大な文字列の配列を、コピーせずに別のコンテナへ移す | `copy(src | as_rvalue, back_inserter(dst))` |

## よくあるミス

??? failure "移したあとの元を読む"
    ムーブされた要素は不定です。移したあとは `src` の中身に頼らないでください。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::move`](../move.md) | 移すアルゴリズム。こちらのほうが直接的 |
| [`std::move`](../../utilities/move.md) | 1 つの値を右辺値にする |

## コンパイラ対応

C++23 の機能です。GCC 13 / MSVC 19.34（VS 2022 17.4）以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 要素を右辺値として見せる
    - [x] コピーのアルゴリズムがムーブになる
    - [x] 元は不定になる

## 関連ページ

- [cpprefjp: std::ranges::as_rvalue_view](https://cpprefjp.github.io/reference/ranges/as_rvalue_view.html)
- [cppreference: std::ranges::as_rvalue_view](https://en.cppreference.com/w/cpp/ranges/as_rvalue_view)
