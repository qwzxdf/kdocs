---
title: std::chrono::year_month_weekday
summary: "「その年のその月の第 n 曜日」を表す型。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::year_month_weekday

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

`2026y / March / Monday[2]` は、2026 年 3 月の第 2 月曜日、つまり 3 月 9 日です。年、月、曜日と回数を組にした `std::chrono::year_month_weekday` は、暦の上の日付を、「第 n 曜日」という形で表したものです。`sys_days` に変換すれば、通常の日付として扱えます。

!!! tip "ポイント"
    - `year / month / weekday_indexed` で作る
    - `sys_days` へ変換でき、日付が求まる
    - 逆に、`sys_days` から `year_month_weekday` にすれば、「その日が第何曜日か」が分かる
    - 第 5 の曜日がない月では、`ok()` が偽になる

!!! info "このページを読む前に"
    [`weekday_indexed`](weekday_indexed.md) と [`month_weekday`](month_weekday.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::year_month_weekday {#year_month_weekday}

<span class="ver ver-20">C++20</span>

```cpp
class year_month_weekday {
 public:
  constexpr year_month_weekday(const chrono::year& y, const chrono::month& m,
                               const chrono::weekday_indexed& wdi) noexcept;
  constexpr explicit year_month_weekday(const sys_days& d) noexcept;
  constexpr chrono::year year() const noexcept;
  constexpr chrono::month month() const noexcept;
  constexpr chrono::weekday weekday() const noexcept;
  constexpr unsigned index() const noexcept;
  constexpr bool ok() const noexcept;
  constexpr operator sys_days() const noexcept;
};
```

### 日付への変換 {#to-days}

`sys_days` へ暗黙に変換できます。`sys_days d = 2026y / March / Monday[2];` が書けて、`2026-03-09` が得られます。

### 日付からの変換 {#from-days}

`sys_days` から作る `explicit` のコンストラクターがあります。日付が、その月の第何曜日かを調べられます。

```cpp
const year_month_weekday ymw{sys_days{2026y / March / 9}};
// ymw.index() == 2, ymw.weekday() == Monday
```

### ok の意味 {#ok}

第 5 の曜日が存在しない月で、第 5 を指定すると、`ok()` が偽になります。2026 年 2 月は 28 日までなので、第 5 月曜日がありません。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  // 第 n 曜日 → 日付
  const year_month_weekday ymw = 2026y / March / Monday[2];
  const sys_days d = ymw;
  std::println("{:%F}", d);

  // 日付 → 第 n 曜日
  const year_month_weekday from_date{sys_days{2026y / March / 9}};
  std::println("第 {} 週の月曜日: {}", from_date.index(),
               from_date.weekday() == Monday);

  // 第 5 月曜日が存在するか
  std::println("2026 年 2 月の第 5 月曜日: {}", (2026y / February / Monday[5]).ok());
  std::println("2026 年 3 月の第 5 月曜日: {}", (2026y / March / Monday[5]).ok());
}
```

```text title="実行結果"
2026-03-09
第 2 週の月曜日: true
2026 年 2 月の第 5 月曜日: false
2026 年 3 月の第 5 月曜日: true
```

2026 年 3 月は月曜日が 2、9、16、23、30 日の 5 回あるので、第 5 月曜日が存在します。

## ゲームでの使いどころ

「第 2 土曜日にイベント」の日取りを求めるときに使います。日付から逆算して、「その日は第何曜日か」を調べて、表示に使うこともできます。

## よくあるミス

??? failure "第 5 を ok() で確かめない"
    存在しない日付を `sys_days` に変換すると、結果が無効になります。変換の前に `ok()` を確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`year_month_weekday_last`](year_month_weekday_last.md) | 最後の曜日 |
| [`month_weekday`](month_weekday.md) | 年を含まない |
| [`year_month_day`](year_month_day.md) | 日の数字で指定する |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: year_month_weekday](https://cpprefjp.github.io/reference/chrono/year_month_weekday.html)
- [cppreference: std::chrono::year_month_weekday](https://en.cppreference.com/w/cpp/chrono/year_month_weekday)
