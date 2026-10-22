---
title: std::is_bind_expression
summary: "型が bind の式かどうかを調べる型特性。"
order: 900
group: 関数オブジェクトと呼び出し（<functional>）
tags:
  - 型・言語サポート
---

# std::is_bind_expression

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <functional>`
</div>

`std::bind` に別の `bind` の結果を渡すと、中の `bind` が先に評価されてその結果が使われます（入れ子の bind）。この「bind の式かどうか」を判定する型特性が `is_bind_expression` です。

!!! tip "ポイント"
    - `std::bind` の戻り値の型に対して `true`。
    - 自作のラッパーを bind 式として扱わせたいときに特殊化する。

!!! info "このページを読む前に"
    [<functional>](../functional.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_bind_expression {#is_bind_expression}

```cpp
template <class T> struct is_bind_expression;
template <class T> inline constexpr bool is_bind_expression_v = is_bind_expression<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べる型 |

- 戻り値: `bind` が返した型なら `true`
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <functional>
#include <print>

int Add(int a, int b) { return a + b; }

int main() {
  auto b = std::bind(Add, std::placeholders::_1, 1);
  std::println("{}", std::is_bind_expression_v<decltype(b)>);
  std::println("{}", std::is_bind_expression_v<int>);
}
```

```text title="実行結果"
true
false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| テンプレートで bind の戻り値かを判定 | `std::is_bind_expression_v<decltype(std::bind(f, _1))>` |

## よくあるミス

??? failure "`std::function` と取り違える"
    `std::function` は bind 式ではありません。`false` になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_placeholder`](is_placeholder.md) | プレースホルダーかを調べる |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] bind 式かどうかの型特性
    - [x] `_v` 版で bool
    - [x] 普通は使わない

## 関連ページ

- [cpprefjp: std::is_bind_expression](https://cpprefjp.github.io/reference/functional/is_bind_expression.html)
- [cppreference: std::is_bind_expression](https://en.cppreference.com/w/cpp/utility/functional/is_bind_expression)
