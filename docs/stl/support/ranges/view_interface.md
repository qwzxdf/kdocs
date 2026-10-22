---
title: std::ranges::view_interface
summary: "begin と end だけ書けば、empty() や front() などを足してくれる view の土台。"
order: 900
tags:
  - 型・言語サポート
---

# std::ranges::view_interface

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

自作の view を作るとき、`begin()` と `end()` のほかに `empty()`・`front()`・`size()`・`operator[]` を全部書くのは大変です。`view_interface<Derived>` を継承（CRTP）すると、`begin` / `end` から、使える関数を自動で足してくれます。

!!! tip "ポイント"
    - `class MyView : public std::ranges::view_interface<MyView>` と書く。
    - `empty`・`front`・`back`・`size`・`operator[]`・`data` などが、条件に応じて使える。
    - コピーが軽く、既定構築できる型にする。

!!! info "このページを読む前に"
    [`std::ranges::range`](range.md) を先に読んでください。

## 関数の詳しい説明

### std::ranges::view_interface {#view_interface}

```cpp
template <class Derived>
requires is_class_v<Derived> && same_as<Derived, remove_cv_t<Derived>>
class view_interface : public view_base;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `Derived` | 型 | 継承するクラス自身 |

- 戻り値: `empty()` などの関数が `Derived` に足される
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <print>
#include <ranges>

int main() {
  struct IntView : std::ranges::view_interface<IntView> {
    const int* b = nullptr;
    const int* e = nullptr;
    IntView() = default;
    IntView(const int* b, const int* e) : b(b), e(e) {}
    const int* begin() const { return b; }
    const int* end() const { return e; }
  };

  int a[] = {3, 4, 5};
  IntView v(a, a + 3);
  std::println("{} {}", v.front(), v.size());
}
```

```text title="実行結果"
3 3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 自作の view を最小限のコードで作る |

## よくあるミス

??? failure "既定構築できない型にする"
    view は既定構築できる必要があります。`= default` のコンストラクタを書きます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`enable_view`](enable_view.md) | view と宣言する |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] begin と end だけ書けば、empty() や front() などを足してくれる view の土台
    - [x] `class MyView : public std::ranges::view_interface<MyView>` と書く
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::ranges::view_interface](https://cpprefjp.github.io/reference/ranges/view_interface.html)
- [cppreference: std::ranges::view_interface](https://en.cppreference.com/w/cpp/ranges/view_interface)
