---
title: std::lldiv
summary: "long long の割り算で、商と余りをいっしょに返す。"
order: 900
tags:
  - 数値
---

# std::lldiv

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdlib>`
</div>

`ldiv` の `long long` 版です。

!!! tip "ポイント"
    - C 由来の関数。
    - 失敗の知らせ方は関数ごとに違う。
    - 新しいコードでは `std::from_chars` や `std::string` が安全。

!!! info "このページを読む前に"
    [`std::atoi`](atoi.md) を先に読んでください。

## 関数の詳しい説明

### std::lldiv {#lldiv}

```cpp
lldiv_t lldiv(long long x, long long y);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x, y` | long long | 割られる数・割る数 |

- 戻り値: `quot`（商）と `rem`（余り）をもつ構造体
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <print>

int main() {
  auto r = std::lldiv(7LL, 2LL);
  std::println("{} {}", r.quot, r.rem);
}
```

```text title="実行結果"
3 1
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 64 ビット整数の商と余り |

## よくあるミス

??? failure "0 で割る"
    y が 0 だと未定義動作です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`div`](div.md) | int の版 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] long long の割り算で、商と余りをいっしょに返す
    - [x] C 由来の関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::lldiv](https://cpprefjp.github.io/reference/cstdlib/lldiv.html)
- [cppreference: std::lldiv](https://en.cppreference.com/w/cpp/c/lldiv)
