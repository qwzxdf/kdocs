---
title: std::chrono::local_days
summary: "ローカル時刻を、日の単位で表す別名（地域のカレンダーの日付）。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::local_days

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

`time_point<system_clock, seconds>` のように毎回書くのは長いので、標準が別名を用意しています。`std::chrono::local_days` は、ローカル時刻を日の単位で表す別名（地域のカレンダーの日付）です。

!!! tip "ポイント"
    - 中身は `local_time<days>`。
    - `time_since_epoch().count()` で基準時刻からの経過を数で取れる。
    - カレンダー型（`year_month_day`）と相互に変換できる。

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要と [`duration`](duration.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::local_days {#local_days}

```cpp
using local_days = local_time<days>;
```

- 戻り値: `local_days` の値
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;
  std::chrono::local_days d{2024y / std::chrono::January / 1};
  std::println("{}", d.time_since_epoch().count());
}
```

```text title="実行結果"
19723
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 時刻を型で区別する | `std::chrono::local_days` |

## よくあるミス

??? failure "ローカル時刻とシステム時刻を混ぜる"
    `local_time` は地域の時刻、`sys_time` は UTC 基準の時刻で、型が別です。変換は `zoned_time` や `time_zone` を通します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`time_point`](time_point.md) | 時点の型 |
| [`zoned_time`](zoned_time.md) | タイムゾーンつきの時刻 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ローカル時刻を日の単位で表す別名（地域のカレンダーの日付）
    - [x] time_since_epoch() で経過を取る
    - [x] 型で時計の種類を区別する

## 関連ページ

- [cpprefjp: std::chrono::local_days](https://cpprefjp.github.io/reference/chrono/time_point.html)
- [cppreference: std::chrono::local_days](https://en.cppreference.com/w/cpp/chrono/time_point)
