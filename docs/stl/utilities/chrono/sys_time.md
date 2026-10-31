---
title: std::chrono::sys_time
summary: "system_clock の時点を表す別名（単位を選べる）。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::sys_time

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

`system_clock::now()` が返す時点を、秒の細かさで持ちたい、日の細かさで持ちたい。`std::chrono::sys_time<Duration>` は、`system_clock` の時点（`time_point`）を、`Duration` の単位で表す別名です。`sys_seconds` や `sys_days` は、この `sys_time` の単位を決めた短い名前です。

!!! tip "ポイント"
    - `time_point<system_clock, Duration>` の別名
    - 起点は 1970-01-01 00:00:00 UTC（Unix 時間）。C++20 で規格が決めた
    - うるう秒は数えない。1 日は常に 86400 秒
    - タイムゾーンを含まない。UTC として扱われる

!!! info "このページを読む前に"
    [`system_clock`](system_clock.md) と [`time_point`](time_point.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::sys_time {#sys_time}

<span class="ver ver-20">C++20</span>

```cpp
template <class Duration>
using sys_time = time_point<system_clock, Duration>;

using sys_seconds = sys_time<seconds>;
using sys_days    = sys_time<days>;
```

C++20 以前の `system_clock::time_point` は、単位が実装ごとに違う（ナノ秒、100 ナノ秒など）ものでした。`sys_time<Duration>` は、単位を自分で選べます。ログに書く時刻は秒、日付は日にそろえる、という使い分けができます。

起点が 1970-01-01 の UTC と、規格で決められたことで、`time_since_epoch().count()` が Unix 時間と同じ意味を持つようになりました。うるう秒は数えないので、時計の秒数と、日付の計算が一致します。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  // 単位を選んで時点を作る
  const sys_time<milliseconds> ms{milliseconds{1500}};
  const sys_seconds s = floor<seconds>(ms);
  std::println("{} ミリ秒 → {} 秒", ms.time_since_epoch().count(),
               s.time_since_epoch().count());

  // 起点は 1970-01-01
  const sys_seconds epoch{};
  std::println("{:%F %T}", epoch);

  // 1 日ぶん進める
  std::println("{:%F}", sys_days{} + days{1});
}
```

```text title="実行結果"
1500 ミリ秒 → 1 秒
1970-01-01 00:00:00
1970-01-02
```

## ゲームでの使いどころ

セーブデータに保存する時刻は、`sys_seconds` の `count()` を `int64_t` で書くと、環境によらず同じ意味になります。

## よくあるミス

??? failure "ローカル時刻だと思う"
    `sys_time` は UTC です。日本時間 9 時間のずれがあります。ローカル時刻は `zoned_time` を通します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`sys_seconds`](sys_seconds.md) | 秒の単位 |
| [`sys_days`](sys_days.md) | 日の単位 |
| [`local_time`](local_time.md) | タイムゾーンのない地域の時刻 |
| [`utc_time`](utc_time.md) | うるう秒を数える |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: sys_time](https://cpprefjp.github.io/reference/chrono/system_clock.html)
- [cppreference: std::chrono::sys_time](https://en.cppreference.com/w/cpp/chrono/system_clock)
