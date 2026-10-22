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

「2024 年 3 月の第 2 月曜日」のような指定です。`sys_days` に変換すると、具体的な日付が分かります。

!!! tip "ポイント"
    - `2024y / March / Monday[2]` で作る。
    - `sys_days` に変換して、`year_month_day` で日にちを取り出す。

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要と [`duration`](duration.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::year_month_weekday {#year_month_weekday}

```cpp
class year_month_weekday {
 public:
  constexpr operator sys_days() const noexcept;
  constexpr std::chrono::weekday_indexed weekday_indexed() const noexcept;
  constexpr bool ok() const noexcept;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `y` | year | 年 |
| `mw` | month_weekday | 月と第 n 曜日 |

- 戻り値: `sys_days` に変換できる
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;
  year_month_weekday ymw = 2024y / March / Monday[2];
  year_month_day ymd{sys_days{ymw}};
  std::println("{}", unsigned(ymd.day()));
}
```

```text title="実行結果"
11
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 毎月第 2 月曜日の日付を求める | `sys_days{year / month / Monday[2]}` |

## よくあるミス

??? failure "無い日付に変換する"
    第 5 曜日などが存在しない月では `ok()` が `false` です。確認してから変換します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`month_weekday`](month_weekday.md) | 年を問わない |
| [`year_month_weekday_last`](year_month_weekday_last.md) | 最後の曜日 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 年つきの第 n 曜日
    - [x] sys_days に変換して日付に
    - [x] ok() で存在確認

## 関連ページ

- [cpprefjp: std::chrono::year_month_weekday](https://cpprefjp.github.io/reference/chrono/year_month_weekday.html)
- [cppreference: std::chrono::year_month_weekday](https://en.cppreference.com/w/cpp/chrono/year_month_weekday)
