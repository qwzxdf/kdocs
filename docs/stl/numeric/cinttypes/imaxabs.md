---
title: std::imaxabs
summary: "`intmax_t` の絶対値を返す。"
order: 900
tags:
  - 数値
---

# std::imaxabs

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cinttypes>`
</div>

最も大きい符号つき整数型（`intmax_t`）の絶対値を求める関数です。`std::abs` で足りるので、ほとんど使いません。

!!! tip "ポイント"
    - `<cinttypes>` の関数。
    - `intmax_t` / `uintmax_t` を扱う。
    - 新しいコードでは `std::from_chars` が安全。

!!! info "このページを読む前に"
    [`<cstdint>`](../cstdint.md) を先に読んでください。

## 関数の詳しい説明

### std::imaxabs {#imaxabs}

```cpp
std::intmax_t imaxabs(std::intmax_t n);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `n` | intmax_t | 絶対値を求める値 |

- 戻り値: `|n|`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cinttypes>
#include <print>

int main() {
  std::println("{}", std::imaxabs(-5));
}
```

```text title="実行結果"
5
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 最大幅の整数の扱い |

## よくあるミス

??? failure "範囲外を確かめない"
    `INTMAX_MIN` の絶対値は表せず、未定義動作です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`cstdint`](../cstdint.md) | 固定幅の整数型 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `intmax_t` の絶対値を返す
    - [x] `<cinttypes>` の関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::imaxabs](https://cpprefjp.github.io/reference/cinttypes/imaxabs.html)
- [cppreference: std::imaxabs](https://en.cppreference.com/w/cpp/c/imaxabs)
