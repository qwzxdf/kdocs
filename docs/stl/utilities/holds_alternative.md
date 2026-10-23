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

`variant` が、いま `int` を持っているのか `float` を持っているのかを知りたい。値を取り出す前に、型を確かめたい場面があります。`std::holds_alternative<T>(v)` は、`variant` が型 `T` の値を持っているかを `bool` で答える関数です。値は取り出さず、型の確認だけをします。

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

ステートや設定値の型を、分岐の条件にするときに使います。`if (std::holds_alternative<Moving>(state)) { ... }` と書けば、移動中かどうかが分かります。

値も取り出したいなら、`get_if` のほうが一度で済みます。`holds_alternative` で確かめたあとに `get` を呼ぶと、型の確認が 2 回になります。

`v.index()` で、番号で調べる方法もあります。ただし、型の並びを変えると番号がずれるので、型で調べるほうが安全です。

## よくあるミス

??? failure "同じ型が 2 つ入る variant"
    `variant<int, int>` のように同じ型が複数あると、型で指定できません。`index()` を使います。

??? failure "同じ型が複数あるときに使う"
    `variant<int, int>` のように同じ型が 2 つあると、`holds_alternative<int>` は曖昧でコンパイルエラーです。番号で調べます。

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
