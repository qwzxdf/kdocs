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

秒だけでは足りない細かい時刻や時間を、C の API とやり取りするときに使う構造体です。`tv_sec`（秒）と `tv_nsec`（ナノ秒）の 2 つのメンバをもちます。

!!! tip "ポイント"
    - `tv_sec` は秒、`tv_nsec` は 0〜999,999,999 のナノ秒。
    - `timespec_get` の結果を受ける。
    - POSIX の API（`nanosleep` など）とも共通。

!!! info "このページを読む前に"
    [`std::time`](time.md) を先に読んでください。

## 関数の詳しい説明

### std::timespec {#timespec}

```cpp
struct timespec {
  std::time_t tv_sec;  // 秒
  long tv_nsec;        // ナノ秒（0〜999,999,999）
};
```

- 戻り値: なし（構造体）
- 計算量: なし


## 実際に動かしてみる

```cpp
#include <ctime>
#include <print>

int main() {
  std::timespec ts{1, 500000000};
  std::println("{} {}", ts.tv_sec, ts.tv_nsec);
}
```

```text title="実行結果"
1 500000000
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ナノ秒単位の時刻を受ける | `std::timespec ts;` |

## よくあるミス

??? failure "ナノ秒が 10 億以上"
    `tv_nsec` は 1 秒未満の範囲に収めます。あふれた分は `tv_sec` に繰り上げます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`timespec_get`](timespec_get.md) | 現在時刻を取得する |
| [`std::chrono::duration`](../../utilities/chrono/duration.md) | C++ の時間の型 |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 秒 + ナノ秒の構造体
    - [x] tv_sec と tv_nsec
    - [x] timespec_get が使う

## 関連ページ

- [cpprefjp: std::timespec](https://cpprefjp.github.io/reference/ctime/timespec.html)
- [cppreference: std::timespec](https://en.cppreference.com/w/cpp/chrono/c/timespec)
