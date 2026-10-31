---
title: std::ranges::owning_view
summary: "右辺値の範囲を引き取って、所有するビュー。"
order: 23
group: ビュー（std::views）
tags:
  - アルゴリズム
---

# std::ranges::owning_view

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

`std::ranges::owning_view<R>` は、コンテナ `R` を<strong>所有</strong>するビューです。一時オブジェクトのコンテナを、ビューのパイプラインに流したいとき、参照だけを持つ `ref_view` ではぶら下がってしまいます。`owning_view` は、コンテナをムーブで受け取って、中に持ちます。

!!! tip "ポイント"
    - コンテナをムーブで受け取って所有する
    - ムーブはできるが、コピーはできない（コンテナのコピーが重いため）
    - `views::all(rvalue)` が返す
    - 一時オブジェクトのパイプラインを、安全にする

!!! info "このページを読む前に"
    [ビュー](../views.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::ranges::owning_view {#owning_view}

<span class="ver ver-20">C++20</span>

```cpp
template <range R>
  requires std::movable<R> && (!is_initializer_list<R>)
class owning_view : public view_interface<owning_view<R>> {
 public:
  constexpr owning_view(R&& r);
  constexpr R& base() & noexcept;
  constexpr R&& base() && noexcept;
};
```

コピーできないので、ビューの要件（コピーが軽い）を満たさないはずですが、C++20 の欠陥報告で、ビューは「ムーブが軽ければよい」に緩められました。

```cpp
auto evens = std::vector{1, 2, 3, 4} | std::views::filter([](int x) { return x % 2 == 0; });
```

右辺値の `vector` が `owning_view` に包まれるので、この式の結果は安全に使えます。以前は、コンパイル エラーになっていました。

`base()` で、所有しているコンテナにアクセスできます。右辺値の `base()` で、中身を取り出せます。

## 実際に動かしてみる

```cpp
#include <print>
#include <ranges>
#include <type_traits>
#include <vector>

int main() {
  std::ranges::owning_view ov(std::vector<int>{1, 2, 3, 4});
  std::println("要素数: {}", ov.size());

  // コピーはできず、ムーブはできる
  static_assert(!std::is_copy_constructible_v<decltype(ov)>);
  static_assert(std::is_move_constructible_v<decltype(ov)>);

  // 一時オブジェクトをパイプラインに流せる
  auto evens = std::vector{1, 2, 3, 4} | std::views::filter([](int x) { return x % 2 == 0; });
  for (int x : evens) std::println("{}", x);
}
```

```text title="実行結果"
要素数: 4
2
4
```

## ゲームでの使いどころ

関数が返したコンテナを、そのまま `views` のパイプラインに流すときに、裏で使われます。

## よくあるミス

??? failure "コピーしようとする"
    コピーできません。ムーブします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`all`](all.md) | これを作る窓口 |
| [`ref_view`](ref_view.md) | 参照だけを持つ版 |
| [`subrange`](subrange.md) | イテレータの組 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::ranges::owning_view](https://cpprefjp.github.io/reference/ranges/owning_view.html)
- [cppreference: std::ranges::owning_view](https://en.cppreference.com/w/cpp/ranges/owning_view)
