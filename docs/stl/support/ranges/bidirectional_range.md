---
title: std::ranges::bidirectional_range
summary: "前後どちらにも進める範囲を要求するコンセプト。"
order: 900
tags:
  - 型・言語サポート
---

# std::ranges::bidirectional_range

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

`std::list` のように、前にも後ろにも 1 つずつ動ける範囲です。`reverse` のように、後ろから歩く処理が使えます。

!!! tip "ポイント"
    - コンセプトなので、`requires` やテンプレートの制約に書く。
    - `std::ranges::bidirectional_range<T>` は `bool` の定数式。
    - `static_assert` でも確かめられる。

!!! info "このページを読む前に"
    [`std::ranges::range`](range.md) を先に読んでください。

## 関数の詳しい説明

### std::ranges::bidirectional_range {#bidirectional_range}

```cpp
template <class T>
concept bidirectional_range = /* begin が bidirectional_iterator を返す */;
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
    std::println("{}", std::ranges::bidirectional_range<std::list<int>>);
    std::println("{}", std::ranges::bidirectional_range<std::forward_list<int>>);
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

??? failure "`forward_list` に reverse を使う"
    `forward_list` は前にしか進めません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`forward_range`](forward_range.md) | より弱い条件 |
| [`random_access_range`](random_access_range.md) | 添字で飛べる |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 前後どちらにも進める範囲を要求するコンセプト
    - [x] コンセプトなので、`requires` やテンプレートの制約に書く
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::ranges::bidirectional_range](https://cpprefjp.github.io/reference/ranges/bidirectional_range.html)
- [cppreference: std::ranges::bidirectional_range](https://en.cppreference.com/w/cpp/ranges/bidirectional_range)
