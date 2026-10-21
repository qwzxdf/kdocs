---
title: std::holds_alternative
summary: "variant が今、その型の値を持っているかを調べる。"
order: 56
tags:
  - ユーティリティ
---

# std::holds_alternative

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-17">C++17</span>
`#include <variant>`
</div>

`std::holds_alternative<T>(v)` は、**`variant` が今、型 `T` の値を持っているか**を `bool` で答える関数です。「中身が `int` か」を調べるだけで、値は取り出しません。

!!! tip "ポイント"
    - 値も取り出したいなら [`std::get_if`](get_if.md) のほうが 1 回で済む。
    - 型は 1 つだけ指定する。variant の型の並びにないと、コンパイルエラー。
    - `v.index()` で、番号でも調べられる。

!!! info "このページを読む前に"
    [`std::variant`](variant.md) を先に読んでください。

## 関数の詳しい説明

### std::holds_alternative {#holds_alternative}

```cpp
template <class T, class... Types>
constexpr bool holds_alternative(const std::variant<Types...>& v) noexcept;
```

- 今 `T` が入っていれば `true`

## 実際に動かしてみる

```cpp
#include <print>
#include <variant>

int main() {
  std::variant<int, float> v = 1;
  std::println("{} {}", std::holds_alternative<int>(v), std::holds_alternative<float>(v));
}
```

```text title="実行結果"
true false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 今の状態が「移動中」か | `std::holds_alternative<Moving>(state)` |

## よくあるミス

??? failure "同じ型が 2 つ入る variant"
    `variant<int, int>` のように同じ型が複数あると、型で指定できません。`index()` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::get_if`](get_if.md) | 調べつつ、値へのポインターを取る |
| [`std::visit`](visit.md) | 型ごとの処理 |

## コンパイラ対応

C++17 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 今その型を持っているかを調べる
    - [x] 値は取り出さない
    - [x] 値も欲しいなら `get_if`

## 関連ページ

- [cpprefjp: std::holds_alternative](https://cpprefjp.github.io/reference/variant/holds_alternative.html)
- [cppreference: std::holds_alternative](https://en.cppreference.com/w/cpp/utility/variant/holds_alternative)
