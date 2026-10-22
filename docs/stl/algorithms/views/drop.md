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

CSV の 1 行目は見出しなので読み飛ばしたい、最初の数フレームのデータは捨てたい。先頭の何個かを飛ばして、残りだけを処理したい場面は、よくあります。`for` の開始位置を `1` にずらす書き方は、`vector` なら動きますが、`list` や他のビューには使えません。`std::views::drop` は、先頭の n 個を飛ばした残りが見える範囲を作ります。

!!! tip "ポイント"
    - 元が n 個より短いなら、空になる。
    - `take` と組み合わせると「n 個目から m 個」のように切り出せる: `drop(n) | take(m)`。
    - ランダムアクセスできる範囲なら、`drop` は O(1)。

!!! info "このページを読む前に"
    [ranges とビュー](../../../basics/ranges.md)と、[ラムダ式](../../../basics/lambda.md)が分かると読みやすいです。

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

### std::ranges::drop_view <span class="ver ver-20">C++20</span> {#drop_view data-toc-label="std::ranges::drop_view"}

```cpp
template <view V>
class drop_view;
```

- 戻り値: `begin()` / `end()` をもつ view の型
- 計算量: begin / end は定数。要素の取り出しは元の範囲と同じ

先頭の n 個を飛ばして見せる view。`views::drop(n)` が作ります。

ふつうは `views::drop` を使って書くので、この型の名前を自分で書くことは少なく、`auto` で受けます。型名が必要なとき（関数の戻り値の型を明示したいときなど）や、CTAD（クラステンプレートの引数推論）で `std::ranges::drop_view v(r, ...)` と直接作るときにだけ登場します。

## ゲームでの使いどころ

ファイルの先頭行を読み飛ばすときに使います。行ごとに読んだ文字列の列に対して、`lines | std::views::drop(1)` と書くと、見出しの行を除いた範囲になります。

ランキングの 4 位以降だけを別の欄に表示する、というときは `ranking | std::views::drop(3)` です。`take` と組み合わせて、`drop(n) | take(m)` と書けば、n 個目から m 個を切り出せます。ページ送りの表示（1 ページに 10 件）は、`items | drop(page * 10) | take(10)` で書けます。

元が n 個より短い場合は、エラーにならず、空の範囲になります。

## よくあるミス

??? failure "`drop` の結果が空で、何も表示されない"
    元の要素数が n 個以下だと、`drop(n)` の結果は空です。例外にならないので気づきにくく、ページ送りで最後のページが空白になる、という形で現れます。範囲の長さを `size()` などで確かめます。

??? failure "`filter` したビューに `drop` を使い、重くなる"
    ランダムアクセスできないビュー（`filter` の結果など）に `drop(n)` を使うと、最初の n 個を実際にたどって飛ばすので、O(n) の時間がかかります。`vector` に直接使えば O(1) です。

??? failure "元のコンテナを変更したあとにビューを使う"
    ビューは元のコンテナを参照しています。`push_back` などで元の要素が動くと、ビューが壊れます。ビューを使い終えてから、元を変更します。

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
