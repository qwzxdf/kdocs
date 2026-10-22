---
title: std::compare_three_way_result
summary: "`<=>` の戻り値の型を求める。"
order: 900
group: 比較（<compare>）
tags:
  - 型・言語サポート
---

# std::compare_three_way_result

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <compare>`
</div>

型 `T` を `<=>` で比べたときの結果の型（`strong_ordering` か `partial_ordering` など）を、テンプレートの中で知りたいときに使います。

!!! tip "ポイント"
    - `<compare>` の部品。
    - C++20 の三方比較（`<=>`）と組み合わせて使う。
    - ふつうは `=default` の `<=>` で足りる。

!!! info "このページを読む前に"
    [`<=>`（宇宙船演算子）](spaceship.md) を先に読んでください。

## 関数の詳しい説明

### std::compare_three_way_result {#compare_three_way_result}

```cpp
template <class T, class U = T>
struct compare_three_way_result { using type = /* <=> の結果の型 */; };
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T, U` | 型 | 比べる 2 つの型 |

- 戻り値: 順序型（`::type`）
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <compare>
#include <print>
#include <type_traits>

int main() {
  std::println("{}", std::is_same_v<std::compare_three_way_result_t<int>, std::strong_ordering>);
  std::println("{}", std::is_same_v<std::compare_three_way_result_t<double>, std::partial_ordering>);
}
```

```text title="実行結果"
true
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | ジェネリックな比較関数の戻り値の型を決める |

## よくあるミス

??? failure "`<=>` を持たない型に使う"
    `<=>` が使えない型では、`::type` がありません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`three_way_comparable`](three_way_comparable.md) | `<=>` で比べられるか |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `<=>` の戻り値の型を求める
    - [x] `<compare>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::compare_three_way_result](https://cpprefjp.github.io/reference/compare/compare_three_way_result.html)
- [cppreference: std::compare_three_way_result](https://en.cppreference.com/w/cpp/utility/compare_three_way_result)
