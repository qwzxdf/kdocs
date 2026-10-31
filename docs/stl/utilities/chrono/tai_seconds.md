---
title: std::chrono::tai_seconds
summary: "tai_clock の時点（秒単位）を表す別名。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::tai_seconds

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

`std::chrono::tai_seconds` は、`tai_clock` の時点を秒の単位で表す型で、`tai_time<seconds>` の別名です。`clock_cast<tai_clock>(sys_seconds)` の結果を受けるのに使います。

!!! tip "ポイント"
    - `tai_time<seconds>` の別名
    - 起点は 1958-01-01。`sys_seconds` との差は、378691210 秒 + うるう秒の累計
    - 書式は `{:%F %T}`
    - `clock_cast` で相互に変換する

!!! info "このページを読む前に"
    [`tai_time`](tai_time.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::tai_seconds {#tai_seconds}

<span class="ver ver-20">C++20</span>

```cpp
using tai_seconds = tai_time<seconds>;
```

書式にかけると、TAI の日付と時刻が表示されます。2026-01-01 00:00:00 UTC は、TAI では 2026-01-01 00:00:37 です。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  const sys_seconds s = sys_days{2026y / January / 1};
  const tai_seconds t = clock_cast<tai_clock>(s);

  std::println("sys: {:%F %T}", s);
  std::println("tai: {:%F %T}", t);
}
```

```text title="実行結果"
sys: 2026-01-01 00:00:00
tai: 2026-01-01 00:00:37
```

## ゲームでの使いどころ

使いません。

## よくあるミス

??? failure "表示が同じ時刻になると思う"
    37 秒進んだ値で表示されます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`tai_time`](tai_time.md) | 単位を選べる元の別名 |
| [`utc_seconds`](utc_seconds.md) | UTC の秒 |
| [`gps_seconds`](gps_seconds.md) | GPS の秒 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: tai_seconds](https://cpprefjp.github.io/reference/chrono/tai_clock.html)
- [cppreference: std::chrono::tai_seconds](https://en.cppreference.com/w/cpp/chrono/tai_clock)
