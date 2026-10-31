---
title: std::chrono::days
summary: "日を数える duration の別名。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::days

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

スタミナが全回復するまで 3 日、ログインして 7 日目の報酬、というように、日の単位で期間を持ちたい場面があります。`std::chrono::days` は、1 日を単位とする `duration` の別名で、C++20 で追加されました。1 日は 86400 秒です。日付（`sys_days`）の足し引きにも使います。

!!! tip "ポイント"
    - `duration<整数, ratio<86400>>` の別名。C++20 から
    - 1 日 = 24 時間 = 86400 秒。夏時間などは考えない、固定の長さ
    - `hours` へは暗黙に変換でき、`weeks` へは `duration_cast` が必要
    - カレンダー上の日付との組み合わせは `sys_days`

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要と [`hours`](hours.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::days {#days}

<span class="ver ver-20">C++20</span>

```cpp
using days = duration<int-at-least-25-bits, std::ratio<86400>>;
```

内部の整数は 25 ビット以上で、5 万年ぶんほどの日が数えられます。

`days{3}` は、72 時間と同じ長さです。`hours h = days{3};` と暗黙に変換できます。1 日の長さは、いつも 86400 秒の固定で、夏時間で 23 時間や 25 時間になる日は考えません。暦の上での 1 日（地域の日付）を扱うときは、`local_days` や `sys_days` と組み合わせます。

`sys_days{2026y/1/1} + days{30}` のように、日付に日数を足して、30 日後の日付を求められます。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  const days d{3};
  const hours h = d;  // 暗黙の変換
  std::println("3 日は {} 時間", h.count());

  // 週は 7 日。days どうしの割り算で整数が出る
  std::println("21 日は {} 週間", days{21} / days{7});

  // 日付に日数を足す
  const sys_days start = year{2026} / January / 1;
  const sys_days later = start + days{45};
  const year_month_day ymd{later};
  std::println("45 日後は {}-{:02}-{:02}",
               static_cast<int>(ymd.year()),
               static_cast<unsigned>(ymd.month()),
               static_cast<unsigned>(ymd.day()));
}
```

```text title="実行結果"
3 日は 72 時間
21 日は 3 週間
45 日後は 2026-02-15
```

`start + days{45}` で 2026 年 1 月 1 日の 45 日後が求まり、`year_month_day` に戻して年月日を取り出しています。

## ゲームでの使いどころ

連続ログイン日数、期間限定イベントの残り日数、セーブデータの古さの判定に使います。日付をまたぐ判定は、`sys_days` に変換して、日数の差を取ります。

## よくあるミス

??? failure "1 日を 86400 秒の固定と考えて、地域の日付とずれる"
    夏時間のある地域では、1 日が 23 時間や 25 時間の日があります。地域の日付で数えるなら、`local_days` を使います。

??? failure "C++17 以前で days を使う"
    `days` は C++20 からです。C++17 では `duration<int, std::ratio<86400>>` と書きます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`hours`](hours.md) | 時間の単位 |
| [`weeks`](weeks.md) | 週の単位。7 日 |
| [`sys_days`](sys_days.md) | 日付を日の単位で表す |
| [`year_month_day`](year_month_day.md) | 年月日の型 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: days](https://cpprefjp.github.io/reference/chrono/duration.html)
- [cppreference: std::chrono::days](https://en.cppreference.com/w/cpp/chrono/duration)
