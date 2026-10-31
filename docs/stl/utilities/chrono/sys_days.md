---
title: std::chrono::sys_days
summary: "system_clock の時点を、日の単位で表す別名（カレンダーの日付）。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::sys_days

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

`2026y / March / 9` は、年月日の組ですが、「3 月 9 日が 1970 年から数えて何日目か」とは別の表現です。`std::chrono::sys_days` は、`system_clock` の時点を日の単位で表す型で、カレンダーの日付を「日数」として扱うのに使います。日付の足し引き、曜日の計算、`year_month_day` との相互変換の中継点です。

!!! tip "ポイント"
    - `sys_time<days>` の別名。日付を 1970-01-01 からの日数で持つ
    - `year_month_day` から暗黙に変換できる。`sys_days{ymd}`
    - 日数の足し引きは `+ days{n}`。2 つの差は `days`
    - 曜日は `weekday{sys_days}` で求まる

!!! info "このページを読む前に"
    [`sys_time`](sys_time.md) と [`year_month_day`](year_month_day.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::sys_days {#sys_days}

<span class="ver ver-20">C++20</span>

```cpp
using sys_days = sys_time<days>;
```

`year_month_day`、`year_month_weekday`、`year_month_day_last` などは、すべて `sys_days` に変換できます。日数に直せば、足し算と引き算が、普通の整数の計算になります。

```cpp
const sys_days a = 2026y / January / 1;
const sys_days b = 2026y / March / 1;
const days diff = b - a;     // 59 日
```

日付の計算は、`sys_days` に直して行い、結果を `year_month_day` に戻して取り出します。月や年を足すときだけは、`year_month_day` の側で行います。

曜日は、`weekday{d}` で求まります。`weekday{sys_days{2026y/January/1}}` は木曜日です。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  const sys_days a = 2026y / January / 1;
  const sys_days b = 2026y / March / 1;
  std::println("1/1 から 3/1 まで: {} 日", (b - a).count());

  // 100 日後の日付
  const year_month_day later{a + days{100}};
  std::println("100 日後: {}-{:02}-{:02}", static_cast<int>(later.year()),
               static_cast<unsigned>(later.month()), static_cast<unsigned>(later.day()));

  // 曜日
  std::println("1/1 は木曜: {}", weekday{a} == Thursday);
}
```

```text title="実行結果"
1/1 から 3/1 まで: 59 日
100 日後: 2026-04-11
1/1 は木曜: true
```

## ゲームでの使いどころ

連続ログインの日数や、期限までの日数の計算に使います。2 つの日付の差が `days` で出るので、`/ 86400` の計算が要りません。

## よくあるミス

??? failure "ローカルの日付にそのまま使う"
    `sys_days` は UTC の日付です。日本時間の 0 時は、UTC では前日の 15 時です。ローカルの日付は `local_days` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`local_days`](local_days.md) | タイムゾーンなしの地域の日付 |
| [`year_month_day`](year_month_day.md) | 年月日の組 |
| [`sys_time`](sys_time.md) | 単位を選べる元の別名 |
| [`days`](days.md) | 日数（期間）の型 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: sys_days](https://cpprefjp.github.io/reference/chrono/system_clock.html)
- [cppreference: std::chrono::sys_days](https://en.cppreference.com/w/cpp/chrono/system_clock)
