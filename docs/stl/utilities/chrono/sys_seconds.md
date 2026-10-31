---
title: std::chrono::sys_seconds
summary: "system_clock の時点を、秒の単位で表す別名。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::sys_seconds

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

ログに書く時刻やセーブデータの保存日時は、秒の細かさで十分です。`std::chrono::sys_seconds` は、`system_clock` の時点を秒の単位で表す型で、`sys_time<seconds>` の別名です。`system_clock::now()` を `floor<seconds>` で切り捨てて作ります。

!!! tip "ポイント"
    - `sys_time<seconds>` の別名
    - `floor<seconds>(system_clock::now())` で現在時刻を秒にそろえる
    - `time_since_epoch().count()` が Unix 時間（秒）
    - 書式は `{:%F %T}`

!!! info "このページを読む前に"
    [`sys_time`](sys_time.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::sys_seconds {#sys_seconds}

<span class="ver ver-20">C++20</span>

```cpp
using sys_seconds = sys_time<seconds>;
```

`system_clock::now()` はナノ秒に近い細かさの値を返します。秒にそろえるには、`floor<seconds>` で切り捨てます。`time_point_cast<seconds>` でも変換できますが、1970 年より前の時刻では、切り捨てにならないので、`floor` が安全です。

`{:%F %T}` で、`2026-01-01 00:00:00` の形に整形できます。`%T` は時・分・秒です。秒の小数部が要るなら、`sys_time<milliseconds>` などを使います。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  // 2026-01-01 00:00:00 UTC
  const sys_seconds t = sys_days{2026y / January / 1};
  std::println("{:%F %T}", t);
  std::println("Unix 時間: {}", t.time_since_epoch().count());

  // 現在時刻を秒にそろえる
  const sys_seconds now = floor<seconds>(system_clock::now());
  std::println("2026 年以降: {}", now >= t);
}
```

```text title="実行結果"
2026-01-01 00:00:00
Unix 時間: 1767225600
2026 年以降: true
```

## ゲームでの使いどころ

セーブデータの更新日時を `int64_t` の秒で保存し、読み込み時に `sys_seconds{seconds{value}}` に戻します。

## よくあるミス

??? failure "now() をそのまま秒として保存する"
    `now()` は細かい単位なので、`count()` は秒ではなくナノ秒に近い数です。`floor<seconds>` で秒にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`sys_time`](sys_time.md) | 単位を選べる元の別名 |
| [`sys_days`](sys_days.md) | 日の単位 |
| [`utc_seconds`](utc_seconds.md) | うるう秒を数える |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: sys_seconds](https://cpprefjp.github.io/reference/chrono/system_clock.html)
- [cppreference: std::chrono::sys_seconds](https://en.cppreference.com/w/cpp/chrono/system_clock)
