---
title: std::views::take_while
summary: "条件を満たす間だけが見える範囲を作る（最初に満たさなくなった所で終わる）。"
order: 4
group: ビュー（std::views）
tags:
  - アルゴリズム
---

# std::views::take_while

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

`std::views::take_while` は、**先頭から、条件を満たす間だけが見える範囲**を作るビューです。最初に条件を満たさなくなった要素で止まり、**その後ろに条件を満たす要素があっても見えません**。

!!! tip "ポイント"
    - [`filter`](filter.md) との違いは、**最初に外れた所で終わる**こと。
    - 整列済みのデータで「しきい値未満の間」を取り出すのに向く。
    - 残りの部分は [`drop_while`](drop_while.md) で取れる。

!!! info "このページを読む前に"
    [ranges とビュー](../../../basics/ranges.md)、[ラムダ式](../../../basics/lambda.md) を先に読むと分かりやすいです。

## 関数の詳しい説明

### views::take_while {#take_while}

```cpp
v | std::views::take_while(pred)
std::views::take_while(v, pred)
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `pred` | 関数・ラムダ | 要素を受け取って、続けるなら `true` |

- 戻り値: 条件を満たす間の要素が見えるビュー
- 計算量: 最初に満たさなくなるまで

```cpp
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3, 10, 4};

  auto small = v | std::views::take_while([](int x) { return x < 5; })
                 | std::ranges::to<std::vector>();
  std::println("{}", small);  // 10 で止まる。後ろの 4 は見えない
}
```

```text title="実行結果"
[1, 2, 3]
```

### std::ranges::take_while_view <span class="ver ver-20">C++20</span> {#take_while_view data-toc-label="std::ranges::take_while_view"}

```cpp
template <view V, class Pred>
class take_while_view;
```

- 戻り値: `begin()` / `end()` をもつ view の型
- 計算量: begin / end は定数。要素の取り出しは元の範囲と同じ

条件が真の間だけ先頭から見せる view。`views::take_while(pred)` が作ります。

ふつうは `views::take_while` を使って書くので、この型の名前を自分で書くことは少なく、`auto` で受けます。型名が必要なとき（関数の戻り値の型を明示したいときなど）や、CTAD（クラステンプレートの引数推論）で `std::ranges::take_while_view v(r, ...)` と直接作るときにだけ登場します。

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 整列済みの経験値表で、到達済みのレベルだけを取り出す | `thresholds | take_while(以下)` |
| 入力バッファの、有効な部分だけを読む | `buf | take_while(非ゼロ)` |

## よくあるミス

??? failure "filter と取り違える"
    `filter` は全部を見て条件に合うものを残します。`take_while` は最初に外れた所で終わります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::views::filter`](filter.md) | 全体から条件に合うものを残す |
| [`std::views::drop_while`](drop_while.md) | 条件を満たす間を飛ばす |
| [`std::views::take`](take.md) | 個数で区切る |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 条件を満たす間だけ見える
    - [x] 最初に外れた所で終わる
    - [x] `filter` とは違う

## 関連ページ

- [cpprefjp: std::ranges::take_while_view](https://cpprefjp.github.io/reference/ranges/take_while_view.html)
- [cppreference: std::ranges::take_while_view](https://en.cppreference.com/w/cpp/ranges/take_while_view)
