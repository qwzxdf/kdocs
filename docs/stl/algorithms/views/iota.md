---
title: std::views::iota
summary: "連番（0, 1, 2, …）を、配列を作らずに並べて見る。"
order: 15
group: ビュー（std::views）
tags:
  - アルゴリズム
---

# std::views::iota

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

`std::views::iota` は、**連番を、配列を作らずに「並べて見る」**ビューです。`iota(1, 5)` なら 1, 2, 3, 4。終わりを省略すると、**無限に続く**連番になります（`take` などで区切って使います）。ループの添字や、ID の表を作るのに使います。

!!! tip "ポイント"
    - `iota(a, b)` は **b を含まない**（`[a, b)`）。
    - 終わりを省略すると無限。必ず [`take`](take.md) などで区切る。
    - `std::iota`（配列に連番を書き込む関数）とは別物。配列が不要なら、こちらのビュー。

!!! info "このページを読む前に"
    [ranges とビュー](../../../basics/ranges.md)、[ラムダ式](../../../basics/lambda.md) を先に読むと分かりやすいです。

## 関数の詳しい説明

### views::iota {#iota}

```cpp
std::views::iota(start)          // start, start+1, ... 無限に続く
std::views::iota(start, bound)   // [start, bound)
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `start` | 整数など | 最初の値 |
| `bound` | 同じ型 | 終わり（この値は含まれない）。省略すると無限 |

- 戻り値: 連番のビュー
- 計算量: O(1)（1 つ進めるたび）

```cpp
#include <print>
#include <ranges>
#include <vector>

int main() {
  auto a = std::views::iota(1, 5) | std::ranges::to<std::vector>();
  std::println("{}", a);

  // 終わりを省略すると無限。take で区切る
  auto b = std::views::iota(0) | std::views::take(3) | std::ranges::to<std::vector>();
  std::println("{}", b);
}
```

```text title="実行結果"
[1, 2, 3, 4]
[0, 1, 2]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 0〜n-1 の添字で回す | `for (int i : std::views::iota(0, n))` |
| ID を 1 から振った一覧 | `iota(1, count + 1)` |
| フレーム番号を 0, 1, 2, … と数える | `iota(0) | take(10)` |

## よくあるミス

??? failure "終わりを含むと思う"
    `iota(1, 5)` に 5 は含まれません。1〜5 にしたいなら `iota(1, 6)`。

??? failure "無限の iota を to<vector> する"
    終わりのない範囲を `vector` にすると、メモリを使い切るまで続きます。必ず `take` で区切ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::iota`](../iota.md) | 配列に連番を書き込む関数 |
| [`std::views::repeat`](repeat.md) | 同じ値を繰り返す |
| [`std::views::take`](take.md) | 個数で区切る |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 連番を作らずに並べる
    - [x] 終わりは含まない
    - [x] 無限なら `take` で区切る

## 関連ページ

- [cpprefjp: std::ranges::iota_view](https://cpprefjp.github.io/reference/ranges/iota_view.html)
- [cppreference: std::ranges::iota_view](https://en.cppreference.com/w/cpp/ranges/iota_view)
