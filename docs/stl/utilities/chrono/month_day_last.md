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

月末の日付は月ごとに違います（28〜31）。`month_day_last` は、「その月の最後の日」を日数を知らなくても表します。`February / last` と書いて作ります。

!!! tip "ポイント"
    - `month / last` で作る。
    - 年をつけると `year_month_day_last` になる。
    - 具体的な日は年を決めてから分かる。

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要と [`duration`](duration.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::month_day_last {#month_day_last}

```cpp
class month_day_last {
 public:
  constexpr std::chrono::month month() const noexcept;
  constexpr bool ok() const noexcept;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `m` | month | 月 |

- 戻り値: `month()` は元の月
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;
  auto mdl = February / last;
  std::println("{}", unsigned(mdl.month()));
}
```

```text title="実行結果"
2
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 月末締めの集計日 | `std::chrono::March / std::chrono::last` |

## よくあるミス

??? failure "日数を自分で場合分けする"
    うるう年や 30 日の月の場合分けは不要です。`last` で表して、年をつけたあと `day()` で取ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`year_month_day_last`](year_month_day_last.md) | 年つきの月末 |
| [`last_spec`](last_spec.md) | `last` の型 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 月の最終日
    - [x] month / last
    - [x] 年をつけると日が決まる

## 関連ページ

- [cpprefjp: std::chrono::month_day_last](https://cpprefjp.github.io/reference/chrono/month_day_last.html)
- [cppreference: std::chrono::month_day_last](https://en.cppreference.com/w/cpp/chrono/month_day_last)
