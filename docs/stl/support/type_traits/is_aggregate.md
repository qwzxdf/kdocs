---
title: std::is_aggregate
summary: "集成体（波かっこでメンバを順に初期化できる型）かを調べる。"
order: 13
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_aggregate

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <type_traits>`
</div>

`std::is_aggregate_v<T>` は、**型 T が集成体（コンストラクターを持たず、`{a, b, c}` でメンバを順に初期化できる型）か**を調べます。単純なデータ構造体かの判定に使えます。

!!! tip "ポイント"
    - 配列と、ユーザー定義コンストラクターのない構造体が該当。
    - 指示付き初期化（`.x = 1`）が使える型。

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。[テンプレート](../../../basics/template.md) の基本が前提です。

## 関数の詳しい説明

### std::is_aggregate_v {#is_aggregate}

- `{1, 2}` のようにメンバを並べて作れる構造体（集成体）か

```cpp
#include <memory>
#include <print>
#include <string>
#include <type_traits>

struct Point {
  int x;
  int y;
};

int main() {
  std::println("{} {} {} {} {}", std::is_arithmetic_v<float>, std::is_const_v<const int>,
               std::is_copy_constructible_v<std::unique_ptr<int>>,
               std::is_nothrow_move_constructible_v<std::string>, std::is_aggregate_v<Point>);
  std::println("{}", std::is_default_constructible_v<Point>);
}
```

```text title="実行結果"
true true false true true
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 単純なデータ構造体だけを扱うシリアライザ | `static_assert(std::is_aggregate_v<T>)` |

## よくあるミス

??? failure "継承や private メンバがあると false"
    条件を満たしません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_trivially_copyable`](is_trivially_copyable.md) | memcpy できるか |

## コンパイラ対応

C++11 から使えます。`_v` と `_t` の簡略形は C++14 / C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 集成体かを調べる
    - [x] `{...}` で初期化できる型
    - [x] C++17

## 関連ページ

- [cpprefjp: std::is_aggregate](https://cpprefjp.github.io/reference/type_traits/is_aggregate.html)
- [cppreference: std::is_aggregate](https://en.cppreference.com/w/cpp/types/is_aggregate)
