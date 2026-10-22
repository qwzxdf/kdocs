---
title: std::compare_weak_order_fallback
summary: "`<=>` が無い型も、`==` と `<` で `weak_ordering` として比べる。"
order: 900
group: 比較（<compare>）
tags:
  - 型・言語サポート
---

# std::compare_weak_order_fallback

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <compare>`
</div>

`<=>` を持たない古い型でも、`==` と `<` があれば順序づけたいことがあります。`compare_weak_order_fallback` は、`<=>` があればそれを使い、なければ `==` と `<` から `weak_ordering` を作ります。

!!! tip "ポイント"
    - `<compare>` の部品。
    - C++20 の三方比較（`<=>`）と組み合わせて使う。
    - ふつうは `=default` の `<=>` で足りる。

!!! info "このページを読む前に"
    [`<=>`（宇宙船演算子）](spaceship.md) を先に読んでください。

## 関数の詳しい説明

### std::compare_weak_order_fallback {#compare_weak_order_fallback}

```cpp
inline constexpr /* カスタマイズポイント */ compare_weak_order_fallback;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `a, b` | 型 | 比べる 2 つの値 |

- 戻り値: `std::weak_ordering`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <compare>
#include <print>

struct V {
  int x;
  bool operator==(const V&) const = default;
  bool operator<(const V& o) const { return x < o.x; }
};

int main() {
  std::println("{}", std::compare_weak_order_fallback(V{1}, V{2}) == std::weak_ordering::less);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 古い型を `<=>` ベースの仕組みに乗せる |

## よくあるミス

??? failure "`==` と `<` が整合しない型"
    `==` と `<` の結果が矛盾していると、結果は意味を持ちません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`weak_order`](weak_order.md) | `<=>` ありの版 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `<=>` が無い型も、`==` と `<` で `weak_ordering` として比べる
    - [x] `<compare>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::compare_weak_order_fallback](https://cpprefjp.github.io/reference/compare/compare_weak_order_fallback.html)
- [cppreference: std::compare_weak_order_fallback](https://en.cppreference.com/w/cpp/utility/compare_weak_order_fallback)
