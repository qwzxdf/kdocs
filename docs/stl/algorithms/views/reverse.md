---
title: std::views::reverse
summary: "逆順に並んで見える範囲を作る（コピーも書き換えもしない）。"
order: 7
group: ビュー（std::views）
tags:
  - アルゴリズム
---

# std::views::reverse

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

`std::views::reverse` は、**要素が逆順に並んで見える範囲**を作るビューです。元の `vector` は変わらず、コピーも作られません。「新しい順に表示する」「後ろから探す」のに使います。

!!! tip "ポイント"
    - 元が**双方向**にたどれる範囲（vector、list、deque など）である必要がある。
    - 並びそのものを書き換えるなら [`ranges::reverse`](../reverse.md)。
    - `reverse | take(3)` で「最後の 3 個」を取れる。

!!! info "このページを読む前に"
    [ranges とビュー](../../../basics/ranges.md)、[ラムダ式](../../../basics/lambda.md) を先に読むと分かりやすいです。

## 関数の詳しい説明

### views::reverse {#reverse}

```cpp
v | std::views::reverse
std::views::reverse(v)
```

- 戻り値: 逆順のビュー
- 計算量: O(1)

```cpp
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::vector<int> history = {1, 2, 3};

  auto newest_first = history | std::views::reverse | std::ranges::to<std::vector>();
  std::println("{}", newest_first);

  // 最後の 2 個だけ
  auto last2 = history | std::views::reverse | std::views::take(2) | std::ranges::to<std::vector>();
  std::println("{}", last2);
}
```

```text title="実行結果"
[3, 2, 1]
[2, 1]
```

### std::ranges::reverse_view <span class="ver ver-20">C++20</span> {#reverse_view data-toc-label="std::ranges::reverse_view"}

```cpp
template <view V>
class reverse_view;
```

- 戻り値: `begin()` / `end()` をもつ view の型
- 計算量: begin / end は定数。要素の取り出しは元の範囲と同じ

逆順に見せる view。`views::reverse` が作ります。

ふつうは `views::reverse` を使って書くので、この型の名前を自分で書くことは少なく、`auto` で受けます。型名が必要なとき（関数の戻り値の型を明示したいときなど）や、CTAD（クラステンプレートの引数推論）で `std::ranges::reverse_view v(r, ...)` と直接作るときにだけ登場します。

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 履歴を新しい順に表示する | `history | reverse` |
| 末尾から条件に合うものを探す | `v | reverse | filter(...)` |

## よくあるミス

??? failure "forward_list に使う"
    `std::forward_list` は後ろへ進めない（片方向）ので、`reverse` できません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::reverse`](../reverse.md) | 並びを実際に逆にする |
| [`std::ranges::find_last`](../find_last.md) | 最後の一致を探す |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 逆順で「見る」
    - [x] 元は変わらない
    - [x] 双方向の範囲が必要

## 関連ページ

- [cpprefjp: std::ranges::reverse_view](https://cpprefjp.github.io/reference/ranges/reverse_view.html)
- [cppreference: std::ranges::reverse_view](https://en.cppreference.com/w/cpp/ranges/reverse_view)
