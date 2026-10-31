---
title: std::chrono::tai_time
summary: "tai_clock の時点（単位を選べる）を表す別名。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::tai_time

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

`std::chrono::tai_time<Duration>` は、`tai_clock` の時点を `Duration` の単位で表す型です。`time_point<tai_clock, Duration>` の別名です。TAI は連続した時間なので、2 つの時点の差は、うるう秒に左右されない、純粋な経過時間になります。

!!! tip "ポイント"
    - `time_point<tai_clock, Duration>` の別名
    - 起点は 1958-01-01 00:00:00 TAI
    - 差はうるう秒に影響されない
    - 秒の単位は `tai_seconds`

!!! info "このページを読む前に"
    [`tai_clock`](tai_clock.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::tai_time {#tai_time}

<span class="ver ver-20">C++20</span>

```cpp
template <class Duration>
using tai_time = time_point<tai_clock, Duration>;
using tai_seconds = tai_time<seconds>;
```

`clock_cast<tai_clock>(sys_time)` で、`sys_time` から変換できます。うるう秒が挟まる期間でも、TAI の差は、本当の経過時間と一致します。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  // うるう秒を挟む 2 秒間
  const sys_seconds before = sys_days{2016y / December / 31} + 23h + 59min + 59s;
  const sys_seconds after = before + 2s;

  const tai_seconds tb = clock_cast<tai_clock>(before);
  const tai_seconds ta = clock_cast<tai_clock>(after);
  std::println("TAI の差: {} 秒", (ta - tb).count());
}
```

```text title="実行結果"
TAI の差: 3 秒
```

`sys_time` では 2 秒でも、うるう秒が間に入るので、TAI の差は 3 秒です。

## ゲームでの使いどころ

使いません。

## よくあるミス

??? failure "sys_time と同じ値だと思う"
    TAI は UTC より 37 秒進み、起点も違います。直接比べず、`clock_cast` で変換します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`tai_seconds`](tai_seconds.md) | 秒の単位 |
| [`utc_time`](utc_time.md) | UTC の時点 |
| [`gps_time`](gps_time.md) | GPS の時点 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: tai_time](https://cpprefjp.github.io/reference/chrono/tai_clock.html)
- [cppreference: std::chrono::tai_time](https://en.cppreference.com/w/cpp/chrono/tai_clock)
