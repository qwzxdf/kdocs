---
title: std::compare_three_way
summary: "`<=>` を関数オブジェクトにしたもの。"
order: 900
group: 比較（<compare>）
tags:
  - 型・言語サポート
---

# std::compare_three_way

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <compare>`
</div>

`std::less` が `<` を関数オブジェクトにしたように、`compare_three_way` は `<=>` を関数オブジェクトにしたものです。アルゴリズムに三方比較を渡したいときに使います。

!!! tip "ポイント"
    - `<compare>` の部品。
    - C++20 の三方比較（`<=>`）と組み合わせて使う。
    - ふつうは `=default` の `<=>` で足りる。

!!! info "このページを読む前に"
    [`<=>`（宇宙船演算子）](spaceship.md) を先に読んでください。

## 関数の詳しい説明

### std::compare_three_way {#compare_three_way}

```cpp
struct compare_three_way {
  template <class T, class U>
  constexpr auto operator()(T&& t, U&& u) const;  // t <=> u
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `t, u` | 型 | 比べる 2 つの値 |

- 戻り値: `t <=> u` の結果（順序型）
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <compare>
#include <print>

int main() {
  std::println("{}", std::compare_three_way{}(1, 2) == std::strong_ordering::less);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | `lexicographical_compare_three_way` の比較に渡す |

## よくあるミス

??? failure "`std::less` と取り違える"
    `less` は `bool`、`compare_three_way` は 3 通りの順序型を返します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`spaceship`](spaceship.md) | `<=>` 演算子 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `<=>` を関数オブジェクトにしたもの
    - [x] `<compare>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::compare_three_way](https://cpprefjp.github.io/reference/compare/compare_three_way.html)
- [cppreference: std::compare_three_way](https://en.cppreference.com/w/cpp/utility/compare_three_way)
