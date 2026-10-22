---
title: std::views::filter
summary: "条件に合う要素だけが見える範囲を作る（元は変わらない）。"
order: 1
group: ビュー（std::views）
tags:
  - アルゴリズム
---

# std::views::filter

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

配列の中から「生きている敵だけ」を処理したいとき、`if (!enemy.alive) continue;` を毎回ループの先頭に書くのは、何度も出てくるうえ、書き忘れるとバグになります。`std::views::filter` は、条件に合う要素だけが見える範囲（ビュー）を作ります。元のコンテナは変わらず、要素のコピーも作られません。

!!! tip "ポイント"
    - **消すのではなく、見ないだけ**。本当に消したいなら [`erase_if`](../erase_if.md)。
    - `|` でほかのビューにつなげられる: `v | filter(f) | transform(g)`。
    - `size()` や `[]` は使えない（全部見ないと個数が分からない）。個数は `std::ranges::distance`。

!!! info "このページを読む前に"
    [ranges とビュー](../../../basics/ranges.md)、[ラムダ式](../../../basics/lambda.md) を先に読むと分かりやすいです。

## 関数の詳しい説明

### views::filter {#filter}

```cpp
v | std::views::filter(pred)
std::views::filter(v, pred)
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `pred` | 関数・ラムダ | 要素を受け取り、**残すなら `true`** を返す |

- 戻り値: 条件に合う要素だけが見えるビュー
- 計算量: 1 つ進めるたびに、次に合う要素まで進む（全体で O(n)）

```cpp
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3, 4, 5, 6};

  auto evens = v | std::views::filter([](int x) { return x % 2 == 0; })
                 | std::ranges::to<std::vector>();  // 欲しいときだけ vector にする
  std::println("{}", evens);
}
```

```text title="実行結果"
[2, 4, 6]
```

### std::ranges::filter_view <span class="ver ver-20">C++20</span> {#filter_view data-toc-label="std::ranges::filter_view"}

```cpp
template <input_range V, indirect_unary_predicate<iterator_t<V>> Pred>
class filter_view;
```

- 戻り値: `begin()` / `end()` をもつ view の型
- 計算量: begin / end は定数。要素の取り出しは元の範囲と同じ

条件に合う要素だけを通す view。`views::filter(pred)` が作ります。

ふつうは `views::filter` を使って書くので、この型の名前を自分で書くことは少なく、`auto` で受けます。型名が必要なとき（関数の戻り値の型を明示したいときなど）や、CTAD（クラステンプレートの引数推論）で `std::ranges::filter_view v(r, ...)` と直接作るときにだけ登場します。

## ゲームでの使いどころ

「生きている敵だけ」「画面内にいるものだけ」「特定のチームだけ」といった絞り込みに使います。`for (auto& e : enemies | std::views::filter(&Enemy::alive))` と書くと、条件に合うものだけがループに現れます。条件が複数あるときは、ラムダ式で書きます。

`filter` は消すのではなく、見えなくするだけです。本当にコンテナから消すなら、`std::erase_if` を使います。

`transform` と組み合わせると、「生きている敵の HP だけを取り出す」ような処理を、ループを書かずに表せます。ただし、`filter` のビューは `size()` を持たないので、個数が必要なら `std::ranges::distance` で数えるか、いったん `vector` に変換します。

## よくあるミス

??? failure "`filter` したものに `size()` や `[]` を使う"
    `filter` のビューは、全部を調べないと個数が分からないため、`size()` もランダムアクセスもありません。個数が欲しいなら `std::ranges::distance(view)`、添え字が欲しいなら `std::ranges::to<std::vector>()` で変換します。

??? failure "元のコンテナを変更したあとのビューを使う"
    ビューは元のコンテナを参照しています。ビューを作ったあとに `push_back` などで元の要素が動くと、ビューが壊れます。ビューを使い終えてから、元を変更します。

??? failure "`filter` の条件に副作用を入れる"
    条件のラムダ式は、`begin()` の呼び出しなどで複数回評価されることがあります。カウンターを増やすなどの副作用を入れると、結果が不安定になります。条件は、状態を変えない式にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::erase_if`](../erase_if.md) | 本当に消す |
| [`std::ranges::copy_if`](../copy.md) | 条件に合うものを別の場所へコピーする |
| [`std::views::take_while`](take_while.md) | 条件を満たす間だけ（途中で止まる） |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 条件に合う要素だけが見える範囲
    - [x] 消さずに見ないだけ
    - [x] 保存せず、その場で使い切る

## 関連ページ

- [cpprefjp: std::ranges::filter_view](https://cpprefjp.github.io/reference/ranges/filter_view.html)
- [cppreference: std::ranges::filter_view](https://en.cppreference.com/w/cpp/ranges/filter_view)
