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

`std::ranges::ref_view<R>` は、コンテナ `R` への参照だけを持つ、軽いビューです。ビューはコピーが軽いことが前提ですが、`std::vector` をそのままコピーすると重いので、ビューのパイプラインの中では、参照だけを持つ `ref_view` に包まれます。

!!! tip "ポイント"
    - コンテナへの参照だけを持つ。コピーは軽い
    - 元のコンテナより長く生かしてはいけない
    - `views::all(lvalue)` が返す
    - 元のコンテナの要素を、読み書きできる

!!! info "このページを読む前に"
    [ビュー](../views.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::ranges::ref_view {#ref_view}

<span class="ver ver-20">C++20</span>

```cpp
template <range R>
  requires std::is_object_v<R>
class ref_view : public view_interface<ref_view<R>> {
 public:
  constexpr ref_view(R& r);
  constexpr R& base() const;
  constexpr auto begin() const;
  constexpr auto end() const;
};
```

内部にポインターを 1 つ持ち、`begin()` と `end()` は、元のコンテナのものを返します。

右辺値からは作れません（一時オブジェクトを参照して、ぶら下がるため）。右辺値には `owning_view` を使います。

元のコンテナの要素を変更すると、`ref_view` から見える要素も変わります。ビューの上で要素を書き換える処理も、元のコンテナに反映されます。

## 実際に動かしてみる

```cpp
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3};
  std::ranges::ref_view<std::vector<int>> r(v);

  std::println("要素数: {}", r.size());
  std::println("同じコンテナ: {}", &r.base() == &v);

  // ビュー経由の変更は、元に反映される
  r[0] = 100;
  std::println("{}", v[0]);
}
```

```text title="実行結果"
要素数: 3
同じコンテナ: true
100
```

## ゲームでの使いどころ

普段は直接書かず、`v | views::filter(...)` の内部で使われます。

## よくあるミス

??? failure "一時オブジェクトに使う"
    右辺値は渡せません。`owning_view` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`all`](all.md) | これを作る窓口 |
| [`owning_view`](owning_view.md) | 所有する版 |
| [`subrange`](subrange.md) | イテレータの組 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::ranges::ref_view](https://cpprefjp.github.io/reference/ranges/ref_view.html)
- [cppreference: std::ranges::ref_view](https://en.cppreference.com/w/cpp/ranges/ref_view)
