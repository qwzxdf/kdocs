---
title: std::integral_constant
summary: "コンパイル時の定数を、型として表す。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::integral_constant

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

型特性は、結果を `::value` に持つ型です。その土台になっているのが `integral_constant<T, v>` で、値 `v` を型の中に持ちます。自分でも、整数の定数を型として渡したいときに使えます。

!!! tip "ポイント"
    - `::value` で値が取れる。
    - 型特性が継承する土台。
    - `constexpr` 変数としても使える。

!!! info "このページを読む前に"
    [<type_traits>](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::integral_constant {#integral_constant}

```cpp
template <class T, T v>
struct integral_constant {
  static constexpr T value = v;
  using value_type = T;
  using type = integral_constant;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T, v` | 型, 値 | 定数の型と値 |

- 戻り値: `value`（定数）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("{}", std::integral_constant<int, 5>::value);
}
```

```text title="実行結果"
5
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
    - [x] コンパイル時の定数を、型として表す
    - [x] `::value` で値が取れる
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::integral_constant](https://cpprefjp.github.io/reference/type_traits/integral_constant.html)
- [cppreference: std::integral_constant](https://en.cppreference.com/w/cpp/types/integral_constant)
