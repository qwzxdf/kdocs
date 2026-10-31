---
title: std::chrono::gps_time
summary: "gps_clock の時点（単位を選べる）を表す別名。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::gps_time

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

`std::chrono::gps_time<Duration>` は、`gps_clock` の時点を `Duration` の単位で表す型です。`time_point<gps_clock, Duration>` の別名で、GPS 時の秒やミリ秒を持つのに使います。

!!! tip "ポイント"
    - `time_point<gps_clock, Duration>` の別名
    - 起点は 1980-01-06 00:00:00 UTC
    - 秒の単位は `gps_seconds`
    - `clock_cast` で他の時計と変換する

!!! info "このページを読む前に"
    [`gps_clock`](gps_clock.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::gps_time {#gps_time}

<span class="ver ver-20">C++20</span>

```cpp
template <class Duration>
using gps_time = time_point<gps_clock, Duration>;
using gps_seconds = gps_time<seconds>;
```

GPS 時は、週番号と週の中の秒で表されることが多いです。`gps_time` の値を 7 日で割れば、週番号が求まります。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  const gps_seconds g = clock_cast<gps_clock>(sys_seconds{sys_days{2026y / January / 1}});
  const weeks w = duration_cast<weeks>(g.time_since_epoch());
  std::println("GPS 週番号: {}", w.count());
}
```

```text title="実行結果"
GPS 週番号: 2399
```

GPS の起点から、2026 年 1 月 1 日までは、2399 週が経過しています。

## ゲームでの使いどころ

使いません。

## よくあるミス

??? failure "sys_time と直接比べる"
    型が違い、起点も違います。`clock_cast` で変換します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`gps_seconds`](gps_seconds.md) | 秒の単位 |
| [`tai_time`](tai_time.md) | TAI の時点 |
| [`utc_time`](utc_time.md) | UTC の時点 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: gps_time](https://cpprefjp.github.io/reference/chrono/gps_clock.html)
- [cppreference: std::chrono::gps_time](https://en.cppreference.com/w/cpp/chrono/gps_clock)
