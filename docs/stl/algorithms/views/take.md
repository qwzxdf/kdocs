---
title: std::views::take
summary: "先頭から n 個だけが見える範囲を作る。"
order: 3
group: ビュー（std::views）
tags:
  - アルゴリズム
---

# std::views::take

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

ランキングの上位 10 件だけを表示したい、ログの最新 5 件だけを出したい。全体の中から先頭の n 個だけが欲しいとき、`for` の中で数えて `break` するコードは、読み取りにくく、書き間違えやすくなります。`std::views::take` は、先頭から n 個だけが見える範囲を作るビューです。元が n 個より短ければ、全部が見えます。無限に続く範囲も、有限にできます。

!!! tip "ポイント"
    - 無限に続く範囲（`views::iota(0)`）に使うと、有限にできる。
    - n 個目より後ろは、評価もされない。
    - 先頭を飛ばすなら [`drop`](drop.md)。

!!! info "このページを読む前に"
    [ranges とビュー](../../../basics/ranges.md)と、[ラムダ式](../../../basics/lambda.md)が分かると読みやすいです。

## 関数の詳しい説明

### views::take {#take}

```cpp
v | std::views::take(n)
std::views::take(v, n)
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `n` | 整数 | 見せたい個数（元より多ければ全部） |

- 戻り値: 先頭 n 個のビュー
- 計算量: O(1) で作成。進めるたびに O(1)

```cpp
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::vector<int> ranking = {100, 90, 80, 70, 60};

  auto top3 = ranking | std::views::take(3) | std::ranges::to<std::vector>();
  std::println("{}", top3);
}
```

```text title="実行結果"
[100, 90, 80]
```

### std::ranges::take_view <span class="ver ver-20">C++20</span> {#take_view data-toc-label="std::ranges::take_view"}

```cpp
template <view V>
class take_view;
```

- 戻り値: `begin()` / `end()` をもつ view の型
- 計算量: begin / end は定数。要素の取り出しは元の範囲と同じ

先頭から n 個だけを見せる view。`views::take(n)` が作ります。

ふつうは `views::take` を使って書くので、この型の名前を自分で書くことは少なく、`auto` で受けます。型名が必要なとき（関数の戻り値の型を明示したいときなど）や、CTAD（クラステンプレートの引数推論）で `std::ranges::take_view v(r, ...)` と直接作るときにだけ登場します。

## ゲームでの使いどころ

ランキングの表示で、上位だけを切り出します。スコアを降順に並べたあと、`ranking | std::views::take(10)` で 10 位までです。

無限の連番から必要な数だけ取り出すときにも使います。`std::views::iota(0) | std::views::take(5)` は 0 から 4 です。生成の途中で止めたい、無限のジェネレーターに終わりを付けたい、という場面で役に立ちます。

先頭を飛ばしてから取るなら、`drop(n) | take(m)` です。ページ送りの 1 ページ分がこの形で書けます。

## よくあるミス

??? failure "n が負の値や大きすぎる値になる"
    負の個数は未定義動作です。`size_t` や、0 以上を保証した値を渡します。元より大きい n は、全部が見えるだけでエラーにはなりません。

??? failure "`take` の結果の要素数を n だと思い込む"
    元が短いと、結果も短くなります。ちょうど n 個あると想定して、添え字で n - 1 番目にアクセスすると、範囲外になります。

??? failure "`filter` したビューに `take` して、全体を評価してしまう"
    `filter` の結果から `take(3)` を取るとき、3 個が見つかった時点で止まるので無駄がありません。ただし `reverse` や `sort` を挟むと、全体を見る必要が出ます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::views::drop`](drop.md) | 先頭 n 個を飛ばす |
| [`std::views::take_while`](take_while.md) | 条件が続く間だけ |
| [`std::ranges::copy_n`](../copy.md) | 先頭 n 個を別の場所へコピーする |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 先頭 n 個だけを見る
    - [x] 無限の範囲を有限にできる
    - [x] 短ければ全部が見える

## 関連ページ

- [cpprefjp: std::ranges::take_view](https://cpprefjp.github.io/reference/ranges/take_view.html)
- [cppreference: std::ranges::take_view](https://en.cppreference.com/w/cpp/ranges/take_view)
