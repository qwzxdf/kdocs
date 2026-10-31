---
title: std::chrono::day
summary: "月の中の日（1〜31）を表す型。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::day

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

日付を `int` で持つと、「15」が日なのか月なのか年なのかが、型から分かりません。`std::chrono::day` は、月の中の日（1〜31）を表す専用の型で、`15d` のリテラルでも書けます。月や年の型と混ざらないので、`year_month_day{2026y, March, 15d}` のように、順番を間違えるとコンパイル エラーになります。

!!! tip "ポイント"
    - 内部は `unsigned char` 相当。1〜31 が有効な値
    - 範囲外の値も持てる（`day{40}`）。有効かは `ok()` で調べる
    - `unsigned` に `static_cast` して数として取り出す
    - その月の実際の日数に合っているかは、`day` 単体では分からない。`year_month_day::ok()` で調べる

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要と [`year_month_day`](year_month_day.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::day {#day}

<span class="ver ver-20">C++20</span>

```cpp
class day {
 public:
  explicit constexpr day(unsigned d) noexcept;
  constexpr bool ok() const noexcept;
  explicit constexpr operator unsigned() const noexcept;
  // ++, --, +=, -=（日数を足し引き）
};
```

`day{15}` で作ります。数からの変換は `explicit` なので、`day d = 15;` とは書けません。逆に、`unsigned` へも `explicit` で、`static_cast<unsigned>(d)` と書きます。

`ok()` は、値が 1 以上 31 以下のときに真です。`day{0}` や `day{32}` を作ること自体はできますが、`ok()` は偽になります。どの月でも使える範囲の検査なので、2 月の 30 日は `day` 単体では有効です。月ごとの日数を含めて調べるには、`year_month_day::ok()` を使います。

`++d` や `d += days{3}` のように、足し引きもできます。31 を超えるとき、ラップアラウンドはしません。値は範囲外になるだけです。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  const day d = 15d;  // リテラル
  std::println("{}", static_cast<unsigned>(d));
  std::println("15 は有効: {}", d.ok());
  std::println("32 は有効: {}", day{32}.ok());
  std::println("2 月 30 日は日だけなら有効: {}", day{30}.ok());

  // 月ごとの検査は year_month_day で
  const year_month_day ymd = 2026y / February / 30d;
  std::println("2026-02-30 は有効: {}", ymd.ok());
}
```

```text title="実行結果"
15
15 は有効: true
32 は有効: false
2 月 30 日は日だけなら有効: true
2026-02-30 は有効: false
```

`day{30}` は 1〜31 の範囲なので有効ですが、2 月の日付としては `year_month_day` が無効と判断しています。

## ゲームでの使いどころ

カレンダーの表示や、「毎月 15 日にリセット」のような設計値を持つときに使います。日だけを `int` で持つ設計に比べて、取り違えが起きません。

## よくあるミス

??? failure "day の ok() が真なら、日付として有効だと思う"
    `day{31}` は、4 月などの 30 日までの月では無効です。年月とセットの `year_month_day` で確かめます。

??? failure "day d = 15; と書く"
    変換が `explicit` なので、コンパイルできません。`day{15}` か `15d` と書きます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`month`](month.md) | 月を表す型 |
| [`year`](year.md) | 年を表す型 |
| [`year_month_day`](year_month_day.md) | 年月日を組にした型。ここで有効性を調べる |
| [`days`](days.md) | 日数（期間）の型 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: day](https://cpprefjp.github.io/reference/chrono/day.html)
- [cppreference: std::chrono::day](https://en.cppreference.com/w/cpp/chrono/day)
