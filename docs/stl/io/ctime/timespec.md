---
title: std::timespec
summary: "秒とナノ秒の組を表す構造体。"
order: 900
tags:
  - 入出力・文字列
---

# std::timespec

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <ctime>`
</div>

`time_t` は秒までしか表せません。ミリ秒やナノ秒の時刻が要る場面のために、C には、秒とナノ秒の 2 つのフィールドを持つ `timespec` 構造体があります。`std::timespec_get` が、現在時刻をこの形で返します。C++17 からは `std::timespec` として標準に入りました。

!!! tip "ポイント"
    - `tv_sec`（秒）と `tv_nsec`（ナノ秒、0 以上 10 億未満）の 2 つのフィールド
    - ナノ秒が 10 億以上のときは、正規化されていない値になる
    - `time_t` の秒の精度では足りないときに使う。C++ では `chrono` のほうが扱いやすい
    - `timespec_get` が返す

!!! info "このページを読む前に"
    [`std::time`](time.md) を先に読んでください。

## 関数の詳しい説明

### std::timespec {#timespec}

<span class="ver ver-17">C++17</span>

```cpp
struct timespec {
  std::time_t tv_sec;  // 秒
  long tv_nsec;        // ナノ秒 [0, 999999999]
};
```

`tv_sec` は、`time_t` と同じ型の整数で、エポックからの秒数が入ります。`tv_nsec` は、秒未満の部分をナノ秒で表します。取りうる範囲は 0 から 999,999,999 までです。1 秒は 10 億ナノ秒なので、これを超える値は、`tv_sec` に繰り上げる決まりです。

2 つの `timespec` の差は、秒の差とナノ秒の差を別々に計算し、ナノ秒が負になったら、秒から 1 を借ります。ミスしやすいところなので、差を何度も取るなら、関数にまとめるか、`chrono` に変換します。

```cpp
double ToSeconds(const std::timespec& ts) {
  return static_cast<double>(ts.tv_sec) + static_cast<double>(ts.tv_nsec) / 1e9;
}
```

## 実際に動かしてみる

```cpp
#include <ctime>
#include <print>

int main() {
  const std::timespec ts{1, 500'000'000};  // 1 秒 + 5 億ナノ秒 = 1.5 秒

  const double sec = static_cast<double>(ts.tv_sec) +
                     static_cast<double>(ts.tv_nsec) / 1e9;
  std::println("{} 秒", sec);
}
```

```text title="実行結果"
1.5 秒
```

## ゲームでの使いどころ

自分で作ることはまずありません。C の API（POSIX の `clock_gettime`、`nanosleep` など）が、この構造体を受け渡しに使います。Windows のゲームでは、`QueryPerformanceCounter` が同じ役目を持つので、`chrono::steady_clock` に包んで使うことが多いです。

## よくあるミス

??? failure "tv_nsec を秒の小数と間違える"
    `tv_nsec` はナノ秒で、小数部ではありません。0.5 秒は `tv_nsec = 500'000'000` です。

??? failure "差を取るときに、ナノ秒の借りを忘れる"
    `(1, 100) - (0, 900)` を、秒とナノ秒を別に引くと `(1, -800)` になり、`tv_nsec` が負になります。秒から 1 を借りて、`(0, 999'999'200)` にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::time_t`](time_t.md) | 秒だけ |
| [`timespec_get`](timespec_get.md) | 現在時刻を `timespec` で取る |
| [`std::chrono::nanoseconds`](../../utilities/chrono/duration.md) | 型で単位を持つ。計算しやすい |

## コンパイラ対応

C++17 から標準です。MSVC、GCC、Clang とも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `timespec` は、秒（`tv_sec`）とナノ秒（`tv_nsec`）の組
    - [x] `tv_nsec` は 0 以上 10 億未満
    - [x] 差を取るときは借りに注意。`chrono` に変換すると楽

## 関連ページ

- [cpprefjp: std::timespec](https://cpprefjp.github.io/reference/ctime/timespec.html)
- [cppreference: std::timespec](https://en.cppreference.com/w/cpp/chrono/c/timespec)
