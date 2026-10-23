---
title: operator<=>（三方比較）
summary: "「小さい・等しい・大きい」を 1 回で調べる比較演算子。= default で全部の比較が生える。"
order: 1
group: 比較（<compare>）
tags:
  - 型・言語サポート
---

# operator<=>（三方比較）

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-20">C++20</span>
`#include <compare>`
</div>

キャラクターの構造体を `sort` で並べたい、`std::set` のキーにしたい。そのためには `<` が必要で、`==`、`!=`、`>`、`<=`、`>=` もほしくなります。C++17 までは、6 つの比較演算子を手で書くか、`<` だけ書いて他を組み立てていました。メンバーが増えるたびに、書き直すことになります。C++20 の三方比較演算子 `<=>` は、「小さい・等しい・大きい」を 1 回で調べる演算子で、`= default` と書くだけで、全部の比較が使えるようになります。

!!! tip "ポイント"
    - **`= default` で書くのが基本。** メンバを宣言順に比べてくれる。
    - これで `sort` や `std::set` のキーに使える。
    - 戻り値は `strong_ordering` / `partial_ordering` / `weak_ordering`（`auto` で受けると自動で決まる）。

!!! info "このページを読む前に"
    構造体とメンバーの基本、そして `std::sort` や `std::set` が比較演算子を使うことが分かると読みやすいです。

## 関数の詳しい説明

### operator<=> {#spaceship}

```cpp
auto operator<=>(const T& other) const = default;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `other` | `const T&` | 比べる相手 |

- 戻り値: 比較結果（`std::strong_ordering` など）
- 計算量: メンバの数に比例

```cpp
#include <compare>
#include <print>

struct Version {
  int major;
  int minor;
  auto operator<=>(const Version&) const = default;  // これだけで 6 つの比較が使える
};

int main() {
  Version a{1, 2};
  Version b{1, 3};
  std::println("{} {}", a < b, a == Version{1, 2});
}
```

```text title="実行結果"
true true
```

## ゲームでの使いどころ

ゲームのデータ型の比較に使います。`struct Score { int points; std::string name; auto operator<=>(const Score&) const = default; };` と書けば、`Score` を `sort` や `std::set` に入れられます。比較は、宣言した順にメンバーを調べます。点数が先なら、点数で比べ、同点なら名前で比べます。メンバーの宣言順が、比較の優先順位になる点に注意します。

ID や座標の組のような小さな型は、`= default` で十分です。特殊な順序（降順など）が必要なときは、手で書いた `<=>` で `strong_ordering` を返します。

`std::map` や `std::set` のキーにする型は、`<` が使えれば足ります。`<=>` を書けば、この要件を満たします。

## よくあるミス

??? failure "メンバーの宣言順を変えて、並び方が変わる"
    `= default` の比較は、メンバーの宣言順に行われます。見た目の整理でメンバーを並べ替えると、`sort` の結果が変わります。比較の優先順位をコードで示したいときは、コメントを添えるか、自分で `<=>` を書きます。

??? failure "浮動小数点のメンバーがあるのに、`strong_ordering` を期待する"
    `float` や `double` のメンバーがあると、`NaN` のために `partial_ordering` になります。`auto` で戻り値を受ける、または `std::partial_ordering` を明示します。`std::strong_ordering` と書くと、コンパイルエラーになります。

??? failure "ポインターや参照のメンバーを比較に含める"
    ポインターを `= default` で比べると、アドレスの順になります。中身で比べたいなら、`<=>` を自分で書きます。

## 類似

| 名前 | 違い |
| --- | --- |
| `operator==` | 等しいかだけを調べる。`<=>` を `= default` にすると、`==` も自動で生える |
| [`std::strong_ordering`](strong_ordering.md) | 全順序の結果。整数や文字列のメンバーで使われる |
| [`std::partial_ordering`](partial_ordering.md) | 比べられない値（NaN）を含む順序。浮動小数点で使われる |

## コンパイラ対応

C++20 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `auto operator<=>(const T&) const = default;` の 1 行で、全部の比較が使える。
    - [x] 比較はメンバーの宣言順。順番を変えると結果が変わる。
    - [x] 浮動小数点を含むと `partial_ordering` になる。

## 関連ページ

- [cpprefjp: operator<=>（三方比較）](https://cpprefjp.github.io/reference/compare/strong_ordering.html)
- [cppreference: operator<=>（三方比較）](https://en.cppreference.com/w/cpp/language/operator_comparison#Three-way_comparison)
