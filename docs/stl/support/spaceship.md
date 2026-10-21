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

`operator<=>`（三方比較演算子、宇宙船演算子）は、**2 つの値を比べて、「小さい・等しい・大きい」を 1 回で返す**演算子です。クラスに `auto operator<=>(const T&) const = default;` と 1 行書くだけで、メンバを順に比べる `<`、`>`、`<=`、`>=`、`==`、`!=` がすべて使えるようになります。

!!! tip "ポイント"
    - **`= default` で書くのが基本。** メンバを宣言順に比べてくれる。
    - これで `sort` や `std::set` のキーに使える。
    - 戻り値は `strong_ordering` / `partial_ordering` / `weak_ordering`（`auto` で受けると自動で決まる）。

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

| 場面 | 書き方 |
| --- | --- |
| バージョン番号・ID の比較 | `auto operator<=>(const Version&) const = default;` |
| `std::map` のキーにする自作の型 | `<=>` を default にして、そのままキーにする |

## よくあるミス

??? failure "メンバの宣言順が比較の順になる"
    メンバは**宣言した順**に比べられます。重要なメンバを先に書きます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`strong_ordering`](strong_ordering.md) | 戻り値の型 |
| `operator==` | `<=>` を default にすると、`==` も自動で生える |

## コンパイラ対応

C++20 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `= default` で全比較が使える
    - [x] メンバを宣言順に比べる
    - [x] 戻り値は ordering 型

## 関連ページ

- [cpprefjp: operator<=>（三方比較）](https://cpprefjp.github.io/reference/compare/strong_ordering.html)
- [cppreference: operator<=>（三方比較）](https://en.cppreference.com/w/cpp/language/operator_comparison#Three-way_comparison)
