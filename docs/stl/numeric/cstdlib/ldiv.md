---
title: std::ldiv
summary: "long の割り算で、商と余りをいっしょに返す。"
order: 900
tags:
  - 数値
---

# std::ldiv

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdlib>`
</div>

`/` と `%` を別々に書くと、割り算が 2 回行われることがあります。`ldiv` は 1 回で商と余りを構造体で返します。

!!! tip "ポイント"
    - C 由来の関数。
    - 失敗の知らせ方は関数ごとに違う。
    - 新しいコードでは `std::from_chars` や `std::string` が安全。

!!! info "このページを読む前に"
    [`std::atoi`](atoi.md) を先に読んでください。

## 関数の詳しい説明

### std::ldiv {#ldiv}

```cpp
ldiv_t ldiv(long x, long y);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x, y` | long | 割られる数・割る数 |

- 戻り値: `quot`（商）と `rem`（余り）をもつ構造体
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <print>

int main() {
  auto r = std::ldiv(7L, 2L);
  std::println("{} {}", r.quot, r.rem);
}
```

```text title="実行結果"
3 1
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 商と余りを同時に使う |

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
    - [x] long の割り算で、商と余りをいっしょに返す
    - [x] C 由来の関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::ldiv](https://cpprefjp.github.io/reference/cstdlib/ldiv.html)
- [cppreference: std::ldiv](https://en.cppreference.com/w/cpp/c/ldiv)
