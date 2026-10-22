---
title: std::ranges::output_range
summary: "書き込める範囲を要求するコンセプト。"
order: 900
tags:
  - 型・言語サポート
---

# std::ranges::output_range

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

結果を書き込む先の範囲を受け取る関数では、「書き込める」ことを要求します。`output_range<R, T>` は、型 `T` の値を書き込める範囲かを調べます。

!!! tip "ポイント"
    - コンセプトなので、`requires` やテンプレートの制約に書く。
    - `std::ranges::output_range<T>` は `bool` の定数式。
    - `static_assert` でも確かめられる。

!!! info "このページを読む前に"
    [`std::ranges::range`](range.md) を先に読んでください。

## 関数の詳しい説明

### std::ranges::output_range {#output_range}

```cpp
template <class T>
concept output_range = /* begin が output_iterator<T> を返す */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べる範囲の型 |

- 戻り値: 条件を満たせば `true`（コンパイル時の定数）
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <print>
#include <ranges>

int main() {
    std::println("{}", std::ranges::output_range<std::vector<int>, int>);
    std::println("{}", std::ranges::output_range<const std::vector<int>, int>);
}
```

```text title="実行結果"
true
false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | テンプレートの引数を制約して、使える範囲だけを受け付ける |

## よくあるミス

??? failure "const な範囲に書く"
    const な範囲は書き込めません。`output_range` を要求しておくと、コンパイル時に分かります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`input_range`](input_range.md) | 読める範囲 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 書き込める範囲を要求するコンセプト
    - [x] コンセプトなので、`requires` やテンプレートの制約に書く
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::ranges::output_range](https://cpprefjp.github.io/reference/ranges/output_range.html)
- [cppreference: std::ranges::output_range](https://en.cppreference.com/w/cpp/ranges/output_range)
