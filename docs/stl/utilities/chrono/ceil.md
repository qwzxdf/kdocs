---
title: std::chrono::ceil
summary: "duration / time_point を、指定した単位に切り上げる。"
order: 900
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::ceil

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <chrono>`
</div>

経過時間 1500 ミリ秒を「何秒かかったか」と表示するとき、`duration_cast<seconds>` は 1 秒に切り捨てます。「少なくとも何秒必要か」、たとえば、タイマーを 1500 ミリ秒を超える最小の秒数に丸めたいときは、切り上げが要ります。`std::chrono::ceil<ToDuration>` は、指定した単位に切り上げて変換します。

!!! tip "ポイント"
    - `ceil<seconds>(1500ms)` は 2 秒。端数があれば、常に上に丸める
    - `floor`（切り捨て）、`round`（四捨五入）、`duration_cast`（0 に向かって丸める）と対になる
    - `duration` にも `time_point` にも使える
    - 負の値では、`duration_cast` と違い、数直線上で大きいほうに丸める（-1.5 秒 → -1 秒）

!!! info "このページを読む前に"
    [`duration_cast`](duration_cast.md) と [`floor`](floor.md) を先に読んでください。

## 関数の詳しい説明

### std::chrono::ceil {#ceil}

<span class="ver ver-17">C++17</span>

```cpp
template <class ToDuration, class Rep, class Period>
constexpr ToDuration ceil(const duration<Rep, Period>& d);

template <class ToDuration, class Clock, class Duration>
constexpr time_point<Clock, ToDuration> ceil(const time_point<Clock, Duration>& tp);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `ToDuration` | テンプレート引数 | 変換先の `duration` の型 |
| `d` / `tp` | `duration` / `time_point` | 変換する値 |

`d` を `ToDuration` に変換したとき、端数があれば、大きい側（正の無限大に近い側）へ丸めます。ちょうど割り切れるなら、そのままです。

`duration_cast` は 0 に向かって丸める（切り捨てに近い）ので、負の値では結果が違います。`-1500ms` を `duration_cast<seconds>` すると -1 秒、`ceil<seconds>` も -1 秒、`floor<seconds>` は -2 秒です。正の値の `ceil` は常に切り上げですが、負の値の `ceil` は、0 に近づく向きです。

`ToDuration` が小数型の `duration` のときは、端数が出ないので、`duration_cast` と同じ結果になります。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;
  using namespace std::chrono_literals;

  std::println("ceil 1500ms  → {} 秒", ceil<seconds>(1500ms).count());
  std::println("ceil 2000ms  → {} 秒", ceil<seconds>(2000ms).count());
  std::println("ceil 1ms     → {} 秒", ceil<seconds>(1ms).count());
  std::println("ceil -1500ms → {} 秒", ceil<seconds>(-1500ms).count());

  // 比較: 同じ値の cast
  std::println("duration_cast 1500ms → {} 秒", duration_cast<seconds>(1500ms).count());
}
```

```text title="実行結果"
ceil 1500ms  → 2 秒
ceil 2000ms  → 2 秒
ceil 1ms     → 1 秒
ceil -1500ms → -1 秒
duration_cast 1500ms → 1 秒
```

## ゲームでの使いどころ

「残り 1.2 秒」を「あと 2 秒」と表示するカウントダウンで使います。切り捨てて「あと 1 秒」と出すと、0 になったのに残っている状態が見えてしまいます。

## よくあるミス

??? failure "負の値で、切り上げが小さい絶対値になるのを知らない"
    `ceil<seconds>(-1500ms)` は -1 秒です。絶対値は小さくなります。

??? failure "duration_cast と同じだと思う"
    正の値では、`duration_cast` は切り捨てです。端数を残さず上に丸めたいなら、`ceil` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`floor`](floor.md) | 切り捨てる（負の無限大の向き） |
| [`round`](round.md) | 四捨五入（ちょうど半分は偶数へ） |
| [`duration_cast`](duration_cast.md) | 0 に向かって丸める |

## コンパイラ対応

C++17 から使えます。

## 関連ページ

- [cpprefjp: ceil](https://cpprefjp.github.io/reference/chrono/ceil.html)
- [cppreference: std::chrono::ceil](https://en.cppreference.com/w/cpp/chrono/ceil)
