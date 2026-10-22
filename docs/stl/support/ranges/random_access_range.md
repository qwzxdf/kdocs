---
title: std::ranges::random_access_range
summary: "添字で好きな位置へ飛べる範囲を要求するコンセプト。"
order: 900
tags:
  - 型・言語サポート
---

# std::ranges::random_access_range

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

`vector` や `deque` のように、`it + n` で一気に飛べる範囲です。`sort` などが要求します。

!!! tip "ポイント"
    - コンセプトなので、`requires` やテンプレートの制約に書く。
    - `std::ranges::random_access_range<T>` は `bool` の定数式。
    - `static_assert` でも確かめられる。

!!! info "このページを読む前に"
    [`std::ranges::range`](range.md) を先に読んでください。

## 関数の詳しい説明

### std::ranges::random_access_range {#random_access_range}

```cpp
template <class T>
concept random_access_range = /* begin が random_access_iterator を返す */;
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
    std::println("{}", std::ranges::random_access_range<std::deque<int>>);
    std::println("{}", std::ranges::random_access_range<std::list<int>>);
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

??? failure "`list` に sort を使う"
    `list` は添字で飛べないので `sort` できません。`list::sort` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`bidirectional_range`](bidirectional_range.md) | より弱い条件 |
| [`contiguous_range`](contiguous_range.md) | メモリが連続 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 添字で好きな位置へ飛べる範囲を要求するコンセプト
    - [x] コンセプトなので、`requires` やテンプレートの制約に書く
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::ranges::random_access_range](https://cpprefjp.github.io/reference/ranges/random_access_range.html)
- [cppreference: std::ranges::random_access_range](https://en.cppreference.com/w/cpp/ranges/random_access_range)
