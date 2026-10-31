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

`std::variant` の中に、いま特定の型が入っているかを調べたい。`std::holds_alternative<T>(v)` は、`v` がいま型 `T` を保持していれば `true` を返します。`v.index() == 番号` と書く代わりに、型で書けるので、選択肢の並びを変えても影響されません。

!!! tip "ポイント"
    - `std::holds_alternative<T>(v)` は、`v` がいま `T` を持っているか
    - `T` は `variant` の選択肢のうち、ちょうど 1 回だけ現れる型
    - 値を取り出すなら `std::get_if<T>(&v)`（持っていれば、ポインタ）
    - valueless のときは `false`

!!! info "このページを読む前に"
    [`std::variant`](variant.md) と [`std::get_if`](get_if.md) を先に読んでください。

## 関数の詳しい説明

### std::holds_alternative {#holds_alternative}

<span class="ver ver-17">C++17</span>

```cpp
template <class T, class... Types>
constexpr bool holds_alternative(const std::variant<Types...>& v) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | テンプレート引数 | 調べる型 |
| `v` | `std::variant<Types...>` | 調べる対象 |

`T` が `Types...` のなかにちょうど 1 回だけ現れなければ、コンパイル エラーです。同じ型が複数あるときは、番号で調べる（`v.index() == I`）か、`std::get_if<I>` を使います。

`v` が valueless by exception のときは、`false` を返します。

型で調べたあとに、その値を使いたいなら、`std::get<T>(v)` か、1 回の呼び出しで済む `std::get_if<T>(&v)` を使うほうが、調べて取り出す 2 段が、1 つにまとまります。

```cpp
if (auto* p = std::get_if<int>(&v)) {
  // *p を使う
}
```

## 実際に動かしてみる

```cpp
#include <print>
#include <string>
#include <variant>

int main() {
  std::variant<int, std::string> v = 5;
  std::println("int: {}", std::holds_alternative<int>(v));
  std::println("string: {}", std::holds_alternative<std::string>(v));

  v = std::string("Hero");
  std::println("int: {}", std::holds_alternative<int>(v));
  std::println("string: {}", std::holds_alternative<std::string>(v));

  // 調べて取り出すなら get_if が 1 回で済む
  if (const auto* s = std::get_if<std::string>(&v)) {
    std::println("文字列: {}", *s);
  }
}
```

```text title="実行結果"
int: true
string: false
int: false
string: true
文字列: Hero
```

## ゲームでの使いどころ

メッセージの種類を `variant` で表したとき、「これは移動のメッセージか」を調べるのに使います。種類が多いときは、`std::visit` のほうが整理しやすくなります。

## よくあるミス

??? failure "同じ型を 2 回持つ variant で使う"
    `variant<int, int>` に `holds_alternative<int>` は、コンパイルできません。番号で調べます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::get_if`](get_if.md) | 持っていればポインタを返す |
| [`std::get`](get.md) | 持っていなければ例外 |
| [`std::visit`](visit.md) | 型ごとに処理を分ける |

## コンパイラ対応

C++17 から使えます。

## 関連ページ

- [cpprefjp: std::holds_alternative](https://cpprefjp.github.io/reference/variant/holds_alternative.html)
- [cppreference: std::holds_alternative](https://en.cppreference.com/w/cpp/utility/variant/holds_alternative)
