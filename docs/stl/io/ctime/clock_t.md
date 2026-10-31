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

`std::clock()` が返す CPU 時間のカウントを受ける型が `std::clock_t` です。単位は秒ではなく「`CLOCKS_PER_SEC` 分の 1 秒」で、`time_t` とは別の型として用意されています。中身は処理系ごとに違い、MSVC では `long`、Linux では `long` が普通です。

!!! tip "ポイント"
    - `clock()` の戻り値の型。単位は `1 / CLOCKS_PER_SEC` 秒
    - 秒ではないので、秒に直すには `CLOCKS_PER_SEC` で割る
    - 引き算した差を使う。1 つの値には意味がない
    - Windows の `long` は 32 ビットなので、約 24 日でカウントがあふれる環境もある

!!! info "このページを読む前に"
    [`std::clock`](clock.md) と [`CLOCKS_PER_SEC`](clocks_per_sec.md) を先に読んでください。

## 関数の詳しい説明

### std::clock_t {#clock_t}

```cpp
using clock_t = /* 実装定義の算術型 */;
```

規格は、「時間を表せる算術型」としか決めていません。`clock()` が使えないときは、`(clock_t)(-1)` が返ります。

型が `long` で 32 ビットの環境では、`CLOCKS_PER_SEC` が 1000 だと、約 24.8 日で最大値に達してあふれます。長時間動かしたまま計測するコードには、向きません。

2 つの `clock_t` の引き算は、同じ型の整数の引き算です。秒にするには、`double` に直してから `CLOCKS_PER_SEC` で割ります。整数のまま割ると、1 秒未満が捨てられます。

## 実際に動かしてみる

```cpp
#include <ctime>
#include <print>
#include <type_traits>

int main() {
  static_assert(std::is_arithmetic_v<std::clock_t>);

  const std::clock_t a = std::clock();
  const std::clock_t b = std::clock();
  const std::clock_t diff = b - a;  // 差を取って使う
  std::println("差は 0 以上: {}", diff >= 0);
}
```

```text title="実行結果"
差は 0 以上: true
```

## ゲームでの使いどころ

古いコードの `clock_t` を読むときに出会います。新しく計測を書くなら、`std::chrono::steady_clock::time_point` を使います。

## よくあるミス

??? failure "clock_t の 1 つの値を、時刻として使う"
    `clock()` の起点は処理系が決めるので、1 つの値には意味がありません。2 回の差を取ります。

??? failure "秒の整数だと思う"
    単位は `1 / CLOCKS_PER_SEC` 秒です。そのまま「秒」として表示すると、1000 倍や 100 万倍の値になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::time_t`](time_t.md) | 時刻（エポックからの秒数） |
| [`CLOCKS_PER_SEC`](clocks_per_sec.md) | `clock_t` を秒に直す単位 |
| [`std::chrono::steady_clock`](../../utilities/chrono/steady_clock.md) | 型で単位を持つ計測用の時計 |

## コンパイラ対応

C 由来の型です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `clock_t` は `clock()` の戻り値の型
    - [x] 単位は `1 / CLOCKS_PER_SEC` 秒。割って秒にする
    - [x] 差を取って使う

## 関連ページ

- [cpprefjp: std::clock_t](https://cpprefjp.github.io/reference/ctime/clock_t.html)
- [cppreference: std::clock_t](https://en.cppreference.com/w/cpp/chrono/c/clock_t)
