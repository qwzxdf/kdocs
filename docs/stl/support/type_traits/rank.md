---
title: std::rank
summary: "配列の次元の数を返す。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::rank

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

`int[2][3]` のような配列が、何次元かを調べます。配列でない型は 0 です。

!!! tip "ポイント"
    - `::value`（または `_v` 版）が `bool` の定数。
    - コンパイル時に決まるので、`if constexpr` や `static_assert` に使える。
    - 型だけを見る（値は見ない）。

!!! info "このページを読む前に"
    [<type_traits>](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::rank {#rank}

```cpp
template <class T>
struct rank;
template <class T>
inline constexpr std::size_t rank_v = rank<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べる型 |

- 戻り値: 次元の数（配列でなければ 0）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("{}", std::rank_v<int[2][3]>);
  std::println("{}", std::rank_v<int>);
}
```

```text title="実行結果"
2
0
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | テンプレートの中で、型の性質に応じて処理を切り替える |

## よくあるミス

??? failure "要素数と取り違える"
    `rank` は次元の数です。要素数は `extent` で調べます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_same`](is_same.md) | 同じ型か |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 配列の次元の数を返す
    - [x] `::value`（または `_v` 版）が `bool` の定数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::rank](https://cpprefjp.github.io/reference/type_traits/rank.html)
- [cppreference: std::rank](https://en.cppreference.com/w/cpp/types/rank)
