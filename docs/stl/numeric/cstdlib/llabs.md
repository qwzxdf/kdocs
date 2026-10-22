---
title: std::llabs
summary: "long long の絶対値を返す。"
order: 900
tags:
  - 数値
---

# std::llabs

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdlib>`
</div>

64 ビット整数（`long long`）の絶対値を求める関数です。

!!! tip "ポイント"
    - C 由来の関数。
    - 失敗の知らせ方は関数ごとに違う。
    - 新しいコードでは `std::from_chars` や `std::string` が安全。

!!! info "このページを読む前に"
    [`std::atoi`](atoi.md) を先に読んでください。

## 関数の詳しい説明

### std::llabs {#llabs}

```cpp
long long llabs(long long n);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `n` | long long | 絶対値を求める値 |

- 戻り値: `|n|`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <print>

int main() {
  std::println("{}", std::llabs(-5LL));
}
```

```text title="実行結果"
5
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 64 ビット整数の差の大きさ |

## よくあるミス

??? failure "最小値の絶対値"
    `LLONG_MIN` の絶対値は表せず、未定義動作です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`abs`](../cmath/abs.md) | 型を選ぶ版 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] long long の絶対値を返す
    - [x] C 由来の関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::llabs](https://cpprefjp.github.io/reference/cstdlib/llabs.html)
- [cppreference: std::llabs](https://en.cppreference.com/w/cpp/c/llabs)
