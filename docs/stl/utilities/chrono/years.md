---
title: std::chrono::years
summary: "年（平均の長さ）を数える duration の別名。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::years

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

`std::chrono::years` は、1 年を平均の長さ（365.2425 日）で数える `duration` です。「5 年後」を暦のとおりに求めるものではなく、固定の秒数としての 1 年です。暦の年を足したいときは、`year` や `year_month_day` に `years` を足します。うるう日（2 月 29 日）に足すと、無効な日付になることがあります。

!!! tip "ポイント"
    - `duration<整数, ratio<31556952>>` の別名。1 年 = 平均 365.2425 日
    - 秒に直せる固定の長さ。暦の年とは違う
    - 暦の計算は `year_month_day + years{n}`
    - 2 月 29 日に足すと、うるう年でない年では無効な日付になる

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要と [`months`](months.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::years {#years}

<span class="ver ver-20">C++20</span>

```cpp
using years = duration<int-at-least-17-bits, std::ratio<31556952>>;
```

31556952 秒は、グレゴリオ暦の 400 年の日数を 400 で割った、平均の 1 年です。400 年に 97 回のうるう年があるので、平均は 365.2425 日です。

`duration_cast<days>(years{1})` は、365 日（切り捨て）です。実際の年は 365 日か 366 日です。経過時間を概算の年数で表示するのに、便利です。

暦の年の足し算は、`year_month_day` の側で行います。`2024y/February/29 + years{1}` は、2025 年 2 月 29 日で、存在しません。`ok()` が `false` になるので、確かめます。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  // 固定の長さ (平均) として見る
  std::println("1 年は {} 日 (切り捨て)", duration_cast<days>(years{1}).count());

  // 暦の年に足す
  const year_month_day d = year{2026} / March / 15;
  const year_month_day next = d + years{2};
  std::println("2 年後: {}-{:02}-{:02}",
               static_cast<int>(next.year()),
               static_cast<unsigned>(next.month()),
               static_cast<unsigned>(next.day()));

  // うるう日に足すと、無効な日付になる
  const year_month_day leap = year{2024} / February / 29;
  std::println("2025-02-29 は有効か: {}", (leap + years{1}).ok());
}
```

```text title="実行結果"
1 年は 365 日 (切り捨て)
2 年後: 2028-03-15
2025-02-29 は有効か: false
```

## ゲームでの使いどころ

プレイ時間の累計を、「約 2 年」のように表示するのに使います。誕生日や記念日のような、暦の年の計算は、`year_month_day` に足して、`ok()` を確かめます。

## よくあるミス

??? failure "years を暦の年と同じだと考える"
    平均の長さなので、365 日の倍数にはなりません。日付の計算は、`year_month_day` に足します。

??? failure "2 月 29 日に足して、無効な日付を使う"
    うるう年でない年には 2 月 29 日がありません。`ok()` で確かめ、`February / 28` か `March / 1` にそろえます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`months`](months.md) | 月の単位。平均の長さ |
| [`year`](year.md) | 年を表す型（暦の年） |
| [`year_month_day`](year_month_day.md) | 年月日の型 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: years](https://cpprefjp.github.io/reference/chrono/duration.html)
- [cppreference: std::chrono::years](https://en.cppreference.com/w/cpp/chrono/duration)
