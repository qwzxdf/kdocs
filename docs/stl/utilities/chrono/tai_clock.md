---
title: std::chrono::tai_clock
summary: "うるう秒を含まず、連続して進む国際原子時（TAI）の時計。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::tai_clock

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

国際原子時（TAI）は、原子時計が刻む、うるう秒のない連続した時間です。UTC は TAI に、うるう秒で調整を加えたもので、現在（2026 年）は、TAI のほうが UTC より 37 秒進んでいます。`std::chrono::tai_clock` は、この TAI を刻む時計です。

!!! tip "ポイント"
    - 起点は 1958-01-01 00:00:00 TAI。UTC とは 10 秒の初期差がある
    - うるう秒がなく、連続して進む。1 日はいつも 86400 秒
    - `utc_clock` とは `clock_cast` で変換する
    - 科学技術向け。ゲームでは使わない

!!! info "このページを読む前に"
    [`utc_clock`](utc_clock.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::tai_clock {#tai_clock}

<span class="ver ver-20">C++20</span>

```cpp
class tai_clock {
 public:
  using duration = chrono::duration<rep, period>;
  using time_point = chrono::time_point<tai_clock>;
  static constexpr bool is_steady = false;

  static time_point now();
  static utc_time<common_type_t<Duration, seconds>> to_utc(const tai_time<Duration>& t);
  static tai_time<common_type_t<Duration, seconds>> from_utc(const utc_time<Duration>& t);
};
```

TAI と UTC の差は、1972 年 1 月 1 日に 10 秒で始まり、うるう秒が入るたびに 1 秒ずつ広がりました。2017 年以降は 37 秒です。

起点は 1958-01-01 です。`tai_clock` の 1970-01-01 の値は、12 年ぶんの秒数に初期差の 10 秒を足した 378691210 秒です。

`to_utc` と `from_utc` で、`utc_clock` と変換します。`sys_time` とは、`utc_clock` を経由して、`clock_cast` で一度に変換できます。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  // 1970-01-01 UTC は、TAI の起点 (1958-01-01) から何秒か
  const tai_seconds t = clock_cast<tai_clock>(sys_seconds{});
  std::println("1970-01-01 の TAI: {} 秒", t.time_since_epoch().count());

  // 2026-01-01 では、TAI は UTC より何秒進んでいるか
  const sys_seconds s = sys_days{2026y / January / 1};
  const tai_seconds a = clock_cast<tai_clock>(s);
  const seconds since_1970 = a.time_since_epoch() - seconds{378691200};
  std::println("TAI - sys: {} 秒", (since_1970 - s.time_since_epoch()).count());
}
```

```text title="実行結果"
1970-01-01 の TAI: 378691210 秒
TAI - sys: 37 秒
```

`378691200` は 1958-01-01 から 1970-01-01 までの 12 年ぶんの日数（4383 日）を秒にした値です。2026 年の TAI は、`system_clock` より 37 秒進んでいます。

## ゲームでの使いどころ

使いません。うるう秒の影響を受けない、連続した時間が要る科学計算で使います。

## よくあるミス

??? failure "TAI を UTC と同じだと思う"
    現在は 37 秒の差があります。UTC の日付と時刻に直すには、`clock_cast` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`utc_clock`](utc_clock.md) | うるう秒を数える |
| [`gps_clock`](gps_clock.md) | TAI より 19 秒遅れた GPS の時間 |
| [`system_clock`](system_clock.md) | うるう秒を数えない、日常の時計 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: tai_clock](https://cpprefjp.github.io/reference/chrono/tai_clock.html)
- [cppreference: std::chrono::tai_clock](https://en.cppreference.com/w/cpp/chrono/tai_clock)
