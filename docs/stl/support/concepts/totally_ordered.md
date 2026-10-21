---
title: std::totally_ordered
summary: "`<`、`>`、`==` などで大小を比べられることを要求するコンセプト。"
order: 8
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::totally_ordered

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <concepts>`
</div>

`std::totally_ordered<T>` は、**T が `<`、`>`、`<=`、`>=`、`==`、`!=` で比べられること**を要求するコンセプトです。`sort` や `std::set` に入れられる型の条件にあたります。

!!! tip "ポイント"
    - `std::min` / `max` を使うテンプレートの制約に便利。
    - `<=>` を default にした型は満たす。

!!! info "このページを読む前に"
    [テンプレートとコンセプト](../../../basics/template.md) の基本が前提です。

## 関数の詳しい説明

### std::totally_ordered {#totally_ordered}

```cpp
template <class T>
concept totally_ordered = /* 条件 */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | テンプレート引数 | 調べる型 |

- 戻り値: 条件を満たせば `true`（コンパイル時の定数）
- 計算量: コンパイル時

```cpp
#include <concepts>
#include <print>

struct NoCompare {};

int main() {
  std::println("{} {}", std::totally_ordered<int>, std::totally_ordered<NoCompare>);
}
```

```text title="実行結果"
true false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 比較できる型だけを受け取る max テンプレート | `template <std::totally_ordered T> T Max(T a, T b)` |

## よくあるミス

??? failure "小数の NaN"
    小数は NaN があるため厳密には全順序ではありませんが、`totally_ordered` は満たします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`operator<=>`](../spaceship.md) | 比較を一括で作る |

## コンパイラ対応

C++20 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 比べられることを要求
    - [x] `sort` できる型の条件
    - [x] `<=>` default で満たす

## 関連ページ

- [cpprefjp: std::totally_ordered](https://cpprefjp.github.io/reference/concepts/totally_ordered.html)
- [cppreference: std::totally_ordered](https://en.cppreference.com/w/cpp/concepts/totally_ordered)
