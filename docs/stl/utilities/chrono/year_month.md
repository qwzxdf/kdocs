---
title: std::chrono::year_month
summary: "年と月の組。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::year_month

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

「2024 年 3 月」のように、日を決めない期間を扱うとき、`year_month` が使えます。月末への移動や月の足し算ができます。

!!! tip "ポイント"
    - `2024y / March` で作る。
    - `+ months{n}` で月を進められる（年の繰り上がりも自動）。
    - 日をつけて `year_month_day` に。

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要と [`duration`](duration.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::year_month {#year_month}

```cpp
class year_month {
 public:
  constexpr year_month(const year& y, const month& m) noexcept;
  constexpr std::chrono::year year() const noexcept;
  constexpr std::chrono::month month() const noexcept;
  constexpr bool ok() const noexcept;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `y` | year | 年 |
| `m` | month | 月 |

- 戻り値: `ok()` は有効なら `true`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;
  auto ym = 2024y / March;
  ym += months{11};
  std::println("{} {}", int(ym.year()), unsigned(ym.month()));
}
```

```text title="実行結果"
2025 2
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 月ごとの集計キー | `std::chrono::year_month` |

## よくあるミス

??? failure "月を足して手計算する"
    `months{n}` を足せば、年の繰り上がりも自動で計算されます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`year_month_day`](year_month_day.md) | 年月日 |
| [`month`](month.md) | 月 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 年と月の組
    - [x] months を足せる
    - [x] 日は含まない

## 関連ページ

- [cpprefjp: std::chrono::year_month](https://cpprefjp.github.io/reference/chrono/year_month.html)
- [cppreference: std::chrono::year_month](https://en.cppreference.com/w/cpp/chrono/year_month)
