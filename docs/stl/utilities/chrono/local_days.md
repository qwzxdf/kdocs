---
title: std::chrono::local_days
summary: "ローカル時刻を、日の単位で表す別名（地域のカレンダーの日付）。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::local_days

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

`std::chrono::local_days` は、タイムゾーンのない地域のカレンダーの日付を、日数で表す型です。`local_time<days>` の別名で、`sys_days` のローカル版にあたります。「日本の 2026 年 3 月 9 日」のように、UTC との差を考えずに、暦の日付だけを扱いたいときに使います。

!!! tip "ポイント"
    - `local_time<days>` の別名
    - `year_month_day` から `local_days{ymd}` で作れる
    - `+ hours{9}` のように時刻を足すと、`local_time` になる
    - UTC の日付と地域の日付が一致するとは限らない

!!! info "このページを読む前に"
    [`local_time`](local_time.md) と [`sys_days`](sys_days.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::local_days {#local_days}

<span class="ver ver-20">C++20</span>

```cpp
using local_days = local_time<days>;
```

`sys_days` との違いは、UTC ではなく、地域の暦に対応していることです。日本時間の 2026 年 1 月 1 日の 0 時は、UTC では 2025 年 12 月 31 日 15 時です。「その地域の 1 月 1 日」を扱うなら、`local_days` です。

`local_days` に `hours` や `minutes` を足すと、`local_time` になります。壁掛け時計の日時を組み立てられます。

```cpp
const local_seconds t = local_days{2026y / March / 9} + 14h;
```

`sys_days` と `local_days` は、暗黙には変換できません。変換するときは、`time_zone` を使います。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  const local_days a{2026y / January / 1};
  const local_days b{2026y / February / 1};
  std::println("1 月は {} 日間", (b - a).count());

  // 日付に時刻を足す
  const local_seconds noon = a + 12h;
  std::println("{:%F %T}", noon);

  // 年月日に戻す
  const year_month_day ymd{b};
  std::println("{}", static_cast<unsigned>(ymd.month()));
}
```

```text title="実行結果"
1 月は 31 日間
2026-01-01 12:00:00
2
```

## ゲームでの使いどころ

プレイヤーの地域の「今日」を基準にした日替わり要素の、日付の計算に使います。

## よくあるミス

??? failure "UTC の日付と同じだと思う"
    日本では UTC より 9 時間早いので、日付が一日ずれることがあります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`sys_days`](sys_days.md) | UTC の日付 |
| [`local_time`](local_time.md) | 単位を選べる元の別名 |
| [`year_month_day`](year_month_day.md) | 年月日の組 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: local_days](https://cpprefjp.github.io/reference/chrono/local_t.html)
- [cppreference: std::chrono::local_days](https://en.cppreference.com/w/cpp/chrono/local_t)
