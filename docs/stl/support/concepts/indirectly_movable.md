---
title: std::indirectly_movable
summary: "あるイテレータから別のイテレータへ、要素をムーブできることを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::indirectly_movable

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

`move` 系のアルゴリズムの制約に使われます。読み取り側と書き込み側の型が合っているかを調べます。

!!! tip "ポイント"
    - コンセプト。`requires` やテンプレートの制約に書く。
    - `std::indirectly_movable<...>` は `bool` の定数式。
    - C++20 のアルゴリズムが引数の制約に使っている。

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::indirectly_movable {#indirectly_movable}

```cpp
template <class In, class Out>
concept indirectly_movable = /* indirectly_readable<In> かつ indirectly_writable<Out, iter_rvalue_reference_t<In>> */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `In` | 型 | 調べる型 |
| `Out` | 型 | 調べる型 |

- 戻り値: 条件を満たせば `true`（コンパイル時の定数）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <iterator>
#include <print>

int main() {
  std::println("{}", std::indirectly_movable<int*, int*>);
  std::println("{}", std::indirectly_movable<int*, const int*>);
}
```

```text title="実行結果"
true
false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 自作のアルゴリズムの引数を制約する |

## よくあるミス

??? failure "const な出力先"
    書き込めない出力先は満たしません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`indirectly_copyable`](indirectly_copyable.md) | コピーする |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] あるイテレータから別のイテレータへ要素をムーブできることを要求する
    - [x] コンセプト。`requires` やテンプレートの制約に書く
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::indirectly_movable](https://cpprefjp.github.io/reference/iterator/indirectly_movable.html)
- [cppreference: std::indirectly_movable](https://en.cppreference.com/w/cpp/iterator/indirectly_movable)
