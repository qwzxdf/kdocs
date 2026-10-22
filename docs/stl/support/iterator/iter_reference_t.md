---
title: std::iter_reference_t
summary: "イテレータの `*it` の型（参照）を取り出す型の別名。"
order: 900
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::iter_reference_t

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

テンプレートの中で、イテレータ型 `It` が指す値の型を知りたいとき、`iterator_traits<It>::value_type` と書くと長くなります。`iter_reference_t<It>` は、C++20 のコンセプトと相性のよい書き方です。

!!! tip "ポイント"
    - `<iterator>` の部品。
    - ふつうは補助関数（`back_inserter` など）経由で使う。
    - アルゴリズムの出力先や入力元に渡す。

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::iter_reference_t {#iter_reference_t}

```cpp
template <class It>
using iter_reference_t = /* イテレータの `*it` の型（参照） */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `It` | 型 | イテレータの型 |

- 戻り値: イテレータの `*it` の型（参照）
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cstddef>
#include <iterator>
#include <print>
#include <type_traits>
#include <vector>

int main() {
  using It = std::vector<int>::iterator;
  std::println("{}", std::is_same_v<std::iter_reference_t<It>, int&>);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | ジェネリックなアルゴリズムで、値の型を取り出す |

## よくあるミス

??? failure "`iterator_traits` と混ぜる"
    C++20 のコードでは、`iter_value_t` などに統一したほうが読みやすいです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`iterator_traits`](iterator_traits.md) | 従来の取り出し方 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] イテレータの `*it` の型（参照）を取り出す型の別名
    - [x] `<iterator>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::iter_reference_t](https://cpprefjp.github.io/reference/iterator/iter_reference_t.html)
- [cppreference: std::iter_reference_t](https://en.cppreference.com/w/cpp/iterator/iter_reference_t)
