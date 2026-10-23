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

直近 5 フレームの平均を取りたい。連続する 3 つの値のパターンを検出したい。「長さ n の窓を 1 つずつずらす」処理は、`for (i = 0; i + n <= size; ++i)` と添え字で書くと、端の計算が面倒です。`std::views::slide(n)` は、長さ n の窓を 1 つずつずらしながら、窓の中身を範囲として並べるビューです。`{1,2,3,4,5}` に `slide(3)` なら、`{1,2,3}`、`{2,3,4}`、`{3,4,5}` になります。

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

### std::ranges::slide_view <span class="ver ver-23">C++23</span> {#slide_view data-toc-label="std::ranges::slide_view"}

```cpp
template <forward_range V>
class slide_view;
```

- 戻り値: `begin()` / `end()` をもつ view の型
- 計算量: begin / end は定数。要素の取り出しは元の範囲と同じ

長さ n の窓を 1 つずつずらして見せる view。`views::slide(n)` が作ります。

ふつうは `views::slide` を使って書くので、この型の名前を自分で書くことは少なく、`auto` で受けます。型名が必要なとき（関数の戻り値の型を明示したいときなど）や、CTAD（クラステンプレートの引数推論）で `std::ranges::slide_view v(r, ...)` と直接作るときにだけ登場します。

## ゲームでの使いどころ

移動平均に使います。直近のフレーム時間を `vector` に溜めておき、`times | views::slide(5)` の各窓に `fold_left` を適用すれば、5 フレームの平均が並びます。スパイクをならして、FPS の表示を安定させる用途です。

連続した入力のパターン検出にも向いています。3 つ続けて同じ方向が入力されたか、といった判定を窓ごとに調べます。

窓の幅が実行時に決まるなら `slide`、コンパイル時に決まっていて構造化束縛で受けたいなら `adjacent` です。要素数が n 未満なら、結果は空になります。

## よくあるミス

??? failure "窓の中身を、コピーだと思う"
    窓は元の要素を参照する範囲です。元の `vector` を変更すると、窓も変わります。

??? failure "n が要素数より大きい"
    要素数が n 未満のときは、窓が 1 つもできず、空になります。エラーにならないので、空の結果を前提にした処理にします。

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
