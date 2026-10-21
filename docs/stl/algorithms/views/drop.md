---
title: std::views::drop
summary: "先頭の n 個を飛ばした、残りが見える範囲を作る。"
order: 5
group: ビュー（std::views）
tags:
  - アルゴリズム
---

# std::views::drop

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

`std::views::drop` は、**先頭の n 個を飛ばした残り**が見える範囲を作るビューです。ヘッダー行を読み飛ばす、最初のフレームを無視する、といったときに使います。

!!! tip "ポイント"
    - 元が n 個より短いなら、空になる。
    - `take` と組み合わせると「n 個目から m 個」のように切り出せる: `drop(n) | take(m)`。
    - ランダムアクセスできる範囲なら、`drop` は O(1)。

!!! info "このページを読む前に"
    [ranges とビュー](../../../basics/ranges.md)、[ラムダ式](../../../basics/lambda.md) を先に読むと分かりやすいです。

## 関数の詳しい説明

### views::drop {#drop}

```cpp
v | std::views::drop(n)
std::views::drop(v, n)
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `n` | 整数 | 飛ばす個数 |

- 戻り値: 先頭 n 個を除いたビュー
- 計算量: O(1)（ランダムアクセスできる範囲の場合）。それ以外は O(n)

```cpp
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3, 4, 5, 6};

  auto rest = v | std::views::drop(2) | std::ranges::to<std::vector>();
  std::println("{}", rest);

  // 「3 つ目から 2 個」を取り出す
  auto part = v | std::views::drop(2) | std::views::take(2) | std::ranges::to<std::vector>();
  std::println("{}", part);
}
```

```text title="実行結果"
[3, 4, 5, 6]
[3, 4]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| CSV の 1 行目（ヘッダー）を読み飛ばす | `lines | drop(1)` |
| ページ送り（2 ページ目以降） | `items | drop(per_page) | take(per_page)` |

## よくあるミス

??? failure "drop したあとの範囲が元より短いと思わない"
    `drop(n)` の n が元より大きくても安全で、空の範囲になります（`erase` のような範囲外の問題は起きません）。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::views::take`](take.md) | 先頭 n 個だけ見る |
| [`std::views::drop_while`](drop_while.md) | 条件を満たす間飛ばす |
| [`std::span::subspan`](../../containers/span.md) | 配列の一部を切り出す |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 先頭 n 個を飛ばす
    - [x] `drop` と `take` で切り出せる
    - [x] 短ければ空になる

## 関連ページ

- [cpprefjp: std::ranges::drop_view](https://cpprefjp.github.io/reference/ranges/drop_view.html)
- [cppreference: std::ranges::drop_view](https://en.cppreference.com/w/cpp/ranges/drop_view)
