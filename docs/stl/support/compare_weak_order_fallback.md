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

`std::compare_weak_order_fallback(a, b)` は、`<=>` や [`std::weak_order`](weak_order.md) が使えない古い型を、`==` と `<` から `std::weak_ordering` として比べます。`weak_ordering` は、「等しくはないが、順序の上では同じ位置にある」ものを許す比較です。大文字小文字を区別しない文字列の比較のように、見た目は違っても、同じ順位になる要素を表せます。

!!! tip "ポイント"
    - `std::weak_order` が使えるならそれを使い、使えなければ `==` と `<` で代用する
    - 戻り値は `std::weak_ordering`（`less`・`equivalent`・`greater`）
    - 代用するには、`a == b` と `a < b` が書けること
    - `strong_ordering` との違いは、区別できないものを置き換えても、結果が同じとは限らないこと

!!! info "このページを読む前に"
    [`std::weak_order`](weak_order.md) と [`<=>`（三方比較）](spaceship.md) を先に読んでください。

## 関数の詳しい説明

### std::compare_weak_order_fallback {#compare_weak_order_fallback}

<span class="ver ver-20">C++20</span>

```cpp
inline constexpr /* 未規定 */ compare_weak_order_fallback = /* 未規定 */;
// 呼び出し: std::compare_weak_order_fallback(a, b) -> std::weak_ordering
```

| 引数 | 意味 |
| --- | --- |
| `a`, `b` | 比べる 2 つの値 |

#### 動作の順序

1. `std::weak_order(a, b)` が書けるなら、その結果を返す
2. 書けなくて、`a == b` と `a < b` が書けるなら、次の規則で `weak_ordering` を作る
    - `a == b` が真なら `equivalent`
    - そうでなくて `a < b` が真なら `less`
    - それ以外は `greater`
3. どちらも書けないなら、コンパイルできない

#### equivalent の意味

`weak_ordering::equivalent` は、「順序の上で同じ位置にある」ことを表します。`std::set` のように、順序だけで要素を区別する連想コンテナでは、`equivalent` な 2 つの要素は、同じ要素として扱われます。

`strong_ordering::equal` との違いは、`equivalent` なものを入れ替えても、結果が変わらないとは限らない点です。たとえば、大文字小文字を無視して比べる文字列で、`"Hero"` と `"hero"` は `equivalent` ですが、同じ文字列ではありません。

#### strong_order との関係

`compare_strong_order_fallback` が `strong_ordering` を返すのに対し、こちらは弱い順序を返します。型が持つ比較の強さに合わせて選びます。

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

const char* Name(std::weak_ordering r) {
  if (r == std::weak_ordering::less) return "less";
  if (r == std::weak_ordering::equivalent) return "equivalent";
  return "greater";
}

int main() {
  Legacy a{1};
  Legacy b{2};
  Legacy c{1};

  std::println("a と b: {}", Name(std::compare_weak_order_fallback(a, b)));
  std::println("b と a: {}", Name(std::compare_weak_order_fallback(b, a)));
  std::println("a と c: {}", Name(std::compare_weak_order_fallback(a, c)));

  // 浮動小数点数: 0.0 と -0.0 は equivalent
  std::println("0.0 と -0.0: {}", Name(std::compare_weak_order_fallback(0.0, -0.0)));
}
```

```text title="実行結果"
a と b: less
b と a: greater
a と c: equivalent
0.0 と -0.0: equivalent
```

## ゲームでの使いどころ

`==` と `<` しかない型を、弱い順序を求めるテンプレートの中で扱えるようにします。

## よくあるミス

??? failure "equivalent を同一と思い込む"
    順序の上で同じ位置にあるだけです。中身が同じとは限りません。

??? failure "== と < の意味が矛盾する型に使う"
    結果は意味を持ちません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`compare_strong_order_fallback`](compare_strong_order_fallback.md) | `strong_ordering` を返す版 |
| [`compare_partial_order_fallback`](compare_partial_order_fallback.md) | `partial_ordering` を返す版 |
| [`weak_order`](weak_order.md) | 元になる関数 |

## コンパイラ対応

C++20 から使えます。MSVC・GCC・Clang とも対応しています。

## 関連ページ

- [cpprefjp: std::compare_weak_order_fallback](https://cpprefjp.github.io/reference/compare/compare_weak_order_fallback.html)
- [cppreference: std::compare_weak_order_fallback](https://en.cppreference.com/w/cpp/utility/compare_weak_order_fallback)
