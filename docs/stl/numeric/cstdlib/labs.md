---
title: std::labs
summary: "long の絶対値を返す。"
order: 900
tags:
  - 数値
---

# std::labs

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdlib>`
</div>

`abs` は引数の型に合わせた版を選びます。`long` の絶対値を明示的に求めたいとき、`labs` が使えます。

!!! tip "ポイント"
    - C 由来の関数。
    - 失敗の知らせ方は関数ごとに違う。
    - 新しいコードでは `std::from_chars` や `std::string` が安全。

!!! info "このページを読む前に"
    [`std::atoi`](atoi.md) を先に読んでください。

## 関数の詳しい説明

### std::labs {#labs}

```cpp
long labs(long n);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `n` | long | 絶対値を求める値 |

- 戻り値: `|n|`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <print>

int main() {
  std::println("{}", std::labs(-5L));
}
```

```text title="実行結果"
5
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 長整数の差の大きさ |

## よくあるミス

??? failure "最小値の絶対値"
    `LONG_MIN` の絶対値は表せず、未定義動作です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`abs`](../cmath/abs.md) | 型を選ぶ版 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] long の絶対値を返す
    - [x] C 由来の関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::labs](https://cpprefjp.github.io/reference/cstdlib/labs.html)
- [cppreference: std::labs](https://en.cppreference.com/w/cpp/c/labs)
