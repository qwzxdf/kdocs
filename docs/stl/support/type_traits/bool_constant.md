---
title: std::bool_constant
summary: "`bool` のコンパイル時の定数を、型として表す。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::bool_constant

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

`integral_constant<bool, B>` の別名です。型特性の戻りの型として、`true_type` / `false_type` と共に使います。

!!! tip "ポイント"
    - `::value` で値が取れる。
    - 型特性が継承する土台。
    - `constexpr` 変数としても使える。

!!! info "このページを読む前に"
    [<type_traits>](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::bool_constant {#bool_constant}

```cpp
using bool_constant = integral_constant<bool, true>;
```

- 戻り値: `value`（定数）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("{}", std::bool_constant<true>::value);
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
    - [x] `bool` のコンパイル時の定数を、型として表す
    - [x] `::value` で値が取れる
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::bool_constant](https://cpprefjp.github.io/reference/type_traits/bool_constant.html)
- [cppreference: std::bool_constant](https://en.cppreference.com/w/cpp/types/integral_constant)
