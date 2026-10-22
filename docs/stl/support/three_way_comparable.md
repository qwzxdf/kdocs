---
title: std::three_way_comparable
summary: "`<=>` と、`==`・`<` などで比べられる型を要求する。"
order: 900
group: 比較（<compare>）
tags:
  - 型・言語サポート
---

# std::three_way_comparable

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <compare>`
</div>

`<=>` が使える型で、さらに `==`・`<` などの普通の比較も一貫して使えることを要求するコンセプトです。

!!! tip "ポイント"
    - `<compare>` の部品。
    - C++20 の三方比較（`<=>`）と組み合わせて使う。
    - ふつうは `=default` の `<=>` で足りる。

!!! info "このページを読む前に"
    [`<=>`（宇宙船演算子）](spaceship.md) を先に読んでください。

## 関数の詳しい説明

### std::three_way_comparable {#three_way_comparable}

```cpp
template <class T, class Cat = partial_ordering>
concept three_way_comparable = /* T 同士で <=> と比較演算子が使える */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べる型 |
| `Cat` | 順序型 | 省略可。最低限の強さ |

- 戻り値: 条件を満たせば `true`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <compare>
#include <print>

struct NoCmp {};

int main() {
  std::println("{}", std::three_way_comparable<int>);
  std::println("{}", std::three_way_comparable<NoCmp>);
}
```

```text title="実行結果"
true
false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | `<=>` で比べられる型だけ受け付ける |

## よくあるミス

??? failure "`<=>` だけ定義して `==` を忘れる"
    `==` も使えることが条件です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`three_way_comparable_with`](three_way_comparable_with.md) | 異なる型どうし |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `<=>` と、`==`・`<` などで比べられる型を要求する
    - [x] `<compare>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::three_way_comparable](https://cpprefjp.github.io/reference/compare/three_way_comparable.html)
- [cppreference: std::three_way_comparable](https://en.cppreference.com/w/cpp/utility/three_way_comparable)
