---
title: std::chrono::clock_cast
summary: "時計どうしの時点を、別の時計の時点に変換する。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::clock_cast

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

`system_clock` の時点を `utc_clock` や `file_clock` に直したいことがあります（たとえばファイルの更新時刻をカレンダー時刻に）。`clock_cast<DestClock>(tp)` は、時計の種類が違う `time_point` を目的の時計に変換します。

!!! tip "ポイント"
    - 変換元と先の組み合わせは、`sys_clock`・`utc_clock`・`tai_clock`・`gps_clock`・`file_clock` の間なら動く。
    - 戻り値は目的の時計の `time_point`。

!!! info "このページを読む前に"
    [`<chrono>`](../chrono.md) の概要と [`duration`](duration.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::clock_cast {#clock_cast}

```cpp
template <class DestClock, class SourceClock, class Duration>
auto clock_cast(const time_point<SourceClock, Duration>& t);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `DestClock` | テンプレート引数 | 変換先の時計 |
| `t` | time_point | 変換元の時点 |

- 戻り値: 変換先の時計の `time_point`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;
  auto sys = sys_days{2024y / January / 1};
  auto tai = clock_cast<tai_clock>(sys);
  auto back = clock_cast<system_clock>(tai);
  std::println("{}", back == sys);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ファイルの更新時刻をカレンダー時刻にする | `clock_cast<system_clock>(fs::last_write_time(p))` |

## よくあるミス

??? failure "変換できない時計を指定する"
    `steady_clock` のように壁時計と結びつかない時計は変換できません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`file_clock`](file_clock.md) | ファイルの時計 |
| [`system_clock`](system_clock.md) | カレンダー時刻 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 時計の種類が違う time_point を変換
    - [x] steady_clock は対象外
    - [x] ファイル時刻の変換で役立つ

## 関連ページ

- [cpprefjp: std::chrono::clock_cast](https://cpprefjp.github.io/reference/chrono/clock_cast.html)
- [cppreference: std::chrono::clock_cast](https://en.cppreference.com/w/cpp/chrono/clock_cast)
