---
title: std::tuple_cat
summary: "複数の tuple を連結して、1 つの tuple にする。"
order: 56
tags:
  - ユーティリティ
---

# std::tuple_cat

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <tuple>`
</div>

`std::tuple_cat` は、**複数の tuple を連結して、1 つの大きな tuple にする**関数です。`{1, 2}` と `{3}` から `{1, 2, 3}` を作ります。

!!! tip "ポイント"
    - pair も連結できる。
    - 要素の型はそのまま並ぶ。
    - 主にテンプレートのコードで使う。

## 関数の詳しい説明

### std::tuple_cat {#tuple_cat}

```cpp
template <class... Tuples>
constexpr std::tuple<CTypes...> tuple_cat(Tuples&&... args);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `args...` | 可変個 | 連結する tuple（pair も可） |

- 戻り値: 連結した tuple
- 計算量: O(n)

```cpp
#include <print>
#include <tuple>

int main() {
  auto a = std::make_tuple(1, 'a');
  auto b = std::make_tuple(2.5);

  auto all = std::tuple_cat(a, b);  // tuple<int, char, double>
  std::println("{}", all);
}
```

```text title="実行結果"
(1, 'a', 2.5)
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| テンプレートで、引数の並びを結合する | `std::tuple_cat(a, b)` |

## よくあるミス

??? failure "実行時に長さが変わると思う"
    tuple の長さはコンパイル時に決まります。実行時に伸ばすなら `std::vector` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::tuple`](tuple.md) | 本体 |
| [`std::views::join`](../algorithms/views/join.md) | 範囲を連結する |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] tuple を連結する
    - [x] 長さはコンパイル時に決まる
    - [x] pair も連結できる

## 関連ページ

- [cpprefjp: std::tuple_cat](https://cpprefjp.github.io/reference/tuple/tuple_cat.html)
- [cppreference: std::tuple_cat](https://en.cppreference.com/w/cpp/utility/tuple/tuple_cat)
