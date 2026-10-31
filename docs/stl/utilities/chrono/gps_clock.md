---
title: std::chrono::gps_clock
summary: "GPS の時刻に合わせた時計。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::gps_clock

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

GPS 衛星が配る時刻は、UTC ではなく、GPS 時と呼ばれる独自の時間です。うるう秒を入れず、連続して進みます。`std::chrono::gps_clock` は、この GPS 時を刻む時計で、起点は 1980-01-06 00:00:00 UTC です。TAI より常に 19 秒遅れています。

!!! tip "ポイント"
    - 起点は 1980-01-06 00:00:00 UTC
    - うるう秒を数えない。連続して進む
    - `GPS = TAI - 19 秒` の関係
    - 現在の UTC との差は、挿入されたうるう秒の数（18 秒、2017 年以降）

!!! info "このページを読む前に"
    [`tai_clock`](tai_clock.md) と [`utc_clock`](utc_clock.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::gps_clock {#gps_clock}

<span class="ver ver-20">C++20</span>

```cpp
class gps_clock {
 public:
  using duration = chrono::duration<rep, period>;
  using time_point = chrono::time_point<gps_clock>;
  static constexpr bool is_steady = false;

  static time_point now();
  static utc_time<common_type_t<Duration, seconds>> to_utc(const gps_time<Duration>& t);
  static gps_time<common_type_t<Duration, seconds>> from_utc(const utc_time<Duration>& t);
};
```

GPS 時は 1980 年に UTC と一致して始まり、その後うるう秒が入っても、GPS 時は連続して進みました。そのため、UTC との差は、1980 年以降に挿入されたうるう秒の数（2017 年以降は 18 秒）だけ広がっています。

`to_utc` と `from_utc` で `utc_clock` と変換します。`clock_cast` で `sys_time` からも一度に変換できます。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  // 起点は 1980-01-06
  const gps_seconds start = clock_cast<gps_clock>(sys_seconds{sys_days{1980y / January / 6}});
  std::println("1980-01-06 の GPS: {} 秒", start.time_since_epoch().count());

  // 2026-01-01 では、GPS は sys_time より何秒進んでいるか
  const sys_seconds s = sys_days{2026y / January / 1};
  const gps_seconds g = clock_cast<gps_clock>(s);
  const seconds epoch_to_1970 = sys_days{1980y / January / 6}.time_since_epoch();
  std::println("GPS - sys: {} 秒",
               (g.time_since_epoch() - (s.time_since_epoch() - epoch_to_1970)).count());
}
```

```text title="実行結果"
1980-01-06 の GPS: 0 秒
GPS - sys: 18 秒
```

GPS は、`sys_time` から 1980-01-06 の分を引いたものより、18 秒進んでいます。

## ゲームでの使いどころ

使いません。位置情報を使うアプリで、衛星の時刻を扱うときに出てきます。

## よくあるミス

??? failure "GPS 時を UTC と同じだと思う"
    18 秒の差があります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`tai_clock`](tai_clock.md) | GPS より 19 秒進んでいる |
| [`utc_clock`](utc_clock.md) | うるう秒を数える |
| [`gps_time`](gps_time.md) | GPS の時点を表す別名 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: gps_clock](https://cpprefjp.github.io/reference/chrono/gps_clock.html)
- [cppreference: std::chrono::gps_clock](https://en.cppreference.com/w/cpp/chrono/gps_clock)
