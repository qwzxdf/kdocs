---
title: std::variant_alternative
summary: "variant の N 番目の選択肢の型を取り出す。"
order: 900
tags:
  - ユーティリティ
---

# std::variant_alternative

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <variant>`
</div>

`std::variant<int, float, std::string>` の 2 番目の型は何か。テンプレートの中で、`variant` の型を番号から取り出したいとき、`std::variant_alternative_t<I, V>` を使います。`tuple_element` の `variant` 版です。

!!! tip "ポイント"
    - `std::variant_alternative_t<I, V>` は、`V` の `I` 番目の型
    - 番号は 0 始まり
    - 範囲外の番号はコンパイル エラー
    - 型から番号を調べるには、別の方法（`std::visit` や自作のテンプレート）が要る

!!! info "このページを読む前に"
    [`std::variant_size`](variant_size.md) を先に読んでください。

## 関数の詳しい説明

### std::variant_alternative {#variant_alternative}

<span class="ver ver-17">C++17</span>

```cpp
template <std::size_t I, class Variant> struct variant_alternative;
template <std::size_t I, class Variant>
using variant_alternative_t = typename variant_alternative<I, Variant>::type;
```

| 引数 | 意味 |
| --- | --- |
| `I` | 取り出したい型の番号（0 始まり） |
| `Variant` | `std::variant` の型 |

`Variant` が `const` や `volatile` の付いた型なら、結果にも同じ修飾が付きます。`I` が `variant_size_v<Variant>` 以上だと、`static_assert` に失敗して、コンパイルできません。

実行時の番号（`v.index()`）から型を取り出すことは、できません。`variant_alternative_t` は、コンパイル時の番号で使います。実行時の分岐には、`std::visit` を使います。

## 実際に動かしてみる

```cpp
#include <print>
#include <string>
#include <variant>

int main() {
  using V = std::variant<int, float, std::string>;

  static_assert(std::is_same_v<std::variant_alternative_t<0, V>, int>);
  static_assert(std::is_same_v<std::variant_alternative_t<1, V>, float>);
  static_assert(std::is_same_v<std::variant_alternative_t<2, V>, std::string>);

  // 2 番目の型で変数を作る
  std::variant_alternative_t<2, V> s = "Hero";
  std::println("{} {}", s, std::variant_size_v<V>);
}
```

```text title="実行結果"
Hero 3
```

## ゲームでの使いどころ

メッセージ型を `variant` にまとめたとき、各メッセージ型の処理をテンプレートで自動生成する、といった場面で使います。

## よくあるミス

??? failure "実行時の番号で使おうとする"
    コンパイル時の定数が必要です。`v.index()` は渡せません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::variant_size`](variant_size.md) | 型の個数 |
| `std::tuple_element` | `tuple` の同じ働き |
| [`std::holds_alternative`](holds_alternative.md) | 型が入っているか調べる |

## コンパイラ対応

C++17 から使えます。

## 関連ページ

- [cpprefjp: std::variant_alternative](https://cpprefjp.github.io/reference/variant/variant_alternative.html)
- [cppreference: std::variant_alternative](https://en.cppreference.com/w/cpp/utility/variant/variant_alternative)
