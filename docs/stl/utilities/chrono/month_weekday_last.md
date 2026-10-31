---
title: std::chrono::month_weekday_last
summary: "「その月の最後の曜日」を表す型（年を問わない）。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::month_weekday_last

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

「11 月の最後の木曜日」のような、年を問わない規則を表す型が `std::chrono::month_weekday_last` です。`November / Thursday[last]` と書き、月と `weekday_last` の組になっています。年と組み合わせると、実際の日付が決まります。

!!! tip "ポイント"
    - `month / weekday_last` で作る
    - 年を含まない。`year / month_weekday_last` で日付になる
    - `month()` と `weekday_last()` で、各部分を取り出せる
    - 第 4 か第 5 かは、年が決まれば自動で決まる

!!! info "このページを読む前に"
    [`weekday_last`](weekday_last.md) と [`month_weekday`](month_weekday.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::month_weekday_last {#month_weekday_last}

<span class="ver ver-20">C++20</span>

```cpp
class month_weekday_last {
 public:
  constexpr month_weekday_last(const chrono::month& m,
                               const chrono::weekday_last& wdl) noexcept;
  constexpr chrono::month month() const noexcept;
  constexpr chrono::weekday_last weekday_last() const noexcept;
  constexpr bool ok() const noexcept;
};
```

`November / Thursday[last]` が、この型です。`ok()` は、月と曜日が有効な範囲かを調べます。

年を決めると、その月の最後の該当する曜日が、日付として決まります。第 4 になる年も第 5 になる年もありますが、書く側は気にしません。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  // 毎年 11 月の最後の木曜日
  const month_weekday_last rule = November / Thursday[last];
  std::println("{}", rule.ok());

  for (const year y : {2025y, 2026y, 2027y}) {
    const sys_days d = y / rule;
    std::println("{:%F}", d);
  }
}
```

```text title="実行結果"
true
2025-11-27
2026-11-26
2027-11-25
```

## ゲームでの使いどころ

季節イベントの最終日を、「何月の最後の何曜日」と持たせます。年ごとの日付を計算しておく必要がありません。

## よくあるミス

??? failure "年を決めずに日付として使う"
    `month_weekday_last` は日付ではありません。年と組み合わせてから `sys_days` にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`month_weekday`](month_weekday.md) | 第 n 曜日 |
| [`year_month_weekday_last`](year_month_weekday_last.md) | 年を含む |
| [`weekday_last`](weekday_last.md) | 月を含まない |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: month_weekday_last](https://cpprefjp.github.io/reference/chrono/month_weekday_last.html)
- [cppreference: std::chrono::month_weekday_last](https://en.cppreference.com/w/cpp/chrono/month_weekday_last)
