---
title: std::compare_partial_order_fallback
summary: "`<=>` が無い型も、`==` と `<` で `partial_ordering` として比べる。"
order: 900
group: 比較（<compare>）
tags:
  - 型・言語サポート
---

# std::compare_partial_order_fallback

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <compare>`
</div>

浮動小数点数の NaN のように、「大きくも小さくも等しくもない」値があると、どんな 2 つの値にも順序がつくわけではありません。`std::compare_partial_order_fallback(a, b)` は、`<=>` や [`std::partial_order`](partial_order.md) が使えない古い型を、`==` と `<` から `std::partial_ordering` として比べます。順序のつかない組を、`unordered` として表せるのが特徴です。

!!! tip "ポイント"
    - `std::partial_order` が使えるならそれを使い、使えなければ `==` と `<` で代用する
    - 戻り値は `std::partial_ordering`（`less`・`equivalent`・`greater`・`unordered`）
    - 代用では、`a == b`、`a < b`、`b < a` が使われる
    - `unordered` は、NaN との比較などで返る

!!! info "このページを読む前に"
    [`std::partial_order`](partial_order.md) と [`<=>`（三方比較）](spaceship.md) を先に読んでください。

## 関数の詳しい説明

### std::compare_partial_order_fallback {#compare_partial_order_fallback}

<span class="ver ver-20">C++20</span>

```cpp
inline constexpr /* 未規定 */ compare_partial_order_fallback = /* 未規定 */;
// 呼び出し: std::compare_partial_order_fallback(a, b) -> std::partial_ordering
```

| 引数 | 意味 |
| --- | --- |
| `a`, `b` | 比べる 2 つの値 |

#### 動作の順序

1. `std::partial_order(a, b)` が書けるなら、その結果を返す
2. 書けなくて、`a == b` と `a < b` が書けるなら、次の規則で `partial_ordering` を作る
    - `a == b` が真なら `equivalent`
    - そうでなくて `a < b` が真なら `less`
    - そうでなくて `b < a` が真なら `greater`
    - どれでもなければ `unordered`
3. どれも書けなければ、コンパイルできない

#### 他の fallback との違い

`strong_order` と `weak_order` の代用では、`==` も `<` も偽なら `greater` としました。`partial_order` の代用では、`b < a` も確かめ、それも偽のときに `unordered` を返します。そのため、`b < a` が書けることも必要です。

#### NaN の扱い

`double` の NaN は、すべての値と `unordered` です。`std::partial_order(NaN, 1.0)` は `unordered` になります。`strong_order` では全順序が決められていますが、`partial_order` は NaN を無理に位置づけません。

`unordered` との比較は、`< 0` も `> 0` も `== 0` も偽になります。使うときは、`std::is_lt(r)` などの関数や、`r == std::partial_ordering::unordered` で、明示的に確かめます。

## 実際に動かしてみる

```cpp
#include <compare>
#include <print>

// <=> を持たない、古い形の型。== と < だけがある
struct Legacy {
  int value;
  bool operator==(const Legacy& other) const { return value == other.value; }
  bool operator<(const Legacy& other) const { return value < other.value; }
};

#include <limits>

const char* Name(std::partial_ordering r) {
  if (r == std::partial_ordering::less) return "less";
  if (r == std::partial_ordering::equivalent) return "equivalent";
  if (r == std::partial_ordering::greater) return "greater";
  return "unordered";
}

int main() {
  Legacy a{1};
  Legacy b{2};

  std::println("a と b: {}", Name(std::compare_partial_order_fallback(a, b)));
  std::println("b と a: {}", Name(std::compare_partial_order_fallback(b, a)));
  std::println("a と a: {}", Name(std::compare_partial_order_fallback(a, a)));

  // NaN との比較は unordered
  double nan = std::numeric_limits<double>::quiet_NaN();
  std::println("NaN と 1.0: {}", Name(std::compare_partial_order_fallback(nan, 1.0)));
  std::println("1.0 と 2.0: {}", Name(std::compare_partial_order_fallback(1.0, 2.0)));
}
```

```text title="実行結果"
a と b: less
b と a: greater
a と a: equivalent
NaN と 1.0: unordered
1.0 と 2.0: less
```

## ゲームでの使いどころ

`==` と `<` しかない古い型を、部分順序を扱うテンプレートの中で使えるようにします。NaN を含みうる浮動小数点数の比較にも向きます。

## よくあるミス

??? failure "unordered を less / greater の一方と思い込む"
    `unordered` との比較演算子はどれも偽です。明示的に確かめます。

??? failure "b < a が書けない型に使う"
    代用で `b < a` を使うので、コンパイルできません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`compare_strong_order_fallback`](compare_strong_order_fallback.md) | `strong_ordering` を返す版 |
| [`compare_weak_order_fallback`](compare_weak_order_fallback.md) | `weak_ordering` を返す版 |
| [`partial_order`](partial_order.md) | 元になる関数 |

## コンパイラ対応

C++20 から使えます。MSVC・GCC・Clang とも対応しています。

## 関連ページ

- [cpprefjp: std::compare_partial_order_fallback](https://cpprefjp.github.io/reference/compare/compare_partial_order_fallback.html)
- [cppreference: std::compare_partial_order_fallback](https://en.cppreference.com/w/cpp/utility/compare_partial_order_fallback)
