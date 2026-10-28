---
title: std::ranges::ref_view
summary: "範囲を参照する、軽いビュー。"
order: 22
group: ビュー（std::views）
tags:
  - アルゴリズム
---

# std::ranges::ref_view

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

`std::ranges::ref_view` は、**ほかの範囲（コンテナなど）への参照を持つだけのビュー**です。コピーが軽く、元の範囲を書き換えることもできます。[`views::all`](all.md) が、コンテナの左辺値に対して返す型です。

!!! tip "ポイント"
    - 元の範囲が**先に消える**と、ビューは壊れる（参照しているだけ）。
    - ビューはコピーが軽い。値渡しで関数に渡せる。
    - `std::ref` 的な役割を範囲に対してしている。

!!! info "このページを読む前に"
    [ranges とビュー](../../../basics/ranges.md)、[ラムダ式](../../../basics/lambda.md) を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::ranges::ref_view {#ref_view}

```cpp
template <range R>
  requires is_object_v<R>
class std::ranges::ref_view;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `r` | 範囲の左辺値 | 参照する元の範囲 |

- 戻り値: `r` を参照するビュー
- 計算量: コピー・作成ともに O(1)

```cpp
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3};

  std::ranges::ref_view<std::vector<int>> view(v);
  view[0] = 99;  // 参照しているだけなので、元の v が変わる
  std::println("{}", v);
}
```

```text title="実行結果"
[99, 2, 3]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 範囲を関数に「軽く」渡す | `process(std::views::all(v))` |

## よくあるミス

??? failure "元の vector を先に破棄する"
    `ref_view` は参照しているだけなので、元が消えると未定義動作です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::owning_view`](owning_view.md) | 右辺値を引き取って所有する |
| [`std::span`](../../containers/span.md) | 連続したメモリへの窓。型を限定して使える |
| [`std::reference_wrapper`](../../support/functional/reference_wrapper.md) | 値を参照として持つ（範囲ではない） |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 範囲への参照だけを持つ
    - [x] 元が先に消えると壊れる
    - [x] 普段は `views::all` 経由で現れる

## 関連ページ

- [cpprefjp: std::ranges::ref_view](https://cpprefjp.github.io/reference/ranges/ref_view.html)
- [cppreference: std::ranges::ref_view](https://en.cppreference.com/w/cpp/ranges/ref_view)
