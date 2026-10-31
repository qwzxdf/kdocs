---
title: std::chrono::is_clock
summary: "型が chrono の「時計」の条件を満たすかを調べる型特性。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::is_clock

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <chrono>`
</div>

`std::chrono::time_point<Clock>` の `Clock` に、時計の条件を満たさない型を渡すと、分かりにくいエラーが出ます。ある型が「時計」として使えるかを、コンパイル時に調べる型特性が `std::chrono::is_clock` です。自作の時計を作るときの確認や、テンプレートの制約に使えます。

!!! tip "ポイント"
    - `is_clock_v<T>` が真なら、`T` は chrono の時計として使える
    - 条件は、`rep`、`period`、`duration`、`time_point`、`is_steady`、`now()` を持つこと
    - `system_clock` と `steady_clock` は真。`local_t` は偽（時計ではない）
    - C++20 から

!!! info "このページを読む前に"
    [`system_clock`](system_clock.md) と [`local_t`](local_t.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::is_clock {#is_clock}

<span class="ver ver-20">C++20</span>

```cpp
template <class T> struct is_clock;
template <class T> inline constexpr bool is_clock_v = is_clock<T>::value;
```

`T` が次のメンバーを持っていれば、真です。

| メンバー | 内容 |
| --- | --- |
| `T::rep` | 時間を数える型（整数や浮動小数点数） |
| `T::period` | 1 カウントが何秒か（`std::ratio`） |
| `T::duration` | `duration<rep, period>` |
| `T::time_point` | `time_point<T>` または、同じ意味の型 |
| `T::is_steady` | 巻き戻らない時計か（`bool` の定数） |
| `T::now()` | 現在の時点を返す関数 |

標準の時計は、`system_clock`、`steady_clock`、`high_resolution_clock`、`utc_clock`、`tai_clock`、`gps_clock`、`file_clock` がすべて真です。`local_t` は `now()` を持たないので偽です。

自作の時計を `time_point` に使う前に、`static_assert(is_clock_v<MyClock>)` と書いておくと、足りないメンバーがすぐ分かります。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

struct NotAClock {};

// 自作の時計: 必要なメンバーをそろえる
struct FrameClock {
  using rep = long long;
  using period = std::ratio<1, 60>;  // 1 カウントが 1/60 秒
  using duration = std::chrono::duration<rep, period>;
  using time_point = std::chrono::time_point<FrameClock>;
  static constexpr bool is_steady = true;
  static time_point now() noexcept { return time_point{duration{0}}; }
};

int main() {
  using namespace std::chrono;

  std::println("system_clock: {}", is_clock_v<system_clock>);
  std::println("steady_clock: {}", is_clock_v<steady_clock>);
  std::println("local_t:      {}", is_clock_v<local_t>);
  std::println("int:          {}", is_clock_v<int>);
  std::println("NotAClock:    {}", is_clock_v<NotAClock>);
  std::println("FrameClock:   {}", is_clock_v<FrameClock>);
}
```

```text title="実行結果"
system_clock: true
steady_clock: true
local_t:      false
int:          false
NotAClock:    false
FrameClock:   true
```

`FrameClock` は、1/60 秒を 1 カウントとする自作の時計で、必要なメンバーをそろえたので真です。

## ゲームでの使いどころ

フレーム数を時間の単位とする自作の時計を作り、`time_point<FrameClock>` で「何フレーム目」を型で表す、といった設計で使います。

## よくあるミス

??? failure "now() の static を忘れる"
    メンバー関数だと、時計の条件を満たさず、`is_clock_v` が偽になります。`static` にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`local_t`](local_t.md) | 時計ではない型の例 |
| [`time_point`](time_point.md) | 時計と組み合わせる型 |
| [`system_clock`](system_clock.md) | 標準の時計 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: is_clock](https://cpprefjp.github.io/reference/chrono/is_clock.html)
- [cppreference: std::chrono::is_clock](https://en.cppreference.com/w/cpp/chrono/is_clock)
