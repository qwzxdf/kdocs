---
title: std::incrementable
summary: "`++` で進められ、何度でも同じ範囲を走査できる型を要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::incrementable

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

`weakly_incrementable` に、「コピーしたイテレータを独立に進めても同じ結果になる」という性質を足したものです。

!!! tip "ポイント"
    - コンセプト。`requires` やテンプレートの制約に書く。
    - `std::incrementable<...>` は `bool` の定数式。
    - C++20 のアルゴリズムが引数の制約に使っている。

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::incrementable {#incrementable}

```cpp
template <class I>
concept incrementable = /* weakly_incrementable かつ regular かつ i++ が i と同じ型を返す */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `I` | 型 | 調べる型 |

- 戻り値: 条件を満たせば `true`（コンパイル時の定数）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <iterator>
#include <print>

int main() {
  std::println("{}", std::incrementable<int>);
  std::println("{}", std::incrementable<const int>);
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

??? failure "const の型を渡す"
    `const int` は `++` できません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`weakly_incrementable`](weakly_incrementable.md) | 弱い条件 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `++` で進められ、何度でも同じ範囲を走査できる型を要求する
    - [x] コンセプト。`requires` やテンプレートの制約に書く
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::incrementable](https://cpprefjp.github.io/reference/iterator/incrementable.html)
- [cppreference: std::incrementable](https://en.cppreference.com/w/cpp/iterator/incrementable)
