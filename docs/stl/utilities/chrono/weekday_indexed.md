---
title: std::chrono::weekday_indexed
summary: "「第 n の曜日」を表す型（第 2 月曜日など）。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::weekday_indexed

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

「毎月第 2 月曜日に開催」「第 3 金曜日に更新」。カレンダーの上で、曜日と回数を組にして指定したい場面は、よくあります。`std::chrono::weekday_indexed` は、`weekday` に「第何回目か」の番号を付けた型で、`Monday[2]` と書きます。これに月や年を組み合わせると、実際の日付が決まります。

!!! tip "ポイント"
    - `weekday[n]` で作る。`n` は 1〜5（第 1〜第 5）
    - 月や年が決まるまでは、日付ではない
    - `month / weekday_indexed` で `month_weekday`、`year_month / weekday_indexed` で `year_month_weekday` になる
    - 第 5 は存在しない月がある。`ok()` で調べる

!!! info "このページを読む前に"
    [`weekday`](weekday.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::weekday_indexed {#weekday_indexed}

<span class="ver ver-20">C++20</span>

```cpp
class weekday_indexed {
 public:
  constexpr weekday_indexed(const chrono::weekday& wd, unsigned index) noexcept;
  constexpr chrono::weekday weekday() const noexcept;
  constexpr unsigned index() const noexcept;
  constexpr bool ok() const noexcept;
};
```

`Monday[2]` が `weekday_indexed{Monday, 2}` と同じです。`index()` が回数、`weekday()` が曜日です。

`ok()` は、曜日が有効で、`index` が 1〜5 の範囲のときに真です。範囲の検査だけで、実際の月に第 5 月曜日があるかは調べません。それは、年月を決めた `year_month_weekday` で調べます。

どの月にも、第 1 から第 4 までは必ずあり、第 5 は、月によって、あったりなかったりします。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  const weekday_indexed second_monday = Monday[2];
  std::println("第 {} 回", second_monday.index());
  std::println("月曜日: {}", second_monday.weekday() == Monday);
  std::println("第 5 は範囲内: {}", Monday[5].ok());
  std::println("第 6 は範囲内: {}", weekday_indexed{Monday, 6}.ok());

  // 2026 年 3 月の第 2 月曜日
  const sys_days d = 2026y / March / Monday[2];
  std::println("{:%F}", d);
}
```

```text title="実行結果"
第 2 回
月曜日: true
第 5 は範囲内: true
第 6 は範囲内: false
2026-03-09
```

`2026y / March / Monday[2]` が `year_month_weekday` になり、`sys_days` に変換すると具体的な日付が得られます。

## ゲームでの使いどころ

「第 2 土曜日にイベント」のような、周期のあるイベントの日取りを、設定データに書くときに使います。

## よくあるミス

??? failure "第 5 週が必ずあると思う"
    月によっては、第 5 の曜日がありません。`year_month_weekday::ok()` で確かめます。

??? failure "index を 0 始まりにする"
    `Monday[0]` は無効です。1 始まりです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`weekday_last`](weekday_last.md) | 「最後の曜日」 |
| [`month_weekday`](month_weekday.md) | 月と組み合わせたもの |
| [`year_month_weekday`](year_month_weekday.md) | 年月と組み合わせたもの。日付になる |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: weekday_indexed](https://cpprefjp.github.io/reference/chrono/weekday_indexed.html)
- [cppreference: std::chrono::weekday_indexed](https://en.cppreference.com/w/cpp/chrono/weekday_indexed)
