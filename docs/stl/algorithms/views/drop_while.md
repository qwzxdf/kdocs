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

文字列の先頭の空白を読み飛ばしたい、ソートされたデータの最初の「しきい値未満」の部分を捨てたい。先頭から条件を満たす間だけを捨てる処理を、`for` で書くと、「いつ捨てるのをやめたか」を覚える変数が要ります。`std::views::drop_while` は、先頭から条件を満たす間は飛ばして、最初に満たさなくなった所から先の全部が見える範囲を作ります。

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

### std::ranges::drop_while_view <span class="ver ver-20">C++20</span> {#drop_while_view data-toc-label="std::ranges::drop_while_view"}

```cpp
template <view V, class Pred>
class drop_while_view;
```

- 戻り値: `begin()` / `end()` をもつ view の型
- 計算量: begin / end は定数。要素の取り出しは元の範囲と同じ

条件が真の間だけ先頭を飛ばして見せる view。`views::drop_while(pred)` が作ります。

ふつうは `views::drop_while` を使って書くので、この型の名前を自分で書くことは少なく、`auto` で受けます。型名が必要なとき（関数の戻り値の型を明示したいときなど）や、CTAD（クラステンプレートの引数推論）で `std::ranges::drop_while_view v(r, ...)` と直接作るときにだけ登場します。

## ゲームでの使いどころ

文字列の前の空白を取り除くときに使います。`str | std::views::drop_while(isspace)` で、先頭の空白を除いた範囲が得られます。

ソート済みのログを、「ある時刻より前」を捨てて、それ以降だけ処理するときにも向いています。

条件を満たさなくなった時点から先は、条件に関係なく全部見えます。そのあとにまた条件を満たす要素があっても、飛ばされません。条件に合う要素を全部除くなら、`filter` です。

## よくあるミス

??? failure "filter と取り違える"
    `filter` は全体から合うものを残しますが、`drop_while` は先頭の連続だけを飛ばします。

??? failure "途中の条件に合う要素も除かれると思う"
    `drop_while` は、先頭の連続だけを捨てます。最初に外れた要素以降は、条件に合っても残ります。全部を除くのは `filter` です。

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
