---
title: std::views::transform
summary: "各要素を変換した結果が見える範囲を作る（元は変わらない）。"
order: 2
group: ビュー（std::views）
tags:
  - アルゴリズム
---

# std::views::transform

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

敵のリストから「HP だけの配列」が欲しい、座標をすべて 2 倍にしたい。要素を 1 つずつ別の値に変換する処理は、`for` で新しい `vector` に `push_back` していくと、数行のコードになります。`std::views::transform` は、変換のルールだけを指定して、変換後の値が見える範囲（ビュー）を作ります。元は変わらず、取り出すときに初めて変換が実行されます。

!!! tip "ポイント"
    - メンバポインター（`&Enemy::name`）を渡せば、メンバだけを取り出せる。
    - 変換はアクセスのたびに行われる。重い計算は結果を保存する。
    - 結果を書き換える用途ではない（ビューは読み取り専用の変換）。

!!! info "このページを読む前に"
    [ranges とビュー](../../../basics/ranges.md)、[ラムダ式](../../../basics/lambda.md) を先に読むと分かりやすいです。

## 関数の詳しい説明

### views::transform {#transform}

```cpp
v | std::views::transform(func)
std::views::transform(v, func)
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `func` | 関数・ラムダ | 要素を受け取って、変換後の値を返す |

- 戻り値: 各要素を変換した値が見えるビュー
- 計算量: 取り出すたびに `func` を 1 回呼ぶ

```cpp
#include <print>
#include <ranges>
#include <string>
#include <vector>

struct Enemy {
  std::string name;
  int hp;
};

int main() {
  std::vector<int> v = {1, 2, 3, 4};
  auto squares = v | std::views::transform([](int x) { return x * x; })
                   | std::ranges::to<std::vector>();
  std::println("{}", squares);

  std::vector<Enemy> enemies = {{"スライム", 10}, {"ゴブリン", 30}};
  // メンバポインターを渡すと、そのメンバだけが見える
  for (const auto& name : enemies | std::views::transform(&Enemy::name)) {
    std::println("{}", name);
  }
}
```

```text title="実行結果"
[1, 4, 9, 16]
スライム
ゴブリン
```

### std::ranges::transform_view <span class="ver ver-20">C++20</span> {#transform_view data-toc-label="std::ranges::transform_view"}

```cpp
template <input_range V, copy_constructible F>
class transform_view;
```

- 戻り値: `begin()` / `end()` をもつ view の型
- 計算量: begin / end は定数。要素の取り出しは元の範囲と同じ

各要素を関数で変換して見せる view。`views::transform(f)` が作ります。

ふつうは `views::transform` を使って書くので、この型の名前を自分で書くことは少なく、`auto` で受けます。型名が必要なとき（関数の戻り値の型を明示したいときなど）や、CTAD（クラステンプレートの引数推論）で `std::ranges::transform_view v(r, ...)` と直接作るときにだけ登場します。

## ゲームでの使いどころ

メンバだけを取り出す処理で使います。`enemies | std::views::transform(&Enemy::hp)` で、HP だけの範囲になります。これを `std::ranges::max` に渡せば最大の HP が、`std::ranges::to<std::vector>` に渡せば HP の配列が得られます。

座標の変換にも使います。ワールド座標を画面の座標へ直す、すべての頂点に行列を掛ける、といった処理を、ループを書かずに表せます。

`filter` と組み合わせることがほとんどです。`enemies | views::filter(alive) | views::transform(&Enemy::position)` で、生きている敵の位置だけが取り出せます。ただし、`transform` は取り出すたびに変換を実行するので、同じ要素を何度も読むと、そのたびに計算されます。何度も使うなら、いったん `vector` に入れます。

## よくあるミス

??? failure "同じビューを何度も読んで、重い変換が毎回走る"
    ビューは遅延評価です。`transform` に重い計算を渡して、そのビューを 2 回ループすると、重い計算も 2 回走ります。何度も使うなら、`std::ranges::to<std::vector>()` で結果を保存します。

??? failure "変換の戻り値が参照のつもりで書く"
    `transform` のラムダ式が値を返すと、その値は一時的なものです。`auto& x : view | transform(...)` のように参照で受けると、コンパイルエラーになります。`auto x` か `const auto& x` で受けます。

??? failure "一時的な `vector` からビューを作る"
    `make_vec() | views::transform(f)` は、`make_vec()` が返した一時オブジェクトが、行の終わりで消えます。以降にビューを使うとぶら下がり参照になります。いったん変数に受けてからビューを作ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::transform`](../transform.md) | 結果を別の場所に書き出す（アルゴリズム） |
| [`std::views::filter`](filter.md) | 絞り込み |
| [`std::views::elements`](elements.md) | tuple の N 番目だけ取り出す |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 各要素を変換して「見る」
    - [x] メンバポインターが渡せる
    - [x] 副作用は書かない

## 関連ページ

- [cpprefjp: std::ranges::transform_view](https://cpprefjp.github.io/reference/ranges/transform_view.html)
- [cppreference: std::ranges::transform_view](https://en.cppreference.com/w/cpp/ranges/transform_view)
