---
title: std::ranges::subrange
summary: "2 つのイテレータ（または先頭と終わり）で表す範囲。"
order: 24
group: ビュー（std::views）
tags:
  - アルゴリズム
---

# std::ranges::subrange

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

`std::ranges::subrange` は、**2 つのイテレータ（先頭と終わり）をまとめて 1 つの範囲にした型**です。`find_end` や `equal_range` のようなアルゴリズムの戻り値として登場します。自分で作れば、「`vector` の途中から途中まで」を範囲として渡せます。

!!! tip "ポイント"
    - アルゴリズムが返す「見つかった部分」は、たいてい `subrange`。
    - 範囲 for や、ほかのビューにそのままつなげられる。
    - `std::span` と似ているが、`span` は連続したメモリ限定。`subrange` はどんなイテレータでも使える。

!!! info "このページを読む前に"
    [ranges とビュー](../../../basics/ranges.md)、[ラムダ式](../../../basics/lambda.md) を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::ranges::subrange {#subrange}

```cpp
template <input_or_output_iterator I, sentinel_for<I> S = I, subrange_kind K = ...>
class std::ranges::subrange;

std::ranges::subrange(first, last)
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `first` | イテレータ | 範囲の先頭 |
| `last` | 番兵（終わり） | 範囲の終わり（含まない） |

- 戻り値: `[first, last)` を表す範囲
- 計算量: O(1)

```cpp
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3, 4, 5};

  std::ranges::subrange part(v.begin() + 1, v.end());  // 2 番目から最後まで
  std::println("個数 {} / 先頭 {}", part.size(), part.front());

  auto vec = part | std::ranges::to<std::vector>();
  std::println("{}", vec);
}
```

```text title="実行結果"
個数 4 / 先頭 2
[2, 3, 4, 5]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 配列の一部だけをアルゴリズムに渡す | `std::ranges::sort(std::ranges::subrange(v.begin(), v.begin() + n))` |
| `find` の結果（見つかった範囲）を後続の処理へ渡す | `auto r = std::ranges::search(...)` の `r` |

## よくあるミス

??? failure "begin() を end() より後ろにする"
    `first` が `last` より後ろだと未定義動作です。

??? failure "元の vector を再確保する"
    `subrange` はイテレータを持つので、`push_back` などで再確保が起きると壊れます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::span`](../../containers/span.md) | 連続したメモリ専用の範囲。軽くて分かりやすい |
| [`std::views::counted`](counted.md) | 先頭と個数から範囲を作る |
| [`std::views::drop`](drop.md) / [`take`](take.md) | 先頭・末尾の個数で切り出す |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 2 つのイテレータを 1 つの範囲にする
    - [x] アルゴリズムの戻り値でよく出てくる
    - [x] 連続メモリなら `span`

## 関連ページ

- [cpprefjp: std::ranges::subrange](https://cpprefjp.github.io/reference/ranges/subrange.html)
- [cppreference: std::ranges::subrange](https://en.cppreference.com/w/cpp/ranges/subrange)
