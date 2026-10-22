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

`std::vector<int> v(first, last)` は、イテレータを 2 つ渡す必要があります。範囲（`views::iota(1, 4)` のような）をそのまま渡したいときは、先頭に `std::from_range` を置いて `v(std::from_range, range)` と書きます。

!!! tip "ポイント"
    - コンテナのコンストラクタ、`assign_range`・`insert_range`・`append_range` などで使う。
    - 範囲を直接渡せるので、イテレータのペアを作らなくてよい。
    - C++23 で追加された。

!!! info "このページを読む前に"
    [`std::ranges::range`](range.md) を先に読んでください。

## 関数の詳しい説明

### std::from_range {#from_range}

```cpp
struct from_range_t { explicit from_range_t() = default; };
inline constexpr from_range_t from_range{};
```

- 戻り値: なし（目印）
- 計算量: コンストラクタに依存


## 実際に動かしてみる

```cpp
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::vector<int> v(std::from_range, std::views::iota(1, 4));
  std::println("{}", v);
}
```

```text title="実行結果"
[1, 2, 3]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | view の結果をそのままコンテナにする |

## よくあるミス

??? failure "目印を忘れる"
    `vector(range)` のように範囲だけを渡すとコンパイルエラーです。`std::from_range` が必要です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`ranges::to`](../../algorithms/ranges_to.md) | 範囲をコンテナに変換する |

## コンパイラ対応

C++23 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] コンテナのコンストラクタに「範囲から作る」と伝える目印
    - [x] コンテナのコンストラクタ、`assign_range`・`insert_range`・`append_range` などで使う
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::from_range](https://cpprefjp.github.io/reference/ranges/from_range.html)
- [cppreference: std::from_range](https://en.cppreference.com/w/cpp/ranges/from_range_t)
