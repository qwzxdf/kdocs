---
title: std::views::to_input
summary: "範囲を、入力範囲（1 回だけ読める）として見せる view。"
order: 900
tags:
  - 型・言語サポート
---

# std::views::to_input

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-26">C++26</span>
`#include <ranges>`
</div>

テストなどで、「この処理は、範囲を 1 回しか読まない」と保証したいことがあります。`views::to_input` は、元の範囲が何であっても、入力範囲（1 回しか読めない）として見せます。

!!! tip "ポイント"
    - 元が `vector` でも、入力範囲に弱められる。
    - ジェネリックなアルゴリズムが入力範囲でも動くかの確認に使える。
    - C++26 の機能。

!!! info "このページを読む前に"
    [`std::ranges::range`](range.md) を先に読んでください。

## 関数の詳しい説明

### std::views::to_input {#to_input}

```cpp
constexpr auto views::to_input;  // 範囲アダプタ
```

- 戻り値: `to_input_view`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3};
  auto in = v | std::views::to_input;
  std::println("{}", std::ranges::forward_range<decltype(in)>);
}
```

```text title="実行結果"
false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 入力範囲でも動くコードをテストする |

## よくあるミス

??? failure "2 回読む"
    入力範囲は 1 回しか読めません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`input_range`](input_range.md) | 入力範囲のコンセプト |

## コンパイラ対応

C++26 の機能です。新しい標準ライブラリで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 範囲を入力範囲（1 回だけ読める）として見せる view
    - [x] 元が `vector` でも、入力範囲に弱められる
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::views::to_input](https://cpprefjp.github.io/reference/ranges/to_input_view.html)
- [cppreference: std::views::to_input](https://en.cppreference.com/w/cpp/ranges/to_input_view)
