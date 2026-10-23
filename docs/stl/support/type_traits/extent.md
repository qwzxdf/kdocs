---
title: std::extent
summary: "配列の指定した次元の要素数を返す。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::extent

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

`int[2][3]` の 0 番目の次元の要素数は 2、1 番目は 3 です。配列でない、または要素数が不明な次元では 0 です。

!!! tip "ポイント"
    - `::value`（または `_v` 版）が `bool` の定数。
    - コンパイル時に決まるので、`if constexpr` や `static_assert` に使える。
    - 型だけを見る（値は見ない）。

!!! info "このページを読む前に"
    [<type_traits>](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::extent {#extent}

```cpp
template <class T, unsigned N = 0>
struct extent;
template <class T, unsigned N = 0>
inline constexpr std::size_t extent_v = extent<T, N>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べる配列の型 |
| `N` | unsigned | 何番目の次元か（既定は 0） |

- 戻り値: 要素数（配列でない、または要素数が不明な次元は 0）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("{}", std::extent_v<int[2][3]>);
  std::println("{}", std::extent_v<int[2][3], 1>);
}
```

```text title="実行結果"
2
3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | テンプレートの中で、型の性質に応じて処理を切り替える |

## よくあるミス

??? failure "要素数が不明な配列で期待する"
    `int[]` のように要素数が不明なら 0 です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_same`](is_same.md) | 同じ型か |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 配列の指定した次元の要素数を返す
    - [x] `::value`（または `_v` 版）が `bool` の定数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::extent](https://cpprefjp.github.io/reference/type_traits/extent.html)
- [cppreference: std::extent](https://en.cppreference.com/w/cpp/types/extent)
