---
title: std::difftime
summary: "2 つの time_t の差を、秒（double）で返す。"
order: 900
tags:
  - 入出力・文字列
---

# std::difftime

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <ctime>`
</div>

`time_t` は整数とは限らず、単位も処理系ごとに違うことがあります。時刻の差を安全に秒で求めるには、引き算ではなく `std::difftime` を使います。

!!! tip "ポイント"
    - 戻り値は秒（`double`）。
    - `end - start` の順で渡す（`difftime(end, start)`）。
    - ゲームの経過時間は [`steady_clock`](../../utilities/chrono/steady_clock.md) が正確。

!!! info "このページを読む前に"
    [`std::time`](time.md) を先に読んでください。

## 関数の詳しい説明

### std::difftime {#difftime}

```cpp
double difftime(std::time_t time_end, std::time_t time_beg);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `time_end` | time_t | 新しいほうの時刻 |
| `time_beg` | time_t | 古いほうの時刻 |

- 戻り値: 秒数（`double`）
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <ctime>
#include <print>

int main() {
  std::time_t a = 100;
  std::time_t b = 40;
  std::println("{}", std::difftime(a, b));
}
```

```text title="実行結果"
60
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| セーブデータの経過日数 | `std::difftime(now, saved) / 86400` |

## よくあるミス

??? failure "引数の順を逆にする"
    `difftime(a, b)` は `a - b` です。新しいほうを先に渡します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`time`](time.md) | 今の時刻 |
| [`steady_clock`](../../utilities/chrono/steady_clock.md) | 精度のよい計測 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] time_t の差を秒で返す
    - [x] 第 1 引数 - 第 2 引数
    - [x] 計測には steady_clock

## 関連ページ

- [cpprefjp: std::difftime](https://cpprefjp.github.io/reference/ctime/difftime.html)
- [cppreference: std::difftime](https://en.cppreference.com/w/cpp/chrono/c/difftime)
