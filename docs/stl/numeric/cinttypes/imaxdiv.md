---
title: std::imaxdiv
summary: "`intmax_t` の割り算で、商と余りをいっしょに返す。"
order: 900
tags:
  - 数値
---

# std::imaxdiv

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cinttypes>`
</div>

`div`・`ldiv` の `intmax_t` 版です。

!!! tip "ポイント"
    - `<cinttypes>` の関数。
    - `intmax_t` / `uintmax_t` を扱う。
    - 新しいコードでは `std::from_chars` が安全。

!!! info "このページを読む前に"
    [`<cstdint>`](../cstdint.md) を先に読んでください。

## 関数の詳しい説明

### std::imaxdiv {#imaxdiv}

```cpp
std::imaxdiv_t imaxdiv(std::intmax_t x, std::intmax_t y);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x, y` | intmax_t | 割られる数・割る数 |

- 戻り値: `quot`（商）と `rem`（余り）をもつ構造体
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cinttypes>
#include <print>

int main() {
  auto r = std::imaxdiv(7, 2);
  std::println("{} {}", r.quot, r.rem);
}
```

```text title="実行結果"
3 1
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
    - [x] `intmax_t` の割り算で、商と余りをいっしょに返す
    - [x] `<cinttypes>` の関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::imaxdiv](https://cpprefjp.github.io/reference/cinttypes/imaxdiv.html)
- [cppreference: std::imaxdiv](https://en.cppreference.com/w/cpp/c/imaxdiv)
