---
title: std::ranges::cbegin
summary: "範囲の先頭を指す、const のイテレータを返す。"
order: 900
group: ranges の基本部品
tags:
  - 型・言語サポート
---

# std::ranges::cbegin

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

読むだけの走査では、書き換えられないイテレータを使うほうが安全です。`ranges::cbegin(r)` は、`ranges::begin` の const 版です。

!!! tip "ポイント"
    - 配列・コンテナ・view に同じ書き方で使える。
    - 関数ではなく、関数オブジェクト（カスタマイズポイント）。
    - 使えない型には、コンパイルエラーになる。

!!! info "このページを読む前に"
    [`std::ranges::begin`](begin.md) を先に読んでください。

## 関数の詳しい説明

### std::ranges::cbegin {#cbegin}

```cpp
inline constexpr /* カスタマイズポイント */ ranges::cbegin;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `t` | 範囲 | 対象の範囲 |

- 戻り値: const のイテレータ
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3};
  std::println("{}", *std::ranges::cbegin(v));
}
```

```text title="実行結果"
1
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | ジェネリックなコードで、範囲を扱う |

## よくあるミス

??? failure "`std::` の同名の関数と混ぜる"
    `std::cbegin` とは別物です。`ranges::` 版は、範囲に必要な条件を満たさない型を、早めに弾いてくれます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`cend`](cend.md) | 対になる関数 |
| [`std::ranges::begin`](begin.md) | 先頭 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 範囲の先頭を指す、const のイテレータを返す
    - [x] 配列・コンテナ・view に同じ書き方で使える
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::ranges::cbegin](https://cpprefjp.github.io/reference/ranges/cbegin.html)
- [cppreference: std::ranges::cbegin](https://en.cppreference.com/w/cpp/ranges/cbegin)
