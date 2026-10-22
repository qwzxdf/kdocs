---
title: RAND_MAX
summary: "rand() が返す最大値のマクロ。"
order: 900
tags:
  - 数値
---

# RAND_MAX

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdlib>`
</div>

`rand()` が返す値は 0 〜 `RAND_MAX` です。この値は処理系によって違います（GCC では約 21 億、Windows の MSVC では 32767）。範囲を狭めるときの割り算で使います。

!!! tip "ポイント"
    - C 由来の関数。
    - 失敗の知らせ方は関数ごとに違う。
    - 新しいコードでは `std::from_chars` や `std::string` が安全。

!!! info "このページを読む前に"
    [`std::atoi`](atoi.md) を先に読んでください。

## 関数の詳しい説明

### RAND_MAX {#rand_max}

```cpp
#define RAND_MAX /* 実装定義 */
```

- 戻り値: `rand()` の最大値
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cstdlib>
#include <print>

int main() {
  std::println("{}", RAND_MAX >= 32767);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | rand() の値を 0.0〜1.0 にする |

## よくあるミス

??? failure "`RAND_MAX` を 32767 だと決めつける"
    環境で違います。必ずマクロを使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`rand`](rand.md) | 乱数を取る |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] rand() が返す最大値のマクロ
    - [x] C 由来の関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: RAND_MAX](https://cpprefjp.github.io/reference/cstdlib/RAND_MAX.html)
- [cppreference: RAND_MAX](https://en.cppreference.com/w/cpp/c/RAND_MAX)
