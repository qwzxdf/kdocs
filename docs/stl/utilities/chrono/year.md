---
title: std::chrono::year
summary: "年を表す型。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::year

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

年を `int` で持つと、月や日との取り違えが起きます。`std::chrono::year` は、年を表す専用の型で、`2026y` のリテラルでも書けます。うるう年かどうかを `is_leap()` で調べられるのが、整数にない利点です。

!!! tip "ポイント"
    - 有効な範囲は -32767〜32767（`year::min()` と `year::max()`）
    - `is_leap()` で、うるう年かが分かる（グレゴリオ暦の規則）
    - 数への変換は `explicit` で、`static_cast<int>(y)` と書く
    - `years` を足し引きできる

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要と [`month`](month.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::year {#year}

<span class="ver ver-20">C++20</span>

```cpp
class year {
 public:
  explicit constexpr year(int y) noexcept;
  constexpr bool is_leap() const noexcept;
  constexpr bool ok() const noexcept;
  explicit constexpr operator int() const noexcept;
  static constexpr year min() noexcept;
  static constexpr year max() noexcept;
};
```

`is_leap()` は、4 で割り切れ、100 で割り切れる年は除き、400 で割り切れる年は含む、というグレゴリオ暦の規則で判定します。2000 年はうるう年、2100 年は違います。

`ok()` は、`min()` 以上 `max()` 以下のときに真です。範囲は -32767 から 32767 までです。紀元前を含む西暦の数え方では、0 年を 1 BC として扱う天文学的な数え方になります。

`year{2026} + years{3}` で、3 年後の `year` が得られます。`y1 - y2` は、`years` を返します。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  for (const year y : {2000y, 2024y, 2026y, 2100y}) {
    std::println("{} はうるう年: {}", static_cast<int>(y), y.is_leap());
  }

  std::println("範囲: {} 〜 {}", static_cast<int>(year::min()),
               static_cast<int>(year::max()));
  std::println("2026 + 3 年: {}", static_cast<int>(2026y + years{3}));
  std::println("2030 - 2026: {} 年", (2030y - 2026y).count());
}
```

```text title="実行結果"
2000 はうるう年: true
2024 はうるう年: true
2026 はうるう年: false
2100 はうるう年: false
範囲: -32767 〜 32767
2026 + 3 年: 2029
2030 - 2026: 4 年
```

## ゲームでの使いどころ

カレンダー機能で、2 月に 29 日があるかを調べるときに使います。年の取り違えが起きにくい型としても有用です。

## よくあるミス

??? failure "year y = 2026; と書く"
    `explicit` なので、コンパイルできません。`year{2026}` か `2026y` です。

??? failure "100 で割り切れる年を、うるう年と考える"
    2100 年はうるう年ではありません。自分で判定せず、`is_leap()` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`month`](month.md) | 月を表す型 |
| [`day`](day.md) | 日を表す型 |
| [`years`](years.md) | 年数（期間）の型 |
| [`year_month_day`](year_month_day.md) | 年月日を組にした型 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: year](https://cpprefjp.github.io/reference/chrono/year.html)
- [cppreference: std::chrono::year](https://en.cppreference.com/w/cpp/chrono/year)
