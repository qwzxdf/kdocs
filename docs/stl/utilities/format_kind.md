---
title: std::format_kind
summary: "範囲の書式化の種類（sequence・map・set など）を表す変数。"
order: 900
tags:
  - ユーティリティ
---

# std::format_kind

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <format>`
</div>

C++23 から、`std::vector<int>` のような範囲（レンジ）も、`std::println("{}", v)` で `[1, 2, 3]` のように表示できます。この書式化が、範囲の種類（普通の並び、`map`、`set`、文字列）によって、括弧の形などを変えます。種類を決める変数が `std::format_kind<R>` で、`std::range_format` の値を取ります。

!!! tip "ポイント"
    - `format_kind<R>` は、範囲 `R` の書式化の種類（`range_format` の値）
    - `vector` は `sequence`、`map` は `map`、`set` は `set`
    - `disabled` なら、その範囲は書式化の対象外
    - 自作の範囲の種類は、`format_kind` を特殊化して指定する

!!! info "このページを読む前に"
    [`std::range_format`](range_format.md) を先に読んでください。

## 関数の詳しい説明

### std::format_kind {#format_kind}

<span class="ver ver-23">C++23</span>

```cpp
template <class R>
constexpr std::range_format format_kind = /* 既定の判定 */;
```

既定の判定は、次のとおりです。

| 条件 | 値 |
| --- | --- |
| 要素が `pair` / `tuple`（2 要素）の、キーと値の範囲（`map`） | `map` |
| 要素が単独で、集合（`set`）のように振る舞う | `set` |
| 上記以外の範囲 | `sequence` |

範囲ではない型（`int` など）では使えません。

`std::string` や `std::string_view` は、範囲でもありますが、専用の `formatter` を持っているので、そちらが使われます。

`map` の表示は `{1: 2, 3: 4}`、`set` は `{1, 2, 3}`、`sequence` は `[1, 2, 3]` です。

自作のコンテナを、`sequence` や `set` として表示させたいなら、`std::format_kind<MyContainer>` を特殊化して、`range_format` の値を指定します。

## 実際に動かしてみる

```cpp
#include <format>
#include <map>
#include <print>
#include <set>
#include <vector>

int main() {
  std::println("vector は sequence: {}", std::format_kind<std::vector<int>> == std::range_format::sequence);
  std::println("map は map: {}", std::format_kind<std::map<int, int>> == std::range_format::map);
  std::println("set は set: {}", std::format_kind<std::set<int>> == std::range_format::set);

  // 実際の表示
  const std::vector<int> v = {1, 2, 3};
  const std::map<int, int> m = {{1, 10}, {2, 20}};
  const std::set<int> s = {3, 1, 2};
  std::println("{}", v);
  std::println("{}", m);
  std::println("{}", s);
}
```

```text title="実行結果"
vector は sequence: true
map は map: true
set は set: true
[1, 2, 3]
{1: 10, 2: 20}
{1, 2, 3}
```

## ゲームでの使いどころ

デバッグ表示で、コンテナをそのまま `println` に渡せます。自作のコンテナを表示したいときだけ、`format_kind` を特殊化します。

## よくあるミス

??? failure "自作のコンテナが表示できない"
    `format_kind` が `disabled` になっている場合があります。特殊化して、`sequence` を指定します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`range_format`](range_format.md) | 値の種類を表す列挙型 |
| [`range_formatter`](range_formatter.md) | 範囲の書式化の部品 |
| [`formattable`](formattable.md) | 書式化できるかのコンセプト |

## コンパイラ対応

C++23 から使えます。

## 関連ページ

- [cpprefjp: std::format_kind](https://cpprefjp.github.io/reference/format/format_kind.html)
- [cppreference: std::format_kind](https://en.cppreference.com/w/cpp/utility/format/format_kind)
