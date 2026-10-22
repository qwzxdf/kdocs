---
title: std::views::zip_transform
summary: "複数の範囲の同じ位置どうしに関数を適用した結果を並べる。"
order: 32
group: ビュー（std::views）
tags:
  - アルゴリズム
---

# std::views::zip_transform

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <ranges>`
</div>

`std::views::zip_transform` は、**複数の範囲の同じ位置どうしを関数に渡して、その結果を並べる**ビューです。[`zip`](zip.md) して [`transform`](transform.md) するのを、1 つにまとめたものです。2 つの配列を足し合わせる、のような処理に向きます。

!!! tip "ポイント"
    - 第 1 引数が関数、残りが範囲。
    - 最も短い範囲の長さまで。
    - 結果は新しい値（参照ではなく、関数が返したもの）。

!!! info "このページを読む前に"
    [ranges とビュー](../../../basics/ranges.md)、[ラムダ式](../../../basics/lambda.md) を先に読むと分かりやすいです。

## 関数の詳しい説明

### views::zip_transform {#zip_transform}

```cpp
std::views::zip_transform(func, r1, r2, ...)
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `func` | 関数 | 各範囲の同じ位置の要素を受け取り、結果を返す |
| `r1, r2, ...` | 範囲 | 同時に回す範囲 |

- 戻り値: 関数の結果を並べたビュー
- 計算量: O(1)（1 つ進めるたび）

```cpp
#include <functional>
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::vector<int> a = {1, 2, 3};
  std::vector<int> b = {10, 20, 30};

  auto sum = std::views::zip_transform(std::plus{}, a, b) | std::ranges::to<std::vector>();
  std::println("{}", sum);
}
```

```text title="実行結果"
[11, 22, 33]
```

### std::ranges::zip_transform_view <span class="ver ver-23">C++23</span> {#zip_transform_view data-toc-label="std::ranges::zip_transform_view"}

```cpp
template <copy_constructible F, input_range... Vs>
class zip_transform_view;
```

- 戻り値: `begin()` / `end()` をもつ view の型
- 計算量: begin / end は定数。要素の取り出しは元の範囲と同じ

複数の範囲をいっしょに歩き、関数で 1 つの値にする view。`views::zip_transform` が作ります。

ふつうは `views::zip_transform` を使って書くので、この型の名前を自分で書くことは少なく、`auto` で受けます。型名が必要なとき（関数の戻り値の型を明示したいときなど）や、CTAD（クラステンプレートの引数推論）で `std::ranges::zip_transform_view v(r, ...)` と直接作るときにだけ登場します。

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 2 つのベクトル配列の足し算 | `zip_transform(plus, a, b)` |
| 位置に速度を足した次の位置の一覧 | `zip_transform(次の位置, pos, vel)` |

## よくあるミス

??? failure "結果の書き込みを期待する"
    ビューは結果を作るだけです。元の配列に書き戻すなら、範囲 for で `zip` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::views::zip`](zip.md) | 組のまま回す |
| [`std::ranges::transform`](../transform.md) | 2 つの範囲から別の場所へ書き出す（アルゴリズム） |

## コンパイラ対応

C++23 の機能です。GCC 13 / MSVC 19.34（VS 2022 17.4）以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 同じ位置どうしに関数を適用する
    - [x] zip + transform を 1 つにしたもの
    - [x] C++23

## 関連ページ

- [cpprefjp: std::ranges::zip_transform_view](https://cpprefjp.github.io/reference/ranges/zip_transform_view.html)
- [cppreference: std::ranges::zip_transform_view](https://en.cppreference.com/w/cpp/ranges/zip_transform_view)
