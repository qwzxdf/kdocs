---
title: std::chrono::month_day
summary: "月と日の組（誕生日のような、年を問わない日付）。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::month_day

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

誕生日や記念日は、年を問わず、毎年の「何月何日」です。`std::chrono::month_day` は、月と日だけの組で、`March / 15` や `3 / 15d` のように書けます。年を含まないので、うるう年かどうかが分からないまま、2 月 29 日も表せます。

!!! tip "ポイント"
    - `month / day` で作る。`year` を足すと、`year_month_day` になる
    - `ok()` は、2 月 29 日も有効とする（うるう年を考えない）
    - 比較できる（月が先、日が後）
    - 特定の年の日付にするには `year / month_day`

!!! info "このページを読む前に"
    [`month`](month.md) と [`day`](day.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::month_day {#month_day}

<span class="ver ver-20">C++20</span>

```cpp
class month_day {
 public:
  constexpr month_day(const chrono::month& m, const chrono::day& d) noexcept;
  constexpr chrono::month month() const noexcept;
  constexpr chrono::day day() const noexcept;
  constexpr bool ok() const noexcept;
};
```

`ok()` は、月が有効で、日がその月の最大日数以下なら真です。最大日数は、2 月を 29 日として数えるので、2 月 29 日は有効、2 月 30 日は無効です。4 月 31 日も無効です。

年を含まない値なので、「その年に実在する日か」は分かりません。`2 / 29` が、ある年に実在するかは、`year / month_day` で `year_month_day` にして、`ok()` を調べます。

大小の比較は、月、日の順です。`March / 1 < March / 15` が成り立ちます。1 年の中の並びを調べるのに使えます。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  const month_day birthday = February / 29;
  std::println("2/29 は month_day として有効: {}", birthday.ok());
  std::println("4/31 は有効: {}", (April / 31).ok());

  // 特定の年にすると、実在するかが分かる
  std::println("2024-02-29 は有効: {}", (2024y / birthday).ok());
  std::println("2026-02-29 は有効: {}", (2026y / birthday).ok());

  std::println("3/1 < 3/15: {}", (March / 1) < (March / 15));
}
```

```text title="実行結果"
2/29 は month_day として有効: true
4/31 は有効: false
2024-02-29 は有効: true
2026-02-29 は有効: false
3/1 < 3/15: true
```

## ゲームでの使いどころ

キャラクターの誕生日のような、毎年同じ日のイベントの設定に使います。年を問わないので、データに年を持たせずに済みます。

## よくあるミス

??? failure "2/29 を、毎年有効だと思う"
    うるう年でない年には存在しません。実際の年と組み合わせて `ok()` を調べます。

??? failure "month と day の順を逆にする"
    `month_day{day, month}` はコンパイルできません。`month` が先です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`year_month_day`](year_month_day.md) | 年を含む |
| [`month_day_last`](month_day_last.md) | 月の最終日を表す |
| [`year_month`](year_month.md) | 日を含まない |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: month_day](https://cpprefjp.github.io/reference/chrono/month_day.html)
- [cppreference: std::chrono::month_day](https://en.cppreference.com/w/cpp/chrono/month_day)
