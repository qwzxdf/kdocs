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

`vector` と `map` と `set` では、書式化の結果が違います（`[1, 2]`・`{1: 2}`・`{1, 2}`）。その分類を表すのが `format_kind<R>` で、`range_format` の値になります。

!!! tip "ポイント"
    - `<format>` の部品。
    - ふつうは `std::format` / `std::println` を使えば足りる。
    - 自作の型に対応させるときに登場する。

!!! info "このページを読む前に"
    [`std::format`](format.md) を先に読んでください。

## 関数の詳しい説明

### std::format_kind {#format_kind}

```cpp
template <class R>
inline constexpr range_format format_kind = /* 実装定義 */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `R` | 型 | 調べる範囲の型 |

- 戻り値: `range_format` の値
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <format>
#include <map>
#include <print>
#include <vector>

int main() {
  std::println("{}", std::format_kind<std::vector<int>> == std::range_format::sequence);
  std::println("{}", std::format_kind<std::map<int, int>> == std::range_format::map);
}
```

```text title="実行結果"
true
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 自作のコンテナの書式化の種類を決める |

## よくあるミス

??? failure "特殊化せずに `set` のように出したい"
    自作のコンテナを `set` 風に出すには、`format_kind` を特殊化します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`range_format`](range_format.md) | 種類の列挙型 |

## コンパイラ対応

C++23 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 範囲の書式化の種類（sequence・map・set など）を表す変数
    - [x] `<format>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::format_kind](https://cpprefjp.github.io/reference/format/format_kind.html)
- [cppreference: std::format_kind](https://en.cppreference.com/w/cpp/utility/format/format_kind)
