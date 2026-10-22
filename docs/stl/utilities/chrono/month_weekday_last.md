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

「毎年 5 月の最後の月曜日」（アメリカの戦没者追悼記念日）のような指定には `month_weekday_last` を使います。`May / Monday[last]` と書きます。

!!! tip "ポイント"
    - `month / weekday[last]` で作る。
    - 年をつけると `year_month_weekday_last`。

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要と [`duration`](duration.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::month_weekday_last {#month_weekday_last}

```cpp
class month_weekday_last {
 public:
  constexpr std::chrono::month month() const noexcept;
  constexpr std::chrono::weekday_last weekday_last() const noexcept;
  constexpr bool ok() const noexcept;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `m` | month | 月 |
| `wdl` | weekday_last | 最後の曜日 |

- 戻り値: `ok()` は有効なら `true`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;
  auto mwl = March / Monday[last];
  std::println("{}", mwl.weekday_last().weekday().c_encoding());
}
```

```text title="実行結果"
1
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 毎月最後の曜日のイベント | `std::chrono::March / std::chrono::Monday[std::chrono::last]` |

## よくあるミス

??? failure "日付だと思う"
    年をつけてから `sys_days` にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`month_weekday`](month_weekday.md) | 第 n 曜日 |
| [`year_month_weekday_last`](year_month_weekday_last.md) | 年つき |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 月の最後の曜日
    - [x] 年を問わない
    - [x] 年をつけて日付に

## 関連ページ

- [cpprefjp: std::chrono::month_weekday_last](https://cpprefjp.github.io/reference/chrono/month_weekday_last.html)
- [cppreference: std::chrono::month_weekday_last](https://en.cppreference.com/w/cpp/chrono/month_weekday_last)
