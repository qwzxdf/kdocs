---
title: std::chrono::months
summary: "月（平均の長さ）を数える duration の別名。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::months

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

「3 か月後」を `std::chrono::months{3}` と書けますが、これは暦の 3 か月ではなく、<strong>平均の月の長さ（30.436875 日）の 3 倍</strong>という、固定の長さの `duration` です。1 月 31 日に足しても、きれいに 4 月 30 日にはなりません。暦の月を足し引きしたいときは、`year_month` や `year_month_day` に `months` を足します。そちらでは、暦のとおりに計算されます。

!!! tip "ポイント"
    - `duration<整数, ratio<2629746>>` の別名。1 か月 = 平均 30.436875 日
    - 秒に直せる固定の長さ。暦の月とは違う
    - 暦の計算は `year_month_day + months{n}`。月末の日がないと、結果が無効になる
    - 暦の月に使うときの結果は、日付の側のチェックが要る

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要と [`days`](days.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::months {#months}

<span class="ver ver-20">C++20</span>

```cpp
using months = duration<int-at-least-20-bits, std::ratio<2629746>>;
```

2629746 秒は、グレゴリオ暦の 400 年を 12 倍の月数で割った、平均の長さです。この `duration` を、時刻（`time_point`）に足すと、固定の秒数ぶん進みます。

日付の型に足す場合は、動作が違います。`year_month_day{2026y/January/31} + months{1}` は、2 月 31 日という存在しない日付になります。この日付は `ok()` が `false` になります。`year_month` に足すなら、日の問題は起きません。

月の長さの変換には、注意が要ります。`duration_cast<days>(months{1})` は 30 日（切り捨て）ですが、実際の月は 28〜31 日です。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  // 固定の長さ (平均) として見る
  std::println("1 か月は {} 時間 (切り捨て)",
               duration_cast<hours>(months{1}).count());

  // 暦の月に足すと、暦のとおり
  const year_month ym = year{2026} / November;
  const year_month next = ym + months{3};
  std::println("2026-11 の 3 か月後: {}-{:02}",
               static_cast<int>(next.year()),
               static_cast<unsigned>(next.month()));

  // 1 月 31 日に 1 か月足すと、存在しない日付になる
  const year_month_day jan31 = year{2026} / January / 31;
  const year_month_day feb31 = jan31 + months{1};
  std::println("2026-02-31 は有効か: {}", feb31.ok());
}
```

```text title="実行結果"
1 か月は 730 時間 (切り捨て)
2026-11 の 3 か月後: 2027-02
2026-02-31 は有効か: false
```

1 か月は約 730.485 時間なので、切り捨てて 730 です。

## ゲームでの使いどころ

「月額のサブスクリプション」のような、暦の月で更新する期限は、`months` で `year_month_day` に足し、`ok()` を確かめます。無効なら、その月の最終日にそろえます。

## よくあるミス

??? failure "months を固定の長さだと思って、日付の計算に使う"
    暦の月と、秒数としての 1 か月は別です。日付の計算は `year_month_day + months{n}` で行い、`ok()` を確かめます。

??? failure "月末の日付に足して、無効な日付を使う"
    1 月 31 日に 1 か月足すと、2 月 31 日です。`ok()` を調べて、最終日（`year_month_day_last`）に直します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`years`](years.md) | 年の単位。平均の長さ |
| [`days`](days.md) | 日の単位 |
| [`year_month`](year_month.md) | 年と月の組。足しても日の問題が起きない |
| [`year_month_day_last`](year_month_day_last.md) | 月末の日 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: months](https://cpprefjp.github.io/reference/chrono/duration.html)
- [cppreference: std::chrono::months](https://en.cppreference.com/w/cpp/chrono/duration)
