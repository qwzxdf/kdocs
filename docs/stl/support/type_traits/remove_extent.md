---
title: std::remove_extent
summary: "配列の最初の次元を取り除く。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::remove_extent

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

`int[3]` から `int` を作ります。多次元配列では、一番外側の次元だけを外します。

!!! tip "ポイント"
    - `::type` の代わりに `std::remove_extent_t<T>` と書ける。
    - コンパイル時に型を作り換える。
    - 値ではなく型を扱う。

!!! info "このページを読む前に"
    [<type_traits>](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::remove_extent {#remove_extent}

```cpp
template <class T>
struct remove_extent { using type = /* 配列の最初の次元を取り除く */; };
template <class T>
using remove_extent_t = typename remove_extent<T>::type;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 元の型 |

- 戻り値: 変換後の型（`::type`）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  using R = std::remove_extent_t<int[3]>;
  std::println("{}", std::is_same_v<R, int>);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | テンプレートの中で、型から余計な修飾を取り除く・付け足す |

## よくあるミス

??? failure "`::type` を付け忘れる"
    `std::remove_extent<T>` は型を持つ構造体です。型そのものが欲しいときは `_t` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`remove_all_extents`](remove_all_extents.md) | 全部の次元を外す |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 配列の最初の次元を取り除く
    - [x] `::type` の代わりに `std::remove_extent_t<T>` と書ける
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::remove_extent](https://cpprefjp.github.io/reference/type_traits/remove_extent.html)
- [cppreference: std::remove_extent](https://en.cppreference.com/w/cpp/types/remove_extent)
