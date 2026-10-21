---
title: std::chrono::year_month_day
summary: "カレンダーの日付（年・月・日）。曜日や日数の計算もできる。"
order: 9
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::year_month_day

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

`std::chrono::year_month_day` は、**年・月・日からなるカレンダーの日付**を表すクラスです。`2026y / October / 21` のようなスラッシュ区切りで書けます。`sys_days`（1970-01-01 からの日数）に変換すると、日数の足し引きや曜日の判定ができます。セーブデータの日付、ログイン日数の判定などに使います。

!!! tip "ポイント"
    - 書き方は `2026y / October / 21` または `2026y / 10 / 21`。
    - 日数の計算は `std::chrono::sys_days` に変換して行い、`year_month_day` に戻す。
    - 曜日は `std::chrono::weekday{sys_days}`。
    - 存在しない日付（2 月 30 日）は `ok()` が `false`。

!!! info "このページを読む前に"
    [`std::chrono`](../chrono.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::chrono::year_month_day {#year_month_day}

```cpp
class year_month_day {
 public:
  constexpr year_month_day(const year&, const month&, const day&) noexcept;
  constexpr year_month_day(const sys_days&) noexcept;   // 日数から
  constexpr operator sys_days() const noexcept;         // 日数へ
  constexpr bool ok() const noexcept;
};
```

- 戻り値: （クラス）。`year()`、`month()`、`day()` で各部分を取り出せる
- 計算量: O(1)

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;
  using namespace std::chrono_literals;

  year_month_day d = 2026y / October / 21;
  std::println("{}", d);

  sys_days sd = d;                                       // 日数に変換
  std::println("{}", weekday{sd});                       // 曜日
  std::println("{}", year_month_day{sd + days{30}});     // 30 日後
  std::println("{}", year_month_day{2026y / February / 30}.ok());  // 存在しない日付
}
```

```text title="実行結果"
2026-10-21
Wed
2026-11-20
false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ログインボーナスの「連続日数」の判定 | 前回の `sys_days` との差が 1 日か |
| セーブデータの日付表示 | `year_month_day{floor<days>(system_clock::now())}` |
| 毎週水曜日のイベント | `weekday{sd} == Wednesday` |

## よくあるミス

??? failure "日数の足し算を年月日のまま行う"
    `d + days{30}` はできません。`sys_days` に変換してから足し、`year_month_day` に戻します。

??? failure "古いコンパイラで使えない"
    カレンダーの機能は C++20 で、GCC 11 / MSVC 19.29 以降です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`system_clock`](system_clock.md) | 今の時刻 |
| [`zoned_time`](zoned_time.md) | タイムゾーンつき |
| `std::time_t` / `std::localtime` | C 由来の日付（古い書き方） |

## コンパイラ対応

C++20 の機能です。GCC 11 / Clang 16 / MSVC 19.29（VS 2019 16.10）以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] カレンダーの日付を表す
    - [x] 日数の計算は `sys_days` に変換して
    - [x] 曜日は `weekday`

## 関連ページ

- [cpprefjp: std::chrono::year_month_day](https://cpprefjp.github.io/reference/chrono/year_month_day.html)
- [cppreference: std::chrono::year_month_day](https://en.cppreference.com/w/cpp/chrono/year_month_day)
