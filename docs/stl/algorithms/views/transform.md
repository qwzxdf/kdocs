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

`std::views::transform` は、**各要素に関数を適用した結果が見える範囲**を作るビューです。元の `vector` は変わらず、変換は取り出すときに行われます。「敵の座標だけ取り出す」「全員のダメージを 2 倍にして見る」といった処理に使います。

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

| 場面 | 書き方 |
| --- | --- |
| 敵の座標だけを取り出して描画する | `enemies | transform(&Enemy::pos)` |
| スコアをパーセント表示に変換する | `scores | transform(パーセント)` |

## よくあるミス

??? failure "transform の中で副作用を起こす"
    `transform` の関数は、取り出すたびに（場合によっては複数回）呼ばれます。副作用を書かないでください。処理を実行したいだけなら範囲 for です。

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
