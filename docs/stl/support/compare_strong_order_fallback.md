---
title: std::compare_strong_order_fallback
summary: "`<=>` が無い型も、`==` と `<` で `strong_ordering` として比べる。"
order: 900
group: 比較（<compare>）
tags:
  - 型・言語サポート
---

# std::compare_strong_order_fallback

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <compare>`
</div>

`<=>` を持たない古い型（`==` と `<` しかない型）を、`std::set` のキーや、比較アルゴリズムに使いたいことがあります。`std::compare_strong_order_fallback(a, b)` は、`<=>` があれば [`std::strong_order`](strong_order.md) を使い、なければ `==` と `<` から `std::strong_ordering` を作って返します。古い型と新しい型を、同じ書き方で比べられます。

!!! tip "ポイント"
    - `std::strong_order` が使える型ならそれを使い、使えなければ `==` と `<` で代用する
    - 戻り値は `std::strong_ordering`（`less`・`equal`・`greater` のどれか）
    - 代用するには、`a == b` と `a < b` が `bool` に変換できる式として書けること
    - 標準の関数ではなく、カスタマイゼーション ポイント オブジェクト

!!! info "このページを読む前に"
    [`std::strong_order`](strong_order.md) と [`<=>`（三方比較）](spaceship.md) を先に読んでください。

## 関数の詳しい説明

### std::compare_strong_order_fallback {#compare_strong_order_fallback}

<span class="ver ver-20">C++20</span>

```cpp
inline constexpr /* 未規定 */ compare_strong_order_fallback = /* 未規定 */;
// 呼び出し: std::compare_strong_order_fallback(a, b) -> std::strong_ordering
```

| 引数 | 意味 |
| --- | --- |
| `a`, `b` | 比べる 2 つの値 |

#### 動作の順序

1. `std::strong_order(a, b)` が書けるなら、その結果を返す
2. 書けなくて、`a == b` と `a < b` が書けるなら、次の規則で `strong_ordering` を作る
    - `a == b` が真なら `equal`
    - そうでなくて `a < b` が真なら `less`
    - それ以外は `greater`
3. どちらも書けないなら、呼び出しがコンパイルできない

#### 同値と等しいの区別

`strong_ordering` は、`equal` のものを区別できない（置き換えても結果が変わらない）ことを表します。`==` で等しいものを `equal` にするのは、その前提に合っているときだけにしてください。`==` と `<` の意味がかみ合っていない型（`a == b` が真なのに、`a < b` も真になる）では、結果は意味を持ちません。

#### 浮動小数点数

`double` のように `<=>` が `partial_ordering` までしか返さない型に対しても、`std::strong_order` が全順序を定義しているので、`compare_strong_order_fallback` は、その結果を返します。NaN も、全順序の中に位置づけられます。

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

const char* Name(std::strong_ordering r) {
  if (r == std::strong_ordering::less) return "less";
  if (r == std::strong_ordering::equal) return "equal";
  return "greater";
}

int main() {
  Legacy a{1};
  Legacy b{2};
  Legacy c{1};

  std::println("a と b: {}", Name(std::compare_strong_order_fallback(a, b)));
  std::println("b と a: {}", Name(std::compare_strong_order_fallback(b, a)));
  std::println("a と c: {}", Name(std::compare_strong_order_fallback(a, c)));

  // <=> を持つ型には、そのまま <=> が使われる
  std::println("1 と 2 (int): {}", Name(std::compare_strong_order_fallback(1, 2)));
}
```

```text title="実行結果"
a と b: less
b と a: greater
a と c: equal
1 と 2 (int): less
```

## ゲームでの使いどころ

昔から使っている自作クラスや外部ライブラリの型が `<=>` を持たないとき、三方比較を期待するテンプレートの中で、その型を扱えるようにします。

## よくあるミス

??? failure "== と < の意味が矛盾する型に使う"
    結果は意味を持ちません。`==` が真なら `<` は偽、という整合が要ります。

??? failure "== か < のどちらかしかない型に使う"
    コンパイルできません。両方が必要です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`compare_weak_order_fallback`](compare_weak_order_fallback.md) | `weak_ordering` を返す版 |
| [`compare_partial_order_fallback`](compare_partial_order_fallback.md) | `partial_ordering` を返す版 |
| [`strong_order`](strong_order.md) | 元になる関数 |

## コンパイラ対応

C++20 から使えます。MSVC・GCC・Clang とも対応しています。

## 関連ページ

- [cpprefjp: std::compare_strong_order_fallback](https://cpprefjp.github.io/reference/compare/compare_strong_order_fallback.html)
- [cppreference: std::compare_strong_order_fallback](https://en.cppreference.com/w/cpp/utility/compare_strong_order_fallback)
