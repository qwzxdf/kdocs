---
title: std::views::single
summary: "1 つの値だけを持つ範囲を作る。"
order: 17
group: ビュー（std::views）
tags:
  - アルゴリズム
---

# std::views::single

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

要素が 1 個だけのビューが欲しい。たとえば、複数の範囲をつなげる `join` や `concat` に、1 つの値を混ぜたいとき、値を範囲の形にする必要があります。`std::views::single(x)` は、`x` を 1 個だけ持つビューです。

!!! tip "ポイント"
    - 要素が 1 個のビューを作る
    - 値のコピー（またはムーブ）を、ビューが持つ
    - `size()` が 1
    - ほかの範囲と組み合わせる部品として使う

!!! info "このページを読む前に"
    [ビュー](../views.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::views::single {#single}

<span class="ver ver-20">C++20</span>

```cpp
inline constexpr /* 未規定 */ single = /* 未規定 */;
// views::single(x)
```

値を所有するビューです。大きな値でも、コピー（右辺値ならムーブ）して持ちます。要素を参照のまま扱うビューではありません。

`begin()` は値へのポインター、`end()` は `begin() + 1` です。要素は書き換えることもできます。

```cpp
auto both = std::views::join_with(...)   // 複数の範囲をつなぐときに、区切りや先頭に 1 要素を足す
```

`std::ranges::concat_view`（C++26）や、`join` の入力として、1 つの値を範囲にそろえるのに使います。

## 実際に動かしてみる

```cpp
#include <print>
#include <ranges>
#include <vector>

int main() {
  auto one = std::views::single(42);
  std::println("要素数: {}", one.size());
  std::println("値: {}", *one.begin());

  // 先頭に 1 つ足した範囲を作る（join で連結する）
  const std::vector<int> v = {1, 2, 3};
  std::vector<std::vector<int>> parts = {{0}, v};
  for (int x : parts | std::views::join) std::println("{}", x);
}
```

```text title="実行結果"
要素数: 1
値: 42
0
1
2
3
```

## ゲームでの使いどころ

範囲の組み立てで、「ここに 1 つの値を足す」という部品として使います。

## よくあるミス

??? failure "参照のまま持てると思う"
    値のコピーを持ちます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`empty`](empty.md) | 要素が 0 個のビュー |
| [`concat`](concat.md) | 範囲をつなげる（C++26） |
| [`iota`](iota.md) | 連続する値のビュー |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::ranges::single_view](https://cpprefjp.github.io/reference/ranges/single_view.html)
- [cppreference: std::ranges::single_view](https://en.cppreference.com/w/cpp/ranges/single_view)
