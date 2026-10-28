---
title: std::common_reference
summary: "複数の型が共有できる、共通の参照型を求める。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::common_reference

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <type_traits>`
</div>

`a ? b : c` のように、2 つの型を 1 つの式で扱うとき、型の「共通の姿」が必要です。`common_type` は値の型を `common_reference` は参照も含めた型を決めます。`int&` と `const int&` からは `const int&` が得られます。

!!! tip "ポイント"
    - `common_reference_t<T...>` で型が取れる。
    - 共通の参照型がなければ、型を持たない（SFINAE で使える）。
    - `ranges` ライブラリが内部で使う。

!!! info "このページを読む前に"
    [<type_traits>](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::common_reference {#common_reference}

```cpp
template <class... T>
struct common_reference { using type = /* 共通の参照型 */; };
template <class... T>
using common_reference_t = typename common_reference<T...>::type;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T...` | 型 | 共通の参照型を求めたい型 |

- 戻り値: 共通の参照型（`::type`）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  using R = std::common_reference_t<int&, const int&>;
  std::println("{}", std::is_same_v<R, const int&>);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | ジェネリックなライブラリで、型の共通の姿を決める |

## よくあるミス

??? failure "`common_type` と取り違える"
    `common_type` は値（コピー）の型です。参照が保たれません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`common_type`](common_type.md) | 値の型 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 複数の型が共有できる、共通の参照型を求める
    - [x] `common_reference_t<T...>` で型が取れる
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::common_reference](https://cpprefjp.github.io/reference/type_traits/common_reference.html)
- [cppreference: std::common_reference](https://en.cppreference.com/w/cpp/types/common_reference)
