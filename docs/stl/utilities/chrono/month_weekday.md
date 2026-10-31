---
title: std::chrono::month_weekday
summary: "「その月の第 n 曜日」を表す型（年を問わない）。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::month_weekday

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

「3 月の第 2 月曜日」のように、年を問わず、毎年同じ規則で決まる日を表すのが `std::chrono::month_weekday` です。`March / Monday[2]` と書き、月と、`weekday_indexed` の組になっています。年を決めると、実際の日付が決まります。

!!! tip "ポイント"
    - `month / weekday_indexed` で作る
    - 年を含まないので、具体的な日付ではない。`year / month_weekday` で日付になる
    - `month()` と `weekday_indexed()` で、各部分を取り出せる
    - `ok()` は、月と曜日と回数が有効かだけを調べる

!!! info "このページを読む前に"
    [`weekday_indexed`](weekday_indexed.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::month_weekday {#month_weekday}

<span class="ver ver-20">C++20</span>

```cpp
class month_weekday {
 public:
  constexpr month_weekday(const chrono::month& m,
                          const chrono::weekday_indexed& wdi) noexcept;
  constexpr chrono::month month() const noexcept;
  constexpr chrono::weekday_indexed weekday_indexed() const noexcept;
  constexpr bool ok() const noexcept;
};
```

`March / Monday[2]` が、`month_weekday{March, Monday[2]}` と同じです。

`ok()` は、月が 1〜12、曜日が有効、回数が 1〜5 の範囲かを調べます。実際に存在するかは、年が決まらないと分かりません。

年と組み合わせるには、`2026y / mw` と書きます。`year_month_weekday` が得られ、`sys_days` に変換して日付にできます。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  // 毎年 3 月の第 2 月曜日
  const month_weekday mw = March / Monday[2];
  std::println("{}", mw.ok());

  // 年ごとに日付が変わる
  for (const year y : {2025y, 2026y, 2027y}) {
    const sys_days d = y / mw;
    std::println("{:%F}", d);
  }
}
```

```text title="実行結果"
true
2025-03-10
2026-03-09
2027-03-08
```

同じ「3 月の第 2 月曜日」でも、年によって日付が 10 日、9 日、8 日と変わります。

## ゲームでの使いどころ

毎年繰り返す祝日や、季節イベントの日取りを、「何月の第何何曜日」という規則のまま持たせます。

## よくあるミス

??? failure "year_month_weekday と取り違える"
    `month_weekday` は年を含みません。日付に直すには年と組み合わせます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`month_weekday_last`](month_weekday_last.md) | 最後の曜日 |
| [`year_month_weekday`](year_month_weekday.md) | 年を含む |
| [`weekday_indexed`](weekday_indexed.md) | 月を含まない |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: month_weekday](https://cpprefjp.github.io/reference/chrono/month_weekday.html)
- [cppreference: std::chrono::month_weekday](https://en.cppreference.com/w/cpp/chrono/month_weekday)
