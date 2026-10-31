---
title: std::this_thread::sleep_until
summary: "今のスレッドを、指定した時刻まで止める。"
order: 76
group: this_thread
tags:
  - 並行処理
---

# std::this_thread::sleep_until

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <thread>`
</div>

`sleep_for` は、「いまから何秒眠る」ですが、`sleep_until` は、「何時何分何秒まで眠る」と、時刻を指定します。フレームの更新を、一定の間隔で正確に行うとき、前回の目標時刻に間隔を足していく書き方に向いています。

!!! tip "ポイント"
    - 指定した時刻まで、現在のスレッドを眠らせる
    - 時計は `steady_clock` を使うのが安全（巻き戻らない）
    - 時刻がすでに過ぎていれば、すぐ戻る
    - 眠りは、指定した時刻より遅れて起きることがある

!!! info "このページを読む前に"
    [`std::thread`](../thread.md) を先に読んでください。

## 関数の詳しい説明

### std::this_thread::sleep_until {#sleep_until}

<span class="ver ver-11">C++11</span>

```cpp
template <class Clock, class Duration>
void sleep_until(const std::chrono::time_point<Clock, Duration>& sleep_time);
```

`sleep_for(間隔)` を毎フレーム呼ぶと、処理にかかった時間のぶん、周期が延びていきます。`sleep_until` なら、「次の目標時刻」を、前回の目標時刻に間隔を足して求めるので、処理時間のばらつきがあっても、周期が一定に保たれます。

```cpp
auto next = steady_clock::now();
while (running) {
  next += 16ms;               // 目標時刻を進める
  Update();
  std::this_thread::sleep_until(next);
}
```

システムの時計（`system_clock`）を指定すると、時刻の調整で、眠る時間が変わります。`steady_clock` を使います。

実際に起きる時刻は、OS のタイマーの精度に依存します。Windows では、既定で 15 ミリ秒ほどの粗さがあります。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>
#include <thread>

int main() {
  using namespace std::chrono_literals;
  using Clock = std::chrono::steady_clock;

  const auto target = Clock::now() + 20ms;
  std::this_thread::sleep_until(target);
  std::println("目標時刻以降に起きた: {}", Clock::now() >= target);

  // 過ぎた時刻なら、すぐ戻る
  const auto before = Clock::now();
  std::this_thread::sleep_until(before - 1s);
  std::println("すぐ戻った: {}", Clock::now() - before < 500ms);
}
```

```text title="実行結果"
目標時刻以降に起きた: true
すぐ戻った: true
```

## ゲームでの使いどころ

固定の更新レート（60 回/秒）で動くゲーム ループの、フレーム間の待ちに使います。

## よくあるミス

??? failure "system_clock を使う"
    時刻の調整で、眠る長さが変わります。`steady_clock` にします。

??? failure "起きる時刻が正確だと思う"
    OS の精度の分だけ、遅れます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`sleep_for`](sleep_for.md) | 時間を指定して眠る |
| [`yield`](yield.md) | CPU を譲る |
| [`steady_clock`](../../utilities/chrono/steady_clock.md) | 巻き戻らない時計 |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::this_thread::sleep_until](https://cpprefjp.github.io/reference/thread/this_thread/sleep_until.html)
- [cppreference: std::this_thread::sleep_until](https://en.cppreference.com/w/cpp/thread/sleep_until)
