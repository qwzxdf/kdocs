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

日付の「日」の部分だけを、1〜31 の範囲で型安全に持ちたいことがあります。`std::chrono::day` は、その専用の型で、`int` のように範囲外の値を気づかないまま持ち歩きません。`ok()` で範囲内かを確かめられます。

!!! tip "ポイント"
    - `day{15}` のように作る。`unsigned` に変換して値を取り出す。
    - `ok()` で 1〜31 の範囲か調べる（月ごとの日数は見ない）。
    - `year/month/day` の形で日付にまとめられる。

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要と [`duration`](duration.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::day {#day}

```cpp
class day {
 public:
  constexpr explicit day(unsigned d) noexcept;
  constexpr explicit operator unsigned() const noexcept;
  constexpr bool ok() const noexcept;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `d` | unsigned | 日（1〜31 が有効） |

- 戻り値: `ok()` は 1〜31 なら `true`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  std::chrono::day d{15};
  std::println("{} {}", unsigned(d), d.ok());
  std::println("{}", std::chrono::day{32}.ok());
}
```

```text title="実行結果"
15 true
false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ユーザー入力の日付チェック | `std::chrono::day{n}.ok()` |

## よくあるミス

??? failure "月ごとの日数まで確かめた気になる"
    `day{31}.ok()` は常に `true` です。2 月 31 日かどうかは [`year_month_day`](year_month_day.md) の `ok()` で確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`month`](month.md) | 月 |
| [`year_month_day`](year_month_day.md) | 年月日 |
| [`month_day`](month_day.md) | 月と日 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 日（1〜31）の型
    - [x] ok() で範囲確認
    - [x] 年月日は year_month_day

## 関連ページ

- [cpprefjp: std::chrono::day](https://cpprefjp.github.io/reference/chrono/day.html)
- [cppreference: std::chrono::day](https://en.cppreference.com/w/cpp/chrono/day)
