---
title: std::ranges::enable_borrowed_range
summary: "自分の型を borrowed_range として扱ってよいと宣言する変数テンプレート。"
order: 900
tags:
  - 型・言語サポート
---

# std::ranges::enable_borrowed_range

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

`string_view` や `span` は、元のデータを借りているだけなので、一時オブジェクトでも、イテレータは元のデータが生きている限り使えます。このことを標準に伝えるのが `enable_borrowed_range<T>` で、自作の view の型に対して `true` に特殊化します。

!!! tip "ポイント"
    - `string_view`・`span`・`subrange` などは最初から `true`。
    - 自作の view がイテレータを自分の中に持たないなら、`true` に特殊化する。
    - `true` にすると `ranges::find` の戻り値が `dangling` にならない。

!!! info "このページを読む前に"
    [`std::ranges::range`](range.md) を先に読んでください。

## 関数の詳しい説明

### std::ranges::enable_borrowed_range {#enable_borrowed_range}

```cpp
template <class R>
inline constexpr bool enable_borrowed_range = false;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `R` | 型 | 宣言する範囲の型 |

- 戻り値: 既定は `false`。特殊化で `true`
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <print>
#include <ranges>
#include <string>
#include <string_view>

int main() {
  std::println("{}", std::ranges::enable_borrowed_range<std::string_view>);
  std::println("{}", std::ranges::enable_borrowed_range<std::string>);
}
```

```text title="実行結果"
true
false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 自作の view を一時オブジェクトでも使えるようにする |

## よくあるミス

??? failure "元のデータを持つ型に `true` を指定する"
    データそのものを持つ型（`vector` など）に `true` を指定すると、壊れたイテレータが返ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`borrowed_range`](borrowed_range.md) | このコンセプトの元になる |
| [`dangling`](dangling.md) | 壊れたイテレータの代わり |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 自分の型を borrowed_range として扱ってよいと宣言する変数テンプレート
    - [x] `string_view`・`span`・`subrange` などは最初から `true`
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::ranges::enable_borrowed_range](https://cpprefjp.github.io/reference/ranges/enable_borrowed_range.html)
- [cppreference: std::ranges::enable_borrowed_range](https://en.cppreference.com/w/cpp/ranges/borrowed_range)
