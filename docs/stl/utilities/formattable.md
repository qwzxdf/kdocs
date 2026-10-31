---
title: std::formattable
summary: "型が `std::format` で書式化できることを要求するコンセプト。"
order: 900
tags:
  - ユーティリティ
---

# std::formattable

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <format>`
</div>

`std::format` に自作の型を渡せるかは、`std::formatter<T>` が用意されているかで決まります。テンプレートの引数として、「`std::format` できる型だけ受け付ける」と制約したいとき、C++23 の `std::formattable<T, CharT>` コンセプトが使えます。

!!! tip "ポイント"
    - `std::formattable<T, char>` が真なら、`T` は `std::format` に渡せる
    - テンプレートの制約（`requires`）に使う
    - 組み込み型、文字列、`string_view`、ポインタなどは真
    - `std::formatter<T>` を特殊化していない型は偽

!!! info "このページを読む前に"
    [`std::formatter`](formatter.md) を先に読んでください。

## 関数の詳しい説明

### std::formattable {#formattable}

<span class="ver ver-23">C++23</span>

```cpp
template <class T, class CharT>
concept formattable = /* formatter<remove_cvref_t<T>, CharT> が使える */;
```

条件は、`std::formatter<std::remove_cvref_t<T>, CharT>` が、`parse` と `format` を備えていることです。`const` かどうか、参照かどうかは、無視されます。

`std::formattable<int, char>` は真です。自作の構造体 `struct S {};` は、`formatter<S>` を用意していないので、偽です。

自作の `formatter` が `formattable` を満たすには、`format` を `std::format_context&` 固定にせず、`template <class FormatContext>` にします。`formattable` は、実装が決める別の出力先の文脈でも `format` が呼べることを確かめるからです。固定にしていると、`std::format` では動くのに、`formattable` が偽になります。

テンプレートの制約に使うと、`format` に渡せない型を渡したときの、長いエラー メッセージの代わりに、短く分かりやすいエラーにできます。

```cpp
template <std::formattable<char> T>
void Show(const T& v) { std::println("{}", v); }
```

## 実際に動かしてみる

```cpp
#include <format>
#include <print>
#include <string>
#include <vector>

struct Plain {};

struct Point { int x, y; };
template <>
struct std::formatter<Point> {
  constexpr auto parse(std::format_parse_context& ctx) { return ctx.begin(); }
  // formattable を満たすには、format を FormatContext のテンプレートにする
  template <class FormatContext>
  auto format(const Point& p, FormatContext& ctx) const {
    return std::format_to(ctx.out(), "({}, {})", p.x, p.y);
  }
};

template <std::formattable<char> T>
void Show(const T& v) {
  std::println("{}", v);
}

int main() {
  std::println("int: {}", std::formattable<int, char>);
  std::println("string: {}", std::formattable<std::string, char>);
  std::println("vector<int>: {}", std::formattable<std::vector<int>, char>);
  std::println("Plain: {}", std::formattable<Plain, char>);
  std::println("Point: {}", std::formattable<Point, char>);

  Show(Point{1, 2});
  // Show(Plain{});   // 制約を満たさない: コンパイル エラー
}
```

```text title="実行結果"
int: true
string: true
vector<int>: true
Plain: false
Point: true
(1, 2)
```

## ゲームでの使いどころ

ログ関数のテンプレートの制約に使い、書式化できない型を渡したときの、エラーを分かりやすくします。

## よくあるミス

??? failure "formatter を用意せずに、制約が通ると思う"
    `formatter<T>` の特殊化がない型は、偽です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`formatter`](formatter.md) | 書式化の実装 |
| [`format_kind`](format_kind.md) | 範囲の書式化の種類 |
| [`format_string`](format_string.md) | 書式文字列の型 |

## コンパイラ対応

C++23 から使えます。

## 関連ページ

- [cpprefjp: std::formattable](https://cpprefjp.github.io/reference/format/formattable.html)
- [cppreference: std::formattable](https://en.cppreference.com/w/cpp/utility/format/formattable)
