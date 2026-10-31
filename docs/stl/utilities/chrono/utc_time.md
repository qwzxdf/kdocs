---
title: std::chrono::utc_time
summary: "utc_clock の時点を表す別名（単位を選べる）。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::utc_time

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

`std::chrono::utc_time<Duration>` は、`utc_clock` の時点を `Duration` の単位で表す型です。`time_point<utc_clock, Duration>` の別名で、うるう秒を数えた UTC の時刻を、秒やミリ秒の細かさで持ちたいときに使います。

!!! tip "ポイント"
    - `time_point<utc_clock, Duration>` の別名
    - うるう秒を挿入した時刻（23:59:60）を表せる
    - `sys_time` とは別の型。`clock_cast` で変換する
    - 秒の単位は `utc_seconds`

!!! info "このページを読む前に"
    [`utc_clock`](utc_clock.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::utc_time {#utc_time}

<span class="ver ver-20">C++20</span>

```cpp
template <class Duration>
using utc_time = time_point<utc_clock, Duration>;
using utc_seconds = utc_time<seconds>;
```

`sys_time` では、23:59:60 という時刻は存在せず、直前の秒にまとめられます。`utc_time` では、うるう秒が実在する時刻として扱われます。書式にかけたとき（`{:%T}`）、うるう秒は `23:59:60` と表示されます。

2 つの `utc_time` の差は、うるう秒を含めた本当の経過時間です。1 日をまたぐ計測で、うるう秒を挟んだとき、`sys_time` の差とは 1 秒ずれます。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  // 2016-12-31 は、23:59:60 のうるう秒が入った日
  const sys_seconds before = sys_days{2016y / December / 31} + 23h + 59min + 59s;
  const sys_seconds after = before + 2s;

  // system_clock では 2 秒の差
  std::println("sys の差: {} 秒", (after - before).count());

  // utc_clock では、うるう秒が入るので 3 秒の差
  const utc_seconds ub = clock_cast<utc_clock>(before);
  const utc_seconds ua = clock_cast<utc_clock>(after);
  std::println("utc の差: {} 秒", (ua - ub).count());
}
```

```text title="実行結果"
sys の差: 2 秒
utc の差: 3 秒
```

2016 年 12 月 31 日の最後に、うるう秒が入っているので、UTC の経過時間は 1 秒長くなります。

## ゲームでの使いどころ

ゲームでは使いません。うるう秒を含めた経過時間が要る場面にだけ使います。

## よくあるミス

??? failure "sys_time と直接引き算する"
    型が違うので、コンパイルできません。`clock_cast` で同じ時計にそろえます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`utc_seconds`](utc_seconds.md) | 秒の単位 |
| [`sys_time`](sys_time.md) | うるう秒を数えない |
| [`tai_time`](tai_time.md) | TAI の時点 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: utc_time](https://cpprefjp.github.io/reference/chrono/utc_clock.html)
- [cppreference: std::chrono::utc_time](https://en.cppreference.com/w/cpp/chrono/utc_clock)
