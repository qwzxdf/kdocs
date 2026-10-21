---
title: std::views::elements
summary: "tuple（や pair）の範囲から、N 番目の要素だけを取り出して見る。"
order: 12
group: ビュー（std::views）
tags:
  - アルゴリズム
---

# std::views::elements

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

`std::views::elements<N>` は、**tuple や pair を並べた範囲から、N 番目の要素だけが見える範囲**を作るビューです。`keys`（0 番目）と `values`（1 番目）は、この特別な形です。

!!! tip "ポイント"
    - `elements<0>` が [`keys`](keys.md)、`elements<1>` が [`values`](values.md)。
    - `map` に使うと、キーだけ・値だけが取れる。
    - `std::tuple` や `std::pair` を並べた `vector` にも使える。

!!! info "このページを読む前に"
    [ranges とビュー](../../../basics/ranges.md)、[ラムダ式](../../../basics/lambda.md) を先に読むと分かりやすいです。

## 関数の詳しい説明

### views::elements {#elements}

```cpp
r | std::views::elements<N>
std::views::elements<N>(r)
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `N` | テンプレート引数 | 取り出す要素の番号（0 始まり） |

- 戻り値: N 番目の要素のビュー
- 計算量: O(1)

```cpp
#include <print>
#include <ranges>
#include <string>
#include <utility>
#include <vector>

int main() {
  std::vector<std::pair<std::string, int>> ranking = {{"Alice", 300}, {"Bob", 520}};

  for (int score : ranking | std::views::elements<1>) {
    std::println("{}", score);
  }
}
```

```text title="実行結果"
300
520
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| (名前, スコア) の並びからスコアだけを取り出す | `ranking | elements<1>` |

## よくあるミス

??? failure "範囲外の番号を指定する"
    N が tuple の要素数以上だと、コンパイルエラーになります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::views::keys`](keys.md) | 0 番目を取る専用の名前 |
| [`std::views::values`](values.md) | 1 番目を取る専用の名前 |
| [`std::views::transform`](transform.md) | 任意の取り出し・変換 |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] tuple の N 番目だけを見る
    - [x] `keys` = `elements<0>`
    - [x] `values` = `elements<1>`

## 関連ページ

- [cpprefjp: std::ranges::elements_view](https://cpprefjp.github.io/reference/ranges/elements_view.html)
- [cppreference: std::ranges::elements_view](https://en.cppreference.com/w/cpp/ranges/elements_view)
