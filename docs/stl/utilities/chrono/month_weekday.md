---
title: std::chrono::month_weekday
summary: "「その月の第 n 曜日」を表す型（年を問わない）。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::month_weekday

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

「毎年 11 月の第 4 木曜日」（アメリカの感謝祭）のような、年を決めない日付の指定が `month_weekday` です。`November / Thursday[4]` と書きます。

!!! tip "ポイント"
    - `month / weekday[n]` で作る。
    - 年をつけて `year_month_weekday` にすると、具体的な日付になる。

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要と [`duration`](duration.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::month_weekday {#month_weekday}

```cpp
class month_weekday {
 public:
  constexpr std::chrono::month month() const noexcept;
  constexpr std::chrono::weekday_indexed weekday_indexed() const noexcept;
  constexpr bool ok() const noexcept;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `m` | month | 月 |
| `wdi` | weekday_indexed | 第 n 曜日 |

- 戻り値: `ok()` は有効なら `true`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;
  auto mw = March / Monday[2];
  std::println("{} {}", mw.ok(), mw.weekday_indexed().index());
}
```

```text title="実行結果"
true 2
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 毎年の祝日の指定 | `std::chrono::November / std::chrono::Thursday[4]` |

## よくあるミス

??? failure "日付だと思う"
    これは日付ではなく「指定」です。年をつけて `sys_days` にして初めて日付になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`month_weekday_last`](month_weekday_last.md) | 最後の曜日 |
| [`year_month_weekday`](year_month_weekday.md) | 年つき |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 月の第 n 曜日
    - [x] 年を問わない
    - [x] 年をつけて日付に

## 関連ページ

- [cpprefjp: std::chrono::month_weekday](https://cpprefjp.github.io/reference/chrono/month_weekday.html)
- [cppreference: std::chrono::month_weekday](https://en.cppreference.com/w/cpp/chrono/month_weekday)
