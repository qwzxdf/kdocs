---
title: std::chrono::month_day_last
summary: "「その月の最終日」を表す型。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::month_day_last

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

月末が何日かは、月によって違います。毎月の最終日に締めるイベントを、「31 日」と固定で書くと、30 日までの月で動きません。`std::chrono::month_day_last` は、「月」と「最終日」を組にした型で、`March / last` と書きます。日の数字を持たないので、月ごとの日数を気にせずに書けます。

!!! tip "ポイント"
    - `month / last` で作る。`last` は `std::chrono::last`
    - 日は持たない。年が分かって初めて、最終日の数字が決まる
    - `year / month_day_last` で `year_month_day_last` になる
    - `ok()` は、月が有効かだけを見る

!!! info "このページを読む前に"
    [`month_day`](month_day.md) と [`last_spec`](last_spec.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::month_day_last {#month_day_last}

<span class="ver ver-20">C++20</span>

```cpp
class month_day_last {
 public:
  explicit constexpr month_day_last(const chrono::month& m) noexcept;
  constexpr chrono::month month() const noexcept;
  constexpr bool ok() const noexcept;
};
```

`March / last` や `last / March` で作れます。`month()` で月を取り出せます。

年を含まないので、2 月の最終日が 28 日か 29 日かは決まりません。`2026y / February / last` のように年と組み合わせて、`year_month_day_last` にすると、`day()` で 28 が得られます。

`ok()` は、月が 1〜12 の範囲かを調べます。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  const month_day_last feb_end = February / last;
  std::println("月は 2: {}", static_cast<unsigned>(feb_end.month()));

  // 年と組み合わせると、最終日の数字が決まる
  for (const year y : {2024y, 2026y}) {
    const year_month_day_last ymdl = y / feb_end;
    std::println("{} 年 2 月の最終日: {}", static_cast<int>(y),
                 static_cast<unsigned>(ymdl.day()));
  }
}
```

```text title="実行結果"
月は 2: 2
2024 年 2 月の最終日: 29
2026 年 2 月の最終日: 28
```

## ゲームでの使いどころ

「毎月末にランキングを締める」といった周期イベントの設定に使います。日の数字を持たないので、月ごとの日数の違いを、判定の側で気にしなくて済みます。

## よくあるミス

??? failure "31 日と固定で書く"
    30 日までの月で、イベントが発生しません。`month_day_last` で書きます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`month_day`](month_day.md) | 日の数字を持つ |
| [`year_month_day_last`](year_month_day_last.md) | 年を含み、最終日の数字が決まる |
| [`last_spec`](last_spec.md) | `last` の型 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: month_day_last](https://cpprefjp.github.io/reference/chrono/month_day_last.html)
- [cppreference: std::chrono::month_day_last](https://en.cppreference.com/w/cpp/chrono/month_day_last)
