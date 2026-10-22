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

0 から 99 までの番号で 100 回繰り返したい、ID の表を作りたい。`for (int i = 0; i < 100; ++i)` は定番ですが、「連番の範囲」として扱いたい場面（他のビューにつなげたい、アルゴリズムに渡したい）では使えません。`std::views::iota` は、連番を配列に作らず、並んでいるものとして見せてくれるビューです。終わりを省略すると無限に続き、`take` などで区切って使います。

!!! tip "ポイント"
    - `iota(a, b)` は **b を含まない**（`[a, b)`）。
    - 終わりを省略すると無限。必ず [`take`](take.md) などで区切る。
    - `std::iota`（配列に連番を書き込む関数）とは別物。配列が不要なら、こちらのビュー。

!!! info "このページを読む前に"
    [ranges とビュー](../../../basics/ranges.md)と、[ラムダ式](../../../basics/lambda.md)が分かると読みやすいです。

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

### std::ranges::iota_view <span class="ver ver-20">C++20</span> {#iota_view data-toc-label="std::ranges::iota_view"}

```cpp
template <weakly_incrementable W, semiregular Bound = unreachable_sentinel_t>
class iota_view;
```

- 戻り値: `begin()` / `end()` をもつ view の型
- 計算量: begin / end は定数。要素の取り出しは元の範囲と同じ

start から 1 ずつ増える値を並べる view。`views::iota(a, b)` が作ります。

ふつうは `views::iota` を使って書くので、この型の名前を自分で書くことは少なく、`auto` で受けます。型名が必要なとき（関数の戻り値の型を明示したいときなど）や、CTAD（クラステンプレートの引数推論）で `std::ranges::iota_view v(r, ...)` と直接作るときにだけ登場します。

## ゲームでの使いどころ

範囲ベースの `for` で、番号のループを書くときに使います。`for (int i : std::views::iota(0, 100))` は、通常の `for` と同じ意味ですが、`filter` や `transform` につなげられます。

無限の連番は、ゲームの ID の発行や、タイムステップの列に使えます。`iota(0) | take(5)` は 0 から 4 までです。

`std::iota` という名前の別の関数があります。こちらは、既存の配列に連番を書き込む関数で、`<numeric>` にあります。配列が要らないなら、ビューの `views::iota` を使います。

## よくあるミス

??? failure "上限を含むつもりで書く"
    `iota(1, 5)` は 1、2、3、4 です。5 は含まれません。`[a, b)` の半開区間です。

??? failure "終わりを省略したまま、全体を使おうとする"
    `iota(0)` は無限に続きます。`for` で回すと、終わらずにオーバーフローします。`take` などで区切ります。

??? failure "`std::iota` と取り違える"
    `std::iota(v.begin(), v.end(), 0)` は、`v` を書き換える関数です。ビューの `views::iota` は、書き込み先を持たず、並びを見せるだけです。

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
