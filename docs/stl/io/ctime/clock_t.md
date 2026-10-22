---
title: std::clock_t
summary: "プロセッサ時間（clock の戻り値）を表す型。"
order: 900
tags:
  - 入出力・文字列
---

# std::clock_t

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <ctime>`
</div>

`std::clock()` が返すのは、プログラムが使ったプロセッサ時間のカウントです。その型が `clock_t` で、秒に直すには `CLOCKS_PER_SEC` で割ります。

!!! tip "ポイント"
    - 算術型（実装定義）。
    - 秒に直すには `CLOCKS_PER_SEC` で割る。
    - 壁時計の時間ではなく CPU 時間。

!!! info "このページを読む前に"
    [`std::time`](time.md) を先に読んでください。

## 関数の詳しい説明

### std::clock_t {#clock_t}

```cpp
using clock_t = /* 算術型（実装定義） */;
```

- 戻り値: なし（型）
- 計算量: なし


## 実際に動かしてみる

```cpp
#include <ctime>
#include <print>
#include <type_traits>

int main() {
  std::println("{}", std::is_arithmetic_v<std::clock_t>);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 処理時間の簡易計測 | `(double)(end - start) / CLOCKS_PER_SEC` |

## よくあるミス

??? failure "壁時計と取り違える"
    スリープ中は進みません。実際の経過時間は `steady_clock` で測ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`clock`](clock.md) | CPU 時間を取る |
| [`CLOCKS_PER_SEC`](clocks_per_sec.md) | 1 秒あたりのカウント |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] clock() の戻り値の型
    - [x] 秒には CLOCKS_PER_SEC で割る
    - [x] CPU 時間

## 関連ページ

- [cpprefjp: std::clock_t](https://cpprefjp.github.io/reference/ctime/clock_t.html)
- [cppreference: std::clock_t](https://en.cppreference.com/w/cpp/chrono/c/clock_t)
