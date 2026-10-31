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

「2026 年 11 月」のように、日を問わずに、年と月だけを指す値が欲しい場面があります。月ごとの集計や、カレンダーの 1 か月ぶんの表示です。`std::chrono::year_month` は、`year` と `month` の組で、`2026y / November` と、`/` でつなげて作れます。

!!! tip "ポイント"
    - `year / month` で作る。`year_month_day` を作るには、さらに `/ day` を足す
    - `+ months` や `+ years` で、月単位・年単位の移動ができる。月末の問題が起きない
    - 2 つの `year_month` の差は `months`
    - `ok()` で、年と月が有効範囲か調べる

!!! info "このページを読む前に"
    [`year`](year.md) と [`month`](month.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::year_month {#year_month}

<span class="ver ver-20">C++20</span>

```cpp
class year_month {
 public:
  constexpr year_month(const chrono::year& y, const chrono::month& m) noexcept;
  constexpr chrono::year year() const noexcept;
  constexpr chrono::month month() const noexcept;
  constexpr bool ok() const noexcept;
};
```

`year{2026} / November` のように作ります。`year()` と `month()` で、各部分を取り出します。

`year_month` に `months` や `years` を足すと、結果は有効な `year_month` のままです。`2026y/November + months{3}` は、`2027y/February` です。月末の日がないという、`year_month_day` の問題が、ここでは起きません。

`ym2 - ym1` は、月数の差を `months` で返します。2026 年 11 月から 2027 年 2 月までは、3 か月です。

`ym / day` で、`year_month_day` を作れます。`ym / last` で、その月の最終日（`year_month_day_last`）になります。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  const year_month ym = 2026y / November;
  std::println("{}-{:02}", static_cast<int>(ym.year()),
               static_cast<unsigned>(ym.month()));

  const year_month later = ym + months{3};
  std::println("3 か月後: {}-{:02}", static_cast<int>(later.year()),
               static_cast<unsigned>(later.month()));

  std::println("月の差: {}", (later - ym).count());

  // 最終日を求める
  const year_month_day_last end = ym / last;
  std::println("最終日: {}", static_cast<unsigned>(end.day()));
}
```

```text title="実行結果"
2026-11
3 か月後: 2027-02
月の差: 3
最終日: 30
```

## ゲームでの使いどころ

月間ランキングのように、月を単位にして集計するときの、キーとして使います。`year_month` を比較すれば、月の前後が分かります。

## よくあるミス

??? failure "year_month_day で月を進めて、月末の問題に当たる"
    1 月 31 日に 1 か月足すと、2 月 31 日になります。月だけの話なら、`year_month` で進めます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`year_month_day`](year_month_day.md) | 日まで含む |
| [`month_day`](month_day.md) | 年を含まない月日 |
| [`months`](months.md) | 月数（期間）の型 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: year_month](https://cpprefjp.github.io/reference/chrono/year_month.html)
- [cppreference: std::chrono::year_month](https://en.cppreference.com/w/cpp/chrono/year_month)
