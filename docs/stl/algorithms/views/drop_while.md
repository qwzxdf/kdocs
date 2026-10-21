---
title: std::views::drop_while
summary: "条件を満たす間は飛ばし、そのあとの全部が見える範囲を作る。"
order: 6
group: ビュー（std::views）
tags:
  - アルゴリズム
---

# std::views::drop_while

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

`std::views::drop_while` は、**先頭から条件を満たす間は飛ばして、最初に満たさなくなった所からの全部**が見える範囲を作るビューです。先頭の空白を読み飛ばすときなどに使います。

!!! tip "ポイント"
    - 最初に条件を満たさなくなった所から先は、**条件に関係なく全部見える**。
    - [`take_while`](take_while.md) の残りの部分にあたる。

!!! info "このページを読む前に"
    [ranges とビュー](../../../basics/ranges.md)、[ラムダ式](../../../basics/lambda.md) を先に読むと分かりやすいです。

## 関数の詳しい説明

### views::drop_while {#drop_while}

```cpp
v | std::views::drop_while(pred)
std::views::drop_while(v, pred)
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `pred` | 関数・ラムダ | 要素を受け取って、飛ばすなら `true` |

- 戻り値: 最初に条件を満たさなくなった所からのビュー
- 計算量: O(n)（最初に取り出すとき）

```cpp
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3, 10, 4};

  auto rest = v | std::views::drop_while([](int x) { return x < 5; })
                | std::ranges::to<std::vector>();
  std::println("{}", rest);  // 10 から後ろは全部見える（4 も）
}
```

```text title="実行結果"
[10, 4]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 行頭の空白を読み飛ばす | `line | drop_while(空白)` |
| ログの最初の「INFO」行を飛ばす | `lines | drop_while(INFOの行)` |

## よくあるミス

??? failure "filter と取り違える"
    `filter` は全体から合うものを残しますが、`drop_while` は先頭の連続だけを飛ばします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::views::take_while`](take_while.md) | 条件を満たす間だけ見る |
| [`std::views::drop`](drop.md) | 個数で飛ばす |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 条件を満たす間は飛ばす
    - [x] 外れた所から先は全部見える
    - [x] `take_while` の残り

## 関連ページ

- [cpprefjp: std::ranges::drop_while_view](https://cpprefjp.github.io/reference/ranges/drop_while_view.html)
- [cppreference: std::ranges::drop_while_view](https://en.cppreference.com/w/cpp/ranges/drop_while_view)
