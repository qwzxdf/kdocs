---
title: std::chrono::gps_seconds
summary: "gps_clock の時点（秒単位）を表す別名。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::gps_seconds

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

`std::chrono::gps_seconds` は、`gps_clock` の時点を秒の単位で表す型で、`gps_time<seconds>` の別名です。

!!! tip "ポイント"
    - `gps_time<seconds>` の別名
    - 起点は 1980-01-06 00:00:00 UTC で、そのときの値は 0
    - `clock_cast<gps_clock>(sys_seconds)` で変換する
    - 書式にかけると、GPS 時の日付と時刻が出る

!!! info "このページを読む前に"
    [`gps_time`](gps_time.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::gps_seconds {#gps_seconds}

<span class="ver ver-20">C++20</span>

```cpp
using gps_seconds = gps_time<seconds>;
```

書式にかけると、GPS 時で表示されます。2026-01-01 00:00:00 UTC は、GPS 時では 2026-01-01 00:00:18 です。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  const sys_seconds s = sys_days{2026y / January / 1};
  const gps_seconds g = clock_cast<gps_clock>(s);

  std::println("sys: {:%F %T}", s);
  std::println("gps: {:%F %T}", g);
}
```

```text title="実行結果"
sys: 2026-01-01 00:00:00
gps: 2026-01-01 00:00:18
```

## ゲームでの使いどころ

使いません。

## よくあるミス

??? failure "表示が UTC と同じになると思う"
    18 秒進んだ値で表示されます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`gps_time`](gps_time.md) | 単位を選べる元の別名 |
| [`tai_seconds`](tai_seconds.md) | TAI の秒 |
| [`utc_seconds`](utc_seconds.md) | UTC の秒 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: gps_seconds](https://cpprefjp.github.io/reference/chrono/gps_clock.html)
- [cppreference: std::chrono::gps_seconds](https://en.cppreference.com/w/cpp/chrono/gps_clock)
