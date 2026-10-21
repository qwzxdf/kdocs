---
title: <climits>（整数の限界マクロ）
summary: "`INT_MAX` など、整数型の最大値・最小値を表す C 由来のマクロ。"
order: 30
tags:
  - 数値
---

# <climits>（整数の限界マクロ）

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <climits>`
</div>

`<climits>` は、**整数型の最大値・最小値・ビット数を表すマクロ**を定義するヘッダーです。`INT_MAX`、`INT_MIN`、`UINT_MAX`、`CHAR_BIT`（1 バイトのビット数）などがあります。C++ では、型安全な [`std::numeric_limits`](limits.md) が代わりに使えます。

!!! tip "ポイント"
    - `INT_MAX` は 2147483647（32 ビット `int`）。
    - `CHAR_BIT` は 8。
    - 新しいコードでは `std::numeric_limits<int>::max()` が型安全。

## 関数の詳しい説明

### <climits> {#climits}

```cpp
#define INT_MAX 2147483647
#define INT_MIN (-INT_MAX - 1)
#define CHAR_BIT 8
```

- 戻り値: 定数
- 計算量: コンパイル時

```cpp
#include <climits>
#include <print>

int main() {
  std::println("{} {}", INT_MAX, CHAR_BIT);
}
```

```text title="実行結果"
2147483647 8
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| C のライブラリの定数をそのまま使う | `INT_MAX` |

## よくあるミス

??? failure "マクロの min / max と混同する"
    Windows の `min` / `max` マクロとは別です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::numeric_limits`](limits.md) | 型安全な代わり |
| [`cfloat`](cfloat.md) | 小数の限界 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 整数の限界マクロ
    - [x] 型安全なのは numeric_limits
    - [x] C 由来

## 関連ページ

- [cpprefjp: <climits>（整数の限界マクロ）](https://cpprefjp.github.io/reference/climits.html)
- [cppreference: <climits>（整数の限界マクロ）](https://en.cppreference.com/w/cpp/types/climits)
