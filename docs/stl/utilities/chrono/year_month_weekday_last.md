---
title: std::chrono::year_month_weekday_last
summary: "「その年のその月の最後の曜日」を表す型。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::year_month_weekday_last

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

「2026 年 11 月の最後の木曜日」を表す型が `std::chrono::year_month_weekday_last` です。`2026y / November / Thursday[last]` と書き、`sys_days` に変換すると、26 日と求まります。第 4 か第 5 かを気にせずに、最終の曜日を指定できます。

!!! tip "ポイント"
    - `year / month / weekday_last` で作る
    - `sys_days` へ変換でき、日付が求まる
    - `weekday()` で曜日を取り出せる
    - 最後の曜日は、どの月にも必ずある。`ok()` は範囲の検査だけ

!!! info "このページを読む前に"
    [`weekday_last`](weekday_last.md) と [`year_month_weekday`](year_month_weekday.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::year_month_weekday_last {#year_month_weekday_last}

<span class="ver ver-20">C++20</span>

```cpp
class year_month_weekday_last {
 public:
  constexpr year_month_weekday_last(const chrono::year& y, const chrono::month& m,
                                    const chrono::weekday_last& wdl) noexcept;
  constexpr chrono::year year() const noexcept;
  constexpr chrono::month month() const noexcept;
  constexpr chrono::weekday weekday() const noexcept;
  constexpr chrono::weekday_last weekday_last() const noexcept;
  constexpr bool ok() const noexcept;
  constexpr operator sys_days() const noexcept;
};
```

`sys_days` へ暗黙に変換できます。`sys_days d = 2026y / November / Thursday[last];` で、その月の最後の木曜日の日付が得られます。

`year_month_weekday`（第 n）と違い、存在しないという事態は起きません。どの曜日も、月に必ず 4 回か 5 回現れるからです。`ok()` が偽になるのは、年・月・曜日が有効な範囲外のときだけです。

月の最後の週の何日かは、`d - last_day_of_month` のような計算で求められます。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  // 2026 年の各月の最後の金曜日（1〜3 月）
  for (const month m : {January, February, March}) {
    const year_month_weekday_last ymwl = 2026y / m / Friday[last];
    const sys_days d = ymwl;
    std::println("{:%F}", d);
  }

  const year_month_weekday_last ymwl = 2026y / November / Thursday[last];
  std::println("曜日は木曜: {}", ymwl.weekday() == Thursday);
}
```

```text title="実行結果"
2026-01-30
2026-02-27
2026-03-27
曜日は木曜: true
```

## ゲームでの使いどころ

「毎月最後の金曜日がボーナス日」のような、月ごとの締めの日を求めるときに使います。

## よくあるミス

??? failure "year_month_weekday の第 5 と取り違える"
    第 5 は存在しない月がありますが、`last` は必ず存在します。最後を指定したいときは `last` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`year_month_weekday`](year_month_weekday.md) | 第 n 曜日 |
| [`month_weekday_last`](month_weekday_last.md) | 年を含まない |
| [`sys_days`](sys_days.md) | 日付を日の単位で表す |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: year_month_weekday_last](https://cpprefjp.github.io/reference/chrono/year_month_weekday_last.html)
- [cppreference: std::chrono::year_month_weekday_last](https://en.cppreference.com/w/cpp/chrono/year_month_weekday_last)
