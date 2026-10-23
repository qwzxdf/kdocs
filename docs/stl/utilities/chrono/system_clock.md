---
title: std::chrono::system_clock
summary: "現実の時刻（カレンダー）を表す時計。"
order: 4
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::system_clock

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-11">C++11</span>
`#include <chrono>`
</div>

セーブデータに日時を残したい、ログにタイムスタンプを付けたい。これらには、現実の日時（カレンダーの時刻）が要ります。`std::chrono::system_clock` は、OS の時計に基づく時計で、「いま何時か」「ファイルの更新日時」を扱えます。ユーザーが時刻を変えたり、ネットワークで時刻が補正されたりすると、巻き戻ることがあります。経過時間の計測には、向いていません。

!!! tip "ポイント"
    - 現在日時の表示や記録は `system_clock`。
    - `std::format` / `std::println` で、日時を直接書式化できる（C++20）。
    - `time_t`（C の時刻）との相互変換は `to_time_t` / `from_time_t`。

!!! info "このページを読む前に"
    [`std::chrono`](../chrono.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### system_clock {#system_clock}

```cpp
struct system_clock {
  using time_point = std::chrono::time_point<system_clock>;
  static constexpr bool is_steady = false;
  static time_point now() noexcept;
  static std::time_t to_time_t(const time_point& t) noexcept;
  static time_point from_time_t(std::time_t t) noexcept;
};
```

- 戻り値: `now()` は今の時点
- 計算量: O(1)

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;

  // 1970-01-01 から 1 日（86400 秒）後の時点
  auto tp = system_clock::from_time_t(86400);
  std::println("{:%F %T}", floor<seconds>(tp));  // 秒未満を切り捨てて出力する
}
```

```text title="実行結果"
1970-01-02 00:00:00
```

### now {#now}

```cpp
static time_point system_clock::now() noexcept;
```

- 計算量: 定数

今の時点を返します。現実の日時の時計なので、時刻合わせで巻き戻ることがあります。

### is_steady {#is_steady}

```cpp
static constexpr bool is_steady;
```

- 計算量: コンパイル時

巻き戻らず、一定の速さで進む時計なら `true`。`system_clock` は `false` です。

### to_time_t {#to_time_t}

```cpp
static std::time_t system_clock::to_time_t(const time_point& t) noexcept;
```

- 計算量: 定数

`time_point` を C の `time_t`（秒単位）に変換します。`std::ctime`・`localtime` など、C の関数に渡すときに使います。

### from_time_t {#from_time_t}

```cpp
static time_point system_clock::from_time_t(std::time_t t) noexcept;
```

- 計算量: 定数

C の `time_t` を `time_point` に変換します。

## ゲームでの使いどころ

セーブデータのタイムスタンプに使います。保存した日時を `system_clock::now()` で取り、ファイルに記録します。読み込み時に表示して「前回のプレイ日時」を出せます。

ログの日時にも使います。C++20 では、`std::format("{:%F %T}", now)` のように、日時を直接書式化できます。

時間の長さの計測には、`steady_clock` を使います。ゲームの時間経過を `system_clock` で測ると、時計を変えられたときに、イベントが飛んだり戻ったりします。

## よくあるミス

??? failure "秒未満まで表示されて長くなる"
    `{:%T}` は、`system_clock` の精度（ナノ秒など）まで表示します。`std::chrono::floor<std::chrono::seconds>(tp)` で秒に切り捨ててから出力します。

??? failure "時刻の変更で計測が壊れる"
    時計を変更されると差が負になることがあります。計測には使いません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`steady_clock`](steady_clock.md) | 計測用。巻き戻らない |
| [`zoned_time`](zoned_time.md) | タイムゾーンつきの日時 |
| [`year_month_day`](year_month_day.md) | カレンダーの日付 |

## コンパイラ対応

C++11 から使えます。書式化は C++20（GCC 13 / MSVC 19.29 以降）です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 現実の日時を表す時計
    - [x] 計測には使わない
    - [x] 書式化は `{:%F %T}`

## 関連ページ

- [cpprefjp: std::chrono::system_clock](https://cpprefjp.github.io/reference/chrono/system_clock.html)
- [cppreference: std::chrono::system_clock](https://en.cppreference.com/w/cpp/chrono/system_clock)
