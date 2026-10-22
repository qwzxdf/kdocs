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

「2024 年 3 月の最後の月曜日」の指定です。`sys_days` に変換すると具体的な日付になります。

!!! tip "ポイント"
    - `2024y / March / Monday[last]` で作る。
    - `sys_days` に変換して日付にする。

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要と [`duration`](duration.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::year_month_weekday_last {#year_month_weekday_last}

```cpp
class year_month_weekday_last {
 public:
  constexpr operator sys_days() const noexcept;
  constexpr std::chrono::weekday_last weekday_last() const noexcept;
  constexpr bool ok() const noexcept;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `y` | year | 年 |
| `mwl` | month_weekday_last | 月と最後の曜日 |

- 戻り値: `sys_days` に変換できる
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;
  year_month_weekday_last ymwl = 2024y / March / Monday[last];
  year_month_day ymd{sys_days{ymwl}};
  std::println("{}", unsigned(ymd.day()));
}
```

```text title="実行結果"
25
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 月末の最後の曜日のイベント日 | `sys_days{year / month / weekday[last]}` |

## よくあるミス

??? failure "最後の曜日が週の何番目かを決め打ちする"
    月によって 4 回の月も 5 回の月もあります。`last` を使えば自動で決まります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`month_weekday_last`](month_weekday_last.md) | 年を問わない |
| [`year_month_weekday`](year_month_weekday.md) | 第 n 曜日 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 年つきの最後の曜日
    - [x] sys_days に変換
    - [x] last で自動決定

## 関連ページ

- [cpprefjp: std::chrono::year_month_weekday_last](https://cpprefjp.github.io/reference/chrono/year_month_weekday_last.html)
- [cppreference: std::chrono::year_month_weekday_last](https://en.cppreference.com/w/cpp/chrono/year_month_weekday_last)
