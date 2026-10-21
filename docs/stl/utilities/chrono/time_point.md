---
title: std::chrono::time_point
summary: "時計の上の「ある時点」。"
order: 2
group: 時間（std::chrono）
tags:
  - ユーティリティ
---

# std::chrono::time_point

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-11">C++11</span>
`#include <chrono>`
</div>

`std::chrono::time_point` は、**ある時計（`Clock`）の上の「ある時点」**を表すクラスです。内部では「その時計の基準時刻からの経過時間（`duration`）」を持っています。時点どうしを引くと `duration`（時間の長さ）、時点に長さを足すと別の時点になります。

!!! tip "ポイント"
    - `time_point - time_point` が `duration`、`time_point + duration` が `time_point`。
    - **違う時計の時点どうしは比べられない**（型が違う）。
    - `time_since_epoch()` で、基準時刻からの経過時間が取れる。

!!! info "このページを読む前に"
    [`std::chrono`](../chrono.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::chrono::time_point {#time_point}

```cpp
template <class Clock, class Duration = typename Clock::duration>
class time_point;
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `Clock` | 時計 | `steady_clock`、`system_clock` など |  |
| `Duration` | `duration` | 時点を表す精度 | `Clock::duration` |

- 戻り値: （クラス）。`+` `-` `<` `==` などが使える
- 計算量: 演算は O(1)

```cpp
#include <chrono>
#include <print>

int main() {
  using namespace std::chrono;
  using namespace std::chrono_literals;

  steady_clock::time_point t0{};   // 基準時刻（エポック）
  auto t1 = t0 + 250ms;            // 250ms 後の時点

  std::println("差 {} / 後ろのほうが新しい？ {}", duration_cast<milliseconds>(t1 - t0), t1 > t0);
}
```

```text title="実行結果"
差 250ms / 後ろのほうが新しい？ true
```

### time_since_epoch {#time_since_epoch}

```cpp
constexpr duration time_since_epoch() const;
```

- 戻り値: 基準時刻（エポック）からの経過時間
- 計算量: O(1)

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| フレームの開始時刻の保存 | `auto last = steady_clock::now();` |
| イベントの発火時刻 | `time_point<steady_clock> fire_at = now + 3s;` |

## よくあるミス

??? failure "違う時計の time_point を引き算する"
    `system_clock` の時点と `steady_clock` の時点は比べられません（コンパイルエラー）。

## 類似

| 名前 | 違い |
| --- | --- |
| [`steady_clock`](steady_clock.md) | 計測用の時計 |
| [`duration`](duration.md) | 時間の長さ |
| [`system_clock`](system_clock.md) | カレンダーの時刻 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 時計の上の「ある時点」
    - [x] 差は duration、足すと別の時点
    - [x] 違う時計は比べられない

## 関連ページ

- [cpprefjp: std::chrono::time_point](https://cpprefjp.github.io/reference/chrono/time_point.html)
- [cppreference: std::chrono::time_point](https://en.cppreference.com/w/cpp/chrono/time_point)
