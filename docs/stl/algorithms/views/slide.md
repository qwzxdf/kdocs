---
title: std::views::slide
summary: "長さ n の窓を、1 つずつずらしながら見る（移動平均など）。"
order: 35
group: ビュー（std::views）
tags:
  - アルゴリズム
---

# std::views::slide

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-23">C++23</span>
`#include <ranges>`
</div>

`std::views::slide(n)` は、**長さ n の「窓」を 1 つずつずらしながら、窓の中身を範囲として並べる**ビューです。`{1,2,3,4,5}` に `slide(3)` なら、`{1,2,3}`, `{2,3,4}`, `{3,4,5}`。**移動平均**や、連続する n 個のパターン検出に便利です。

!!! tip "ポイント"
    - 窓は**範囲**なので、`fold_left` などにそのまま渡せる。
    - 窓の幅 n は実行時に決められる（コンパイル時に決まるなら [`adjacent`](adjacent.md)）。
    - 要素数が n 未満なら、空になる。

!!! info "このページを読む前に"
    [ranges とビュー](../../../basics/ranges.md)、[ラムダ式](../../../basics/lambda.md) を先に読むと分かりやすいです。

## 関数の詳しい説明

### views::slide {#slide}

```cpp
r | std::views::slide(n)
std::views::slide(r, n)
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `n` | 整数 | 窓の幅 |

- 戻り値: 長さ n の部分範囲を並べたビュー
- 計算量: O(1)（1 つ進めるたび）

```cpp
#include <algorithm>
#include <functional>
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3, 4, 5};

  // 幅 3 の移動合計
  for (auto window : v | std::views::slide(3)) {
    std::println("{}", std::ranges::fold_left(window, 0, std::plus{}));
  }
}
```

```text title="実行結果"
6
9
12
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| FPS の移動平均（直近 n フレーム） | `times | slide(n)` |
| 連続する 3 つの入力から、コンボ入力を検出する | `inputs | slide(3)` |

## よくあるミス

??? failure "窓の中身を、コピーだと思う"
    窓は元の要素を参照する範囲です。元の `vector` を変更すると、窓も変わります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::views::adjacent`](adjacent.md) | 組（tuple）として返す。N がコンパイル時に決まるとき |
| [`std::views::chunk`](chunk.md) | 重ならずに n 個ずつ区切る |
| [`std::views::stride`](stride.md) | n 個おきに取る |

## コンパイラ対応

C++23 の機能です。GCC 13 / MSVC 19.34（VS 2022 17.4）以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 長さ n の窓をずらして見る
    - [x] 移動平均に使える
    - [x] 要素が n 未満なら空

## 関連ページ

- [cpprefjp: std::ranges::slide_view](https://cpprefjp.github.io/reference/ranges/slide_view.html)
- [cppreference: std::ranges::slide_view](https://en.cppreference.com/w/cpp/ranges/slide_view)
