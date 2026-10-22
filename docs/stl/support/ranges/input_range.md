---
title: std::ranges::input_range
summary: "入力として一度だけ読める範囲を要求するコンセプト。"
order: 900
tags:
  - 型・言語サポート
---

# std::ranges::input_range

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

ストリームのように、先頭から一方向に 1 回だけ読める範囲もあります。`input_range` は、そうした最も弱い条件の範囲です。ほとんどの標準コンテナと view が満たします。

!!! tip "ポイント"
    - コンセプトなので、`requires` やテンプレートの制約に書く。
    - `std::ranges::input_range<T>` は `bool` の定数式。
    - `static_assert` でも確かめられる。

!!! info "このページを読む前に"
    [`std::ranges::range`](range.md) を先に読んでください。

## 関数の詳しい説明

### std::ranges::input_range {#input_range}

```cpp
template <class T>
concept input_range = /* begin が input_iterator を返す */;
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
    std::println("{}", std::ranges::input_range<std::vector<int>>);
    std::println("{}", std::ranges::input_range<int>);
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

??? failure "入力範囲を 2 回読む"
    入力専用の範囲（`istream_view` など）は、2 回走査できません。2 回読むなら `forward_range` を要求します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`forward_range`](forward_range.md) | 何度でも読める |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 入力として一度だけ読める範囲を要求するコンセプト
    - [x] コンセプトなので、`requires` やテンプレートの制約に書く
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::ranges::input_range](https://cpprefjp.github.io/reference/ranges/input_range.html)
- [cppreference: std::ranges::input_range](https://en.cppreference.com/w/cpp/ranges/input_range)
