---
title: std::iota
summary: "範囲を、1 ずつ増える連番で埋める。"
order: 46
tags:
  - アルゴリズム
---

# std::iota

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <numeric>`
</div>

`std::iota` は、**範囲を「開始値, 開始値+1, 開始値+2, …」という連番で埋める**関数です。0 から n-1 までの添字の表を作る、ID を振る、といったときに使います。名前はギリシャ文字のイオタ（ι）に由来し、APL 言語の連番を作る記号から来ています。

!!! tip "ポイント"
    - ヘッダーは `<algorithm>` ではなく **`<numeric>`**。
    - C++23 には `std::ranges::iota` もあるが、使える環境はまだ少ない。普通は `std::iota(begin, end, 開始値)`。
    - 0 から並べた添字を作って、それを [`sort`](sort.md) で並べ替える（間接ソート）のが定番の使い方。

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::iota {#iota}

```cpp
template <class ForwardIt, class T>
constexpr void iota(ForwardIt first, ForwardIt last, T value);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `first`, `last` | イテレータ | 埋める範囲 |
| `value` | `T` | 最初の値。1 ずつ増える |

- `<numeric>` にあります。C++23 では `std::ranges::iota(r, value)` もあります

<div class="anim" data-label="std::iota(v.begin(), v.end(), 1)">
0 0 0 0 # v
+1 +2 +3 +4 # 1 から順に増やしながら入れる
</div>

```cpp
#include <numeric>
#include <print>
#include <vector>

int main() {
  std::vector<int> order(4);
  std::iota(order.begin(), order.end(), 0);  // 0, 1, 2, 3（添字の配列を作る定番）
  std::println("{}", order);
}
```

```text title="実行結果"
[0, 1, 2, 3]
```


## フラグ・オプション

| 書き方 | 重要度 | 意味 |
| --- | --- | --- |
| `std::iota(first, last, 値)` | <span class="rank rank-sometimes">たまに</span> | 従来の書き方（C++11 から） |
| `std::ranges::iota(r, 値)` | <span class="rank rank-rare">知ってるだけ</span> | 範囲版（C++23） |
| [`std::views::iota`](views/iota.md) | <span class="rank rank-often">よく使う</span> | 配列を作らず、連番を「遅延して」並べる |

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| スプライトの ID を 0, 1, 2, … と振る | `std::iota(ids.begin(), ids.end(), 0)` |
| 間接ソートの添字の表 | `iota` で 0〜n-1 を作って、スコア順に並べ替える |
| カードの山に 1 から 52 の番号を振る | `std::iota(deck.begin(), deck.end(), 1)` |

## よくあるミス

??? failure "<algorithm> だけを include して、iota が見つからない"
    `std::iota` は `<numeric>` にあります。`#include <numeric>` を足します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::views::iota`](views/iota.md) | 配列を作らずに連番を並べる |
| [`std::ranges::fill`](fill.md) | 同じ値で埋める |
| [`std::ranges::generate`](generate.md) | 関数を呼んだ結果で埋める |

## コンパイラ対応

`std::iota` は C++11 です。範囲版の `std::ranges::iota` は C++23 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 連番で埋める
    - [x] ヘッダーは `<numeric>`
    - [x] 添字の表を作って間接ソートに使う

## 関連ページ

- [cpprefjp: std::iota](https://cpprefjp.github.io/reference/numeric/iota.html)
- [cppreference: std::iota](https://en.cppreference.com/w/cpp/algorithm/iota)
