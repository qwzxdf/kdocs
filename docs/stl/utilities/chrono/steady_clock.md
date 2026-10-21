---
title: std::chrono::steady_clock
summary: "巻き戻らない時計。時間の計測に使う。"
order: 3
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::steady_clock

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-11">C++11</span>
`#include <chrono>`
</div>

`std::chrono::steady_clock` は、**時間が巻き戻らないことが保証された時計**です。PC の時刻を変更されても、夏時間の切り替えがあっても、進み方は変わりません。フレーム時間や処理時間の**計測**には、必ずこれを使います。カレンダーの時刻は表せません（それは [`system_clock`](system_clock.md)）。

!!! tip "ポイント"
    - <strong>経過時間の計測は `steady_clock`。</strong> `system_clock` は時刻を変更されると巻き戻るので、計測には使わない。
    - `steady_clock::now()` の差が `duration`（経過時間）。
    - 「今何時か」は分からない（基準時刻は不定）。

!!! info "このページを読む前に"
    [`std::chrono`](../chrono.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### steady_clock::now {#steady_clock}

```cpp
struct steady_clock {
  using time_point = std::chrono::time_point<steady_clock>;
  static constexpr bool is_steady = true;
  static time_point now() noexcept;
};
```

- 戻り値: 今の時点（`time_point`）
- 計算量: O(1)（1 回あたり数十ナノ秒）

```cpp
#include <chrono>
#include <print>

int main() {
  using Clock = std::chrono::steady_clock;

  auto start = Clock::now();
  auto end = Clock::now();
  std::println("巻き戻らない: {} / is_steady: {}", end >= start, Clock::is_steady);
}
```

```text title="実行結果"
巻き戻らない: true / is_steady: true
```

### フレーム時間の測り方 {#frame_time}

```cpp
// 毎フレームの先頭で
auto now = Clock::now();
std::chrono::duration<float> dt = now - last;   // 秒（小数）
last = now;
```

- 戻り値: 前のフレームからの経過時間（秒、小数）
- 計算量: O(1)

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| デルタタイム（前のフレームからの経過秒） | `duration<float>(now - last).count()` |
| 処理時間の計測（プロファイル） | `steady_clock::now()` を処理の前後で取る |

## よくあるミス

??? failure "system_clock で計測する"
    時刻の変更（NTP の同期、手動の変更）で、差が負になったり、極端に大きくなったりします。計測は `steady_clock` です。

??? failure "high_resolution_clock を使う"
    実体が `system_clock` の環境があり、巻き戻ることがあります。`steady_clock` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`system_clock`](system_clock.md) | 現実の時刻（カレンダー） |
| [`high_resolution_clock`](high_resolution_clock.md) | 使わない |
| `QueryPerformanceCounter` | Windows の高精度タイマー（`steady_clock` が内部で使っている） |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 計測は `steady_clock`
    - [x] 巻き戻らない
    - [x] 今何時かは分からない

## 関連ページ

- [cpprefjp: std::chrono::steady_clock](https://cpprefjp.github.io/reference/chrono/steady_clock.html)
- [cppreference: std::chrono::steady_clock](https://en.cppreference.com/w/cpp/chrono/steady_clock)
