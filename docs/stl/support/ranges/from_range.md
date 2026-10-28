---
title: std::from_range
summary: "コンテナのコンストラクタに「範囲から作る」と伝える目印。"
order: 900
tags:
  - 型・言語サポート
---

# std::from_range

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <ranges>`
</div>

コンテナのコンストラクターに範囲を渡すとき、イテレーターを 2 つ書くのは面倒です。C++23 では、`std::from_range` という印を先頭に付けて、範囲をそのまま渡せます。`std::vector<int> v(std::from_range, range);` です。

!!! tip "ポイント"
    - `std::from_range` は、範囲から構築することを示すタグ
    - `vector`、`list`、`set` などのコンストラクターに渡せる
    - イテレーターを 2 つ書かずに済む
    - C++23 で追加

!!! info "このページを読む前に"
    [範囲（ranges）の基礎](../../../basics/ranges.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::from_range {#from_range}

<span class="ver ver-23">C++23</span>

```cpp
inline constexpr std::from_range_t from_range{};
```

`std::from_range` は、値を持たないタグです。コンストラクターのオーバーロード選択に使われます。`std::vector<T>(std::from_range, r)` は、範囲 `r` の要素を全部コピーして構築します。

`std::ranges::to`（範囲からコンテナへの変換）と合わせて、範囲とコンテナの行き来が、短く書けるようになりました。

## 実際に動かしてみる

```cpp
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::vector<int> v(std::from_range, std::views::iota(1, 4));   // 1, 2, 3
  for (int x : v) std::print("{} ", x);
  std::println("");
}
```

```text title="実行結果"
1 2 3 
```

## ゲームでの使いどころ

ビューの結果を、コンテナに詰めます。

```cpp
std::vector<int> evens(std::from_range, nums | std::views::filter(IsEven));
```

## よくあるミス

??? failure "C++20 のコンパイラで使えない"
    C++23 の機能です。`std::ranges::to` も C++23 です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`ranges_to`](../../algorithms/ranges_to.md) | 範囲をコンテナに変換 |
| [`range`](range.md) | 基本の範囲 |

## コンパイラ対応

C++23 から使えます。GCC 14 以降、Clang 18 以降、Visual Studio 2022 17.x 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::from_range` は範囲からの構築を示すタグ
    - [x] コンストラクターの先頭に付ける
    - [x] C++23

## 関連ページ

- [cpprefjp: std::from_range](https://cpprefjp.github.io/reference/ranges/from_range.html)
- [cppreference: std::from_range](https://en.cppreference.com/w/cpp/ranges/from_range_t)
