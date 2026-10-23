---
title: std::ranges::ssize
summary: "範囲の要素数を、符号付きの整数で返す。"
order: 900
group: ranges の基本部品
tags:
  - 型・言語サポート
---

# std::ranges::ssize

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

`size()` は符号なしなので、`size() - 1` のような計算が桁あふれ（0 のときに大きな値）を起こします。`ranges::ssize(r)` は、符号付きの整数で返すので、この問題を避けられます。

!!! tip "ポイント"
    - 配列・コンテナ・view に同じ書き方で使える。
    - 関数ではなく、関数オブジェクト（カスタマイズポイント）。
    - 使えない型には、コンパイルエラーになる。

!!! info "このページを読む前に"
    [`std::ranges::begin`](begin.md) を先に読んでください。

## 関数の詳しい説明

### std::ranges::ssize {#ssize}

```cpp
inline constexpr /* カスタマイズポイント */ ranges::ssize;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `t` | 範囲 | 対象の範囲 |

- 戻り値: 符号付きの要素数
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3};
  std::println("{}", std::ranges::ssize(v));
}
```

```text title="実行結果"
3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | ジェネリックなコードで、範囲を扱う |

## よくあるミス

??? failure "`std::` の同名の関数と混ぜる"
    `std::ssize` とは別物です。`ranges::` 版は、範囲に必要な条件を満たさない型を、早めに弾いてくれます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`size`](size.md) | 対になる関数 |
| [`std::ranges::begin`](begin.md) | 先頭 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 範囲の要素数を、符号付きの整数で返す
    - [x] 配列・コンテナ・view に同じ書き方で使える
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::ranges::ssize](https://cpprefjp.github.io/reference/ranges/ssize.html)
- [cppreference: std::ranges::ssize](https://en.cppreference.com/w/cpp/ranges/ssize)
