---
title: std::three_way_comparable_with
summary: "2 つの型を `<=>` で比べられることを要求する。"
order: 900
group: 比較（<compare>）
tags:
  - 型・言語サポート
---

# std::three_way_comparable_with

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <compare>`
</div>

`int` と `long` のように、型が違う値を `<=>` で比べられるかを調べるコンセプトです。

!!! tip "ポイント"
    - `<compare>` の部品。
    - C++20 の三方比較（`<=>`）と組み合わせて使う。
    - ふつうは `=default` の `<=>` で足りる。

!!! info "このページを読む前に"
    [`<=>`（宇宙船演算子）](spaceship.md) を先に読んでください。

## 関数の詳しい説明

### std::three_way_comparable_with {#three_way_comparable_with}

```cpp
template <class T, class U, class Cat = partial_ordering>
concept three_way_comparable_with = /* T と U で <=> が使える */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T, U` | 型 | 調べる 2 つの型 |
| `Cat` | 順序型 | 省略可。最低限の強さ |

- 戻り値: 条件を満たせば `true`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <compare>
#include <print>
#include <string>

int main() {
  std::println("{}", std::three_way_comparable_with<int, long>);
  std::println("{}", std::three_way_comparable_with<int, std::string>);
}
```

```text title="実行結果"
true
false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 異なる型を比べるテンプレートの制約 |

## よくあるミス

??? failure "暗黙変換できるだけで満たすと思う"
    共通の参照型を持ち、両方向の `<=>` が使える必要があります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`three_way_comparable`](three_way_comparable.md) | 同じ型どうし |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 2 つの型を `<=>` で比べられることを要求する
    - [x] `<compare>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::three_way_comparable_with](https://cpprefjp.github.io/reference/compare/three_way_comparable_with.html)
- [cppreference: std::three_way_comparable_with](https://en.cppreference.com/w/cpp/utility/three_way_comparable_with)
