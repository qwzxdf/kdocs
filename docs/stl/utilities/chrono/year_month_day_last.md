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

2 月の最終日は、28 日だったり 29 日だったりします。`std::chrono::year_month_day_last` は、年と月に「最終日」を組み合わせた型で、`2026y / February / last` と書きます。`day()` で、その月の実際の最終日の数字が求まり、`sys_days` に変換すると、日付になります。

!!! tip "ポイント"
    - `year / month / last` で作る
    - `day()` が、年月に応じた最終日の数字（28〜31）を返す
    - `sys_days` へ変換できる。月末の日付が求まる
    - `+ months` で月を進めても、無効な日付にならない

!!! info "このページを読む前に"
    [`month_day_last`](month_day_last.md) と [`year_month_day`](year_month_day.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::year_month_day_last {#year_month_day_last}

<span class="ver ver-20">C++20</span>

```cpp
class year_month_day_last {
 public:
  constexpr year_month_day_last(const chrono::year& y,
                                const chrono::month_day_last& mdl) noexcept;
  constexpr chrono::year year() const noexcept;
  constexpr chrono::month month() const noexcept;
  constexpr chrono::day day() const noexcept;
  constexpr bool ok() const noexcept;
  constexpr operator sys_days() const noexcept;
};
```

`day()` は、年と月から計算した、最終日です。1 月、3 月、5 月などは 31、4 月、6 月などは 30、2 月はうるう年なら 29、そうでなければ 28 です。

`sys_days` へ暗黙に変換できます。`sys_days d = 2026y / February / last;` で、2026 年 2 月 28 日の日付が得られます。

`year_month_day_last + months{1}` のように、月を足しても、月末のまま有効な日付になります。1 月 31 日に月を足すと無効になる `year_month_day` と違い、「月末」という意味が保たれます。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  for (const year y : {2024y, 2026y}) {
    const year_month_day_last end = y / February / last;
    std::println("{} 年 2 月は {} 日まで", static_cast<int>(y),
                 static_cast<unsigned>(end.day()));
  }

  // 日付にする
  const sys_days d = 2026y / April / last;
  std::println("{:%F}", d);

  // 月を足しても、月末のまま
  const year_month_day_last next = (2026y / January / last) + months{1};
  std::println("1 月末 + 1 か月 → 2 月の最終日: {}", static_cast<unsigned>(next.day()));
}
```

```text title="実行結果"
2024 年 2 月は 29 日まで
2026 年 2 月は 28 日まで
2026-04-30
1 月末 + 1 か月 → 2 月の最終日: 28
```

## ゲームでの使いどころ

月末の締め日、月額課金の更新日（月末の場合）を、日付の数字を直接持たずに表します。

## よくあるミス

??? failure "最終日の数字を 31 固定で書く"
    30 日までの月で、存在しない日付になります。`last` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`month_day_last`](month_day_last.md) | 年を含まない |
| [`year_month_day`](year_month_day.md) | 日の数字を持つ |
| [`sys_days`](sys_days.md) | 日付を日の単位で表す |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: year_month_day_last](https://cpprefjp.github.io/reference/chrono/year_month_day_last.html)
- [cppreference: std::chrono::year_month_day_last](https://en.cppreference.com/w/cpp/chrono/year_month_day_last)
