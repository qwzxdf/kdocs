---
title: std::true_type
summary: "`true` を表すコンパイル時の定数の型。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::true_type

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

`bool_constant<true>` の別名です。型特性を自分で書くとき、真のときに継承します（`struct IsFoo : std::true_type {}`）。

!!! tip "ポイント"
    - `::value` で値が取れる。
    - 型特性が継承する土台。
    - `constexpr` 変数としても使える。

!!! info "このページを読む前に"
    [<type_traits>](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::true_type {#true_type}

```cpp
using true_type = integral_constant<bool, true>;
```

- 戻り値: `value`（定数）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("{}", std::true_type::value);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 自作の型特性の土台にする |

## よくあるミス

??? failure "実行時の値を渡す"
    テンプレート引数は、コンパイル時の定数です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_same`](is_same.md) | 型が同じか |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `true` を表すコンパイル時の定数の型
    - [x] `::value` で値が取れる
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::true_type](https://cpprefjp.github.io/reference/type_traits/true_type.html)
- [cppreference: std::true_type](https://en.cppreference.com/w/cpp/types/integral_constant)
