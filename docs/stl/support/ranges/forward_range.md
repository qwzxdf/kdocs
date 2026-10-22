---
title: std::ranges::forward_range
summary: "何度でも先頭から読み直せる範囲を要求するコンセプト。"
order: 900
tags:
  - 型・言語サポート
---

# std::ranges::forward_range

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

ストリームと違って、`std::forward_list` のような範囲は、何度でも先頭から読み直せます。`forward_range` は、その性質を要求します。

!!! tip "ポイント"
    - コンセプトなので、`requires` やテンプレートの制約に書く。
    - `std::ranges::forward_range<T>` は `bool` の定数式。
    - `static_assert` でも確かめられる。

!!! info "このページを読む前に"
    [`std::ranges::range`](range.md) を先に読んでください。

## 関数の詳しい説明

### std::ranges::forward_range {#forward_range}

```cpp
template <class T>
concept forward_range = /* begin が forward_iterator を返す */;
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
    std::println("{}", std::ranges::forward_range<std::forward_list<int>>);
    std::println("{}", std::ranges::forward_range<std::ranges::istream_view<int>>);
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

??? failure "`istream_view` に使う"
    入力ストリームは 1 回しか読めません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`input_range`](input_range.md) | より弱い条件 |
| [`bidirectional_range`](bidirectional_range.md) | 後ろにも戻れる |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 何度でも先頭から読み直せる範囲を要求するコンセプト
    - [x] コンセプトなので、`requires` やテンプレートの制約に書く
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::ranges::forward_range](https://cpprefjp.github.io/reference/ranges/forward_range.html)
- [cppreference: std::ranges::forward_range](https://en.cppreference.com/w/cpp/ranges/forward_range)
