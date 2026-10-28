---
title: std::sized_sentinel_for
summary: "イテレータとの差（距離）を定数時間で求められる終端を要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::sized_sentinel_for

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

`sentinel_for` に加えて、`end - begin` で要素数を求められることを要求します。`vector` のイテレータは満たしますが、`list` は満たしません。

!!! tip "ポイント"
    - コンセプト。`requires` やテンプレートの制約に書く。
    - `std::sized_sentinel_for<...>` は `bool` の定数式。
    - C++20 のアルゴリズムが引数の制約に使っている。

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::sized_sentinel_for {#sized_sentinel_for}

```cpp
template <class S, class I>
concept sized_sentinel_for = /* sentinel_for<S, I> かつ S - I が使える */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `S` | 型 | 調べる型 |
| `I` | 型 | 調べる型 |

- 戻り値: 条件を満たせば `true`（コンパイル時の定数）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <iterator>
#include <list>
#include <print>

int main() {
  std::println("{}", std::sized_sentinel_for<int*, int*>);
  std::println("{}", std::sized_sentinel_for<std::list<int>::iterator, std::list<int>::iterator>);
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

??? failure "`list` の距離を速いと思う"
    `list` は 1 つずつ数えるので、差が定数時間では求まりません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`sentinel_for`](sentinel_for.md) | 差は不要 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] イテレータとの差（距離）を定数時間で求められる終端を要求する
    - [x] コンセプト。`requires` やテンプレートの制約に書く
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::sized_sentinel_for](https://cpprefjp.github.io/reference/iterator/sized_sentinel_for.html)
- [cppreference: std::sized_sentinel_for](https://en.cppreference.com/w/cpp/iterator/sized_sentinel_for)
