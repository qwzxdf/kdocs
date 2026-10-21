---
title: std::floating_point
summary: "小数型であることを要求するコンセプト。"
order: 3
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::floating_point

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <concepts>`
</div>

`std::floating_point<T>` は、**T が小数型（`float`、`double`、`long double`）であること**を要求するコンセプトです。数学関数のテンプレートで、整数を弾くのに使います。

!!! tip "ポイント"
    - `template <std::floating_point T>` と書く。
    - 整数も受け取りたいなら `std::integral` と組み合わせる。

!!! info "このページを読む前に"
    [テンプレートとコンセプト](../../../basics/template.md) の基本が前提です。

## 関数の詳しい説明

### std::floating_point {#floating_point}

```cpp
template <class T>
concept floating_point = /* 条件 */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | テンプレート引数 | 調べる型 |

- 戻り値: 条件を満たせば `true`（コンパイル時の定数）
- 計算量: コンパイル時

```cpp
#include <concepts>
#include <print>

template <std::floating_point T>
T Half(T v) {
  return v / 2;
}

int main() {
  std::println("{}", Half(7.0));
}
```

```text title="実行結果"
3.5
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 小数専用の数学関数 | `template <std::floating_point T> T Lerp(T a, T b, T t)` |

## よくあるミス

??? failure "整数を渡して意図しない切り捨て"
    このコンセプトで整数を弾けば、`Half(7)` がコンパイルエラーになります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`integral`](integral.md) | 整数型 |
| [`is_floating_point`](../type_traits/is_floating_point.md) | 変数テンプレート版 |

## コンパイラ対応

C++20 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 小数型を要求
    - [x] 整数を弾く
    - [x] 数学関数のテンプレートに

## 関連ページ

- [cpprefjp: std::floating_point](https://cpprefjp.github.io/reference/concepts/floating_point.html)
- [cppreference: std::floating_point](https://en.cppreference.com/w/cpp/concepts/floating_point)
