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

毎年同じ日にあるイベント（誕生日、記念日）は、年を決めずに「3 月 5 日」と持ちたくなります。`std::chrono::month_day` は、月と日の組を表します。

!!! tip "ポイント"
    - `March / 5` または `month_day{March, day{5}}` で作る。
    - 2 月 29 日は有効（うるう年かどうかは年がないので判断しない）。
    - 年をつけて `year_month_day` にする。

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要と [`duration`](duration.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::month_day {#month_day}

```cpp
class month_day {
 public:
  constexpr month_day(const month& m, const day& d) noexcept;
  constexpr month month() const noexcept;
  constexpr day day() const noexcept;
  constexpr bool ok() const noexcept;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `m` | month | 月 |
| `d` | day | 日 |

- 戻り値: `ok()` は有効な月日なら `true`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;
  auto md = February / 29;
  std::println("{}", md.ok());
  std::println("{}", (February / 30).ok());
}
```

```text title="実行結果"
true
false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 毎年のイベントの日付 | `std::chrono::December / 25` |

## よくあるミス

??? failure "2 月 29 日を無条件で有効だと思う"
    `month_day` としては有効ですが、年をつけると平年では無効になります。年をつけて確認します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`month`](month.md) | 月 |
| [`day`](day.md) | 日 |
| [`year_month_day`](year_month_day.md) | 年月日 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 月と日の組
    - [x] 年を問わない日付
    - [x] 2/29 は有効

## 関連ページ

- [cpprefjp: std::chrono::month_day](https://cpprefjp.github.io/reference/chrono/month_day.html)
- [cppreference: std::chrono::month_day](https://en.cppreference.com/w/cpp/chrono/month_day)
