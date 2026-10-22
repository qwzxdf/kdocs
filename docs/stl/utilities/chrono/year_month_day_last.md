---
title: std::chrono::year_month_day_last
summary: "「その年のその月の最終日」を表す型。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::year_month_day_last

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

月末の日付は、月とうるう年で決まります。`year_month_day_last` は `2024y / February / last` のように書くと、具体的な最終日（`day()`）を計算してくれます。

!!! tip "ポイント"
    - `year / month / last` で作る。
    - `day()` で最終日が分かる。
    - `sys_days` に変換して日付にできる。

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要と [`duration`](duration.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::year_month_day_last {#year_month_day_last}

```cpp
class year_month_day_last {
 public:
  constexpr std::chrono::day day() const noexcept;
  constexpr operator sys_days() const noexcept;
  constexpr bool ok() const noexcept;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `y` | year | 年 |
| `mdl` | month_day_last | 月末の指定 |

- 戻り値: `day()` は最終日
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;
  std::println("{}", unsigned((2024y / February / last).day()));
  std::println("{}", unsigned((2023y / February / last).day()));
}
```

```text title="実行結果"
29
28
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 月末締めの日付を求める | `(year / month / std::chrono::last).day()` |

## よくあるミス

??? failure "自分で日数の表を書く"
    うるう年の判定を含む日数の計算は、この型に任せます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`month_day_last`](month_day_last.md) | 年を問わない月末 |
| [`year_month_day`](year_month_day.md) | 年月日 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 月末の日を計算する
    - [x] うるう年も考慮
    - [x] year/month/last

## 関連ページ

- [cpprefjp: std::chrono::year_month_day_last](https://cpprefjp.github.io/reference/chrono/year_month_day_last.html)
- [cppreference: std::chrono::year_month_day_last](https://en.cppreference.com/w/cpp/chrono/year_month_day_last)
