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

`std::this_thread::sleep_until` は、**今のスレッドを指定した時刻まで止める**関数です。「次のフレームの開始時刻まで待つ」のように、**期限が決まっている**待ち方に向いています。時間の長さで指定する [`sleep_for`](sleep_for.md) と違い、処理にかかった時間のぶれが積み重なりません。

!!! tip "ポイント"
    - 時刻は `steady_clock::time_point` で指定する。
    - 一定の間隔で処理をするなら、「前回の予定時刻 + 間隔」を渡すと、ずれが溜まらない。
    - 指定時刻を過ぎていれば、すぐ戻る。

!!! info "このページを読む前に"
    [並行処理の基本](../../../basics/concurrency.md) を先に読んでください。

## 関数の詳しい説明

### std::this_thread::sleep_until {#sleep_until}

```cpp
template <class Clock, class Duration>
void sleep_until(const std::chrono::time_point<Clock, Duration>& time);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `time` | `time_point` | 再開する時刻 |

- 戻り値: なし
- 計算量: 指定時刻まで

```cpp
#include <chrono>
#include <print>
#include <thread>

int main() {
  using namespace std::chrono_literals;

  auto wake = std::chrono::steady_clock::now() + 10ms;
  std::this_thread::sleep_until(wake);
  std::println("起きた: {}", std::chrono::steady_clock::now() >= wake);
}
```

```text title="実行結果"
起きた: true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 一定周期（例: 10ms ごと）で処理するスレッド | `next += 10ms; sleep_until(next);` |

## よくあるミス

??? failure "system_clock の時刻で指定する"
    時刻を変更されると待ち時間が狂います。`steady_clock` で指定します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::this_thread::sleep_for`](sleep_for.md) | 時間の長さで指定 |
| [`std::chrono::steady_clock`](../../utilities/chrono/steady_clock.md) | time_point の元 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 時刻まで止める
    - [x] 一定周期の処理に向く
    - [x] `steady_clock` で指定

## 関連ページ

- [cpprefjp: std::this_thread::sleep_until](https://cpprefjp.github.io/reference/thread/this_thread/sleep_until.html)
- [cppreference: std::this_thread::sleep_until](https://en.cppreference.com/w/cpp/thread/sleep_until)
